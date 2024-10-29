# 全部扒起来，然后人工+手动
import random
import time
from time_helper import *
import copy
from task import Task, TASK_DICT
import requests
from logger import logger


class Piggy:
    def __init__(self,number, tg_webapp_data, proxy):
        self.token = ""
        self.number = number
        self.task_dict = {}
        self.tg_webapp_data = tg_webapp_data
        self.proxy = proxy

        self.get_token_bll()

    def get_proxies(self):
        if self.proxy != "":
            return {
                "http": f"socks5://{self.proxy}",
                "https": f"socks5://{self.proxy}",
            }
        else:
            return None

    def get_token_bll(self):
        res = self.get_token()
        res.raise_for_status()
        res_json = res.json()
        token = res_json.get("data").get("token")
        self.token = token
        logger.info(f"账号：{self.number} | 成功获取token | {self.token}")

    def get_token(self):
        url = f"https://api.prod.piggypiggy.io/tgBot/login?{self.tg_webapp_data}"
        headers = {
            "content-type": "application/json",
            "Referer": "https://restaurant-v2.piggypiggy.io/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        response = requests.get(url, headers=headers, proxies=self.get_proxies())
        return response

    def get_headers(self):
        headers = {
            "authorization": f"bearer {self.token}",
            "content-type": "application/json",
            "sec-ch-ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Referer": "https://restaurant-v2.piggypiggy.io/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        return headers

    def get_achievement_config(self):
        url = "https://api.prod.piggypiggy.io/game/GetAchievementConfig"
        response = requests.post(url, headers=self.get_headers(), json=None, proxies=self.get_proxies())
        return response

    def finish_achievement_bll(self, achievement_id_list):
        for achievement_id in achievement_id_list:
            res = self.take_achievement(achievement_id)
            res_json = res.json()
            logger.info(f"账号：{self.number} | 执行任务：{achievement_id} | {res_json}")

            res = self.complete_achievement(achievement_id)
            res_json = res.json()
            logger.info(f"账号：{self.number} | 完成任务：{achievement_id} | {res_json}")

    def get_achievement_info(self):
        url = "https://api.prod.piggypiggy.io/game/GetAchievementInfo"
        response = requests.post(url, headers=self.get_headers(), json=None, proxies=self.get_proxies())
        return response

    def complete_achievement(self, achievement_id):
        url = "https://api.prod.piggypiggy.io/game/CompleteAchievement"
        data = {
            "AchievementID": achievement_id,
            "PlayerID": 0
        }
        response = requests.post(url, headers=self.get_headers(), json=data, proxies=self.get_proxies())
        return response

    def take_achievement(self,achievement_id):
        url = "https://api.prod.piggypiggy.io/game/AddSchedule"
        data = {
            "Type": 2,
            "Id": achievement_id,
            "PlayerID": 0
        }
        response = requests.post(url, headers=self.get_headers(), json=data, proxies=self.get_proxies())
        return response

    def refresh_task_dict_and_return_current_task_id(self):
        res = self.get_daily_task_info()
        res_json = res.json()
        logger.info(f"账号：{self.number} | 获取已完成工作信息 | {res_json}")

        map_task = res_json.get("data").get("mapTask")
        task_dict = copy.deepcopy(TASK_DICT)
        task_id_list = TASK_DICT.keys()
        for task_id in task_id_list:
            complete_count = 0
            last_complete_time = -1
            if map_task != None and str(task_id) in map_task:
                complete_count = map_task.get(str(task_id)).get("compeleteCount")
                last_complete_time = map_task.get(str(task_id)).get("lastCompleteTime")

            TASK = TASK_DICT.get(task_id)
            TASKS_LEFT = TASK.tasks_left

            task = task_dict.get(task_id)
            task.tasks_left = task.tasks_left - complete_count
            task.last_complete_time = last_complete_time

            logger.info(f"账号：{self.number} | "
                        f"任务：{task_id} 剩余次数：{task.tasks_left}/{TASKS_LEFT}")
        self.task_dict = task_dict

        current_task_id = res_json.get("data", {}).get("curTaskID", -1)
        return current_task_id

    def complete_task_bll(self, task_id):
        task = TASK_DICT.get(task_id)
        random_sleep_time = task.duration + random.randint(1,5)
        logger.info(f"账号：{self.number} | {task_id} | 等待获取奖励，睡眠：{random_sleep_time}秒")
        time.sleep(random_sleep_time)
        self.complete_task(task_id)

    def setup_shop_bll(self):
        res = self.setup_shop()
        res.raise_for_status()
        logger.info(f"账号：{self.number} | 成功启动工作面板")

    def get_task_id(self):
        task_id = -1
        for key,value in self.task_dict.items():
            if (value.tasks_left > 0 and
                    get_time_difference_now(value.last_complete_time) > value.cd_time):
                task_id = key
                break
        return task_id

    def take_task_bll(self, task_id):
        logger.info(f"账号：{self.number} | 正在开始进行任务 | {task_id}")
        res = self.take_task(task_id)
        res_json = res.json()
        logger.info(f"账号：{self.number} | 开始执行任务 | {task_id} | {res_json}")

    def get_most_close_task_cd_time(self):
        close_time = 999999999
        for key,value in self.task_dict.items():
            if value.tasks_left > 0:
                sleep_time = value.cd_time - get_time_difference_now(value.last_complete_time)
                if sleep_time < close_time:
                    close_time = sleep_time
        return close_time

    def take_all_task_bll(self):
        self.setup_shop_bll()
        while True:
            current_task_id = self.refresh_task_dict_and_return_current_task_id()

            if current_task_id != -1:
                self.complete_task_bll(current_task_id)
            else:
                task_id = self.get_task_id()

                # 有可能是当前所有任务都在cd
                if task_id == -1:
                    sleep_time = self.get_most_close_task_cd_time()
                    if sleep_time == 999999999:
                        logger.info(f"账号：{self.number} | 已经完成所有任务，正在关闭进程")
                        return

                    logger.info(f"账号：{self.number} | 正在等待任务cd中，睡眠：{sleep_time}")
                    time.sleep(sleep_time)
                    continue

                self.take_task_bll(task_id)
                self.complete_task_bll(task_id)

    def airdrop_code_take_bll(self, code_list):
        for code in code_list:
            res = self.airdrop_cdoe_take(code)
            res_json = res.json()
            if res_json.get("msg") == "faild":
                logger.info(f"账号：{self.number} | 激活码：<yellow>{code}</yellow> | <red>失败</red>")
            else:
                logger.info(f"账号：{self.number} | 激活码：<yellow>{code}</yellow> | <green>成功</green>")


    def airdrop_cdoe_take(self, code):
        url = "https://api.prod.piggypiggy.io/game/AirdropCodeTake"
        data = {
            "Code" : code,
            "PlayerID": 0
        }

        response = requests.post(url, headers=self.get_headers(), json=data,proxies=self.get_proxies())
        return response

    def setup_shop(self):
        url = "https://api.prod.piggypiggy.io/game/SetUpShop"
        data = {
            "PlayerID": 0
        }

        response = requests.post(url, headers=self.get_headers(), json=data,proxies=self.get_proxies())
        return response

    def take_task(self, taskid):
        url = "https://api.prod.piggypiggy.io/game/TakeTask"
        data = {
            "TaskID": taskid,
            "PlayerID": 0,
            "Ad": 0
        }

        response = requests.post(url, headers=self.get_headers(), json=data, proxies=self.get_proxies())
        return response

    def complete_task(self, taskid):
        url = "https://api.prod.piggypiggy.io/game/CompleteTask"
        data = {
            "TaskID": taskid,
            "PlayerID": 0,
            "Ad": 0
        }

        response = requests.post(url, headers=self.get_headers(), json=data, proxies=self.get_proxies())
        return response

    def get_daily_task_info(self):
        url = "https://api.prod.piggypiggy.io/game/GetDailyTaskInfo"
        data = {
            "PlayerID": 0
        }

        response = requests.post(url, headers=self.get_headers(), json=data, proxies=self.get_proxies())
        return response
