# 后端接口文档 · zero to tech API

> 版本 `v0.2.0`　｜　实现 [`backend/main.py`](main.py)　｜　框架 FastAPI
>
> `/api/analyze` 已经是**真实实现**：拼音用 `pypinyin`，情感用 `snownlp`，不再是写死的常量。
> `/api/profile` 仍然是模块里的常量，等接数据库再说。

---

## 1. 基本约定

| 项 | 值 |
| --- | --- |
| 本地地址 | `http://127.0.0.1:8000` |
| 线上地址 | `https://tanyi.fun` |
| 线上转发方式 | nginx 把 `/api` 反代到 `127.0.0.1:8000`（后端不直接对外暴露） |
| 路径前缀 | 全部以 `/api` 开头 |
| 请求体 | `application/json`（UTF-8） |
| 响应体 | `application/json`（UTF-8） |
| 认证 | 无 |

### 怎么访问

- **交互式调试页（推荐）**：<http://127.0.0.1:8000/docs> —— FastAPI 自动生成，可以直接在页面上点按钮发请求
- 备用文档：<http://127.0.0.1:8000/redoc>　｜　机器可读：<http://127.0.0.1:8000/openapi.json>
- **前端代码里**：统一走 [`lib/api.js`](../lib/api.js) 的 `getJSON()` / `postJSON()`

> ⚠️ 根路径 `http://127.0.0.1:8000/` **没有定义**，访问返回 404，这是正常的 —— 8000 是接口服务，不是网站。
> 给人看的网页在 **3000**（本地开发）或 **tanyi.fun**（线上）。

### CORS

本地开发时前端在 `:3000`、后端在 `:8000`，属于跨域。后端已放行这些来源：

```
http://localhost:3000
http://127.0.0.1:3000
http://tanyi.fun
https://tanyi.fun
```

线上由 nginx 反代成同一个域，用不到 CORS。

---

## 2. 接口一览

| # | 方法 | 路径 | 说明 | 前端调用方 |
| --- | --- | --- | --- | --- |
| 1 | `GET` | `/api/health` | 健康检查 | nginx / systemd / 运维脚本 |
| 2 | `GET` | `/api/profile` | 首页展示内容 | [`components/HomeView.jsx`](../components/HomeView.jsx) |
| 3 | `POST` | `/api/analyze` | 文字分析（拼音 + 情感） | [`components/TextLabView.jsx`](../components/TextLabView.jsx) |

---

## 3. `GET /api/health`

健康检查。给 nginx、systemd、运维脚本探活用，前端不调用。

**请求参数**：无

**响应 `200`**

```json
{ "status": "ok" }
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `status` | string | 固定为 `"ok"`，能返回就说明服务活着 |

**示例**

```bash
curl http://127.0.0.1:8000/api/health
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

---

## 4. `GET /api/profile`

返回首页要显示的全部内容。

**请求参数**：无

**响应 `200`**

```json
{
  "heroTitle": "关于我（来自后端）",
  "heroSubtitle": "项目，创意，灵感，心得，我的作品",
  "featuredWork": {
    "kicker": "作品",
    "title": "文字实验室",
    "copy": "拼音和情绪，挖掘中文里的细节",
    "linkLabel": "打开作品"
  },
  "identity": {
    "motto": "已识乾坤大，尤怜草木青",
    "learning": "零到全栈"
  }
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `heroTitle` | string | 页面大标题。目前带「（来自后端）」后缀，是为了在页面上一眼确认数据来自接口 |
| `heroSubtitle` | string | 页面副标题 |
| `featuredWork.kicker` | string | 作品卡片的小标签 |
| `featuredWork.title` | string | 作品名 |
| `featuredWork.copy` | string | 作品简介 |
| `featuredWork.linkLabel` | string | 跳转链接的文案 |
| `identity.motto` | string | 座右铭 |
| `identity.learning` | string | 「正在学习」那一栏 |

> 这个结构是照着前端 [`data/site.js`](../data/site.js) 里 `home` 的形状做的。
> 换成接口之后，前端组件一个字都没改，只改了「值从哪来」。

**示例**

```bash
curl http://127.0.0.1:8000/api/profile
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/profile
```

---

## 5. `POST /api/analyze`

文字实验室的「开始分析」。前端点按钮时调用。

**请求体**（`application/json`）

| 字段 | 类型 | 必填 | 默认 | 说明 |
| --- | --- | --- | --- | --- |
| `text` | string | 否 | `""` | 待分析的中文文本 |

```json
{ "text": "今天天气真好，我很开心" }
```

**响应 `200`**

```json
{
  "text": "今天天气真好，我很开心",
  "pinyin": "jin1 tian1 tian1 qi4 zhen1 hao3 ， wo3 hen3 kai1 xin1",
  "score": 0.8051,
  "label": "正面"
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `text` | string | 原文。把请求里的 `text` **原样回显** |
| `pinyin` | string | 拼音。带声调数字、用空格分隔（`pypinyin` 的 `Style.TONE3` + `neutral_tone_with_five`）。**标点原样保留**；空文本返回 `""` |
| `score` | number | 情感分数，范围 `0`~`1`，保留 4 位小数（`snownlp` 算出） |
| `label` | string | 情感判断，只有这三个值：`"正面"`（`score > 0.66`）、`"负面"`（`score < 0.33`）、`"中性"`（其余） |

**几个要注意的行为**

- **空文本不会报错。** `text` 为 `""`、纯空格、或者请求体里干脆没有 `text` 字段时，直接返回 `{"pinyin":"", "score":0.5, "label":"中性"}`。
  （`SnowNLP("")` 本身会抛 `ZeroDivisionError`，代码里已经挡掉了。）
- **拼音是字符串，不是数组。** `lazy_pinyin()` 返回的是 list，代码里 `" ".join(...)` 过一道。
  直接返回 list 的话，前端 React 渲染数组会把元素**不带分隔符**地拼起来，变成 `jin1tian1tian1qi4`。
- **`snownlp` 的模型偏乐观。** 它的语料是商品评论，日常中性句子也常给出 0.97 以上的高分。
  实测："今天风很轻，适合把脑海里的想法慢慢写下来。" → `0.9994`；"气死我了，太糟糕了" → `0.0936`。
  阈值 `0.66 / 0.33` 是自己的选择，觉得不好用就调这两个数。
- **纯英文 / 数字原样返回**，不报错。实测 `"hello 123"` → `{"pinyin":"hello 123","score":0.5,"label":"中性"}`。

**示例**

```bash
curl -X POST http://127.0.0.1:8000/api/analyze \
     -H "Content-Type: application/json" \
     -d '{"text":"今天天气真好，我很开心"}'
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/analyze -Method Post `
  -ContentType 'application/json' `
  -Body ([System.Text.Encoding]::UTF8.GetBytes('{"text":"今天天气真好"}'))
```

---

## 6. 错误响应

FastAPI 的默认错误格式，`detail` 字段说明原因。

| 状态码 | 场景 | 响应体 |
| --- | --- | --- |
| `404` | 路径不存在（例如访问 `/` 或 `/api/nothing`） | `{"detail":"Not Found"}` |
| `405` | 方法不对（例如用 `GET` 访问 `/api/analyze`） | `{"detail":"Method Not Allowed"}` |
| `422` | 请求体不是合法 JSON，或字段类型不对 | `{"detail":[{"loc":[...],"msg":"...","type":"..."}]}` |

> 常见困惑：在浏览器地址栏敲 `http://127.0.0.1:8000/api/analyze` 会得到 **405** 而不是 404 ——
> 因为地址栏发的是 `GET`，而这个接口只接受 `POST`。要试就用 <http://127.0.0.1:8000/docs>。

---

## 7. 前端在哪调用

```
浏览器打开 /            →  components/HomeView.jsx
                            └─ getJSON("/api/profile")          GET  /api/profile

浏览器打开 /text-lab    →  components/TextLabView.jsx
                            ├─ 打字          → setText（纯本地，不发请求）
                            └─ 点「开始分析」 → postJSON("/api/analyze")   POST /api/analyze
                                                 ↓
                                            setResult(data)
                                                 ↓
                                            components/ResultCard.jsx 重新渲染
```

地址由 [`lib/api.js`](../lib/api.js) 统一决定：

- **本地**：`.env.local` 里 `NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000` → 请求打到 8000
- **线上**：该变量为空 → 走同域相对路径 `/api/...` → nginx 反代到 8000

---

## 8. 后续要做

- [x] ~~`POST /api/analyze` 换成真正的拼音（`pypinyin`）和情感分析~~ —— v0.2.0 已完成
- [ ] `snownlp` 偏乐观，考虑换模型或调阈值
- [ ] `/api/profile` 的数据改从数据库读，而不是模块里的常量
- [ ] 加鉴权（如果以后有需要登录的接口）
- [ ] 统一错误响应格式，别直接把 FastAPI 的 `detail` 抛给前端
