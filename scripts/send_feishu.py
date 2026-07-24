import os
import json
import glob
import urllib.request
from datetime import datetime


WEBHOOK = os.getenv("FEISHU_WEBHOOK")


def get_latest_json():

    files = glob.glob(
        "data/runs/*.json"
    )

    if not files:
        return None

    files.sort(
        key=os.path.getmtime,
        reverse=True
    )

    return files[0]


def load_json():

    path = get_latest_json()

    if not path:
        return None

    print("Load:", path)

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)



def format_report(data):

    picks = data.get(
        "picks",
        []
    )

    if not picks:
        return "没有选股结果"


    text = ""

    text += (
        f"策略: {data.get('strategy')}\n"
        f"市场: {data.get('market')}\n"
        f"股票池: {data.get('snapshot_count')}\n"
        f"筛选后: {data.get('after_filter_count')}\n\n"
    )


    text += "📌 Top 10股票\n\n"


    for stock in picks[:10]:


        text += (
            f"{stock.get('rank')}. "
            f"{stock.get('code')} "
            f"{stock.get('name')}\n"
        )


        text += (
            f"价格: {stock.get('price')}  "
            f"涨跌: {stock.get('change_pct')}%\n"
        )


        text += (
            f"综合评分: {stock.get('final_score')}\n"
        )


        text += (
            f"量化评分: {stock.get('screen_score')}\n"
        )


        if stock.get("llm_score"):

            text += (
                f"LLM评分: {stock.get('llm_score')}\n"
            )


        if stock.get("risk_level"):

            text += (
                f"风险: {stock.get('risk_level')}\n"
            )


        text += "\n"


    if data.get("llm_ranked"):

        text += "🤖 LLM已参与排序"

    else:

        text += (
            "⚠️ LLM未参与排序，使用纯量化评分"
        )


    return text



def send_feishu(content):

    if not WEBHOOK:

        print(
            "FEISHU_WEBHOOK missing"
        )

        return


    payload={

        "msg_type":"interactive",

        "card":{

            "elements":[

                {

                    "tag":"markdown",

                    "content":

                    content

                }

            ]

        }

    }


    req=urllib.request.Request(

        WEBHOOK,

        data=json.dumps(payload).encode(
            "utf-8"
        ),

        headers={

            "Content-Type":
            "application/json"

        }

    )


    urllib.request.urlopen(req)


    print(
        "Feishu OK"
    )



if __name__=="__main__":


    data=load_json()


    if data:

        report=format_report(data)

    else:

        report="AlphaSift没有生成JSON"


    send_feishu(report)
