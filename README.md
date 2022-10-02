[![Docker image build](https://github.com/hrjp/yolox_ros1/actions/workflows/yolox-tl_detect-image-build.yml/badge.svg)](https://github.com/hrjp/yolox_ros1/actions/workflows/yolox-tl_detect-image-build.yml)
# yolox_ros1
YOLOX ROS1 Bridge

# setup
## 1. dockerコンテナの構築
```bash
git clone https://github.com/hrjp/yolox_ros1

# -g をつけるとGPUに対応
./yolox_ros1/docker/run.bash -g
```

## 2. demo
```bash
roslaunch yolox_ros1 demo.launch
```

