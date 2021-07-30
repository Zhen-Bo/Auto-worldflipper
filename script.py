import os
from ppadb.client import Client
import sys
import argparse
import zipfile
from tqdm import tqdm
import win32file
import requests
from bs4 import BeautifulSoup
import urllib.request
__author__ = "Paver(Zhen_Bo)"
local_version = "1.3"


def app_path():
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)  # 使用pyinstaller打包后的exe目录
    return os.path.dirname(__file__)  # 没打包前的py目录


def setup():
    adb_path = "{}/adb/adb.exe".format(app_path())
    os.system("{0} start-server".format(adb_path))
    client = Client(host="127.0.0.1", port=5037)
    devices = client.devices()
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


def get_info():
    battle_info = list()
    boss = {"0": "大蛇", "1": "亞多明尼斯", "2": "白虎", "3": "詛咒艾基爾之長",
            "4": "寄居蟹船長", "5": "遺跡魔像", "6": "不死族之王雷希塔洛", "7": "風之隱者"}
    boss_code = {"0": "snake", "1": "robot", "2": "tiger", "3": "curse",
                 "4": "crab", "5": "golem", "6": "undead", "7": "owl"}
    level = {"0": "超級", "1": "高級+", "2": "高級", "3": "中級", "4": "初級"}
    level_code = {"0": "level_super", "1": "level_high+",
                  "2": "level_high", "3": "level_middle", "4": "level_begin"}
    select_boss = None
    while True:
        os.system('cls')
        print("請問要選擇的共鬥王為")
        for index in boss:
            print("{}: {}".format(index, boss[index]))
        print("====================================")
        number = int(input("請輸入數字代號(0~7): "))
        if number >= 0 and number <= 7:
            select_boss = boss[str(number)]
            battle_info.append(boss_code[str(number)])
            break
    while True:
        os.system('cls')
        print("已選定BOSS: {}".format(select_boss))
        print("====================================")
        print("請問要選擇的難度為")
        for index in level:
            print("{}: {}".format(index, level[index]))
        print("====================================")
        number = int(input("請輸入數字代號(0~4): "))
        if number >= 0 and number <= 4:
            battle_info.append(level_code[str(number)])
            break
    return [battle_info[0], battle_info[1]]


def check_update(version):
    print("檢查更新中...")
    # remote_version = requests.get(
    #     "https://zhen-bo.github.io/Auto-worldflipper/").text
    remote_version = urllib.request.urlopen(
        "https://zhen-bo.github.io/Auto-worldflipper/")
    remote_version = remote_version.read().decode("utf8")
    soup = BeautifulSoup(remote_version, features="html.parser")
    remote_version = soup.find_all("p", {"class": "version"})
    remote_version = remote_version[0].text.split("\n")[0]
    remote_link = "https://github.com/Zhen-bo/Auto-worldflipper/releases/download/{}/Auto-worldflipper.zip".format(
        remote_version)
    if remote_version == version:
        print("當前為最新版: {}".format(local_version))
    elif remote_version != version:
        print("即將從 {} 版 升級成 {} 版".format(version, remote_version))
        r = requests.get(remote_link, stream=True, allow_redirects=True)
        print("開始下載更新...")
        total_size = int(r.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size, unit='ib', unit_scale=True)
        with open(os.path.join(app_path(), "update.zip"), 'wb') as file:
            for data in r.iter_content(1024):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        print("下載完成")
        print("正在更新中...")
        temp_dir = os.path.join(app_path(), "_update_tmp/")
        with zipfile.ZipFile(os.path.join(app_path(), "update.zip"), 'r') as zip_ref:
            if not os.path.exists(temp_dir):
                os.mkdir(temp_dir)
            for file in tqdm(iterable=zip_ref.namelist(), total=len(zip_ref.namelist())):
                try:
                    zip_ref.extract(member=file, path=app_path())
                except:
                    try:
                        win32file.MoveFileEx(os.path.join(app_path(), file), os.path.join(
                            temp_dir, file), win32file.MOVEFILE_REPLACE_EXISTING)
                    except Exception as e:
                        if e.args[0] == 3:
                            dir_path = temp_dir
                            for folder in file.split('/')[:-1]:
                                dir_path = os.path.join(dir_path, folder)
                            file_name = file.split('/')[-1]
                            os.makedirs(dir_path)
                        win32file.MoveFileEx(os.path.join(app_path(), file), os.path.join(
                            dir_path, file_name), win32file.MOVEFILE_REPLACE_EXISTING)
                    zip_ref.extract(member=file, path=app_path())
        #os.system("start {}".format(os.path.join(app_path(), "Auto-worldflipper.exe")))
        os.system("start {}".format(
            "choice /C Y /N /D Y /T 1 & Auto-worldflipper.exe"))
        sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # 如果只有一個隊員的話是否招募並等待
    parser.add_argument("--wait_people", type=str, default="False")
    # quit=退出模式 close=重啟模式
    parser.add_argument("--mode", type=str, default="quit",)
    args = parser.parse_args()
    mode = args.mode
    os.system('cls')
    if os.path.exists(os.path.join(app_path(), "_update_tmp/")):
        os.system('choice /C Y /N /D Y /T 1 & rmdir /s {}'.format(
            os.path.join(app_path(), "_update_tmp/")))
    check_update(local_version)
    from core.bot import auto
    from core.worker import worker
    dev = setup()
    boss, level = get_info()
    try:
        if len(dev) == 2:
            main = worker(dev[0], "隊員")
            ap = worker(dev[1], "隊長")
            bot = auto(boss=boss, level=level,
                       wait_people=args.wait_people, main=main, ap=ap)
            bot.start(mode)
        else:
            main_1 = worker(dev[0], "隊員1")
            main_2 = worker(dev[1], "隊員2")
            ap = worker(dev[2], "隊長")
            bot = auto(boss=boss, level=level, wait_people=args.wait_people,
                       main=main_1, main2=main_2, ap=ap)
            bot.start(mode)
    except KeyboardInterrupt:
        print("STOP")
        sys.exit()
    except:
        os.system("PAUSE")
