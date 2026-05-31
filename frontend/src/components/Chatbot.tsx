import { useState } from "react";
import { Header } from "./Header";
import { Card } from "./ui-bits";
import { Send, BookOpen, User, Bot } from "lucide-react";

type Msg = { role: "user" | "bot"; text: string; sources?: string[] };

const seed: Msg[] = [
  {
    role: "bot",
    text: "Xin chào! Mình là trợ lý RAG đã index 7 PDF giáo trình. Bạn muốn hỏi gì về thiết kế hệ dẫn động?",
  },
  {
    role: "user",
    text: "Cách chọn số răng đĩa xích nhỏ z₁?",
  },
  {
    role: "bot",
    text: "Số răng đĩa xích nhỏ z₁ được chọn theo tỉ số truyền u. Công thức: z₁ = 29 − 2u, đồng thời z₁ ≥ z_min (thường 17). Với xích con lăn nên lấy z₁ là số lẻ để mòn đều.",
    sources: ["Trịnh Chất - Lê Văn Uyển · trang 80", "TCVN 1592:1974"],
  },
];

export function Chatbot() {
  const [msgs, setMsgs] = useState<Msg[]>(seed);
  const [input, setInput] = useState("");

  const send = () => {
    if (!input.trim()) return;
    setMsgs((m) => [
      ...m,
      { role: "user", text: input },
      {
        role: "bot",
        text: "(Mock) Backend RAG chưa cắm — câu trả lời thật sẽ retrieve từ ChromaDB top-k chunks rồi tổng hợp bằng LLM.",
        sources: ["Mock source"],
      },
    ]);
    setInput("");
  };

  return (
    <div className="flex-1 overflow-hidden flex flex-col">
      <Header title="AI Chatbot · RAG" desc="Hỏi đáp dựa trên 7 PDF giáo trình + tiêu chuẩn TCVN" />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-3xl mx-auto space-y-4">
          {msgs.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
              <div
                className={`shrink-0 w-9 h-9 rounded-full flex items-center justify-center ${
                  m.role === "user"
                    ? "bg-gradient-to-br from-yellow-300 to-pink-300 text-stone-800"
                    : "bg-white border border-pink-200 text-stone-600"
                }`}
              >
                {m.role === "user" ? <User size={16} /> : <Bot size={16} />}
              </div>
              <div className={`max-w-[75%] ${m.role === "user" ? "text-right" : ""}`}>
                <div
                  className={`inline-block px-4 py-3 rounded-2xl ${
                    m.role === "user"
                      ? "bg-gradient-to-br from-yellow-100 to-pink-100 text-stone-800"
                      : "bg-white/80 border border-pink-100 text-stone-700"
                  }`}
                >
                  {m.text}
                </div>
                {m.sources && (
                  <div className="mt-2 flex gap-2 flex-wrap">
                    {m.sources.map((s) => (
                      <span key={s} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-pink-50 text-stone-700 border border-pink-100">
                        <BookOpen size={12} /> {s}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="p-6 border-t border-pink-100 bg-white/40 backdrop-blur">
        <div className="max-w-3xl mx-auto flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Hỏi gì đó về thiết kế hệ dẫn động..."
            className="flex-1 px-4 py-3 rounded-xl bg-white border border-pink-100 focus:border-pink-300 focus:ring-2 focus:ring-pink-100 outline-none"
          />
          <button
            onClick={send}
            className="px-5 py-3 rounded-xl bg-gradient-to-r from-yellow-300 to-pink-300 text-stone-800 flex items-center gap-2"
          >
            <Send size={16} /> Gửi
          </button>
        </div>
      </div>
    </div>
  );
}
