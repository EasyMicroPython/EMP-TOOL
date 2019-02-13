from rawrepl import RawRepl
import os
import pypi
import fire


class EmpTool:
    def __init__(self, device):
        self.repl = RawRepl(device)

    def pip_install(self, pkg, output='/lib'):
        pkg_name = pypi.download_pkg(pkg)
        pypi.unzip_pkg(pkg_name)
        self.sync_folder(pkg_name.replace('.tar.gz', ''), output=output)
        pypi.remove_trash(pkg_name)

    def sync_folder(self, target, output='/'):
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

    def download(self):
        pass

    def put(self, target, output='/'):
        if output != '/':
            self.repl.mkdir(output)
        with open(target, 'r') as f:
            print('==> sending file %s...' % target)
            self.repl.put_file(output+'/'+target, f.read())

    def get(self):
        pass


def main():
    fire.Fire(EmpTool)


if __name__ == '__main__':
    main()
