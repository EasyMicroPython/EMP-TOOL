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
sudo emptool put example.py 

