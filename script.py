from logging import debug
import os
from core.bot import auto
from core.worker import worker
from ppadb.client import Client
import sys
import argparse
__author__ = "Paver(Zhen_Bo)"

os.system('cls')


def app_path():
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)  # 使用pyinstaller打包后的exe目录
    return os.path.dirname(__file__)  # 没打包前的py目录


def setup(debug=False):
    adb_path = "{}/adb/adb.exe".format(app_path())
    os.system("{0} start-server".format(adb_path))
    client = Client(host="127.0.0.1", port=5037)
    devices = client.devices()
    if debug == 'True':
        print("請選擇設備")
        get_dev, devices = select_devices(devices)
        return get_dev
    else:
        dev = []
        print("請輸入有幾個隊員(1/2)?")
        main_count = input()
        for i in range(int(main_count)):
            print("請選擇隊員 {}".format(i+1))
            get_dev, devices = select_devices(devices)
            dev.append(get_dev)
        print("請選擇隊長")
        get_dev, devices = select_devices(devices)
        dev.append(get_dev)
        return dev


def select_devices(devices, error=0):
    for i in range(len(devices)):
        print("\033[1;32m{}: {}\033[0m".format(i+1, devices[i].serial))
    if error == 1:
        print("\033[1;31m{}\033[0m".format("!!!輸入設備編號過大!!!"))
    elif error == 2:
        print("\033[1;31m{}\033[0m".format("!!!編號輸入錯誤,請在試一次!!!"))
    inputIndex = input("請輸入編號 [1 ~ {0}]:".format(len(devices)))
    try:
        value = int(inputIndex)
        if value < 1:
            exit()
        elif value > len(devices):
            return select_devices(devices, 1)
        else:
            device = devices[value-1]
            del devices[value-1]
            return (device, devices)
    except (KeyboardInterrupt, SystemExit):
        raise Exception("KeyboardInterrupt")
    except:
        return select_devices(devices, 2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="quest")
    parser.add_argument("--debug", type=str, default="False")
    parser.add_argument("--wait_people", type=str, default="False")
    args = parser.parse_args()
    mode = args.mode
    os.system('cls')
    dev = setup(args.debug)
    try:
        if len(dev) == 2:
            main = worker(dev[0], "隊員")
            ap = worker(dev[1], "隊長")
            bot = auto(wait_people=args.wait_people, main=main, ap=ap)
            bot.start(mode=mode)
        else:
            main_1 = worker(dev[0], "隊員1")
            main_2 = worker(dev[1], "隊員2")
            ap = worker(dev[2], "隊長")
            bot = auto(wait_people=args.wait_people,
                       main=main_1, main2=main_2, ap=ap)
            bot.start(mode=mode)
    except KeyboardInterrupt:
        print("STOP")
