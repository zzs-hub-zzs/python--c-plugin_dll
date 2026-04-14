import pandas as pd

ERROR_DICT = {
    4001: "请求 JSON 格式错误",
    4002: "数据标准化失败",
    4003: "综合得分计算失败",
    4221: "参数校验失败",
    5001: "服务器内部错误"
}


def build_error_response(code):
    return {
        "results": [],
        "errorCode": code,
        "errorMsg": ERROR_DICT.get(code, "未知错误")
    }


def build_success_response(results):
    return {
        "results": results,
        "errorCode": 0,
        "errorMsg": "成功"
    }


def normalize(df):
    return (df - df.min()) / (df.max() - df.min() + 1e-9)


def classify(score):
    if score >= 0.75:
        return "A"
    elif score >= 0.4:
        return "B"
    else:
        return "C"


def run(data):

    try:

        weights = data["weights"]
        items = data["items"]

        if not items:
            return build_success_response([])

        raw_list = []

        for item in items:
            raw_list.append({
                "itemId": item["itemId"],
                "itemName": item["itemName"],
                "value": item["value"],
                "turnoverRate": item["turnoverRate"],
                "usageRate": item["usageRate"]
            })

        df = pd.DataFrame(raw_list)

        try:
            df_norm = normalize(df[["value", "turnoverRate", "usageRate"]])
        except:
            return build_error_response(4002)

        try:
            df["score"] = (
                df_norm["value"] * weights["value"] +
                df_norm["turnoverRate"] * weights["turnoverRate"] +
                df_norm["usageRate"] * weights["usageRate"]
            )
        except:
            return build_error_response(4003)

        df["level"] = df["score"].apply(classify)

        results = []

        for _, row in df.iterrows():
            results.append({
                "itemId": row["itemId"],
                "itemName": row["itemName"],
                "score": round(row["score"], 6),
                "level": row["level"]
            })

        return build_success_response(results)

    except Exception:
        return build_error_response(5001)