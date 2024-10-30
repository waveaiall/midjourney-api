__version__ = '0.0.1'


from apscheduler.schedulers.background import BackgroundScheduler
from auth import refreshToken
from util._queue import get_task_size, execute_task_by_period

scheduler = BackgroundScheduler()


# 示例 4: 每天的每隔 5 分钟执行一次
scheduler.add_job(refreshToken, 'cron', minute='*/5')
# 示例 4: 每天的每隔 5 分钟执行一次
scheduler.add_job(get_task_size, 'cron', minute='*/5')
# 示例 4: 每天的每隔 5 分钟执行一次
scheduler.add_job(execute_task_by_period, 'cron', minute='*/5')

scheduler.start()