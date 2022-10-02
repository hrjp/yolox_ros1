FROM hrjp/yolox:noetic

# package setup
RUN apt update &&\
    cd /home/catkin_ws/src &&\
    git clone https://github.com/hrjp/yolox_ros1 &&\
    cd /home/catkin_ws &&\
    rosdep install -i -y --from-paths src &&\
    catkin build
# sample weight data download
RUN cd /home/catkin_ws/src/yolox/config/weight &&\
    wget https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.pth &&\
    cp /home/catkin_ws/src/YOLOX/exps/default/yolox_s.py /home/catkin_ws/src/yolox/config/exp
