FROM hrjp/yolox:noetic

# package setup
RUN apt update &&\
    cd /home/catkin_ws/src &&\
    git clone https://github.com/hrjp/yolox_ros1 &&\
    git clone https://github.com/hrjp/TL_detect &&\
    cd /home/catkin_ws &&\
    rosdep install -i -y --from-paths src &&\
    catkin build
# sample weight data download
RUN cd /home/catkin_ws/src/yolox_ros1/config/yolox/weight &&\
    wget https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.pth &&\
    cp /home/catkin_ws/src/YOLOX/exps/default/yolox_s.py /home/catkin_ws/src/yolox_ros1/config/yolox/exp/yolox_s.py &&\
    cp /home/catkin_ws/src/YOLOX/exps/default/yolox_m.py /home/catkin_ws/src/yolox_ros1/config/yolox/exp/yolox_m.py &&\
    cp /home/catkin_ws/src/YOLOX/exps/default/yolox_l.py /home/catkin_ws/src/yolox_ros1/config/yolox/exp/yolox_l.py &&\
    cp /home/catkin_ws/src/YOLOX/exps/default/yolox_x.py /home/catkin_ws/src/yolox_ros1/config/yolox/exp/yolox_x.py &&\
    cp /home/catkin_ws/src/YOLOX/exps/default/yolox_nano.py /home/catkin_ws/src/yolox_ros1/config/yolox/exp/yolox_nano.py &&\
    cp /home/catkin_ws/src/YOLOX/exps/default/yolox_tiny.py /home/catkin_ws/src/yolox_ros1/config/yolox/exp/yolox_tiny.py
RUN apt clean