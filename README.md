# RuyiCapture
> 通过命令行调用，借助 Ruyi Client 获取手机截图和 VH 信息

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

请确保在运行项目之前，您已经正确配置了 `config/config.yaml` 文件中的相关参数。