class Task:
    def __init__(self,task_id, tasks_left, duration, cd_time, last_complete_time = -1):
        self.task_id = task_id
        self.tasks_left = tasks_left
        self.duration = duration
        self.cd_time = cd_time
        self.last_complete_time = last_complete_time

TASK_DICT = {
    1001: Task(
        task_id=1001,
        tasks_left=2,
        duration=30,
        cd_time=3 * 60 * 60
    ),
    1002: Task(
        task_id=1002,
        tasks_left=3,
        duration=20,
        cd_time=5 * 60
    ),
    1003: Task(
        task_id=1003,
        tasks_left=4,
        duration=10,
        cd_time=5 * 60
    ),
    1004: Task(
        task_id=1004,
        tasks_left=4,
        duration=20,
        cd_time=6 * 60
    ),
    1005: Task(
        task_id=1005,
        tasks_left=5,
        duration=10,
        cd_time=10 * 60
    ),
    1006: Task(
        task_id=1006,
        tasks_left=5,
        duration=30,
        cd_time=15 * 60
    )
}