from config import settings
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import random
import time

from logger import logger
from piggy import Piggy

def process_row(row):
    number = row[0]
    tg_wabapp_data = row[1]
    proxy = row[2] if len(row) > 2 else ""
    piggy = Piggy(number,tg_wabapp_data,proxy)
    piggy.finish_achievement_bll(settings.LEFT_SIDE_TASK_LIST)
    piggy.airdrop_code_take_bll(settings.AIRDROP_CODE_LIST)
    piggy.take_all_task_bll()

if __name__ == "__main__":
    csv_data = []
    data_path = 'data.csv'
    with open(data_path, mode='r') as file:
        csv_data = list(csv.reader(file))
        csv_data = [row for row in csv_data if any(row)]  # 过滤掉空行
        csv_data = csv_data[1:]
        logger.info(f"成功读取{data_path} | 总共{len(csv_data)}行数据")

        with ThreadPoolExecutor(max_workers=len(csv_data)) as executor:
            future_to_row = {executor.submit(process_row, row): row for row in csv_data}

            for future in as_completed(future_to_row):
                row = future_to_row[future]