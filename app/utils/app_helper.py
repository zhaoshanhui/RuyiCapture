from .adb_helper import ADBHelper

class AppHelper:
    """
    辅助进行与 app 相关的操作：
    1. 根据包名获取 app 名称
    2. 判断 Ruyi Client 是否安装
    3. 安装 Ruyi Client
    4. 启动 Ruyi Client
    5. 判断 Ruyi Client 的权限是否授予
    """
    def __init__(self, device=""):
        self.device = device
        self.remote_aapt_path = '/data/local/tmp/aapt-arm-pie'
        self.apk_path = ''
        self.package_name = ''
        self.app_name = ''
        self.adb_helper = ADBHelper()

    def forward_port(self, device_id, port):
        """
        转发手机的 6666 端口到本地 port 端口
        """
        if device_id:
            self.adb_helper.run_cmd(f'adb -s {device_id} forward tcp:{port} tcp:6666')
        else:
            self.adb_helper.run_cmd(f'adb forward tcp:{port} tcp:6666')

if __name__ == '__main__':
    app_helper = AppHelper()

    print(app_helper.get_ruyi_client_authorized('MXG0222125015306'))

