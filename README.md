[![Docker image build](https://github.com/hrjp/yolox_ros1/actions/workflows/yolox-tl_detect-image-build.yml/badge.svg)](https://github.com/hrjp/yolox_ros1/actions/workflows/yolox-tl_detect-image-build.yml)
# yolox_ros1
YOLOX ROS1 Bridge

# Setup
## 1. dockerコンテナの構築
```bash
git clone https://github.com/hrjp/yolox_ros1

# -g をつけるとGPUに対応
./yolox_ros1/docker/run.bash -g
```

## 2. demo
docker コンテナ内に入った状態で
```bash
roslaunch yolox_ros1 demo.launch
```

## 3. 次から以下のコマンドでコンテナに入る
```bash
./yolox_tl_detect.bash
```
