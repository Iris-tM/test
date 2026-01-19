"""
数据导出器

支持将数据导出为 CSV、Excel、JSON 格式
"""

import os
import json
import pandas as pd
from typing import Dict, List, Union, Optional
from datetime import datetime
from pathlib import Path

from stork_agent.config import Config


def export_data(
    data: Union[Dict, List],
    format: str = "csv",
    filename: Optional[str] = None,
    export_dir: Optional[str] = None
) -> str:
    """
    导出数据到文件

    Args:
        data: 要导出的数据（字典或列表）
        format: 导出格式 - csv, excel, json
        filename: 文件名（不含扩展名），默认自动生成
        export_dir: 导出目录，默认为 output/exports/

    Returns:
        导出文件的绝对路径
    """
    format = format.lower()
    if format not in {"csv", "excel", "json"}:
        raise ValueError(f"不支持的导出格式: {format}")

    # 确定导出目录
    if export_dir is None:
        export_dir = os.path.join(Config.OUTPUT_DIR, "exports")
    os.makedirs(export_dir, exist_ok=True)

    # 生成文件名
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{timestamp}"

    # 添加扩展名
    extensions = {"csv": ".csv", "excel": ".xlsx", "json": ".json"}
    filepath = os.path.join(export_dir, f"{filename}{extensions[format]}")

    # 转换数据为 DataFrame
    df = _data_to_dataframe(data)

    # 导出
    if format == "csv":
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
    elif format == "excel":
        df.to_excel(filepath, index=False, engine="openpyxl")
    elif format == "json":
        with open(filepath, "w", encoding="utf-8") as f:
            if isinstance(data, dict):
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                json.dump({"data": data}, f, ensure_ascii=False, indent=2)

    return os.path.abspath(filepath)


def _data_to_dataframe(data: Union[Dict, List]) -> pd.DataFrame:
    """
    将数据转换为 DataFrame

    Args:
        data: 数据（字典或列表）

    Returns:
        DataFrame
    """
    if isinstance(data, list):
        # 列表数据直接转换
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        # 字典数据处理
        if "stocks" in data and isinstance(data["stocks"], list):
            # 股票列表
            return pd.DataFrame(data["stocks"])
        elif "data" in data and isinstance(data["data"], list):
            # 历史数据等
            return pd.DataFrame(data["data"])
        elif "stocks" in data and isinstance(data["stocks"], dict):
            # 对比数据
            return pd.DataFrame(data["stocks"]["stocks"])
        else:
            # 单条数据，转为单行 DataFrame
            return pd.DataFrame([data])
    else:
        return pd.DataFrame()


def export_stock_list(
    stocks: List[Dict],
    criteria: Optional[Dict] = None,
    format: str = "csv"
) -> str:
    """
    导出股票列表

    Args:
        stocks: 股票列表
        criteria: 筛选条件（用于文件名）
        format: 导出格式

    Returns:
        导出文件路径
    """
    # 生成描述性文件名
    if criteria:
        parts = []
        for key, value in criteria.items():
            if value is not None and key != "limit":
                parts.append(f"{key}_{value}")
        filename = "screen_" + "_".join(parts) if parts else "screen_result"
    else:
        filename = "stock_list"

    return export_data(stocks, format=format, filename=filename)


def export_history_data(
    data: Dict,
    format: str = "csv"
) -> str:
    """
    导出历史K线数据

    Args:
        data: 历史数据字典
        format: 导出格式

    Returns:
        导出文件路径
    """
    code = data.get("code", "unknown")
    filename = f"history_{code}_{datetime.now().strftime('%Y%m%d')}"

    return export_data(data, format=format, filename=filename)


def export_comparison_data(
    data: Dict,
    format: str = "csv"
) -> str:
    """
    导出对比数据

    Args:
        data: 对比数据字典
        format: 导出格式

    Returns:
        导出文件路径
    """
    stocks = data.get("stocks", [])
    if not stocks:
        raise ValueError("没有可导出的对比数据")

    # 使用股票代码生成文件名
    codes = "_".join([s.get("code", "unknown") for s in stocks])
    filename = f"compare_{codes}"

    return export_data(data, format=format, filename=filename)


def get_export_summary(filepath: str) -> Dict:
    """
    获取导出文件的摘要信息

    Args:
        filepath: 导出文件路径

    Returns:
        摘要信息字典
    """
    path = Path(filepath)

    # 读取数据
    if path.suffix == ".csv":
        df = pd.read_csv(filepath)
    elif path.suffix == ".xlsx":
        df = pd.read_excel(filepath)
    elif path.suffix == ".json":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data.get("data", data))
    else:
        return {"error": "不支持的文件格式"}

    return {
        "filepath": os.path.abspath(filepath),
        "filename": path.name,
        "rows": len(df),
        "columns": len(df.columns),
        "size_mb": path.stat().st_size / (1024 * 1024),
        "format": path.suffix[1:],
    }
