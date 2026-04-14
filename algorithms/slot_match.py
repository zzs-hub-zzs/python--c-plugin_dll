import numpy as np


def size_match(item_dim, slot_dim):
    """
    尺寸匹配评分
    """
    return float(np.exp(-np.sum(np.abs(item_dim - slot_dim))))


def storage_match(reqs, attrs):
    """
    存储属性匹配
    """
    if not reqs:
        return 1.0

    match_count = sum(1 for r in reqs if r in attrs)

    return match_count / len(reqs)


def freq_match(freq, slot_center):
    """
    访问频率匹配
    """
    dist = np.linalg.norm(slot_center)

    return float(freq / (1 + dist))


def run(data):

    try:

        items = data["items"]
        slots = data["slots"]
        weights = data["weights"]

        if not items or not slots:
            return {
                "assignments": [],
                "errorCode": 1,
                "errorMsg": "items 或 slots 为空"
            }

        # -------------------------
        # 计算货位已有堆叠高度
        # -------------------------
        slot_stack_height = {}

        for sl in slots:

            h = 0.0

            for ex in sl["existingItems"]:
                h += ex["dimensions"]["z"]

            slot_stack_height[sl["slotId"]] = h

        # -------------------------
        # 计算所有匹配得分
        # -------------------------
        score_list = []

        for it in items:

            item_dim = np.array([
                it["dimensions"]["x"],
                it["dimensions"]["y"],
                it["dimensions"]["z"]
            ])

            for sl in slots:

                sl_dim = np.array([
                    sl["dimensions"]["x"],
                    sl["dimensions"]["y"],
                    sl["dimensions"]["z"]
                ])

                slot_center = np.array([
                    sl["center"]["x"],
                    sl["center"]["y"],
                    sl["center"]["z"]
                ])

                s1 = size_match(item_dim, sl_dim)

                s2 = storage_match(
                    it["storageRequirements"],
                    sl["attributes"]
                )

                s3 = freq_match(
                    it["accessFrequency"],
                    slot_center
                )

                total = (
                    weights["size"] * s1 +
                    weights["storageReq"] * s2 +
                    weights["frequency"] * s3
                )

                score_list.append(
                    (it["itemId"], sl["slotId"], total)
                )

        # -------------------------
        # 按得分排序
        # -------------------------
        score_list.sort(
            key=lambda x: x[2],
            reverse=True
        )

        assignments = []
        placed_items = set()

        # -------------------------
        # 贪心匹配
        # -------------------------
        for itemId, slotId, score in score_list:

            if itemId in placed_items:
                continue

            it = next(i for i in items if i["itemId"] == itemId)
            sl = next(s for s in slots if s["slotId"] == slotId)

            item_vol = (
                it["dimensions"]["x"] *
                it["dimensions"]["y"] *
                it["dimensions"]["z"]
            )

            if sl["remainingVolume"] >= item_vol:

                sl["remainingVolume"] -= item_vol

                placed_items.add(itemId)

                base_z = (
                    sl["center"]["z"] -
                    sl["dimensions"]["z"] / 2
                )

                cur_h = slot_stack_height[slotId]

                new_z = (
                    base_z +
                    cur_h +
                    it["dimensions"]["z"] / 2
                )

                slot_stack_height[slotId] += it["dimensions"]["z"]

                assignments.append({
                    "itemId": itemId,
                    "slotId": slotId,
                    "score": round(score, 6),
                    "placedCenter": {
                        "x": sl["center"]["x"],
                        "y": sl["center"]["y"],
                        "z": new_z
                    }
                })

        return {
            "assignments": assignments,
            "errorCode": 0,
            "errorMsg": "成功"
        }

    except Exception as e:

        return {
            "assignments": [],
            "errorCode": 500,
            "errorMsg": str(e)
        }