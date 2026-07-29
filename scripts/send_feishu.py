import os
import json
import glob
import urllib.request


WEBHOOK = os.getenv("FEISHU_WEBHOOK")



# =====================
# 获取最新运行JSON
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
# 格式工具
# =====================

def val(v):

    if v is None or v == "":

        return "-"

    return v



def fmt(v):

    if v is None or v == "":

        return "-"

    try:

        return round(
            float(v),
            2
        )

    except:

        return v



def money(v):

    if not v:

        return "-"

    try:

        return (
            f"{float(v)/100000000:.1f}亿"
        )

    except:

        return "-"



def join_list(v):

    if not v:

        return "-"


    if isinstance(v,list):

        return "、".join(
            map(str,v)
        )


    return str(v)




# =====================
# 生成报告
# =====================

def format_report(data):


    picks=data.get(
        "picks",
        []
    )


    if not picks:

        return "⚠️ 今日无选股结果"



    status = (
        "🤖LLM排序"
        if data.get("llm_ranked")
        else
        "📊量化排序"
    )



    text=f"""
策略 {val(data.get('strategy'))}
| 市场 {val(data.get('market'))}

股票池 {val(data.get('snapshot_count'))}
| 过滤 {val(data.get('after_filter_count'))}

状态 {status}
| LLM覆盖 {fmt(data.get('llm_coverage'))}

"""



    # 市场观点

    if data.get("llm_market_view"):

        text += (
            "\n🌏市场:\n"
            +
            data.get("llm_market_view")
            +
            "\n"
        )



    if data.get("llm_selection_logic"):

        text += (
            "\n📌逻辑:\n"
            +
            data.get("llm_selection_logic")
            +
            "\n"
        )



    text += "\n━━━━━━━━━━\n"



    # Top10

    for stock in picks[:10]:


        rank = stock.get(
            "rank",
            0
        )


        icon = (
            "🔥"
            if rank <=3
            else
            "👀"
        )


        factor = stock.get(
            "factor_scores",
            {}
        )



        text += f"""

{icon}{rank} {stock.get('code')} {stock.get('name')}

💰 {fmt(stock.get('price'))}元 | 涨{fmt(stock.get('change_pct'))}% | 换手{fmt(stock.get('turnover_rate'))}%

📊 总分{fmt(stock.get('final_score'))} | 量化{fmt(stock.get('screen_score'))} | LLM{fmt(stock.get('llm_score'))}

💵 市值{money(stock.get('total_mv'))} | PE{fmt(stock.get('pe_ratio'))} | PB{fmt(stock.get('pb_ratio'))}

🏷 {val(stock.get('industry'))} | {val(stock.get('concepts'))}

🧮 价值{fmt(factor.get('value'))} | 流动{fmt(factor.get('liquidity'))} | 动量{fmt(factor.get('momentum'))} | 稳定{fmt(factor.get('stability'))}

📈 MACD {val(stock.get('macd_status'))} | RSI {val(stock.get('rsi_status'))} | 突破{fmt(stock.get('breakout_20d_pct'))}%

🤖 {val(stock.get('llm_thesis') or stock.get('ranking_reason'))}

🔥 {join_list(stock.get('llm_catalysts'))}

⚠️ {val(stock.get('risk_level'))} | {join_list(stock.get('risk_flags'))}

━━━━━━━━━━
"""


    # LLM异常

    errors=data.get(
        "llm_parse_errors",
        []
    )


    if errors:

        text += (
            "\n⚠️ LLM异常:\n"
            +
            str(errors[0])[:300]
        )



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
