from config import config
from app.ruyi_capture import RuyiCapture

def main():
    ruyi_capture = RuyiCapture()
    ruyi_capture.set_device(config.device_id)
    while True:
        name = input("请输入要保存的文件名: ")
        ruyi_capture.get_vh(name)
        ruyi_capture.get_screenshot(name)

if __name__ == "__main__":
    main()
