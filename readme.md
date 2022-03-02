# 前言
还在完善，有部分功能没添加，例如：连接方式支持telnet、多线程模式并发操作等，目前日志也只是简单记录在ssh远程端运行的命令，不过目前基本可以满足使用，后面有需要再慢慢补充吧...
* 连接设备机型：华为*USG6000*
* 运行环境：*Python3*
# 使用
### 1、打开config.ini进行配置【*详见配置文件注释*】
在【device_info】项中输入想要连接的设备信息
>例如:
>>ip=192.168.1.1  
>>connection_method=ssh  
>>port=22  
>>username = yourname  
>>password = yourpassword

**注意事项**：目前暂时只支持ssh连接，后续考虑增加其他

在【chinaip_config】中输入部分自定义设置
>例如:
>>chinaip_online_data = 1  
>>write_text_switch = 0  
>>ip_number = 3500  
>>remote_name = vrpcfg.zip  
>>local_path = device_config  
>>time_out = 0.5

**注意事项**：务必使ip组分为两个组，目前部分代码只针对两个组进行了操作，为保证命令成功执行time_out的时延参数不建议修改

#### 在【custom_script】中确认自定义脚本模式
>例如:
>>custom_script_mode = 0  
>>script_file = scripts.txt

**注意事项**：需要输入脚本文件的绝对路径，若放在程序运行目录可以不用写绝对路径  

### 2、确认python环境已部署
构建环境使用*python3*，使用额外的module，请使用pip命令安装这些模块：
>pip install urllib3  
>pip install paramiko  
>pip install requests

**注意**：如果使用*Linux*运行，因*Linux*默认环境为python2，请按以下命令操作，全部执行完后cd至程序目录，使用*python3 main.py*执行脚本
>yum install python3  
>yum install epel-release  
>yum install python-pip  
>pip3 install --upgrade pip  
>pip3 install urllib3  
>pip3 install paramiko   
>pip3 install requests 

### 3、第一次运行
第一次打开会判断*lock.ini*文件是否存在（源码默认存在*lock.ini*，请根据需要删除），不存在即为第一次运行本程序，默认新建两个ip组，并向内插入数据 

**注意**：为保证每条命令插入成功，每条命令执行后的延时为**0.5**，预计6000条命令，运行时间大概**50分钟**

*提示：若觉得过慢，第一次可手动插入，**只要保证命名的ip组与下方所示两个ip组相同**，且在插入数据后，在程序目录新建一个**lock.ini**即可*
* china_ip_group_1
* china_ip_group_2

### 4、第二次运行：
第二次检测到*lock.ini*文件存在后，将直接拉取防火墙上的配置文件，并读取两个*IP*组的数据，同时拉取互联网最新的中国*IP*段数据，两者进行比对，生成两个列表
* 添加列表：防火墙中不存在的IP数据  
* 删除列表：防火墙中存在但互联网中已过时的IP数据  

预计比对更新时间**5秒**（根据变动数据的多少来决定）

#  申明
当你查阅、下载了本项目源代码或二进制程序，即代表你接受了以下条款

* 本软件仅供技术交流，学术交流使用
* 本软件作者编写出该软件旨在学习 Python
* 用户在使用本软件时，若用户在当地产生一切违法行为由用户承担
* 严禁用户将本软件使用于商业和个人其他意图
* 若用户不同意上述条款任意一条，请勿使用本软件

# 结束
有问题可联系邮箱：luoyunda@outlook.com
