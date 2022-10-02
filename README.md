[![Docker image build](https://github.com/hrjp/yolox_ros1/actions/workflows/yolox-tl_detect-image-build.yml/badge.svg)](https://github.com/hrjp/yolox_ros1/actions/workflows/yolox-tl_detect-image-build.yml)
# yolox_ros1
YOLOX ROS1 Bridge

# Setup
## 1. リポジトリのclone
```bash
git clone https://github.com/hrjp/yolox_ros1
```

## 2. dockerコンテナの構築
```bash
./yolox_ros1/docker/run.bash -g
```
必要に応じて以下のオプションを指定する
| Option | Default | Details |
| :--- | :--- | :--- |
| -g | | GPUを使用する |
| -r | | コンテナからexitした際にコンテナを自動消去する | 
| -n CONTAINER_NAME | yolox_tl_detect | コンテナの名前 |
| -s SHARE_FOLDER_PATH | | コンテナ内部と共有するディレクトリのパス<br>rosbagをやデータを外部と共有する際に使用<br>(ex.　shareフォルダを作ってから　/home/user/share ) |

## 3. demoの実行
docker コンテナ内に入った状態で
```bash
roslaunch yolox_ros1 demo.launch
```

## 4. 次から以下のコマンドでコンテナに入る
```bash
./yolox_tl_detect.bash
```

## Demo video
https://user-images.githubusercontent.com/36100321/193454739-9725bdbd-ce8b-4433-84b0-6b7302a7b3c0.mp4

