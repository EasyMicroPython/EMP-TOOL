import json
import sys
import textwrap
import time

import serial


class RawReplError(BaseException):
    pass


class RawRepl:

    def __init__(self, device, baudrate=115200, rawdelay=0, BUFFER_SIZE=1024):
        super().__init__()
        self._rawdelay = rawdelay
        self.BUFFER_SIZE = BUFFER_SIZE

        if isinstance(device, str):
            self.repl = serial.Serial(device, baudrate)
        elif isinstance(device, serial.Serial):
            self.repl = device
        else:
            raise RawReplError('can not init RawRepl')

    def read_until(self, min_num_bytes, ending, timeout=10, data_consumer=None):
        data = self.repl.read(min_num_bytes)
        if data_consumer:
            data_consumer(data)
        timeout_count = 0
        while True:
            if data.endswith(ending):
                break
            elif self.repl.inWaiting() > 0:
                new_data = self.repl.read(1)
                data = data + new_data
                if data_consumer:
                    data_consumer(new_data)
                timeout_count = 0
            else:
                timeout_count += 1
                if timeout is not None and timeout_count >= 100 * timeout:
                    break
                time.sleep(0.01)
        return data

    def enter_raw_repl(self):
        # print('==> Entering Raw REPL')
        # Brief delay before sending RAW MODE char if requests
        if self._rawdelay > 0:
            time.sleep(self._rawdelay)

        # ctrl-C twice: interrupt any running program
        self.repl.write(b'\r\x03\x03')

        # flush input (without relying on serial.flushInput())
        n = self.repl.inWaiting()
        while n > 0:
            self.repl.read(n)
            n = self.repl.inWaiting()
        time.sleep(2)

        self.repl.write(b'\r\x01')  # ctrl-A: enter raw REPL
        data = self.read_until(1, b'raw REPL; CTRL-B to exit\r\n>')
        if not data.endswith(b'raw REPL; CTRL-B to exit\r\n>'):
            print(data)
            raise RawReplError('could not enter raw repl')

    def exit_raw_repl(self):
        # print('==> Exit Raw REPL')
        self.repl.write(b'\r\x02')  # ctrl-B: enter friendly REPL

    def follow(self, timeout, data_consumer=None):
        # wait for normal output
        data = self.read_until(1, b'\x04', timeout=timeout,
                               data_consumer=data_consumer)
        if not data.endswith(b'\x04'):
            raise RawReplError('timeout waiting for first EOF reception')
        data = data[:-1]

        # wait for error output
        data_err = self.read_until(1, b'\x04', timeout=timeout)
        if not data_err.endswith(b'\x04'):
            raise RawReplError('timeout waiting for second EOF reception')
        data_err = data_err[:-1]

        # return normal and error output
        return data, data_err

    def exec_raw_no_follow(self, command):
        if isinstance(command, bytes):
            command_bytes = command
        else:
            command_bytes = bytes(command, encoding='utf8')

        # check we have a prompt
        # data = self.read_until(1, b'>')
        # if not data.endswith(b'>'):
        #     raise RawReplError('could not enter raw repl')

        # write command
        for i in range(0, len(command_bytes), 256):
            self.repl.write(
                command_bytes[i:min(i + 256, len(command_bytes))])
            time.sleep(0.01)
        self.repl.write(b'\x04')

        # check if we could exec command
        # data = self.repl.read(2)
        # if data != b'OK':
        #     raise RawReplError('could not exec command')

    def exec_raw(self, command, timeout=10, data_consumer=None):
        self.exec_raw_no_follow(command)
        return self.follow(timeout, data_consumer)

    def eval(self, expression):
        ret = self.exec__('print({})'.format(expression))
        ret = ret.strip()
        return ret

    def exec__(self, command):
        ret, ret_err = self.exec_raw(command)
        if ret_err:
            raise RawReplError('exception', ret, ret_err)
        return ret

    def execfile(self, filename):
        with open(filename, 'rb') as f:
            pyfile = f.read()
        return self.exec__(pyfile)

    def get_file(self, filename):
        """Retrieve the contents of the specified file and return its contents
        as a byte string.
        """
        # Open the file and read it a few bytes at a time and print out the
        # raw bytes.  Be careful not to overload the UART buffer so only write
        # a few bytes at a time, and don't use print since it adds newlines and
        # expects string data.
        command = """
                import sys
                with open('{0}', 'rb') as infile:
                    while True:
                        result = infile.read({1})
                        if result == b'':
                            break
                        len = sys.stdout.write(result)
            """.format(
            filename, self.BUFFER_SIZE
        )
        self.enter_raw_repl()
        try:
            out = self.exec__(textwrap.dedent(command))
        except RawReplError as ex:
            # Check if this is an OSError #2, i.e. file doesn't exist and
            # rethrow it as something more descriptive.
            if ex.args[2].decode("utf-8").find("OSError: [Errno 2] ENOENT") != -1:
                raise RuntimeError("No such file: {0}".format(filename))
            else:
                raise ex
        self.exit_raw_repl()
        return out[2::]

    def put_file(self, filename, data):
        """Create or update the specified file with the provided data.
        """
        self.enter_raw_repl()
        data = data.encode('utf-8')
        # Open the file for writing on the board and write chunks of data.
        # self.enter_raw_repl()
        self.exec__("f = open('{0}', 'wb')".format(filename))
        size = len(data)
        # Loop through and write a buffer size chunk of data at a time.
        for i in range(0, size, self.BUFFER_SIZE):
            chunk_size = min(self.BUFFER_SIZE, size - i)
            chunk = repr(data[i: i + chunk_size])
            # Make sure to send explicit byte strings (handles python 2 compatibility).
            if not chunk.startswith("b"):
                chunk = "b" + chunk
            self.exec__("f.write({0})".format(chunk))
        self.exec__("f.close()")
        self.exit_raw_repl()

    def mkdir(self, folder):
        command = """
        import os
        os.mkdir('{0}')""".format(folder)

        self.enter_raw_repl()
        try:
            out = self.exec__(textwrap.dedent(command))
        except:
            pass
        self.exit_raw_repl()
        # return out[2::]

    def walk(self, folder='/'):
        command = """
            import os
            import sys
            def is_folder(path):
                try:
                    os.listdir(path)
                    return True
                except:
                    return False
            s = []
            def _listdir(path):
                global s
                n = [path, [], []]
                for i in os.listdir(path):
                    if is_folder(path + '/' + i):
                        n[1].append(_listdir(path + '/' + i))
                    else:
                        n[2].append(i)
                s.append(n)
            _listdir('{0}')
            import json
            sys.stdout.write(json.dumps(s))
        """.format(folder)

        self.enter_raw_repl()
        try:
            out = self.exec__(textwrap.dedent(command))
        except RawReplError as ex:
            raise ex
        self.exit_raw_repl()
        # print(out)
        return out[2::]

    def clear(self, path='/'):
        print('!!! Attention')
        answer = input('Are you sure about clear %s?[y/n]' % path)
        if answer in ['y', 'yes', 'YES', 'Yes']:
            command = """
                def clear_up(path):
                    for i in os.listdir(path):
                        if i == 'boot.py':
                            continue
                        try:
                            os.remove(path+'/'+i)
                        except:
                            clear_up(path+'/'+i)
                    os.rmdir(path)
                clear_up('{0}')
                """.format(path)
            self.enter_raw_repl()
            try:
                self.exec__(textwrap.dedent(command))
            except RawReplError as ex:
                raise ex
            self.exit_raw_repl()
        else:
            print('==> Cancled.')
