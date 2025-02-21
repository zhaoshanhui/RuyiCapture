import subprocess
import platform

class ADBHelper:
    """
    跨平台的 ADB 命令执行助手
    统一处理 Windows/Mac/Linux 平台上的 ADB 命令执行
    """
    def __init__(self):
        self.is_windows = platform.system().lower() == 'windows'
        # Windows 平台特定的 startupinfo 配置
        if self.is_windows:
            self.startupinfo = subprocess.STARTUPINFO()
            self.startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.startupinfo.wShowWindow = subprocess.SW_HIDE
        else:
            self.startupinfo = None

    def run_cmd(self, cmd, **kwargs):
        """
        执行 ADB 命令
        Args:
            cmd: 要执行的命令，可以是字符串或列表
            **kwargs: 传递给 subprocess.run 的其他参数
        Returns:
            subprocess.CompletedProcess 对象
        """
        default_kwargs = {
            'shell': isinstance(cmd, str),
            'capture_output': True,
            'text': True,
            'encoding': 'utf-8'
        }

        # 在 Windows 上添加 startupinfo
        if self.is_windows:
            default_kwargs['startupinfo'] = self.startupinfo

        # 合并默认参数和传入的参数
        kwargs = {**default_kwargs, **kwargs}
        
        try:
            return subprocess.run(cmd, **kwargs)
        except subprocess.CalledProcessError as e:
            print(f"ADB command failed: {e}")
            raise 