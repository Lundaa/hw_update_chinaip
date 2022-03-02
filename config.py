import configparser
import os



class ReadConfigFile(object):
    def __init__(self):
        self.conn = configparser.ConfigParser()
        file_path = os.path.join(os.path.abspath('.'), 'config.ini')
        try:
            self.conn.read(file_path, encoding="utf-8-sig")
        except:
            self.conn.read(file_path, encoding="utf-8")
        if not os.path.exists(file_path):
            raise FileNotFoundError("配置文件不存在")

    def read_device_config(self):
        """
            读取设备信息
        :return: 返回设备信息键值对字典
        """
        # 读取device_info配置文件
        configs = self.conn.items('device_info')
        # 遍历配置文件device，获取键值对字典
        device_info = {}
        for info in configs:
            device_info[info[0]] = info[1]
        return device_info

    def read_chinaip_config(self):
        """
            读取自配置信息
        :return: 返回自配置信息字典
        """
        # 读取配置文件
        configs = self.conn.items('chinaip_config')
        chinaip_config = {}
        # 遍历配置文件customize_config，获取键值对字典
        for info in configs:
            chinaip_config[info[0]] = info[1]
        return chinaip_config

    def read_custom_script(self):
        """
            读取自定义脚本配置信息
        :return: 返回自定义脚本配置信息字典
        """
        # 读取配置文件
        configs = self.conn.items('custom_script')
        custom_script = {}
        # 遍历配置文件custom_script，获取键值对字典
        for info in configs:
            custom_script[info[0]] = info[1]
        return custom_script
