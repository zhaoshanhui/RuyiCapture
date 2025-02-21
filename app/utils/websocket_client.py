import websocket
import threading
import json
import PIL.Image
import base64
import io
import time

from app.utils import AppHelper
from config import config
def default_on_error(ws, error):
    print(f"WebSocket错误发生: {error}")


def default_on_close(ws, close_status_code, close_msg):
    print("WebSocket连接已关闭")


class WebSocketClient:
    def __init__(self, server_address=None, on_start_message=None, on_error=default_on_error,
                 on_close=default_on_close):
        self.on_start_message = on_start_message
        self.server_address = server_address
        self.response_event = threading.Event()  # 用于同步
        self.is_running = threading.Event()
        self.response_message = None  # 用于存储服务器返回的信息
        self.is_connected = False  # 连接状态标志
        self.connection_error = None  # 错误状态存储

        # 保存用户传入的回调函数
        self.user_on_error = on_error
        self.user_on_close = on_close

        # 在 WebSocketClient 的构造函数中，不能直接将调用方传入的 on_error 和 on_close（默认时为 default_on_error 和 default_on_close）传递给 websocket.WebSocketApp。
        # 这会导致当 WebSocket 连接关闭或出错时，实际回调被调用的是这些外部函数，而不是类内定义的 on_error 和 on_close 方法（这两个方法负责更新 self.is_connected 等内部状态）。
        # 因此，当服务器关闭了服务后，内部状态没有被正确更新，导致在调用 WebSocketManager 的 ensure_connected 方法时，即使 server 关闭了连接，但依然返回 True。
        self.ws = websocket.WebSocketApp(
            server_address,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self._internal_on_error,
            on_close=self._internal_on_close
        )
        self.ws.client_instance = self  # 将当前实例传递给 WebSocketApp
        self.thread = threading.Thread(target=self.ws.run_forever)

    # 此处不能使用
    def _internal_on_error(self, ws, error):
        """
        内部错误回调：
        1. 更新内部状态；
        2. 调用用户传入的 on_error 回调（默认为 default_on_error）。
        """
        self.is_connected = False
        self.connection_error = error
        self.is_running.set()  # 解除 start() 中的等待
        if self.user_on_error:
            self.user_on_error(ws, error)

    def _internal_on_close(self, ws, close_status_code, close_msg):
        """
        内部关闭回调：
        1. 更新内部状态；
        2. 调用用户传入的 on_close 回调（默认为 default_on_close）。
        """
        self.is_connected = False
        if self.user_on_close:
            self.user_on_close(ws, close_status_code, close_msg)

    def on_message(self, ws, message):
        # 将消息存入 WebSocketClient 实例中
        self.response_message = message
        # 解除阻塞
        self.response_event.set()

    def on_open(self, ws):
        self.is_connected = True
        self.connection_error = None  # 清除错误状态
        self.is_running.set()

    def start(self, timeout=1):
        self.thread.start()
        self.is_running.wait(timeout=timeout)
        if self.connection_error:
            print(f"WebSocket连接失败: {self.connection_error}")
            raise ConnectionError(f"WebSocket连接失败: {self.connection_error}")
        if not self.is_connected:
            print("WebSocket连接超时")
            raise ConnectionError("WebSocket连接超时")

    def send_message(self, message, timeout=1):
        # 发送消息并等待服务器的响应
        self.response_event.clear()  # 重置事件
        self.response_message = None  # 清空之前的响应消息
        self.ws.send(message)
        if not self.response_event.wait(timeout):  # wait() 方法在超时时返回 False
            raise TimeoutError(f"等待服务器响应超时，超时时间：{timeout}秒")
        return self.response_message  # 返回服务器的响应

    def close(self):
        self.ws.close()
        if self.thread.is_alive():
            self.thread.join(timeout=2)

    def is_alive(self):
        """
        更完善的连接状态检查
        """
        sock_connected = bool(self.ws.sock and self.ws.sock.connected)
        return all([
            self.is_connected,  # 连接标志为 True
            sock_connected,     # socket 确实已连接
            not self.connection_error,  # 没有发生错误
            self.thread.is_alive()  # websocket 线程正在运行
        ])


class WebSocketManager:
    def __init__(self, device_url="", device_id="", on_start_message=None, on_error=default_on_error, on_close=default_on_close):
        self.server_address = device_url
        self.device_id = device_id
        self.client = None
        # 保存传入的回调函数，以便后续使用
        self.on_start_message = on_start_message
        self.on_error = on_error
        self.on_close = on_close

        if self.server_address:
            try:
                self.client = WebSocketClient(self.server_address, on_start_message, on_error, on_close)
                self.client.start()
            except Exception as e:
                print(f"WebSocket连接失败: {e}")

        self.app_helper = AppHelper()
    def close(self):
        self.client.close()

    def is_connected(self):
        if self.client:
            # 增加心跳检测机制
            try:
                # 发送空消息测试真实连接状态。目前 server 没有提供检测的接口，所以无法检测
                # connected_check_result = self.client.send_message("check_connection")
                # print(f"connected_check_result: {connected_check_result}")
                return self.client.is_alive()
            except Exception as e:
                print(f"connected_check_result: {e}")
                self.client.is_connected = False
                return False
        else:
            return False
    
    def ensure_connected(self, max_retries=2, retry_interval=0.5):
        """确保 WebSocket 连接是活跃的，如果断开则重新连接
        Args:
            max_retries (int): 最大重试次数
            retry_interval (int/float): 重试间隔（秒），支持小数（如0.5表示500ms）
        """
        # print("----- WebSocketManager ensure_connected -----")
        if not self.is_connected():
            if self.client:
                self.client.close()
                self.client = None
            
            for attempt in range(max_retries):
                try:
                    print(f"尝试连接 WebSocket (第{attempt + 1}次)")
                    self.client = WebSocketClient(
                        self.server_address,
                        on_start_message=self.on_start_message,  # 使用保存的回调
                        on_error=self.on_error,
                        on_close=self.on_close
                    )
                    self.client.start()
                    if self.is_connected():
                        return True
                except Exception as e:
                    print(f"WebSocket连接失败: {e}")
                    if attempt < max_retries - 1:  # 如果不是最后一次尝试

                        # 如果连接失败，则转发端口
                        self.app_helper.forward_port(self.device_id, config.device_port)
                        time.sleep(retry_interval)  # 等待一段时间后重试
                    continue
            return False
        return True

    def change_server_address(self, server_address):
        """
        修改 WebSocket 的 server_address, 并重新连接
        Args:
            server_address: 新的 WebSocket 服务器地址
        Returns:
            bool: 连接是否成功
        """
        # 关闭现有连接
        if self.client:
            self.client.close()
        
        # 更新服务器地址
        self.server_address = server_address
        
        try:
            # 创建新的WebSocket客户端并连接
            self.client = WebSocketClient(self.server_address)
            self.client.start()
            return True
        except Exception as e:
            print(f"更改WebSocket服务器地址失败: {e}")
            return False

    def get_vh(self):
        """
        获取当前视图层级, 返回 dict
        """
        # self.ensure_connected()
        res = self.client.send_message("view_hierarchy")
        res = json.loads(res)
        views = json.loads(res['message'])
        height = res['height']
        width = res['width']
        return views, height, width

    def get_screenshot(self):
        """
        获取当前屏幕截图, 返回 PIL.Image.Image 对象
        """
        print("WebSocket Manager get screenshot")
        res = self.client.send_message("screenshot")
        print("WebSocket Manager send_message success")
        res = json.loads(res)
        res = res["data"]
        res = base64.b64decode(res)

        print("WebSocket Manager decode success")

        img = PIL.Image.open(io.BytesIO(res))
        print("WebSocket Manager open success")
        return img

    def set_device_id(self, device_id):
        self.device_id = device_id

if __name__ == "__main__":
    device_url = "ws://127.0.0.1:6667"
    print("device_url: ", device_url)
    manager = WebSocketManager(device_url)
    print("WebSocketManager init success")
    img = manager.get_screenshot()
    print("WebSocketManager get_screenshot success")
    img.show()
    img.save("screenshot.png", format="PNG")
    manager.close()
