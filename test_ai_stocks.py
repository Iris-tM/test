# -*- coding: utf-8 -*-
"""测试查询 AI 应用板块公司上市时间"""

import sys
import akshare as ak
import pandas as pd

# 设置输出编码
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

print("=" * 80)
print("AI 应用板块公司上市时间查询")
print("=" * 80)

# 方法1：使用行业板块筛选
print("\n【方法1】通过行业板块获取 AI 相关公司...")
try:
    # 获取行业成分股
    # 尝试获取计算机、软件等AI相关行业
    industry_stocks = ak.stock_board_industry_name_em()

    # 查找 AI 相关行业
    ai_industries = []
    for idx, row in industry_stocks.iterrows():
        industry_name = row.get("板块名称", "")
        if any(keyword in industry_name for keyword in ["软件", "计算机", "人工智能", "AI", "信息技术", "互联网"]):
            ai_industries.append(industry_name)

    print(f"\n找到 AI 相关行业: {ai_industries[:10]}")  # 显示前10个

    # 获取第一个AI相关行业的成分股
    if ai_industries:
        target_industry = ai_industries[0]
        print(f"\n正在获取【{target_industry}】板块的成分股...")

        stocks_df = ak.stock_board_industry_cons_em(symbol=target_industry)
        print(f"\n该板块共有 {len(stocks_df)} 只股票")

        # 显示前20只股票及其代码
        print("\n前20只股票:")
        print(f"{'代码':<10}{'名称':<12}")
        print("-" * 25)
        for idx, row in stocks_df.head(20).iterrows():
            code = row.get("代码", "")
            name = row.get("名称", "")
            print(f"{code:<10}{name:<12}")

except Exception as e:
    print(f"方法1失败: {e}")

# 方法2：搜索关键词
print("\n" + "=" * 80)
print("【方法2】通过关键词搜索 AI 相关公司...")

# 搜索常见 AI 公司名称关键词
keywords = ["人工智能", "AI", "智能", "软件", "科技", "信息", "数据", "云计算", "大数据"]

all_ai_stocks = []
try:
    # 获取股票列表
    stock_list = ak.stock_info_a_code_name()

    for keyword in keywords[:3]:  # 只搜索前3个关键词避免太多
        mask = stock_list["name"].str.contains(keyword, na=False)
        matched = stock_list[mask]
        for _, row in matched.iterrows():
            all_ai_stocks.append({
                "code": row["code"],
                "name": row["name"]
            })

    # 去重
    seen = set()
    unique_stocks = []
    for stock in all_ai_stocks:
        if stock["code"] not in seen:
            seen.add(stock["code"])
            unique_stocks.append(stock)

    print(f"\n通过关键词找到 {len(unique_stocks)} 只相关股票")
    print("\n前30只股票:")
    print(f"{'代码':<10}{'名称':<12}")
    print("-" * 25)
    for stock in unique_stocks[:30]:
        print(f"{stock['code']:<10}{stock['name']:<12}")

except Exception as e:
    print(f"方法2失败: {e}")

# 方法3：获取概念板块
print("\n" + "=" * 80)
print("【方法3】通过概念板块获取 AI 相关公司...")

try:
    # 获取概念板块列表
    concept_boards = ak.stock_board_concept_name_em()

    # 查找 AI 相关概念
    ai_concepts = []
    for idx, row in concept_boards.iterrows():
        concept_name = row.get("板块名称", "")
        if any(keyword in concept_name for keyword in ["人工智能", "AI", "人工智能", "AIGC", "ChatGPT", "机器人"]):
            ai_concepts.append(concept_name)

    print(f"\n找到 AI 相关概念板块: {ai_concepts}")

    # 获取人工智能概念成分股
    if "人工智能" in ai_concepts:
        print(f"\n正在获取【人工智能】概念板块的成分股...")
        ai_stocks_df = ak.stock_board_concept_cons_em(symbol="人工智能")

        print(f"\n人工智能概念板块共有 {len(ai_stocks_df)} 只股票")
        print("\n所有股票列表:")
        print(f"{'代码':<10}{'名称':<15}{'最新价':<10}{'市值(亿)':<12}")
        print("-" * 50)

        # 保存股票列表
        ai_stocks_list = []

        for idx, row in ai_stocks_df.iterrows():
            code = row.get("代码", "")
            name = row.get("名称", "")
            price = row.get("最新价", 0)
            market_cap = row.get("总市值", 0) / 100000000  # 转换为亿元

            print(f"{code:<10}{name:<15}{float(price):<10.2f}{float(market_cap):<12.2f}")

            ai_stocks_list.append({
                "code": code,
                "name": name
            })

        print(f"\n共找到 {len(ai_stocks_list)} 只人工智能概念股票")

except Exception as e:
    print(f"方法3失败: {e}")

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)
