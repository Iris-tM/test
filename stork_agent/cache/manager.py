"""
缓存管理器

提供内存和磁盘双层缓存，支持不同数据类型的 TTL 策略
- JSON 缓存：用于简单数据，可读性好
- Pickle 缓存：用于复杂数据（如 DataFrame），支持 Python 对象
"""

import os
import json
import pickle
import hashlib
from typing import Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from stork_agent.config import Config


class CacheManager:
    """缓存管理器，支持内存和磁盘双层缓存"""

    # TTL 策略（秒）
    TTL_HISTORICAL = 86400      # 历史数据：1天
    TTL_REALTIME = 300          # 实时数据：5分钟
    TTL_SCREENING = 3600        # 筛选结果：1小时
    TTL_STATIC = 604800         # 静态数据：7天

    def __init__(self, cache_dir: Optional[str] = None):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录，默认为 output/cache/
        """
        if cache_dir is None:
            cache_dir = os.path.join(Config.OUTPUT_DIR, "cache")

        self.cache_dir = Path(cache_dir)
        self.json_dir = self.cache_dir / "json"
        self.pickle_dir = self.cache_dir / "pickle"

        # 创建缓存目录
        self.json_dir.mkdir(parents=True, exist_ok=True)
        self.pickle_dir.mkdir(parents=True, exist_ok=True)

    def _generate_key(self, prefix: str, params: dict) -> str:
        """
        生成缓存键

        Args:
            prefix: 键前缀（如 "stock", "history" 等）
            params: 参数字典

        Returns:
            缓存键
        """
        # 将参数排序后生成哈希
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:12]
        return f"{prefix}_{param_hash}"

    def _get_cache_path(self, key: str, use_pickle: bool = False) -> Path:
        """
        获取缓存文件路径

        Args:
            key: 缓存键
            use_pickle: 是否使用 pickle 格式

        Returns:
            缓存文件路径
        """
        subdir = self.pickle_dir if use_pickle else self.json_dir
        extension = ".pkl" if use_pickle else ".json"
        return subdir / f"{key}{extension}"

    def _is_expired(self, filepath: Path, ttl: int) -> bool:
        """
        检查缓存是否过期

        Args:
            filepath: 缓存文件路径
            ttl: 生存时间（秒）

        Returns:
            是否过期
        """
        if not filepath.exists():
            return True

        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
        return datetime.now() - mtime > timedelta(seconds=ttl)

    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """
        获取缓存

        Args:
            key: 缓存键
            ttl: 生存时间（秒），None 表示使用默认检查

        Returns:
            缓存数据，如果不存在或过期则返回 None
        """
        # 尝试 JSON 缓存
        json_path = self._get_cache_path(key, use_pickle=False)
        if json_path.exists():
            if ttl is None or not self._is_expired(json_path, ttl):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except (json.JSONDecodeError, IOError):
                    pass

        # 尝试 Pickle 缓存
        pickle_path = self._get_cache_path(key, use_pickle=True)
        if pickle_path.exists():
            if ttl is None or not self._is_expired(pickle_path, ttl):
                try:
                    with open(pickle_path, "rb") as f:
                        return pickle.load(f)
                except (pickle.PickleError, IOError):
                    pass

        return None

    def set(self, key: str, value: Any, use_pickle: bool = False, ttl: Optional[int] = None) -> None:
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值
            use_pickle: 是否使用 pickle 格式
            ttl: 生存时间（秒），仅用于元数据记录
        """
        filepath = self._get_cache_path(key, use_pickle)

        try:
            if use_pickle:
                with open(filepath, "wb") as f:
                    pickle.dump(value, f)
            else:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(value, f, ensure_ascii=False, indent=2)
        except (IOError, pickle.PickleError) as e:
            # 缓存失败不影响主流程
            print(f"Warning: Failed to write cache: {e}")

    def delete(self, key: str) -> None:
        """
        删除缓存

        Args:
            key: 缓存键
        """
        json_path = self._get_cache_path(key, use_pickle=False)
        pickle_path = self._get_cache_path(key, use_pickle=True)

        for path in [json_path, pickle_path]:
            if path.exists():
                try:
                    path.unlink()
                except IOError:
                    pass

    def clear(self, older_than_days: int = 7) -> int:
        """
        清理过期缓存

        Args:
            older_than_days: 清理多少天前的缓存

        Returns:
            清理的文件数量
        """
        count = 0
        cutoff = datetime.now() - timedelta(days=older_than_days)

        for directory in [self.json_dir, self.pickle_dir]:
            for filepath in directory.iterdir():
                if filepath.is_file():
                    mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                    if mtime < cutoff:
                        try:
                            filepath.unlink()
                            count += 1
                        except IOError:
                            pass

        return count

    def is_realtime_query(self, intent: str) -> bool:
        """
        判断是否为实时查询

        Args:
            intent: 查询意图

        Returns:
            是否为实时查询
        """
        realtime_intents = {"realtime", "quote", "price"}
        return intent.lower() in realtime_intents

    def get_ttl_for_intent(self, intent: str) -> int:
        """
        根据查询意图获取 TTL

        Args:
            intent: 查询意图

        Returns:
            TTL（秒）
        """
        intent = intent.lower()

        if intent in {"realtime", "quote", "price"}:
            return self.TTL_REALTIME
        elif intent in {"history", "kline", "financial"}:
            return self.TTL_HISTORICAL
        elif intent in {"screen", "screener", "filter"}:
            return self.TTL_SCREENING
        else:
            return self.TTL_STATIC


# 全局缓存管理器实例
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
