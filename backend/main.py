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
import os
from dotenv import load_dotenv
import uuid
from fastapi import Request, Response, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypinyin import Style, lazy_pinyin
from snownlp import SnowNLP
from datetime import datetime, timezone
from storage import init_db, save_record, get_history

load_dotenv()                        # ← 读同目录下的 .env

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS").split(",")

init_db()
app = FastAPI(title="zero to tech API", version="0.2.0")

# 本地联调时前端在 3000、后端在 8000，属于"跨域"，浏览器会先发预检请求。
# 线上由 nginx 把 /api 反代成同一个域，这段 CORS 其实用不到，留着是为了本地开发方便。
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        ALLOWED_ORIGINS,
        "http://tanyi.fun",
        "https://tanyi.fun",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# ---------------------------------------------------------------------------
# 首页要显示的内容。还是写死的常量。
# 形状和前端 data/site.js 里的 home 完全一致。
# ---------------------------------------------------------------------------
def get_session_id(request: Request, response: Response) -> str:
    sid = request.cookies.get("session_id")      # 先看有没有纸条
    if not sid:                                  # 第一次来，没有——发一张
        sid = uuid.uuid4().hex                    # 一串随机、不重复的 id
        response.set_cookie(
            "session_id", sid,
            httponly=True, samesite="lax",
            max_age=60 * 60 * 24 * 30,            # 记 30 天
        )
    return sid   


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

    score = round(SnowNLP(text).sentiments, 2)  # .sentiments 才是 float，对象本身不是

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


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest, request: Request, response: Response):
    sid = get_session_id(request, response)
    text = req.text
    score , label = analyze_sentiment(text)
    result = {
        "text": text,
        "score": score,
        "label": label,
        "pinyin": " ".join(lazy_pinyin(text, style=Style.TONE)),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    save_record(sid, result)          # 存的时候盖上这个会话的记号
    return result                     # ← 返回体一个字没变，session_id 只走 cookie

@app.get("/api/history")
def history(request: Request, response: Response, limit: int = 5):
    sid = get_session_id(request, response)
    return get_history(sid, limit)    # 只回这个会话自己的