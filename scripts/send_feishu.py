import os
import json
import glob
import urllib.request
from datetime import datetime



WEBHOOK = os.getenv(
    "FEISHU_WEBHOOK"
)



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




def load_result():


    file=get_latest_json()


    if not file:

        return None



    print(
        "Loading:",
        file
    )


    with open(

        file,

        "r",

        encoding="utf-8"

    ) as f:


        return json.load(f)




def parse_result(data):


    text=""


    # 尝试兼容不同字段

    stocks=(

        data.get("stocks")

        or data.get("results")

        or data.get("ranking")

        or []

    )


    if not stocks:


        return "没有找到股票结果"



    for i,s in enumerate(

        stocks[:10],

        1

    ):


        code=(

            s.get("symbol")

            or s.get("code")

            or ""

        )


        score=(

            s.get("score")

            or s.get("rank_score")

            or ""

        )


        reason=(

            s.get("reason")

            or s.get("explanation")

            or ""

        )



        text += (

            f"{i}. {code}\n"

            f"评分: {score}\n"

        )


        if reason:

            text += (

                f"逻辑: {reason}\n"

            )


        text += "\n"



    return text




def send_feishu(content):


    if not WEBHOOK:


        print(
            "No FEISHU_WEBHOOK"
        )

        return



    msg=f"""
📈 AlphaSift每日选股


时间:
{datetime.now()}


策略:
{os.getenv("STRATEGY")}


模型:
{os.getenv("LLM_MODEL")}


----------------


{content}

----------------


GitHub:
https://github.com/{os.getenv("GITHUB_REPOSITORY")}/actions/runs/{os.getenv("GITHUB_RUN_ID")}

"""



    body={


        "msg_type":

        "interactive",



        "card":{


            "elements":[


                {


                    "tag":

                    "markdown",


                    "content":

                    msg


                }


            ]


        }


    }



    req=urllib.request.Request(


        WEBHOOK,


        data=json.dumps(body).encode("utf-8"),


        headers={

            "Content-Type":

            "application/json"

        }

    )



    urllib.request.urlopen(req)



    print(
        "Feishu sent"
    )





if __name__=="__main__":


    data=load_result()


    if data:


        report=parse_result(data)


    else:


        report="AlphaSift没有生成结果"



    send_feishu(report)
