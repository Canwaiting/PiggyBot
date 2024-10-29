import math
import time

def get_time_difference_now(timestamp_ms):
    timestamp_sec = timestamp_ms / 1000
    current_time_sec = time.time()
    difference = current_time_sec - timestamp_sec
    return int(difference)


