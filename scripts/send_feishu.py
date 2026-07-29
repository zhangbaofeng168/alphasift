import os
import json
import glob
import urllib.request


WEBHOOK = os.getenv("FEISHU_WEBHOOK")


# ==========================
# 找最新运行结果
# ==========================

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



# ==========================
# 格式化报告
# ==========================

def format_report(data):


    picks = data.get(
        "picks",
        []
    )


    if not picks:

        return "⚠️ AlphaSift没有生成选股结果"



    llm_status = (
        "🤖 LLM参与排序"
        if data.get("llm_ranked")
        else
        "📊 纯量化排序"
    )


    text = f"""
# 📈 AlphaSift每日选股报告


## 基础信息

策略:
{data.get('strategy')}

策略版本:
{data.get('strategy_version')}

市场:
{data.get('market')}

运行ID:
{data.get('run_id')}


股票池:
{data.get('snapshot_count')}

过滤后:
{data.get('after_filter_count')}


状态:
{llm_status}

LLM覆盖率:
{data.get('llm_coverage',0)}


"""


    # 市场观点

    if data.get("llm_market_view"):

        text += f"""
## 🌏 AI市场观点

{data.get('llm_market_view')}

"""


    if data.get("llm_selection_logic"):

        text += f"""
## 📌 AI选股逻辑

{data.get('llm_selection_logic')}

"""


    if data.get("llm_portfolio_risk"):

        text += f"""
## ⚠️ AI组合风险

{data.get('llm_portfolio_risk')}

"""



    text += """

# ⭐ Top10股票


"""



    for stock in picks[:10]:


        factor = stock.get(
            "factor_scores",
            {}
        )


        text += f"""
━━━━━━━━━━━━━━

## {stock.get('rank')}. {stock.get('code')} {stock.get('name')}


### 💰行情

价格:
{stock.get('price')}

涨跌:
{stock.get('change_pct')}%

成交额:
{format_amount(stock.get('amount'))}

总市值:
{format_amount(stock.get('total_mv'))}

换手率:
{stock.get('turnover_rate')}%



### 📊评分

综合评分:
{stock.get('final_score')}

量化评分:
{stock.get('screen_score')}

LLM评分:
{stock.get('llm_score')}



### 🏷行业

行业:
{stock.get('industry')}

概念:
{stock.get('concepts')}


LLM行业:
{stock.get('llm_sector')}


LLM主题:
{stock.get('llm_theme')}




### 🧮因子评分

价值:
{factor.get('value')}

流动性:
{factor.get('liquidity')}

动量:
{factor.get('momentum')}

反转:
{factor.get('reversal')}

活跃:
{factor.get('activity')}

稳定:
{factor.get('stability')}

规模:
{factor.get('size')}

热点:
{factor.get('theme_heat')}



### 📈技术指标


MACD:
{stock.get('macd_status')}


RSI:
{stock.get('rsi_status')}


20日突破:
{stock.get('breakout_20d_pct')}%


20日波动:
{stock.get('volatility_20d_pct')}%


最大回撤:
{stock.get('max_drawdown_20d_pct')}%


ATR:
{stock.get('atr_20_pct')}%




### 🤖 AI分析


投资逻辑:

{stock.get('llm_thesis')}


风格:

{stock.get('llm_style_fit')}


催化:

{join_list(stock.get('llm_catalysts'))}


风险:

{join_list(stock.get('llm_risks'))}




### ⚠️风险


风险等级:

{stock.get('risk_level')}


风险评分:

{stock.get('risk_score')}


风险标签:

{join_list(stock.get('risk_flags'))}


"""


    # LLM错误

    errors=data.get(
        "llm_parse_errors",
        []
    )


    if errors:


        text += """

━━━━━━━━━━━━━━

⚠️ LLM异常

"""


        text += str(errors[0])[:500]



    return text




# ==========================
# 工具函数
# ==========================


def join_list(value):

    if not value:

        return "无"

    if isinstance(value,list):

        return "、".join(
            map(str,value)
        )

    return str(value)



def format_amount(value):

    if not value:

        return "0"


    try:

        return (
            f"{value/100000000:.2f} 亿"
        )

    except:

        return str(value)



# ==========================
# 飞书发送
# ==========================


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
                    "📈 AlphaSift每日选股"

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



    req = urllib.request.Request(

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




# ==========================
# main
# ==========================


if __name__=="__main__":


    data = load_json()


    if data:

        report = format_report(data)

    else:

        report = (
            "❌ AlphaSift没有生成JSON"
        )


    send_feishu(report)
