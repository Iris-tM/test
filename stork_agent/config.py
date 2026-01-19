"""
配置管理模块
"""

import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置"""

    # 数据源配置
    AKSHARE_ENABLED: bool = os.getenv("AKSHARE_ENABLED", "true").lower() == "true"
    TUSHARE_TOKEN: Optional[str] = os.getenv("TUSHARE_TOKEN")
    TUSHARE_ENABLED: bool = os.getenv("TUSHARE_ENABLED", "false").lower() == "true"

    # API 配置
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    # 缓存配置
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 秒
    CACHE_DIR: str = os.getenv("CACHE_DIR", "./output/cache")

    # 图表配置（Plotly HTML）
    CHART_DPI: int = int(os.getenv("CHART_DPI", "100"))
    CHART_FORMAT: str = os.getenv("CHART_FORMAT", "html")  # html, png

    # 输出配置
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./output")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # MCP 服务器配置
    MCP_SERVER_PORT: Optional[int] = int(os.getenv("MCP_SERVER_PORT")) if os.getenv("MCP_SERVER_PORT") else None
    MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "localhost")

    # 会话配置
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "1800"))  # 30分钟
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "50"))

    @classmethod
    def setup(cls):
        """初始化配置"""
        # 创建输出目录
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        # 创建缓存目录
        os.makedirs(cls.CACHE_DIR, exist_ok=True)
        # 创建图表输出目录
        os.makedirs(os.path.join(cls.OUTPUT_DIR, "charts"), exist_ok=True)
        # 创建导出目录
        os.makedirs(os.path.join(cls.OUTPUT_DIR, "exports"), exist_ok=True)


# 初始化配置
Config.setup()
