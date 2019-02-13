import os
def is_folder(path):
    try:
        os.listdir(path)
        return True
    except:
        return False

s = []

def traverse(path):
    global s
    n = [path, [], []]
    for i in os.listdir(path):

        if is_folder(path + '/' + i):
            n[1].append(traverse(path + '/' + i))
        else:
            n[2].append(i)
    s.append(n)


if __name__ == '__main__':
    traverse('./src')
    # print(s)
    for folder, _, filenames in s:
        for f in filenames:
            print('%s/%s' % (folder, f))
