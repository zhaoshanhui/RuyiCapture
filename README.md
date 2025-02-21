# RuyiCapture
> 通过命令行调用，借助 Ruyi Client 获取手机截图和 VH 信息

## 使用说明
- 如果电脑中只连接了一个设备，可以直接启动。
- 如果连接了多个设备，启动前需要在 `config/config.yaml` 的 `device_id` 项中配置所用设备的 id 信息（可通过 `adb devices` 获取）。

## 安装指南

### 使用 Conda 安装依赖

1. 克隆项目到本地：

   ```bash
   git clone https://github.com/zhaoshanhui/RuyiCapture.git
   cd RuyiCapture
   ```

2. 创建 Conda 环境，并安装相关依赖，也可以直接使用 RuyiAgent 的环境：

   ```bash
   conda create --name ruyi_capture python=3.12
   conda activate ruyi_capture
   conda install --file requirements.txt
   ```

4. 运行项目：

   ```bash
   python main.py
   ```
