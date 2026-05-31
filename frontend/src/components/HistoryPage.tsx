import { useState, useEffect } from "react";
import { Header } from "./Header";
import { Card, Badge } from "./ui-bits";
import { Search, Trash2, Download, Eye, Filter, Lollipop } from "lucide-react";
import { createClient } from "@/utils/supabase/client";
import { SchemeReport, SchemeDetail } from "./SchemeReport";

type Row = {
  id: string;
  projectID: string;
  schemeNo: number;
  name: string;
  date: string;
  P: number;
  n: number;
  motor: string;
  u: number;
  status: "Đạt" | "Chưa đạt" | "Nháp";
};

const tones: Record<Row["status"], "green" | "amber" | "rose" | "stone"> = {
  "Đạt": "green",
  "Chưa đạt": "rose",
  "Nháp": "stone",
};

export function HistoryPage({ user }: { user?: { id?: string } }) {
  const [q, setQ] = useState("");
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewing, setViewing] = useState<SchemeDetail | null>(null);
  const supabase = createClient();

  useEffect(() => {
    async function fetchHistory() {
      if (!user?.id) return;
      setLoading(true);
      const { data: projects, error } = await supabase
        .from("PROJECT")
        .select(`
          projectID,
          projectName,
          DESIGN_SCHEME (
            schemeNo,
            date,
            P_dc,
            n_dc,
            motorCode,
            u_total,
            status
          )
        `)
        .eq("userID", user.id)
        .order("createdDate", { ascending: false });

      if (projects) {
        const allRows: Row[] = [];
        projects.forEach((p: any) => {
          if (p.DESIGN_SCHEME) {
            p.DESIGN_SCHEME.forEach((s: any) => {
              allRows.push({
                id: `P${p.projectID}-S${s.schemeNo}`,
                projectID: p.projectID.toString(),
                schemeNo: s.schemeNo,
                name: p.projectName,
                date: new Date(s.date).toLocaleString("vi-VN"),
                P: parseFloat(s.P_dc),
                n: parseFloat(s.n_dc),
                motor: s.motorCode || "—",
                u: parseFloat(s.u_total),
                status: s.status === "SUCCESS" ? "Đạt" : s.status === "FAILED" ? "Chưa đạt" : "Nháp",
              });
            });
          }
        });
        allRows.sort((a, b) => b.date.localeCompare(a.date));
        setRows(allRows);
      }
      setLoading(false);
    }
    fetchHistory();
  }, [user]);

  if (viewing) {
    return <SchemeReport scheme={viewing} onBack={() => setViewing(null)} />;
  }

  const filtered = rows.filter((r) => r.name.toLowerCase().includes(q.toLowerCase()) || r.id.toLowerCase().includes(q.toLowerCase()));

  const handleView = (r: Row) => {
    setViewing({
      projectID: r.projectID,
      projectName: r.name,
      schemeNo: r.schemeNo,
      date: r.date,
      status: r.status === "Đạt" ? "ok" : r.status === "Chưa đạt" ? "fail" : "draft",
      P_dc: r.P,
      n_dc: r.n,
      u_total: r.u,
    });
  };

  return (
    <div className="flex-1 overflow-y-auto">
      <Header title="Lịch sử phiên thiết kế" desc="Các phiên tính toán đã lưu vào Supabase" />
      <div className="p-8 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { k: "Tổng phiên", v: rows.length },
            { k: "Phương án đạt", v: rows.filter((r) => r.status === "Đạt").length },
            { k: "Lần chỉnh sửa gần nhất", v: rows.length ? rows[0].date : "—" },
          ].map((s) => (
            <Card key={s.k}>
              <div className="text-stone-500">{s.k}</div>
              <div className="text-stone-800 font-serif mt-1" style={{ fontSize: 22 }}>{s.v}</div>
            </Card>
          ))}
        </div>

        <Card>
          <div className="flex items-center gap-3 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" size={16} />
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Tìm theo tên dự án hoặc ID..."
                className="w-full pl-10 pr-3 py-2.5 rounded-xl bg-white border border-pink-100 focus:border-pink-300 focus:ring-2 focus:ring-pink-100 outline-none"
              />
            </div>
            <button className="px-4 py-2.5 rounded-xl bg-white border border-pink-200 text-stone-700 hover:bg-pink-50 flex items-center gap-2">
              <Filter size={16} /> Lọc
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-stone-500 border-b border-pink-100" style={{ fontSize: 13, letterSpacing: '0.04em' }}>
                  <th className="text-left py-3 px-2 whitespace-nowrap">ID</th>
                  <th className="text-left py-3 px-2 whitespace-nowrap">TÊN DỰ ÁN</th>
                  <th className="text-left py-3 px-2 whitespace-nowrap">THỜI GIAN</th>
                  <th className="text-right py-3 px-2 whitespace-nowrap">P (KW)</th>
                  <th className="text-left py-3 px-2 whitespace-nowrap">ĐỘNG CƠ</th>
                  <th className="text-right py-3 px-2 whitespace-nowrap">U_CHUNG</th>
                  <th className="text-center py-3 px-2 whitespace-nowrap">TRẠNG THÁI</th>
                  <th className="text-right py-3 px-2 whitespace-nowrap">THAO TÁC</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={8} className="py-10 text-center text-stone-400"><Lollipop className="animate-spin inline mr-2 text-pink-400" size={16} />Đang tải dữ liệu...</td></tr>
                ) : filtered.length === 0 ? (
                  <tr><td colSpan={8} className="py-10 text-center text-stone-400">Chưa có phiên tính toán nào trong DB.</td></tr>
                ) : (
                  filtered.map((r) => (
                    <tr key={r.id} className="border-b border-pink-50 hover:bg-pink-50/40">
                      <td className="py-3 px-2 text-stone-800 font-mono" style={{ fontSize: 13 }}>{r.id}</td>
                      <td className="py-3 px-2 text-stone-800">{r.name}</td>
                      <td className="py-3 px-2 text-stone-500" style={{ fontSize: 13 }}>{r.date}</td>
                      <td className="py-3 px-2 text-right text-stone-700 font-mono">{r.P}</td>
                      <td className="py-3 px-2 text-stone-700 font-mono" style={{ fontSize: 13 }}>{r.motor}</td>
                      <td className="py-3 px-2 text-right text-stone-700 font-mono">{r.u}</td>
                      <td className="py-3 px-2 text-center"><Badge tone={tones[r.status]}>{r.status}</Badge></td>
                      <td className="py-3 px-2">
                        <div className="flex items-center justify-end gap-1">
                          <button onClick={() => handleView(r)} className="p-2 rounded-lg hover:bg-pink-50 text-stone-500 hover:text-stone-700 flex items-center gap-1 font-medium"><Eye size={15} /> Xem báo cáo</button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}
