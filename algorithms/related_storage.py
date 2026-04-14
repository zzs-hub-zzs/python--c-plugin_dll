import math
from collections import defaultdict
from datetime import datetime


def compute_time_weight(ts, decay):
    try:
        t = datetime.fromisoformat(ts)
        delta = (datetime.now() - t).days
        return math.exp(-decay * delta)
    except:
        return 1.0


def recommend_for_group(target_group,
                        history_records,
                        min_support,
                        max_k,
                        decay):

    target_ids = {i["id"] for i in target_group}

    pair_weight = defaultdict(float)
    ratio_map = defaultdict(list)

    total_weight = 0

    for record in history_records:

        ids = {i["id"] for i in record["items"]}

        if not target_ids.issubset(ids):
            continue

        weight = compute_time_weight(
            record["timestamp"],
            decay
        )

        total_weight += weight

        qty_map = {
            i["id"]: i["qty"]
            for i in record["items"]
        }

        for item in record["items"]:

            if item["id"] in target_ids:
                continue

            pair_weight[item["id"]] += weight

            base_id = target_group[0]["id"]

            ratio = item["qty"] / qty_map[base_id]

            ratio_map[item["id"]].append(ratio)

    results = []

    for item_id in pair_weight:

        support = pair_weight[item_id]

        if support < min_support:
            continue

        confidence = support / total_weight

        avg_ratio = sum(ratio_map[item_id]) / len(ratio_map[item_id])

        predicted_qty = target_group[0]["qty"] * avg_ratio

        results.append({
            "id": item_id,
            "qty": round(predicted_qty),
            "confidence": round(confidence, 3)
        })

    results.sort(
        key=lambda x: x["confidence"],
        reverse=True
    )

    return results[:max_k]


def recommend(data):

    target_items = data["target_items"]
    history_records = data["history_records"]
    min_support = data["min_support"]
    max_recommendations = data["max_recommendations"]
    time_decay = data["time_decay"]

    results = []

    for group in target_items:

        recs = recommend_for_group(
            group,
            history_records,
            min_support,
            max_recommendations,
            time_decay
        )

        results.append({
            "target_items": group,
            "recommendations": recs
        })

    return {
        "results": results,
        "errorCode": 0,
        "errorMsg": "成功"
    }


# -------------------------
# 统一插件入口
# -------------------------
def run(data):

    try:

        return recommend(data)

    except Exception as e:

        return {
            "results": [],
            "errorCode": 500,
            "errorMsg": str(e)
        }