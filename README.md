# EMP-TOOL
`emptool` 是一个由1Z实验室开发的MicroPython的命令行工具。

## Features
- PC到MicroPython设备端的指定文件传输
- PC到MicroPython设备端的指定工程目录的同步传输
- MicroPython设备到PC端的指定文件的传输
- MicroPython设备到PC端的指定工程目录的下载
- PC端pip辅助安装Pypi上的扩展
- 打印目录
- 打印指定脚本文件的代码


## 安装
```bash
pip install emptool
```

## 快速开始

### 向MicroPython设备传输文件
```bash
sudo emptool put --target=example.py --device=/dev/ttyUSB0
```
以上指令将文件`exmaple.py`传输到MicroPython的根目录下

```bash
sudo emptool put --target=example.py --path=/lib --device=/dev/ttyUSB0   
# 或者可简写为：
sudo emptool put example.py /lib --device=/dev/ttyUSB0
```
以上指令将文件`example.py`传输到MicroPython的`/lib`目录下

### 从MicroPython设备下载指定文件到PC的指定目录下
```bash
sudo emptool get --target=boot.py --path=~/Test/boot.py --device=/dev/ttyUSB0
# 或者可简写为：
sudo emptool get boot.py ~/Test/boot.py --device=/dev/ttyUSB0
```
以上指令将MicroPython文件系统中根目录下的`boot.py`下载到PC上的`～/Test`目录下。

### PC到MicroPython设备端的指定工程目录的同步传输
```bash
sudo emptool sync --target=./lib --path=/lib --device=/dev/ttyUSB0
# 或者可简写为：
sudo emptool sync ./lib /lib --device=/dev/ttyUSB0
```

以上指令可将PC当前目录下`lib`文件夹中的所有内容，全部同步传输到MicroPython的`/lib`目录下

### MicroPython设备到PC端的指定工程目录的下载
```bash
sudo emptool download --target=/ --path=~/Test --device=/dev/ttyUSB0
# 或者可简写为：
sudo emptool download / ~/Test --device=/dev/ttyUSB0
```
以上指令可以将MicroPython根目录下的所有内容，同步下载到PC的`～/Test`目录下


### PC端pip辅助安装Pypi上的扩展
由于8266之类的内存太少，导致无法使用upip进行正常的下载,或者说那些根本不带Wifi模块的MicriPython设备而言,可以在与PC串口连接的情况下让PC辅助进行安装。

```bash
sudo emptool pip_install --pkg=emp-ext --path=/lib --device=/dev/ttyUSB0
# 或者可简写为：
sudo emptool pip_install emp-ext /lib --device=/dev/ttyUSB0
# 安装的目录默认为/lib，如果不特定指定为其他目录，因此path参数也可以省略：
sudo emptool pip_install emp-ext --device=/dev/ttyUSB0
```
以上的指令将会从Pypi上寻找 名为`emp-ext`的包，并下载解压后，按照指定的路径同步传输到MicroPython的文件系统中。

### 显示指定目录下的文件列表
```bash
# 不指明路径参数时，默认会列出MicroPython文件系统根目录下所有的内容
sudo emptool ls --device=/dev/ttyUSB0
# 罗列/lib目录下的内容
sudo emptool ls --dir=/lib --device=/dev/ttyUSB0
# 或简写为：
sudo emptool ls /lib --device=/dev/ttyUSB0
```

### 在终端中直接打印出某个文件中的内容
```bash
# 例如查看boot.py
sudo emptool showcode --target=/boot.py --device=/dev/ttyUSB0
# 或者简写为
sudo emptool showcode boot.py --device=/dev/ttyUSB0
```