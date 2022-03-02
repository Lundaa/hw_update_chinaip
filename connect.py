import paramiko
from config import ReadConfigFile
import time
import os


class Connect(object):
    def __init__(self):
        self.device_info = ReadConfigFile().read_device_config()
        self.addr = self.device_info['ip']
        self.port = int(self.device_info['port'])
        self.username = self.device_info['username']
        self.password = self.device_info['password']

    def ssh_coon(self, scripts, time_out):
        """
            ssh连接
        """
        try:
            ssh = paramiko.SSHClient()
            key = paramiko.AutoAddPolicy()
            ssh.set_missing_host_key_policy(key)
            # ssh连接
            ssh.connect(self.addr, self.port, self.username, self.password, timeout=2)
            print('连接成功！')
            ssh_shell = ssh.invoke_shell()
            # 运行脚本
            print("Begin... Please wait...")
            for i in range(len(scripts)):
                ssh_shell.send(scripts[i])
                # 延时time_out秒以使得命令能成功执行
                time.sleep(time_out)
            # 延迟2秒等候关闭ssh连接
            time.sleep(2)
            ssh.close()
            # 判定是否第一次运行
            if os.path.isfile("lock.ini"):
                pass
            else:
                # 第一次成功执行后写入锁定文件
                with open('data/lock.ini', 'w', encoding='utf8') as f:
                    f.write('判断是否第一次运行的锁定文件')
            print('执行完毕！')
        except:
            print('异常错误！请重试！')

    def sftp_down_file(self, remote, local_path):
        """
            获取远程配置文件
        :param remote: 远程文件路径及名字
        :param local_path: 本地保存文件路径及名字
        :return:
        """
        try:
            t = paramiko.Transport(self.addr, self.port)
            t.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(t)
            if os.path.isdir(local_path):
                pass
            else:
                os.mkdir(local_path)
            sftp.get(remote, local_path + '/' + remote)
            t.close()
        except:
            print("sftp下载配置出错，请判断远程是否有此配置文件或检查配置文件设备ip及账号密码是否正确！")
