from loguru import logger
import sys
logger.remove()
logger.add(sink=sys.stdout, format="<white>{time:YYYY-MM-DD HH:mm:ss}</white>"
                                   " | <level>{level: <8}</level>"
                                   " | <cyan><b>{line}</b></cyan>"
                                   " - <white><b>{message}</b></white>")
logger = logger.opt(colors=True)