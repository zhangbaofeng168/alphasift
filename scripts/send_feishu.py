import os
import json
import glob
import urllib.request


WEBHOOK = os.getenv("FEISHU_WEBHOOK")


# =====================
# 获取最新JSON
# =====================

def get_latest_json():

    files = glob.glob(
        "data/runs/*.json"
    )

    if not files:
        return None

    return max(
        files,
        key=os.path.getmtime
    )



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



# =====================
# 工具函数
# =====================

def val(v, default="-"):

    if v is None or v == "":

        return default

    return v



def join_list(arr):

    if not arr:

        return "-"

    if isinstance(arr,list):

        return "、".join(
            map(str,arr)
        )

    return str(arr)



def money(v):

    if not v:

        return "-"

    try:

        return (
            f"{v/100000000:.1f}亿"
        )

    except:

        return str(v)



# =====================
# 生成飞书内容
# =====================

def format_report(data):


    picks=data.get(
        "picks",
        []
    )


    if not picks:

        return "⚠️ 今日无选股结果"



    llm_status = (
        "🤖LLM排序"
        if data.get("llm_ranked")
        else
        "📊量化排序"
    )


    text=f"""
# 📈 AlphaSift每日选股

策略 {val(data.get('strategy'))}
| 市场 {val(data.get('market'))}

股票池 {val(data.get('snapshot_count'))}
| 过滤 {val(data.get('after_filter_count'))}

状态 {llm_status}
| LLM覆盖 {val(data.get('llm_coverage'))}


"""


    # 市场总结

    if data.get("llm_market_view"):

        text += f"""
🌏市场:
{data.get('llm_market_view')}

"""


    if data.get("llm_selection_logic"):

        text += f"""
📌逻辑:
{data.get('llm_selection_logic')}

"""


    text += "\n━━━━━━━━━━━━\n"



    # TOP10

    for stock in picks[:10]:


        rank=stock.get(
            "rank",
            0
        )


        if rank <=3:

            icon="🔥"

        else:

            icon="👀"



        factor=stock.get(
            "factor_scores",
            {}
        )


        text += f"""

{icon}{rank} {stock.get('code')} {stock.get('name')}

💰 {val(stock.get('price'))}元 
| 涨跌 {val(stock.get('change_pct'))}%
| 换手 {val(stock.get('turnover_rate'))}%

📊 总分 {val(stock.get('final_score'))}
| 量化 {val(stock.get('screen_score'))}
| LLM {val(stock.get('llm_score'))}

💵 市值 {money(stock.get('total_mv'))}
| PE {val(stock.get('pe_ratio'))}
| PB {val(stock.get('pb_ratio'))}

🏷 {val(stock.get('industry'))}
| {val(stock.get('concepts'))}


🧮 因子:
价值{val(factor.get('value'))}
流动{val(factor.get('liquidity'))}
动量{val(factor.get('momentum'))}
稳定{val(factor.get('stability'))}


📈 技术:
MACD {val(stock.get('macd_status'))}
| RSI {val(stock.get('rsi_status'))}
| 突破 {val(stock.get('breakout_20d_pct'))}%


🤖 AI:
{val(stock.get('llm_thesis') or stock.get('ranking_reason'))}


🔥催化:
{join_list(stock.get('llm_catalysts'))}


⚠️风险:
{val(stock.get('risk_level'))}
| {join_list(stock.get('risk_flags'))}


━━━━━━━━━━━━

"""


    # LLM错误

    errors=data.get(
        "llm_parse_errors",
        []
    )


    if errors:


        text += f"""

⚠️ LLM异常:

{str(errors[0])[:300]}

"""


    return text



# =====================
# 飞书发送
# =====================

def send_feishu(content):


    if not WEBHOOK:

        print(
            "FEISHU_WEBHOOK missing"
        )

        return



    payload={

        "msg_type":
        "interactive",


        "card":{


            "header":{

                "title":{

                    "tag":
                    "plain_text",

                    "content":
                    "📈 AlphaSift日报"

                }

            },


            "elements":[

                {

                    "tag":
                    "markdown",

                    "content":
                    content[:30000]

                }

            ]

        }

    }



    req=urllib.request.Request(

        WEBHOOK,

        data=json.dumps(
            payload,
            ensure_ascii=False
        ).encode(
            "utf-8"
        ),

        headers={

            "Content-Type":
            "application/json"

        }

    )


    urllib.request.urlopen(
        req,
        timeout=10
    )


    print(
        "Feishu OK"
    )



# =====================
# main
# =====================

if __name__=="__main__":


    data=load_json()


    if data:

        report=format_report(data)

    else:

        report="❌ AlphaSift没有生成JSON"



    send_feishu(report)
