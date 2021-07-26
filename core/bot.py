import os
import time
import threading


class info():
    def __init__(self):
        self.start_time = time.time()
        self.round = 0
        self.round_total = 0
        self.round_begin = 0
        self.round_end = 0
        self.room_number = None
        self.info = list()

    def ouput(self, message: str, start=False):
        if start == True:
            self.round_begin = time.time()
        self.info.append(message)
        runtime = time.time() - self.start_time
        runtime = round(runtime/60, 1)
        os.system("cls")
        print("現在為第 {} 輪".format(self.round))
        print("已運行 {} 分, 上輪共使用 {} 分".format(
            runtime, round(self.round_total/60, 1)))
        print("目前房號為: {}".format(self.room_number))
        print("====================================")
        for msg in self.info:
            print(msg)

    def display(self, end=False):
        if self.round > 1 and end:
            self.info.clear()
            self.round_end = time.time()
            self.round_total = self.round_end - self.round_begin
        runtime = time.time() - self.start_time
        runtime = round(runtime/60, 1)
        os.system("cls")
        print("現在為第 {} 輪".format(self.round))
        print("已運行 {} 分, 上輪共使用 {} 分".format(
            runtime, round(self.round_total/60, 1)))
        print("目前房號為: {}".format(self.room_number))
        print("====================================")
        for msg in self.info:
            print(msg)

    def set_room_number(self, number):
        self.room_number = number
        self.display()


class auto():
    def __init__(self, boss, level, wait_people="False", main=None, main2=None, ap=None):
        self.info = info()
        self.info.round = 1
        self.people = 0  # 人數
        self.boss = boss
        self.level = level
        self.wait_people = wait_people
        self.ap = ap
        self.ap.info = self.info
        self.main = main
        self.main.info = self.info
        if main2 is not None:
            self.main2 = main2
            self.main2.info = self.info
            self.people = 3
        else:
            self.people = 2

    def start(self, version):
        if version == "quit":
            if self.people == 2:
                while True:
                    self.quit_2p(self.main, self.ap)
                    self.info.round += 1
            else:
                while True:
                    self.quit_3p(self.main, self.main2, self.ap)
                    self.info.round += 1
        else:
            if self.people == 2:
                while True:
                    self.close_2p(self.main, self.ap)
                    self.info.round += 1
            else:
                while True:
                    self.close_3p(self.main, self.main2, self.ap)
                    self.info.round += 1

    def quit_2p(self, main, ap):
        self.info.display(end=True)
        ap.open_room()
        while main.finish:
            time.sleep(0.1)
        main.enter_room(self.info.room_number)
        time.sleep(1)
        if self.wait_people == "True":
            ap.wait_people()
        ap.standby(["start_battle"])
        self.info.ouput("[隊長]進入關卡")
        ap.standby(["quit_battle"], coordinates=[30, 60])
        self.info.ouput("[隊長]準備離開戰鬥")
        ap.standby(["yes"])
        ap.room_open = False
        main_battle = threading.Thread(target=main.complete)
        main_battle.start()
        while True:
            if main.finish:
                break

    def quit_3p(self, main, main2, ap):
        self.info.display(end=True)
        ap.open_room()
        while main.finish or main2.finish:
            time.sleep(0.1)
        main_enter = threading.Thread(
            target=main.enter_room, kwargs=dict(room_number=self.info.room_number))
        main2_enter = threading.Thread(
            target=main2.enter_room, kwargs=dict(room_number=self.info.room_number))
        main_enter.start()
        time.sleep(0.3)
        main2_enter.start()
        main_enter.join()
        main2_enter.join()
        time.sleep(1)
        ap.standby(["start_battle"])
        self.info.ouput("[隊長]進入關卡")
        ap.standby(["please_wait"], tap=False)
        ap.standby(["quit_battle"], coordinates=[30, 60])
        self.info.ouput("[隊長]準備離開戰鬥")
        ap.standby(["yes"])
        ap.room_open = False
        main_battle = threading.Thread(target=main.complete)
        main2_battle = threading.Thread(target=main2.complete)
        main_battle.start()
        time.sleep(0.3)
        main2_battle.start()
        while True:
            if main.finish or main2.finish:
                break
            time.sleep(0.1)

    def close_2p(self, main, ap):
        # TODO 待新增
        pass

    def close_3p(self, main, main2, ap):
        self.info.display(end=True)
        ap.open_room()
        while main.finish or main2.finish:
            time.sleep(0.1)
        main_enter = threading.Thread(
            target=main.enter_room, kwargs=dict(room_number=self.info.room_number))
        main2_enter = threading.Thread(
            target=main2.enter_room, kwargs=dict(room_number=self.info.room_number))
        main_enter.start()
        time.sleep(0.3)
        main2_enter.start()
        main_enter.join()
        main2_enter.join()
        time.sleep(1)
        ap.standby(["start_battle"])
        self.info.ouput("[隊長]進入關卡")
        ap.standby(["please_wait"], tap=False)
        time.sleep(3)
        ap.device.shell("am force-stop air.com.gamania.worldflipper")
        time.sleep(0.3)
        self.info.ouput("[隊長]關閉遊戲")
        ap.device.shell(
            "am start -n air.com.gamania.worldflipper/air.com.gamania.worldflipper.AppEntry")
        self.info.ouput("[隊長]開啟遊戲")
        new_room = threading.Thread(
            target=ap.goto_boss, kwargs=dict(boss=self.boss, level=self.level))
        self.info.ouput("[隊長]回到開房頁面中...")
        new_room.start()
        ap.room_open = False
        main_battle = threading.Thread(target=main.complete)
        main2_battle = threading.Thread(target=main2.complete)
        main_battle.start()
        time.sleep(0.3)
        main2_battle.start()
        while True:
            if main.finish or main2.finish:
                break
            time.sleep(0.1)
