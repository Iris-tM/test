"""
缓存模块

提供内存和磁盘双层缓存，支持不同数据类型的 TTL 策略
"""

from .manager import CacheManager

__all__ = ["CacheManager"]
