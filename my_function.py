import time
import urllib.request
from config import ReadConfigFile
import ssl
import zipfile
import os


class Myfunction(object):
    def __init__(self):
        self.chinaip_config = ReadConfigFile().read_chinaip_config()
        self.custom_script = ReadConfigFile().read_custom_script()
        self.fw_china_ip_group = {'ip address-set china_ip_group_1': [], 'ip address-set china_ip_group_2': []}
        self.huawei_cmd_end = ['return\n', 'save\n', 'Y\n', '\n']

    def get_ispipipnet_list(self):
        """
            获取的ipip.net在github上免费维护的数据源（较为准确）,更新频率每月
        """
        try:
            # 跳过证书检查
            ssl._create_default_https_context = ssl._create_unverified_context
            # 获取ipip.net网站上的中国ip数据列表
            html_ip = urllib.request.urlopen(
                'https://raw.githubusercontent.com/17mon/china_ip_list/master/china_ip_list.txt').readlines()
            ispipipnet_list = []
            for line in html_ip:
                str_line = str(line, encoding="utf-8")
                ispipipnet_list.append(str_line)
            return ispipipnet_list
        except:
            print("获取错误ipip.net在github维护的chinaip失败，请检查网络连接")

    def get_ispclang_list(self):
        """
            获取 ispip.clang.cn网站上最新的中国ip段信息，更新频率每日
        :return: 列表
        """
        try:
            # 跳过证书检查
            ssl._create_default_https_context = ssl._create_unverified_context
            # 获取clang.cn网站的中国ip数据列表
            count = 0
            html_ip = urllib.request.urlopen('https://ispip.clang.cn/all_cn_cidr.html').readlines()
            ispclang_list = []
            for line in html_ip:
                str_line = str(line, encoding="utf-8")
                if 'END' in str(str_line):
                    break
                if count >= 27:
                    ispclang_list.append(str_line)
                count += 1
            return ispclang_list
        except:
            print("获取错误clang.cn在线ip地址失败，请检查网络连接")

    def write_text(self, list_target):
        """
            生成text文本
        :param list_target: 需要生成的目标列表
        """
        folder = os.path.exists('data')
        # 判断是否存在data文件夹
        if not folder:
            os.mkdir('data')
        with open(r'data/china_all_ip_%s.txt' % (str(time.strftime('%Y_%m_%d'))), 'w', encoding='utf-8') as f:
            for i in range(len(list_target)):
                if i == 0:
                    f.write(
                        "生成时间：%s，共计数据：%d" % (
                            str(time.strftime("%Y-%m-%d, %H:%M:%S")), len(list_target)) + '\n')
                    f.write(list_target[i])
                elif i == len(list_target) - 1:
                    f.write(list_target[i].strip('\n'))
                else:
                    f.write(list_target[i])
            f.close()

    def write_script_log(self, script_list):
        folder = os.path.exists('data')
        # 判断是否存在data文件夹
        if not folder:
            os.mkdir('data')
        with open(r'data/run_scripts_logs.txt', 'a', encoding='utf-8') as f:
            for i in range(len(script_list) - 1):
                if i == 0:
                    f.write(
                        "脚本运行时间：%s，共计命令：%d" % (
                            str(time.strftime("%Y-%m-%d, %H:%M:%S")), len(script_list)) + '\n')
                    f.write(script_list[i])
                else:
                    f.write(script_list[i])
            f.write('\n')
            f.close()

    def web_alter_ip(self, list_target):
        """
            将ip列表整形为华为防火墙ip组命令行可插入的格式
        :param list_target: 需要整形的ip
        :return: 整形后的列表
        """
        ip_group_format_list = []
        for ip in list_target:
            new_ip = 'address ' + ip.replace('/', ' mask ')
            ip_group_format_list.append(new_ip)
        return ip_group_format_list

    def first_huawei_scripts(self, split_data):
        """
             生成本程序第一次运行时华为防火墙更新中国ip段的命令行操作脚本
        :param split_data: 传入切割后的列表数据.生成器类型
        :return:运行脚本，first
        """
        # 华为防火墙初始脚本列表
        first_run_scripts = ['sys\n']
        # 计数器，可以动态的更改ip_group组数量的命令
        count = 1
        # 先执行删除ip组操作，目的清空原ip组数据
        for ip_list in split_data:
            # 执行添加ip组操作
            first_run_scripts.append('ip address-set china_ip_group_%d type group\n' % (count))
            # 进行清空ip组内IP段操作
            first_run_scripts.append('undo address all\n')
            first_run_scripts.append("description updatetime:%s\n" % (
                str(time.strftime("%Y-%m-%d, %H:%M:%S"))))
            for ip in ip_list:
                # huawei_cmd_scripts.append('#\n')
                first_run_scripts.append(ip)
            count += 1
        # 华为防火墙退出和保存命令
        for cmd in self.huawei_cmd_end:
            first_run_scripts.append(cmd)
        return first_run_scripts

    def script_mode(self, script_file):
        """
            自定义脚本模式
        :return: 返回自定义脚本列表
        """
        # 判断是否开启了自定义脚本模式

        scripts_list = []
        with open(script_file, 'r', encoding='utf-8') as f:
            for line in f:
                scripts_list.append(line)
            return scripts_list

    def un_zip(self, file_name, unzip_path):
        """
            解压方法
        :param file_name: 需要解压的配置文件的路径+文件名
        :param unzip_path: 解压路径
        :return:
        """
        zip_file = zipfile.ZipFile(file_name)
        for names in zip_file.namelist():
            zip_file.extract(names, unzip_path)
        zip_file.close()

    def read_vrpcfg(self, file_path):
        """
            读取解压后的配置文件
        :param file_path: 配置文件路径
        :return: 返回防火墙配置文件列表
        """
        vrpcfg_list = []
        try:
            with open(file_path, 'r', encoding='utf8', errors='ignore') as f:
                for line in f:
                    vrpcfg_list.append(line)
        except:
            print("读取防火墙配置文件错误！")
        return vrpcfg_list

    def get_vrpcfg_chinaip_list(self, vrpcfg_list):
        """
            获取防火墙配置中的chinaip列表，并进行数据整形，方便与huawei_alter_ip函数输出的列表进行比较
        :return: 防火墙中的chinaip字典
        """
        # fw_conf_list = []  # 配置列表
        # 计数器，方便k值的下一个循环在前一个k值的后面序列开始查找，根据需求看是否需要本计数器
        count_temp = 0
        # 读取需要的防火墙chinaip组中的数据
        for k, v in self.fw_china_ip_group.items():
            # 计数器，提升遍历效率
            for i in range(count_temp, len(vrpcfg_list)):
                if k in vrpcfg_list[i]:
                    for c in range(i + 2, len(vrpcfg_list)):
                        v.append(vrpcfg_list[c].strip())
                        # fw_conf_list.append(vrpcfgfile[c].strip())
                        if "#" in vrpcfg_list[c]:
                            count_temp = c
                            v.remove(vrpcfg_list[c].strip())
                            # 退出本次for循环
                            break
                    # 退出本次for循环
                    break
        return self.fw_china_ip_group

    def fw_alter_ip_list(self, fw_china_ip_dict):
        """
            将配置文件数据整形
        :param fw_china_ip_group: 防火墙中的chinaip字典
        :return: 防火墙中的chinaip列表
        """
        # 整形数据为huawei_alter_ip输出格式的数据
        fw_chian_ip = []
        for v in fw_china_ip_dict.values():
            for item in v:
                count = 0
                for d in range(len(item)):
                    if item[d] == ' ':
                        count += 1
                        if count == 2:
                            x = item[7:d + 1]
                            # print(d)
                            new_item = item.replace(x, ' ') + '\n'
                            fw_chian_ip.append(new_item)
        return fw_chian_ip

    def compare_list(self, weblist, fwlist):
        """
            比较防火墙配置中的chinaip和web上的chinaip
        :return:返回一个添加列表temp，一个删除列表temp，元组类型
        """
        add_list_temp, delete_list_temp = [], []
        # 获取需要添加的ip列表，与防火墙对比
        for x in weblist:
            if x not in fwlist:
                add_list_temp.append(x.replace('\n', ''))
        # 获取需要删除的ip列表,与互联网对比
        for y in fwlist:
            if y not in weblist:
                new_y = y.replace('address', '')
                delete_list_temp.append(new_y.replace('\n', ''))
        # 根据需要是否开启update添加过多数据退出本次程序
        # if len(add_list) > 500:
        # exit()
        return add_list_temp, delete_list_temp

    def get_delete_id(self, delete_list_temp, fw_china_ip_dict):
        """
            根据delete_list_temp获取防火墙对应ip组内ip所属id
        :param delete_list_temp: 删除列表temp
        :param fw_china_ip_dict: 防火墙中的chinaip字典
        :return: 最终删除列表，元组类型
        """
        final_delete_group1 = ['ip address-set china_ip_group_1']
        final_delete_group2 = ['ip address-set china_ip_group_2']
        for x in delete_list_temp:
            for k, v in fw_china_ip_dict.items():
                for item in v:
                    if x in item:
                        count = 0
                        for d in range(len(item)):
                            if item[d] == ' ':
                                count += 1
                                if count == 2:
                                    id_str = item[7:d + 1]
                                    new_id = id_str.replace(' ', '')
                                    if k in "ip address-set china_ip_group_1":
                                        final_delete_group1.append('undo address %s' % new_id)
                                    else:
                                        final_delete_group2.append('undo address %s' % new_id)
        return final_delete_group1, final_delete_group2

    def get_add_list(self, add_list_temp):
        """
            目的为将添加数据均分至两个组
        :param add_list_temp: 添加列表temp
        :return: 返回组成为两个ip组的元组
        """
        final_add_group1 = ['ip address-set china_ip_group_1']
        final_add_group2 = ['ip address-set china_ip_group_2']
        for i in range(len(add_list_temp)):
            if i % 2 == 0:
                final_add_group1.append(add_list_temp[i])
            else:
                final_add_group2.append(add_list_temp[i])
        return final_add_group1, final_add_group2

    def update_ip_group(self, final_add, final_delete):
        """
            生成更新的脚本
        :param add_list:需要添加的ip段，元组类型
        :param delete_list: 需要删除的ip段列表
        :return: 返回更新脚本，列表类型
        """
        update_fw_chinaip = list(['sys\n'])
        # 先运行删除命令
        for x in final_delete:
            for y in x:
                update_fw_chinaip.append(y + '\n')

        # 运行添加命令
        for x in final_add:
            for y in x:
                update_fw_chinaip.append(y + '\n')

        # 运行description备注命令
        for x in self.fw_china_ip_group.keys():
            update_fw_chinaip.append(x + '\n')
            update_fw_chinaip.append("description updatetime:%s\n" % (
                str(time.strftime("%Y-%m-%d, %H:%M:%S"))))

        # 添加脚本结束命令
        for x in self.huawei_cmd_end:
            update_fw_chinaip.append(x)
        return update_fw_chinaip
