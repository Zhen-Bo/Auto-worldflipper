from cv2 import cv2
import numpy as np
import time
import pyperclip
from core.match_func import match_template as match
import image_byte
import base64


def byte_to_img(name):
    byte_data = base64.b64decode(image_byte.get_pic(name))
    return cv2.imdecode(np.frombuffer(byte_data, dtype='uint8'), cv2.IMREAD_COLOR)


class worker():
    def __init__(self, device, name):
        self.device = device
        self.name = name
        self.screenshot = None
        self.screen_muti = int(self.get_screen(detect=True))
        self.finish = False
        self.room_opened = False
        self.info = None

    def get_screen(self, detect=False, debug=False):
        """
        # 取得螢幕截圖
        detect  為True時回傳螢幕比例(基準960*540)\n
                為False時回傳螢幕截圖(寬度540)\n
        """
        image = cv2.imdecode(np.fromstring(
            bytes(self.device.screencap()), np.uint8), cv2.IMREAD_COLOR)
        if not debug:
            if detect:
                # 偵測螢幕比例
                return int(image.shape[1]/540)
            else:
                if self.screen_muti == 1:
                    self.screenshot = image
                else:
                    height = int(image.shape[0] / self.screen_muti)
                    image = cv2.resize(image, (540, height))
                    self.screenshot = image
        else:
            height = int(image.shape[1] / self.screen_muti)
            image = cv2.resize(image, (540, height))
            cv2.imwrite("debug.png", image)

    def tap(self, pos):
        """
        # 點擊指定座標\n
        pos[0] 為X軸\n
        pos[1] 為Y軸\n
        """
        pos = np.multiply(self.screen_muti, pos)
        self.device.shell("input tap {} {}".format(pos[0], pos[1]))

    def swipe(self, pos1, pos2, delay=1000):
        """
        #滑動
        start 為起始點
        end 為終點
        delay為滑動用時(單位:ms)
        """
        pos1 = np.multiply(self.screen_muti, pos1)
        pos2 = np.multiply(self.screen_muti, pos2)
        self.device.shell(
            "input swipe {} {} {} {} {}".format(pos1[0], pos1[1], pos2[0], pos2[1], delay))

    def compare(self, templates, crop=None, cap=True, debug=False):
        """
        # 比較截圖與模板圖\n
        templates 為含有模板圖名稱之圖片dict() -> {"名稱": 圖片的nparray}\n
        crop 為鎖定特定區域 -> {'x': 起始X座標:int,'y': 起始Y座標:int,'height': 區域高度,'width': 區域寬度}\n
        cap 為True時重新擷取螢幕
        """
        if cap:
            self.get_screen()
        if crop is not None:
            self.screenshot = self.screenshot[int(crop['y']):int(crop['y'])+int(crop['height']),
                                              int(crop['x']):int(crop['x'])+int(crop['width'])]
        for name in templates:
            pos = match(templates[name], self.screenshot, debug=debug)
            if isinstance(pos, list):
                return name, np.int32(pos)
        return False

    def standby(self, img, coordinates=None, tap=True, debug=False):
        """
        # 持續比較直到結果出現\n
        img 為模板圖名稱 為list內含string\n
        coordinates 是辨識時是否要持續觸碰特定一座標\n
        tap 為辨識成功時是否點擊該目標\n
        """
        if isinstance(img, str):
            # 防呆誤傳字串
            temp = list()
            temp.append(img)
            img = temp
        templates = dict()
        for name in img:
            templates[name] = byte_to_img(name)
        pos = False
        while isinstance(pos, bool):
            pos = self.compare(templates, debug=debug)
            if coordinates is not None:
                self.tap([coordinates[0], coordinates[1]])
        if tap:
            self.tap(pos[1])
        else:
            return pos

    def open_room(self):
        """
        隊長開啟房間
        """
        self.info.ouput("[{}]開啟房間中..".format(self.name), start=True)
        self.standby(["start_room"])
        enhance = ["boss_enhance", "please_wait"]
        result = self.standby(enhance, tap=False)
        if result[0] == "boss_enhance":
            self.standby(["no"])
        self.standby(["copy"])
        time.sleep(0.3)
        number = pyperclip.paste()
        self.info.set_room_number(number)
        self.room_open = True
        self.standby(["share"])
        time.sleep(1)
        self.standby(["recruit"])

    def wait_people(self):
        """等待第三個玩家進入房間"""
        crop = {'x': 365, 'y': 210, 'width': 155, 'height': 75}
        flag = [0, 0]
        while not isinstance(flag, bool):
            flag = self.compare(byte_to_img("third"), crop=crop)

    def enter_room(self, room_number):
        """
        隊員進入房間並準備開始\n
        room_number 為房號
        """
        while self.finish:
            time.sleep(0.1)
        self.info.ouput("[{}]準備輸入房號".format(self.name))
        time.sleep(1)
        self.standby(["snake"], tap=False)
        self.standby(["input_room"])
        self.info.ouput("[{}]輸入房號中...".format(self.name))
        time.sleep(1)
        self.get_screen()
        for n in room_number:
            temp = dict()
            image = "number_{}".format(n)
            temp[image] = byte_to_img(image)
            self.tap(self.compare(temp, cap=False)[1])
        self.standby(["ok"])
        enhance = ["boss_enhance", "get_ready"]
        result = self.standby(enhance, tap=False)
        if result[0] == "boss_enhance":
            self.standby(["yes"])
            self.info.ouput("[{}]進入房間".format(self.name))
            self.standby(["get_ready"])
        else:
            self.info.ouput("[{}]進入房間".format(self.name))
            self.tap(result[1])
        self.info.ouput("[{}]準備開始".format(self.name))
        self.finish = False

    def complete(self):
        self.info.ouput("等待[{}]完成關卡中...".format(self.name))
        self.standby(["next"])
        self.finish = True
        time.sleep(1)
        self.standby(["next"], coordinates=[210, 480])
        time.sleep(1)
        self.standby(["next"], coordinates=[210, 480])
        time.sleep(1)
        self.standby(["leave"], coordinates=[210, 480])
        self.finish = False

    def goto_boss(self, boss, level):
        """
        返回共鬥啟動介面\n
        boss 為要開啟的共鬥王
        level 為等級
        """
        self.standby(["menu"], tap=False)
        self.tap([0, 0])
        self.standby(["ok"])
        self.standby(["goto_quit"])
        self.standby(["boss"])
        self.standby(["snake"], tap=False)
        template = dict()
        template[boss] = byte_to_img(boss)
        pos = self.compare(template)
        if pos == False:
            start = (270, self.screenshot.shape[0]*0.75)
            end = (270, self.screenshot.shape[0]*0.45)
            self.swipe(start, end)
            time.sleep(1)
            pos = self.compare(template)
            try:
                self.tap(pos[1])
            except:
                raise "找不到BOSS"
        else:
            self.tap(pos[1])
        self.standby(["info"], tap=False)
        self.standby([level])
