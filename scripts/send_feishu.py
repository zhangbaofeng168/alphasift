import os
import json
import glob
import urllib.request
from datetime import datetime


WEBHOOK = os.environ.get(
    "FEISHU_WEBHOOK"
)


def find_report():

    files=[]

    for p in [
        "reports/*.md",
        "reports/*.txt",
        "data/*.csv"
    ]:

        files.extend(
            glob.glob(p)
        )


    if not files:
        return None


    return files[0]



def parse_report():

    file=find_report()


    if not file:

        return """

没有找到AlphaSift报告

"""


    with open(
        file,
        "r",
        encoding="utf-8"
    ) as f:

        content=f.read()



    # 限制长度避免飞书超长

    return content[:3000]



def send_feishu():

    if not WEBHOOK:

        print(
            "No FEISHU_WEBHOOK"
        )

        return



    report=parse_report()



    msg=f"""

📈 AlphaSift每日选股报告


时间:

{datetime.now()}



策略:

{os.getenv(
    "ALPHASIFT_STRATEGY"
)}



模型:

{os.getenv(
    "LLM_MODEL"
)}



================


{report}



================


GitHub运行:

https://github.com/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}

"""


    body={

        "msg_type":
        "interactive",

        "card":{

            "header":{

                "title":{

                    "tag":"plain_text",

                    "content":
                    "AlphaSift股票分析"

                }

            },

            "elements":[

                {

                    "tag":"markdown",

                    "content":msg

                }

            ]

        }

    }



    req=urllib.request.Request(

        WEBHOOK,

        data=json.dumps(
            body
        ).encode("utf-8"),

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

    send_feishu()
