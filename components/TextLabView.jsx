"use client";

// 文字实验室页。这一节多了一件事：把历史记录显示出来。
// 历史放在弹窗里（而不是再加一张卡），点结果卡右上角的按钮才打开——
// 也是打开的那一刻才去请求 /api/history，没必要每次进页面都拉一遍。
import { useState } from "react";
import Nav from "./Nav.jsx";
import PageHeading from "./PageHeading.jsx";
import AnimatedCardGrid from "./AnimatedCardGrid.jsx";
import InputCard from "./InputCard.jsx";
import ResultCard from "./ResultCard.jsx";
import HistoryModal from "./HistoryModal.jsx";
import { textLab } from "../data/site.js";

// 后端地址。这个值【已经带上 /api 了】（本地联调时是 http://127.0.0.1:8000/api），
// 所以下面拼路径只写 /history，千万别再写 /api/history ——
// 那会拼成 /api/api/history，后端没这个路由，返回 404。
// 和 HomeView / InputCard 保持同一个约定：API 到 /api 为止。
// 线上没有 .env.local，回退成同域的 "/api"，由 nginx 反代到 FastAPI。
const API = (process.env.NEXT_PUBLIC_API_BASE_URL || "/api").replace(/\/+$/, "");

export default function TextLabView() {
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyError, setHistoryError] = useState("");

  async function openHistory() {
    setHistoryOpen(true);
    setHistoryError("");

    try {
      const res = await fetch(`${API}/history`, { credentials: "include" });

      // 必须检查 res.ok。404 / 500 的响应体也是【合法 JSON】（{"detail":"Not Found"}），
      // 不看状态码就 res.json()，就会把错误对象当成记录数组塞进 state，
      // 紧接着 HistoryModal 里的 items.map 就炸成 "items.map is not a function"。
      if (!res.ok) {
        throw new Error(`后端返回 ${res.status}`);
      }

      const data = await res.json();

      // 再挡一道：后端万一返回的不是数组，也不往 .map 上送
      if (!Array.isArray(data)) {
        throw new Error("后端返回的不是数组");
      }

      setHistory(data);
    } catch (error) {
      // 出任何问题都退回空数组 —— 保证弹窗拿到的 items 永远是数组
      setHistory([]);
      setHistoryError(error.message);
    }
  }

  return (
    <AnimatedCardGrid className="dashboard-grid">
      <article className="hero-stage panel-full">
        <Nav />
        <PageHeading title={textLab.heroTitle} subtitle={textLab.heroSubtitle} />
      </article>

      <InputCard onResult={setResult} />
      <ResultCard result={result} onOpenHistory={openHistory} />

      <HistoryModal
        open={historyOpen}
        items={history}
        error={historyError}
        onClose={() => setHistoryOpen(false)}
      />
    </AnimatedCardGrid>
  );
}
