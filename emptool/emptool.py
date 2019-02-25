from emptool.rawrepl import RawRepl
import os
from emptool import pypi
import json
from osprofile import OSProfile


class EmpToolError(BaseException):
    pass


class EmpTool(OSProfile):
    def _profile(self):
        pass

    def __init__(self, device=None, buffer=1024):
        super().__init__(appname='emptool', profile='emptool_cfg.json',
                         options=dict(device=None, buffer=1024))
        if device is None:
            device = self.read_profile()['device']
            if device is None:
                raise EmpToolError(
                    """Init Error. The first time you use emptool, please specify the device parameter.""")
        else:
            self.update_profile(dict(device=device, buffer=buffer))

        self.repl = RawRepl(device, BUFFER_SIZE=buffer)

    def config(self, device, buffer):
        self.update_profile(dict(device=port, buffer=buffer_size))

    def pip_install(self, pkg, path='/lib'):
        # 由于8266之类的内存太少，导致无法使用upip进行正常的下载
        # 或者说那些根本不带Wifi模块的MicriPython设备而言
        # 需要PC辅助进行安装
        pkg_name = pypi.download_pkg(pkg)
        pypi.unzip_pkg(pkg_name)
        self.sync(pkg_name.replace('.tar.gz', ''), path=path)
        pypi.remove_trash(pkg_name)

    def sync(self, target, path='/'):
        # 将当前PC的某个指定路径内的文件内容，同步到MicroPython上的指定路径
        print('==> Start sync %s' % target)
        if path != '/':
            self.repl.mkdir(path)
        for folder, _, files in os.walk(target):
            if not '__pycache__' in folder:
                self.repl.mkdir(path+'/'+folder.replace(target, ''))
                for f in files:
                    filename = '%s/%s' % (folder, f)
                    with open(filename, 'r') as f:
                        print('  -> Sending file %s...' % filename)
                        self.repl.put_file(
                            path+filename.replace(target, ''), f.read())
        print('==> Done.')

    def download(self, target, path=None):
        # 将MicroPython上指定路径的内容，下载到PC
        if path is None and not isinstance(path, str):
            raise EmpToolError('Please indicate an path path')
        print('==> Getting dir...')
        data = json.loads(self.repl.walk(target))
        print('==> Starting download...')
        for folder, _, files in data:
            for _file in files:

                target = ('%s/%s' % (folder, _file)).replace('//', '/')
                des = ('%s/%s' % (path, target)).replace('//', '/')
                # print('/'.join(des.split('/')[:-1:]))
                if not os.path.exists('/'.join(des.split('/')[:-1:])):
                    print('  -> making dir %s' %
                          '/'.join(des.split('/')[:-1:]))
                    os.system('mkdir -p %s' % ('/'.join(des.split('/')[:-1:])))
                self.get(target, path=des)

    def put(self, target, path='/'):
        if path != '/':
            self.repl.mkdir(path)
        with open(target, 'r') as f:
            print('==> sending file %s...' % target)
            self.repl.put_file(path+'/'+target.split('/')
                               [:1:-1][0], f.read())

    def get(self, target, path=None):
        print('==> Getting %s' % target)
        if path is None or not os.path.exists(os.path.dirname(path)):
            raise EmpToolError('No such file or directory: %s' % path)
        with open(path, 'w') as f:
            data = self.repl.get_file(target)
            f.write(data.decode('utf-8'))

    def showcode(self, target):
        data = self.repl.get_file(target)
        print(data.decode('utf-8'))

    def ls(self, dir='/'):
        data = json.loads(self.repl.walk(dir))
        for folder, _, filenames in data:
            for f in filenames:
                print(('%s/%s' % (folder, f)).replace('//', '/'))

    def clear(self, path='/'):
        self.repl.clear(path=path)
