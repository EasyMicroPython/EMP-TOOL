from rawrepl import RawRepl
import os
import pypi
import fire
import json


class EmpToolError(BaseException):
    pass


class EmpTool:
    def __init__(self, device):
        self.repl = RawRepl(device)

    def pip_install(self, pkg, output='/lib'):
        # 由于8266之类的内存太少，导致无法使用upip进行正常的下载
        # 或者说那些根本不带Wifi模块的MicriPython设备而言
        # 需要PC段辅助进行安装
        pkg_name = pypi.download_pkg(pkg)
        pypi.unzip_pkg(pkg_name)
        self.sync_folder(pkg_name.replace('.tar.gz', ''), output=output)
        pypi.remove_trash(pkg_name)

    def sync_folder(self, target, output='/'):
        # 将当前PC的某个指定路径内的文件内容，同步到MicroPython上的指定路径
        if output != '/':
            self.repl.mkdir(output)
        for folder, _, files in os.walk(target):
            if not '__pycache__' in folder:
                self.repl.mkdir(output+'/'+folder.replace(target, ''))
                for f in files:
                    filename = '%s/%s' % (folder, f)
                    with open(filename, 'r') as f:
                        print('==> sending file %s...' % filename)
                        self.repl.put_file(
                            output+filename.replace(target, ''), f.read())

    def download(self, dir):
        # 将MicroPython上指定路径的内容，下载到PC
        pass

    def put(self, target, output='/'):
        if output != '/':
            self.repl.mkdir(output)
        with open(target, 'r') as f:
            print('==> sending file %s...' % target)
            self.repl.put_file(output+'/'+target, f.read())

    def get(self, target, output=None):
        if output is None and not isinstance(output, str):
            raise EmpToolError('Please indicate an output path')
        with open(output, 'w') as f:
            data = self.repl.get_file(target)
            f.write(data.decode('utf-8'))

    def ls(self, dir):
        data = json.loads(self.repl.walk(dir))
        for folder, _, filenames in data:
            for f in filenames:
                print(('%s/%s' % (folder, f)).replace('//', '/'))


def main():
    fire.Fire(EmpTool)


if __name__ == '__main__':
    main()
