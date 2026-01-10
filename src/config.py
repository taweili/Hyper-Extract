# src/hyperextract/config.py
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# 1. 自动加载 .env
# 寻找项目根目录的 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 2. 配置 Loguru
# 移除默认的 handler (避免重复或格式不统一)
logger.remove()

# 添加控制台输出 (开发模式下级别可以是 DEBUG)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logger.add(
    sys.stderr,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# 添加文件输出 (自动轮转，保存日志文件)
logger.add(
    "logs/hyperextract.log",
    rotation="10 MB",  # 文件超过 10MB 就分割
    retention="10 days",  # 只保留最近 10 天
    level="DEBUG",  # 文件里记录更详细的信息
    compression="zip",  # 历史日志压缩
)


# 导出 logger 供其他模块使用
__all__ = ["logger"]
