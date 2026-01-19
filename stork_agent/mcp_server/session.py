"""
MCP 会话状态管理

管理查询状态，支持分页和导出功能
"""

import time
from typing import Optional, Dict, List, Any
from datetime import datetime


class QuerySession:
    """管理查询状态，支持分页和导出"""

    def __init__(self, session_timeout: int = 1800):
        """
        初始化会话

        Args:
            session_timeout: 会话超时时间（秒），默认 30 分钟
        """
        self.current_query: Optional[str] = None
        self.current_page: int = 1
        self.page_size: int = 50
        self.total_pages: int = 1
        self.total_count: int = 0
        self.complete_data: Optional[List[Dict]] = None
        self.session_timeout: int = session_timeout
        self.last_activity: float = time.time()
        self.query_criteria: Optional[Dict] = None

    def is_expired(self) -> bool:
        """
        检查会话是否过期

        Returns:
            是否过期
        """
        return time.time() - self.last_activity > self.session_timeout

    def update_activity(self) -> None:
        """更新最后活动时间"""
        self.last_activity = time.time()

    def set_query(
        self,
        query: str,
        data: List[Dict],
        criteria: Optional[Dict] = None,
        page_size: int = 50
    ) -> None:
        """
        设置当前查询

        Args:
            query: 查询描述
            data: 完整数据
            criteria: 查询条件
            page_size: 每页数量
        """
        self.current_query = query
        self.complete_data = data
        self.query_criteria = criteria
        self.total_count = len(data)
        self.page_size = page_size
        self.total_pages = (self.total_count + page_size - 1) // page_size
        self.current_page = 1
        self.update_activity()

    def get_current_page(self) -> List[Dict]:
        """
        获取当前页数据

        Returns:
            当前页数据
        """
        if self.complete_data is None:
            return []

        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        return self.complete_data[start:end]

    def next_page(self) -> List[Dict]:
        """
        获取下一页数据

        Returns:
            下一页数据
        """
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_activity()
        return self.get_current_page()

    def prev_page(self) -> List[Dict]:
        """
        获取上一页数据

        Returns:
            上一页数据
        """
        if self.current_page > 1:
            self.current_page -= 1
            self.update_activity()
        return self.get_current_page()

    def goto_page(self, page: int) -> List[Dict]:
        """
        跳转到指定页

        Args:
            page: 目标页码

        Returns:
            指定页数据
        """
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self.update_activity()
        return self.get_current_page()

    def get_page_info(self) -> Dict[str, Any]:
        """
        获取分页信息

        Returns:
            分页信息字典
        """
        return {
            "current_page": self.current_page,
            "total_pages": self.total_pages,
            "total_count": self.total_count,
            "page_size": self.page_size,
            "has_next": self.current_page < self.total_pages,
            "has_prev": self.current_page > 1,
        }

    def clear(self) -> None:
        """清除会话数据"""
        self.current_query = None
        self.current_page = 1
        self.total_pages = 1
        self.total_count = 0
        self.complete_data = None
        self.query_criteria = None


# 全局会话管理器
_sessions: Dict[str, QuerySession] = {}


def get_session(session_id: str = "default") -> QuerySession:
    """
    获取或创建会话

    Args:
        session_id: 会话 ID

    Returns:
        会话对象
    """
    if session_id not in _sessions:
        _sessions[session_id] = QuerySession()
    else:
        # 检查是否过期
        if _sessions[session_id].is_expired():
            _sessions[session_id] = QuerySession()
        else:
            _sessions[session_id].update_activity()

    return _sessions[session_id]


def clear_session(session_id: str = "default") -> None:
    """
    清除指定会话

    Args:
        session_id: 会话 ID
    """
    if session_id in _sessions:
        _sessions[session_id].clear()
        del _sessions[session_id]


def cleanup_expired_sessions() -> int:
    """
    清理过期会话

    Returns:
        清理的会话数量
    """
    expired = [
        sid for sid, session in _sessions.items()
        if session.is_expired()
    ]

    for sid in expired:
        del _sessions[sid]

    return len(expired)
