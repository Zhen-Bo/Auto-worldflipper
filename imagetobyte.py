import base64
import os

path = './template'
name = list()


def pic2byte(file, image_name):
    name.append(image_name)
    pic = open(file, 'rb')
    content = '        \"{}\" : {},\n'.format(
        image_name, base64.b64encode(pic.read()))
    pic.close()
    with open('image_byte.py', 'a') as f:
        f.write(content)


if __name__ == '__main__':
    with open('image_byte.py', 'w') as f:
        pass
    with open('image_byte.py', 'a') as f:
        f.write("def get_pic(var):\n")
        f.write("    return {\n")
    for file in os.listdir(path):
        if ".png" in file:
            pic2byte(os.path.join(path, file), file.split('.')[0])
    with open('image_byte.py', 'a') as f:
        f.write("    }.get(var, 'error')\n")

    with open('image_byte.py', 'a') as f:
        f.write("def get_list():\n")
        f.write("    return {}".format(name))
