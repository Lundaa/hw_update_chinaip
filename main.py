from my_function import Myfunction
from config import ReadConfigFile
from connect import Connect
from list_helper import *
import os


class MainProgram(object):
    def __init__(self):
        """
            读取配置文件设置及设置部分PATH
        """
        self.chinaip_config = ReadConfigFile().read_chinaip_config()  # 生成chinaip_config配置文件对象
        self.custom_script = ReadConfigFile().read_custom_script()  # 生成自定义模式对象
        self.online_url = int(self.chinaip_config['chinaip_online_data'])  # 获取互联网chinaip来源
        self.write_switch = int(self.chinaip_config['write_text_switch'])  # 读取配置文件生成chinaip.txt文本开关
        self.custom_script_switch = int(self.custom_script['custom_script_mode'])  # 读取自定义模式开关
        self.ip_number = int(self.chinaip_config['ip_number'])  # 读取chinaip_config设置项
        self.script_file = self.custom_script['script_file']  # 读取自定义模式设置项
        self.remote = self.chinaip_config['remote_name']  # 读取chinaip_config设置项
        self.local_path = self.chinaip_config['local_path']  # 读取chinaip_config设置项
        self.time_out = float(self.chinaip_config['time_out'])  # 读取chinaip_config设置项
        self.local_cfg_path = self.local_path + '/vrpcfg.cfg'  # 设置防火墙配置文件PATH
        self.china_online_list = []

    def main_program(self):
        """
            程序入口
        """
        # 判断互联网chinaip来源连接
        if self.online_url == 1:
            self.china_online_list = Myfunction().get_ispipipnet_list()
        elif self.online_url == 2:
            self.china_online_list = Myfunction().get_ispclang_list()
        # 判断是否生成中国ip列表text文件
        if self.write_switch == 1:
            Myfunction().write_text(self.china_online_list)
        # 判断是否是自定义模式
        if self.custom_script_switch == 1:
            Connect().ssh_coon(Myfunction().script_mode(self.script_file), self.time_out)
        else:
            # 判断lock.ini是否存在
            if os.path.isfile("lock.ini"):
                try:
                    print("info:no first,run update mode!")
                    # 下载sftp配置文件
                    Connect().sftp_down_file(self.remote, self.local_path)
                    # 判断远程文件是否需要解压
                    if 'zip' in self.remote:
                        Myfunction().un_zip(self.local_path + '/' + self.remote, self.local_path)
                    else:
                        pass
                    # 读取配置文件
                    cfg_list = Myfunction().read_vrpcfg(self.local_cfg_path)
                    # 遍历配置文件,获得fwdict字典
                    fwdict = Myfunction().get_vrpcfg_chinaip_list(cfg_list)
                    # 整形字典values值，获得fwlist列表
                    fwlist = Myfunction().fw_alter_ip_list(fwdict)
                    # 获取网络weblist
                    weblist = Myfunction().web_alter_ip(self.china_online_list)
                    # 比较web中chinaip和fw配置文件中chinaip,获得删除和添加的ip_temp列表,返回值是一个元组类型
                    change_temp = Myfunction().compare_list(weblist, fwlist)
                    # 获得最终删除数据列表
                    final_delete_list = Myfunction().get_delete_id(change_temp[1], fwdict)
                    # 获得最终添加数据列表
                    final_add_list = Myfunction().get_add_list(change_temp[0])
                    # 生成删除和添加列表的执行脚本
                    scripts = Myfunction().update_ip_group(final_add_list, final_delete_list)
                    # 执行ssh连接，并传入脚本文件
                    Connect().ssh_coon(scripts, self.time_out)
                    # 输出脚本文件执行命令记录
                    Myfunction().write_script_log(scripts)
                except:
                    print("更新错误")
            else:
                try:
                    print("first run!")
                    # 把网站上获取的数据进行整形处理
                    weblist = Myfunction().web_alter_ip(self.china_online_list)
                    # 获取可插入华为防火墙ip组格式的中国ip列表,并均分为ip段数量为ip_number的列表,返回的是一个生成器
                    china_ip_generator = ListHelper.list_cut(weblist, self.ip_number)
                    # 生成第一次运行本程序时的脚本文件
                    scripts = Myfunction().first_huawei_scripts(china_ip_generator)
                    # 连接ssh并写入数据，成功运行后会输出一个lock.ini锁定文件,第一次运行时间较长，大约30分钟
                    Connect().ssh_coon(scripts, self.time_out)
                    # 输出脚本文件执行命令记录,默认不开启，第一次运行时的脚本命令过多，可能影响效能，调试时可开启
                    # Myfunction().write_script_log(scripts)
                except:
                    print("运行错误！")


if __name__ == '__main__':
    # 切换目录至main.py所在工作目录，否则使用绝对路径运行此程序时会报错
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # 运行主程序
    MainProgram().main_program()
