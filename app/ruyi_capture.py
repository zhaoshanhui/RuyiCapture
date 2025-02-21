import json
import os
from config import config
from app.utils import WebSocketManager, AppHelper, ADBHelper
import subprocess

class RuyiCapture:
    def __init__(self):
        self.device_id = ""
        self.app_helper = AppHelper()
        self.adb_helper = ADBHelper()

        self.websocket_manager = WebSocketManager()

        self.record_dir_screenshot = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'RecordResult')
        os.makedirs(self.record_dir_screenshot, exist_ok=True)

    def set_device(self, device_id = ""):
        """
        设置设备，传入 device_id
        """

        # 修改 adb forward 命令的执行
        device_port = config.device_port
        self.app_helper.forward_port(device_id, device_port)

        # 根据 device_id 通过 adb 获取 device_url
        device_url = f"ws://localhost:{device_port}"
        print(device_url)

        self.websocket_manager.change_server_address(device_url)
        self.websocket_manager.set_device_id(device_id)
        return 

    def get_vh(self, vh_name):
        views, height, width = self.websocket_manager.get_vh()
        view_hierarchy = {
            "width": width,
            "height": height,
            "views": views
        }
        vh_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'RecordResult', vh_name+".json")
        with open(vh_path, 'w', encoding='utf-8') as f:
            json.dump(view_hierarchy, f, ensure_ascii=False, indent=4)
        print(f"vh 保存成功: {vh_path}")
        return vh_path


    def record_screenshot_adb(self, image_name):
        # adb shell screencap -p /sdcard/screenshot.png
        self.screenshot_name = f"{image_name}.png"
        screenshot_path_in_device = f"{self.record_dir_screenshot}/{self.screenshot_name}"
        if self.device_id:
            adb_cmd = f"adb -s {self.device_id} shell screencap -p {screenshot_path_in_device}"
        else:
            adb_cmd = f"adb shell screencap -p {screenshot_path_in_device}"
        self.record_screenshot_process = subprocess.run(adb_cmd, shell=True)

        if self.device:
            adb_cmd = f"adb -s {self.device} pull {screenshot_path_in_device} {self.record_dir_screenshot}"
        else:
            adb_cmd = f"adb pull {screenshot_path_in_device} {self.record_dir_screenshot}"
        self.pull_screenshot_process = subprocess.run(adb_cmd, shell=True)
    
    def record_screenshot_adb_without_pull(self, image_name):
        # adb shell screencap -p /sdcard/screenshot.png
        self.screenshot_name = f"{image_name}.png"
        screenshot_path = f"{self.record_dir_screenshot}/{self.screenshot_name}"
        result = subprocess.run(
            f"adb exec-out screencap -p > {screenshot_path}",
            shell=True,
            check=True
        )
        return screenshot_path

    def get_screenshot_websocket(self, image_name):
        screenshot = self.websocket_manager.get_screenshot()
        image_path = os.path.join(self.record_dir_screenshot, image_name+".png")
        screenshot.save(image_path, format="PNG")
        return image_path

    def get_screenshot(self, image_name):
        try:
            image_path = self.get_screenshot_websocket(image_name)
            print(f"screenshot 保存成功: {image_path}")
            return image_path
        except Exception as e:
            input("Ruyi Client 捕获截图失败，请手动关闭 Ruyi Client 悬浮窗，然后按回车使用 adb 捕获截图")

            try:
                image_path = self.record_screenshot_adb_without_pull(image_name)
                print(f"screenshot 保存成功: {image_path}")
                return image_path
            except Exception as e:
                try:
                    image_path = self.record_screenshot_adb(image_name)
                    print(f"screenshot 保存成功: {image_path}")
                    return image_path
                except Exception as e:
                    print(f"screenshot 保存失败，请重试")
                    return None
