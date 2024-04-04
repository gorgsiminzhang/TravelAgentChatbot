import logging
from colorlog import ColoredFormatter

# 创建一个日志记录器
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# 创建一个流处理器
stream_handler = logging.StreamHandler()

# 设置颜色格式
formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# # 测试不同级别的日志输出
logger.debug('一个调试消息')
logger.info('一个信息消息')
logger.warning('一个警告消息')
logger.error('一个错误消息')
logger.critical('一个严重错误消息')
