# backend/config/__init__.py
import os
import yaml

class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            
        for key, value in config_data.items():
            setattr(self, key, value)

    def get(self, key, default=None):
        """获取配置项,支持默认值"""
        self._load_config()  # 每次获取配置时重新加载
        return getattr(self, key, default)
    
    def update(self, **kwargs):
        """更新配置项"""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def reload(self):
        """重新加载配置文件"""
        self._load_config()

# 创建单例实例
config = Config()


# if __name__ == "__main__":
#     # 访问配置项
#     print(config.adb_path)
#     # 获取配置,支持默认值
#     api_key = config.get('fm_api_key', 'default_key')
#     # 更新配置
#     config.update(name="NewName", output_dir="./new_output")
#     # 重新加载配置
#     config.reload()
