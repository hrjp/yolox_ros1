#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) Megvii, Inc. and its affiliates.

import argparse
from copy import deepcopy
#from distutils.command.build_scripts import first_line_re
import os
import time
from loguru import logger

import cv2

import torch

from yolox.data.data_augment import ValTransform
from yolox.data.datasets import COCO_CLASSES
from yolox.exp import get_exp
from yolox.utils import fuse_model, get_model_info, postprocess, vis

import rospy
import std_msgs.msg
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

#ros setting
rospy.init_node("yolox_ros1")
bridge = CvBridge()
first_callback=False
def image_callback(msg):
    global sub_image_msg, sub_image,first_callback
    sub_image_msg=msg
    sub_image=bridge.imgmsg_to_cv2(sub_image_msg,"bgr8")
    first_callback=True
rospy.Subscriber("image_raw", Image, image_callback)
image_pub = rospy.Publisher("yolo_image", Image, queue_size=1)
trim_image_pub = rospy.Publisher("tl_image", Image, queue_size=1)
rate = rospy.Rate(10)
#ros param
weight_path = rospy.get_param('~weight_file',os.path.dirname(__file__)+'/../config/yolox/weight/yolox_s.pth')
exp_path = rospy.get_param('~exp_file',os.path.dirname(__file__)+'/../config/yolox/exp/yolox_s.py')
compute_device = rospy.get_param('~compute_device','gpu')


IMAGE_EXT = [".jpg", ".jpeg", ".webp", ".bmp", ".png"]

def make_parser():
    parser = argparse.ArgumentParser("YOLOX Demo!")
    parser.add_argument(
        "demo", default="image", help="demo type, eg. image, video and webcam"
    )
    parser.add_argument("-expn", "--experiment-name", type=str, default=None)
    parser.add_argument("-n", "--name", type=str, default=None, help="model name")

    parser.add_argument(
        "--path", default="./assets/dog.jpg", help="path to images or video"
    )
    parser.add_argument("--camid", type=int, default=0, help="webcam demo camera id")
    parser.add_argument(
        "--save_result",
        action="store_true",
        help="whether to save the inference result of image/video",
    )

    # exp file
    parser.add_argument(
        "-f",
        "--exp_file",
        default=None,
        type=str,
        help="please input your experiment description file",
    )
    parser.add_argument("-c", "--ckpt", default=None, type=str, help="ckpt for eval")
    parser.add_argument(
        "--device",
        default="cpu",
        type=str,
        help="device to run our model, can either be cpu or gpu",
    )
    parser.add_argument("--conf", default=0.3, type=float, help="test conf")
    parser.add_argument("--nms", default=0.3, type=float, help="test nms threshold")
    parser.add_argument("--tsize", default=None, type=int, help="test img size")
    parser.add_argument(
        "--fp16",
        dest="fp16",
        default=False,
        action="store_true",
        help="Adopting mix precision evaluating.",
    )
    parser.add_argument(
        "--legacy",
        dest="legacy",
        default=False,
        action="store_true",
        help="To be compatible with older versions",
    )
    parser.add_argument(
        "--fuse",
        dest="fuse",
        default=False,
        action="store_true",
        help="Fuse conv and bn for testing.",
    )
    parser.add_argument(
        "--trt",
        dest="trt",
        default=False,
        action="store_true",
        help="Using TensorRT model for testing.",
    )
    return parser

class Predictor(object):
    def __init__(
        self,
        model,
        exp,
        cls_names=COCO_CLASSES,
        trt_file=None,
        decoder=None,
        device="cpu",
        fp16=False,
        legacy=False,
    ):
        self.model = model
        self.cls_names = cls_names
        self.decoder = decoder
        self.num_classes = exp.num_classes
        self.confthre = exp.test_conf
        self.nmsthre = exp.nmsthre
        self.test_size = exp.test_size
        self.device = device
        self.fp16 = fp16
        self.preproc = ValTransform(legacy=legacy)
        if trt_file is not None:
            from torch2trt import TRTModule

            model_trt = TRTModule()
            model_trt.load_state_dict(torch.load(trt_file))

            x = torch.ones(1, 3, exp.test_size[0], exp.test_size[1]).cuda()
            self.model(x)
            self.model = model_trt

    def inference(self, img):
        img_info = {"id": 0}
        if isinstance(img, str):
            img_info["file_name"] = os.path.basename(img)
            img = cv2.imread(img)
        else:
            img_info["file_name"] = None

        height, width = img.shape[:2]
        img_info["height"] = height
        img_info["width"] = width
        img_info["raw_img"] = img

        ratio = min(self.test_size[0] / img.shape[0], self.test_size[1] / img.shape[1])
        img_info["ratio"] = ratio

        img, _ = self.preproc(img, None, self.test_size)
        img = torch.from_numpy(img).unsqueeze(0)
        img = img.float()
        if self.device == "gpu":
            img = img.cuda()
            if self.fp16:
                img = img.half()  # to FP16

        with torch.no_grad():
            t0 = time.time()
            outputs = self.model(img)
            if self.decoder is not None:
                outputs = self.decoder(outputs, dtype=outputs.type())
            outputs = postprocess(
                outputs, self.num_classes, self.confthre,
                self.nmsthre, class_agnostic=True
            )
            logger.info("Infer time: {:.4f}s".format(time.time() - t0))
        return outputs, img_info

    def visual(self, output, img_info, cls_conf=0.35):
        ratio = img_info["ratio"]
        img = img_info["raw_img"]
        #if output is None:
        #    return
        output = output.cpu()

        bboxes = output[:, 0:4]
        bboxes_int =bboxes
        # preprocessing: resize
        bboxes /= ratio

        cls = output[:, 6]
        scores = output[:, 4] * output[:, 5]

        vis_res = vis(img, bboxes, scores, cls, cls_conf, self.cls_names)
        names=[]
        for name_num in cls:
            names.append(self.cls_names[int(name_num)])

        return vis_res,bboxes,scores,names


def ros_main(predictor, vis_folder, current_time, args):

    while not rospy.is_shutdown():
        frame=deepcopy(sub_image)
        outputs, img_info = predictor.inference(sub_image)
        #yolox result
        if outputs[0] != None:
            result_frame,bboxes,scores,names = predictor.visual(outputs[0], img_info, predictor.confthre)
            for i, name in enumerate(names):
                if(name=='traffic light'):
                    trim_frame=frame[int(bboxes[i][1]):int(bboxes[i][3]), int(bboxes[i][0]):int(bboxes[i][2])]
                    width=bboxes[i][3]-bboxes[i][1]
                    height=bboxes[i][2]-bboxes[i][0]
                    #????????????????????????????????????
                    if width>height:
                        trim_msg=bridge.cv2_to_imgmsg(trim_frame, encoding="bgr8")
                        trim_image_pub.publish(trim_msg)
                        break
            msg = bridge.cv2_to_imgmsg(result_frame, encoding="bgr8")
            image_pub.publish(msg)
            #cv2.namedWindow('color_image', cv2.WINDOW_AUTOSIZE)
            #cv2.imshow('color_image', frame)
            #cv2.waitKey(1)
        rate.sleep()


def main(exp, args):
    if not args.experiment_name:
        args.experiment_name = exp.exp_name

    file_name = os.path.join(exp.output_dir, args.experiment_name)
    os.makedirs(file_name, exist_ok=True)

    vis_folder = None
    if args.save_result:
        vis_folder = os.path.join(file_name, "vis_res")
        os.makedirs(vis_folder, exist_ok=True)

    if args.trt:
        args.device = "gpu"

    logger.info("Args: {}".format(args))

    if args.conf is not None:
        exp.test_conf = args.conf
    if args.nms is not None:
        exp.nmsthre = args.nms
    if args.tsize is not None:
        exp.test_size = (args.tsize, args.tsize)

    model = exp.get_model()
    logger.info("Model Summary: {}".format(get_model_info(model, exp.test_size)))

    if args.device == "gpu":
        model.cuda()
        if args.fp16:
            model.half()  # to FP16
    model.eval()

    if not args.trt:
        if args.ckpt is None:
            ckpt_file = os.path.join(file_name, "best_ckpt.pth")
        else:
            ckpt_file = args.ckpt
        logger.info("loading checkpoint")
        ckpt = torch.load(ckpt_file, map_location="cpu")
        # load the model state dict
        model.load_state_dict(ckpt["model"])
        logger.info("loaded checkpoint done.")

    if args.fuse:
        logger.info("\tFusing model...")
        model = fuse_model(model)

    if args.trt:
        assert not args.fuse, "TensorRT model is not support model fusing!"
        trt_file = os.path.join(file_name, "model_trt.pth")
        assert os.path.exists(
            trt_file
        ), "TensorRT model is not found!\n Run python3 tools/trt.py first!"
        model.head.decode_in_inference = False
        decoder = model.head.decode_outputs
        logger.info("Using TensorRT to inference")
    else:
        trt_file = None
        decoder = None

    predictor = Predictor(
        model, exp, COCO_CLASSES, trt_file, decoder,
        args.device, args.fp16, args.legacy,
    )
    current_time = time.localtime()
    while not first_callback:
        time.sleep(0.001)
    ros_main(predictor, vis_folder, current_time, args)


if __name__ == "__main__":
    #args = make_parser().parse_args()
    args = make_parser().parse_args(['webcam', '-f', exp_path, '-c', weight_path, '--conf', '0.25', '--nms', '0.45', '--tsize', '640', '--device', compute_device])
    exp = get_exp(args.exp_file, args.name)

    main(exp, args)
