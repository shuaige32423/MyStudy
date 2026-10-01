"""
文字实验室后端 —— 模块 5。

现在两个能力都是真的了，不再是写死的常量：
    /api/analyze  →  pypinyin 转拼音 + snownlp 做情感分析
    /api/profile  →  仍是模块里的常量（等接数据库再说）

本地跑：
    cd backend
    .venv\\Scripts\\python.exe -m uvicorn main:app --reload --port 8000
    # Linux / macOS:  .venv/bin/python -m uvicorn main:app --reload --port 8000

线上跑：systemd 托管，只监听 127.0.0.1:8000，由 nginx 把 /api 反代进来。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypinyin import Style, lazy_pinyin
from snownlp import SnowNLP
import json
from datetime import datetime, timezone


app = FastAPI(title="zero to tech API", version="0.2.0")

# 本地联调时前端在 3000、后端在 8000，属于"跨域"，浏览器会先发预检请求。
# 线上由 nginx 把 /api 反代成同一个域，这段 CORS 其实用不到，留着是为了本地开发方便。
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://tanyi.fun",
        "https://tanyi.fun",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# 首页要显示的内容。还是写死的常量。
# 形状和前端 data/site.js 里的 home 完全一致。
# ---------------------------------------------------------------------------
PROFILE = {
    "heroTitle": "关于我",
    "heroSubtitle": "项目，创意，灵感，心得，我的作品",
    "featuredWork": {
        "kicker": "作品",
        "title": "文字实验室",
        "copy": "拼音和情绪，挖掘中文里的细节",
        "linkLabel": "打开作品",
    },
    "identity": {
        "motto": "已识乾坤大，尤怜草木青",
        "learning": "零到全栈",
    },
}

HISTORY_FILE = "history.json"

def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_record(record):
    records = load_history()
    records.append(record)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)



class AnalyzeRequest(BaseModel):
    """前端 POST 上来的请求体：{ "text": "..." }"""

    text: str = ""


# ---------------------------------------------------------------------------
# 两个小工具函数。放在外面，路由函数里只负责"把结果拼成 JSON"。
# ---------------------------------------------------------------------------

def to_pinyin(text: str) -> str:
    """中文转带声调数字的拼音，用空格连成一个字符串。

    lazy_pinyin() 返回的是 list，比如 ['jin1', 'tian1', 'qi4']，
    必须 join 成字符串再返回 —— 直接返回 list 的话，前端渲染数组
    会把元素不带分隔符地拼在一起，变成 'jin1tian1qi4'。

    例：'今天天气真好' -> 'jin1 tian1 tian1 qi4 zhen1 hao3'
    """
    if not text.strip():
        return ""


def analyze_sentiment(text: str) -> tuple[float, str]:
    """情感分析，返回 (分数, 判断)。

    分数范围 0~1，越接近 1 越正面。
    注意 SnowNLP("") 会抛 ZeroDivisionError，所以空文本要先挡掉。
    """
    if not text.strip():
        return 0.5, "中性"

    score = SnowNLP(text).sentiments   # .sentiments 才是 float，对象本身不是

    if score > 0.66:
        label = "正面"
    elif score < 0.33:
        label = "负面"
    else:
        label = "中性"

    return score, label


# ---------------------------------------------------------------------------
# 路由
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    """给 nginx / systemd / 运维脚本探活用。"""
    return {"status": "ok"}


@app.get("/api/profile")
def get_profile():
    return PROFILE

@app.get("/api/history")
def history():
    records = load_history()
    records.reverse()          # 倒过来：新的排前面
    return records[:3]        # 切一刀：只留最近 3 条


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    text = req.text
    score = analyze_sentiment(text)[0]
    label = analyze_sentiment(text)[1]
    result = {
        "text": text,
        "score": score,
        "label": label,
        "pinyin": " ".join(lazy_pinyin(text, style=Style.TONE)),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),  # ← 新增
    }
    save_record(result)                                                          # ← 存档到文件
    return result
