import base64
import os
import sys


def app_path():
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)  # 使用pyinstaller打包后的exe目录
    return os.path.dirname(__file__)  # 没打包前的py目录


# path = os.path.join(app_path(), "template")
dir_path = os.path.abspath(os.path.join(app_path(), os.path.pardir))
path = os.path.join(dir_path, "template")
name = list()


def pic2byte(file, image_name):
    name.append(image_name)
    pic = open(file, 'rb')
    content = '        \"{}\" : {},\n'.format(
        image_name, base64.b64encode(pic.read()))
    pic.close()
    with open(os.path.join(dir_path, 'image_byte.py'), 'a') as f:
        f.write(content)


if __name__ == '__main__':
    with open(os.path.join(dir_path, 'image_byte.py'), 'w') as f:
        pass
    with open(os.path.join(dir_path, 'image_byte.py'), 'a') as f:
        f.write("def get_pic(var):\n")
        f.write("    return {\n")
    for file in os.listdir(path):
        if ".png" in file:
            pic2byte(os.path.join(path, file), file.split('.')[0])
    with open(os.path.join(dir_path, 'image_byte.py'), 'a') as f:
        f.write("    }.get(var, 'error')\n")

    with open(os.path.join(dir_path, 'image_byte.py'), 'a') as f:
        f.write("def get_list():\n")
        f.write("    return {}".format(name))
