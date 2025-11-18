import json
from collections import Counter, defaultdict
from pathlib import Path


def main():
    """
    统计 cladder 数据集中因果阶梯相关字段的分布情况。

    - 目标文件: src/dataset/cladder/data_full_v1.5_default.jsonl
    - 输出内容:
      * 样本总数
      * rung (1/2/3) 的计数分布
      * 不同 rung 下 query_type 的分布情况
    """
    root = Path(__file__).resolve().parents[1]
    jsonl_path = root / "src" / "dataset" / "cladder" / "data_full_v1.5_default.jsonl"

    if not jsonl_path.exists():
        raise FileNotFoundError(f"找不到数据文件: {jsonl_path}")

    rung_counter: Counter[int] = Counter()
    query_type_counter: Counter[str] = Counter()
    rung_to_query: defaultdict[int, Counter[str]] = defaultdict(Counter)

    total = 0
    missing_rung = 0
    missing_query_type = 0

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                print(f"[WARN] 第 {total} 行 JSON 解析失败，跳过。")
                continue

            # rung: 因果阶梯层级 (1/2/3)
            if "rung" in obj:
                rung = obj["rung"]
                rung_counter[rung] += 1
            else:
                missing_rung += 1
                rung = None

            # query_type: 更细粒度的因果查询类型 (如 marginal/ate/nde/nie/backadj/ett/correlation 等)
            if "query_type" in obj:
                qt = obj["query_type"]
                query_type_counter[qt] += 1
                if rung is not None:
                    rung_to_query[rung][qt] += 1
            else:
                missing_query_type += 1

    print("=== cladder 阶梯标签统计 (data_full_v1.5_default.jsonl) ===")
    print(f"样本总数: {total}")
    print()

    print("1) rung 字段分布 (因果阶梯层级)")
    if rung_counter:
        for k in sorted(rung_counter.keys()):
            print(f"  rung = {k}: {rung_counter[k]}")
    else:
        print("  未找到任何 rung 字段。")
    if missing_rung:
        print(f"  缺失 rung 的样本数: {missing_rung}")
    print()

    print("2) query_type 字段总体分布")
    if query_type_counter:
        for qt, cnt in sorted(query_type_counter.items(), key=lambda x: x[0]):
            print(f"  {qt}: {cnt}")
    else:
        print("  未找到任何 query_type 字段。")
    if missing_query_type:
        print(f"  缺失 query_type 的样本数: {missing_query_type}")
    print()

    print("3) 各 rung 内部的 query_type 分布")
    if rung_to_query:
        for rung in sorted(rung_to_query.keys()):
            print(f"  rung = {rung}:")
            for qt, cnt in sorted(rung_to_query[rung].items(), key=lambda x: x[0]):
                print(f"    {qt}: {cnt}")
    else:
        print("  未能统计到 (rung, query_type) 的联合分布。")


if __name__ == "__main__":
    main()


