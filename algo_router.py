import importlib
import json
def run(algo_name, data):

    try:
        module = importlib.import_module(
            f"algorithms.{algo_name}"
        )

        result= module.run(data)
        # ✅ 强制 UTF-8 安全
        return json.loads(json.dumps(result, ensure_ascii=False))
    
    except Exception as e:

        return {
            "errorCode": 500,
            "errorMsg": str(e)
        }