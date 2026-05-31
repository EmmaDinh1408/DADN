import { useState } from "react";
import { Card, Field, Select, Button, Badge } from "./ui-bits";
import { ArrowLeft, Plus, Play, FileText, Sparkles, ArrowUpRight, X, FolderKanban, Lollipop } from "lucide-react";

export type Scheme = {
  schemeNo: number;
  date: string;
  status: "draft" | "ok" | "fail";
  P_dc: number;
  n_dc: number;
  u_total: number;
  L_h: number;
  shiftNum: 1 | 2 | 3;
  load_type: "tinh" | "va_nhe" | "va_manh";
  motorCode?: string;
};

export type Project = {
  projectID: string;
  projectName: string;
  projectDescription: string;
  createdDate: string;
  schemes: Scheme[];
};

const statusTone = { draft: "stone", ok: "green", fail: "rose" } as const;
const statusLabel = { draft: "Nháp", ok: "Đạt", fail: "Chưa đạt" } as const;

export function ProjectWorkspace({
  project,
  onBack,
  onAddScheme,
  onOpenScheme,
  onRunPipeline,
}: {
  project: Project;
  onBack: () => void;
  onAddScheme: (s: Scheme) => void;
  onOpenScheme: (s: Scheme) => void;
  onRunPipeline: (s: Scheme) => void;
}) {
  const sortedSchemes = [...project.schemes].sort((a, b) => b.date.localeCompare(a.date) || b.schemeNo - a.schemeNo);
  const last = sortedSchemes[0];
  const maxNo = project.schemes.reduce((m, s) => Math.max(m, s.schemeNo), 0);
  const [P, setP] = useState(last ? String(last.P_dc) : "4.5");
  const [n, setN] = useState(last ? String(last.n_dc) : "50");
  const [L_h, setL_h] = useState(last?.L_h ? String(last.L_h) : "5");
  const [shiftNum, setShiftNum] = useState<string>(last?.shiftNum ? String(last.shiftNum) : "2");
  const [load_type, setLoadType] = useState<string>(last?.load_type ?? "va_nhe");
  const [u_t, setUT] = useState(last ? String(last.u_total) : "22.2");

  const build = (): Scheme => ({
    schemeNo: maxNo + 1,
    date: new Date().toISOString().slice(0, 16).replace("T", " "),
    status: "draft",
    P_dc: parseFloat(P) || 0,
    n_dc: parseFloat(n) || 0,
    u_total: parseFloat(u_t) || 0,
    L_h: parseFloat(L_h) || 0,
    shiftNum: (parseInt(shiftNum, 10) as 1 | 2 | 3) || 2,
    load_type: load_type as Scheme["load_type"],
  });

  const errs = {
    P:  /^\d*\.?\d+$/.test(P)  && parseFloat(P)  > 0 ? "" : "Phải là số dương",
    n:  /^\d*\.?\d+$/.test(n)  && parseFloat(n)  > 0 ? "" : "Phải là số dương",
    u:  /^\d*\.?\d+$/.test(u_t) && parseFloat(u_t) > 1 ? "" : "Phải > 1",
    L:  /^\d*\.?\d+$/.test(L_h) && parseFloat(L_h) > 0 ? "" : "Phải là số dương",
  };
  const invalid = Object.values(errs).some(Boolean);

  const [saving, setSaving] = useState(false);

  const createDraft = async () => {
    if (invalid) return;
    setSaving(true);
    await onAddScheme(build());
    setSaving(false);
  };
  
  const createAndRun = async () => {
    if (invalid) return;
    setSaving(true);
    const s = build();
    await onAddScheme(s);
    setSaving(false);
    onRunPipeline(s);
  };

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="sticky top-0 z-10 bg-white/95 backdrop-blur border-b border-stone-200">
        <div className="px-8 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-5 min-w-0">
            <button
              onClick={onBack}
              className="group relative p-2.5 rounded-xl border border-stone-200 text-stone-500 hover:bg-stone-50 hover:text-stone-800 hover:border-stone-300 transition-all shrink-0"
            >
              <ArrowLeft size={16} />
              <span className="pointer-events-none absolute -bottom-8 left-1/2 -translate-x-1/2 whitespace-nowrap px-2.5 py-1 rounded-lg bg-stone-800 text-white text-[11px] opacity-0 group-hover:opacity-100 transition-opacity shadow-lg z-50">
                Danh sách dự án
              </span>
            </button>

            <div className="w-px h-8 bg-stone-200 shrink-0"></div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5 text-stone-500 font-medium" style={{ fontSize: 11, letterSpacing: '0.08em' }}>
                <FolderKanban size={13} /> DỰ ÁN <span className="text-stone-300 mx-0.5">/</span> {project.projectID}
              </div>
              <div className="text-stone-900 font-bold truncate mt-1" style={{ fontSize: 18, letterSpacing: '0.02em' }}>
                {project.projectName.toUpperCase()}
              </div>
            </div>
          </div>
          
          <div className="shrink-0">
            <div className="flex items-center gap-2 bg-stone-50 px-3 py-1.5 rounded-xl border border-stone-200/60 shadow-sm">
              <span className="text-stone-500 font-medium" style={{ fontSize: 12 }}>Đã có:</span>
              <Badge tone="stone"><span className="font-bold">{project.schemes.length}</span> scheme</Badge>
            </div>
          </div>
        </div>
      </div>

      <div className="p-8 grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div className="lg:col-span-3 space-y-6">
          <Card
            accent
            title={<span className="font-bold">Tạo Design Scheme mới</span>}
            action={<Badge tone="amber"><Sparkles size={11} className="mr-1" /> Nhập input đầu vào</Badge>}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Field label="Công suất trục công tác P_dc" unit="kW" value={P} onChange={setP} error={errs.P} />
              <Field label="Số vòng quay trục công tác n_dc" unit="vg/ph" value={n} onChange={setN} error={errs.n} />
              <Field label="Tỉ số truyền tổng u_total" value={u_t} onChange={setUT} error={errs.u} />
              <Field label="Thời gian phục vụ L_h" unit="năm" value={L_h} onChange={setL_h} error={errs.L} />
              <Select
                label="Số ca làm việc"
                value={shiftNum}
                onChange={setShiftNum}
                options={[
                  { value: "1", label: "1 ca" },
                  { value: "2", label: "2 ca" },
                  { value: "3", label: "3 ca" },
                ]}
              />
              <Select
                label="Đặc tính tải trọng"
                value={load_type}
                onChange={setLoadType}
                options={[
                  { value: "tinh", label: "Tĩnh" },
                  { value: "va_nhe", label: "Va đập nhẹ" },
                  { value: "va_manh", label: "Va đập mạnh" },
                ]}
              />
            </div>

            <div className="mt-5 p-3 rounded-xl bg-stone-50 text-stone-500" style={{ fontSize: 12, lineHeight: 1.7 }}>
              * Sau khi tạo scheme, bạn có thể chạy lần lượt qua các bước: Động cơ → AI Optimizer → Xích → Bánh răng → Báo cáo.
              Mỗi lần bấm "Tính" ở các module sẽ cập nhật scheme này.
            </div>

            <div className="mt-4 flex flex-wrap items-center justify-end gap-2">
              <Button variant="outline" size="sm" onClick={createDraft} disabled={invalid || saving} title={invalid ? "Sửa các trường nhập sai trước" : ""}>
                {saving ? <><Lollipop size={14} className="animate-spin text-pink-400" /> Đang lưu...</> : <><Plus size={14} /> Lưu nháp</>}
              </Button>
              <Button size="sm" onClick={createAndRun} disabled={invalid || saving} title={invalid ? "Sửa các trường nhập sai trước" : ""}>
                {saving ? <><Lollipop size={14} className="animate-spin text-white" /> Đang lưu...</> : <><Play size={13} /> Tạo & Chạy pipeline</>}
              </Button>
            </div>
          </Card>

          <Card title={<span className="font-bold">Lịch sử Design Scheme · {project.schemes.length}</span>}>
            {project.schemes.length === 0 ? (
              <div className="py-10 text-center text-stone-400" style={{ fontSize: 13 }}>
                Chưa có scheme nào. Tạo scheme mới ở trên ↑
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-stone-500 border-b border-stone-200" style={{ fontSize: 12, letterSpacing: '0.04em' }}>
                      <th className="text-left py-2 px-2 whitespace-nowrap">#</th>
                      <th className="text-left py-2 px-2 whitespace-nowrap">NGÀY</th>
                      <th className="text-right py-2 px-2 whitespace-nowrap">P</th>
                      <th className="text-right py-2 px-2 whitespace-nowrap">N</th>
                      <th className="text-right py-2 px-2 whitespace-nowrap">U</th>
                      <th className="text-center py-2 px-2 whitespace-nowrap">T.THÁI</th>
                      <th className="text-center py-2 px-2 w-10"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedSchemes.map((s) => (
                      <tr
                        key={s.schemeNo}
                        onClick={() => onOpenScheme(s)}
                        className="border-b border-stone-100 hover:bg-gradient-to-r hover:from-yellow-50/60 hover:to-pink-50/60 cursor-pointer"
                      >
                        <td className="py-2.5 px-2 text-stone-800 font-mono font-bold" style={{ fontSize: 13 }}>#{s.schemeNo}</td>
                        <td className="py-2.5 px-2 text-stone-500" style={{ fontSize: 12 }}>{s.date}</td>
                        <td className="py-2.5 px-2 text-right text-stone-700 font-mono" style={{ fontSize: 12 }}>{s.P_dc.toFixed(1)}</td>
                        <td className="py-2.5 px-2 text-right text-stone-700 font-mono" style={{ fontSize: 12 }}>{s.n_dc}</td>
                        <td className="py-2.5 px-2 text-right text-stone-700 font-mono" style={{ fontSize: 12 }}>{s.u_total.toFixed(1)}</td>
                        <td className="py-2.5 px-2 text-center">
                          <Badge tone={statusTone[s.status]}>{statusLabel[s.status]}</Badge>
                        </td>
                        <td className="py-2.5 px-2 text-center">
                          <button
                            onClick={(e) => { e.stopPropagation(); onOpenScheme(s); }}
                            className="group relative p-2 rounded-lg text-stone-400 hover:bg-white hover:text-stone-700 hover:shadow-sm border border-transparent hover:border-stone-200 transition-all"
                            title="Xem báo cáo"
                          >
                            <FileText size={14} />
                            <span className="pointer-events-none absolute -bottom-7 left-1/2 -translate-x-1/2 whitespace-nowrap px-2 py-0.5 rounded-md bg-stone-800 text-white text-[10px] opacity-0 group-hover:opacity-100 transition-opacity shadow-lg z-50">
                              Xem báo cáo
                            </span>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <Card title="Thông tin dự án">
            <InfoRow k="Project ID" v={project.projectID} mono />
            <InfoRow k="Tên" v={project.projectName} />
            <InfoRow k="Mô tả" v={project.projectDescription || "—"} />
            <InfoRow k="Ngày tạo" v={project.createdDate} mono />
          </Card>

          <Card title="Mẹo">
            <ul className="space-y-2 text-stone-600" style={{ fontSize: 13, lineHeight: 1.7 }}>
              <li className="flex gap-2"><FileText size={14} className="text-stone-400 mt-0.5 shrink-0" /> Mỗi lần "Chạy pipeline" sẽ ghi lại 1 scheme mới.</li>
              <li className="flex gap-2"><Sparkles size={14} className="text-stone-400 mt-0.5 shrink-0" /> Thông số tối ưu AI Q-Learning (ψ_ba, u_d, u_x, z₁...) áp dụng tự động.</li>
              <li className="flex gap-2"><ArrowUpRight size={14} className="text-stone-400 mt-0.5 shrink-0" /> Bấm vào từng scheme để xem báo cáo siêu chi tiết.</li>
            </ul>
          </Card>
        </div>
      </div>
    </div>
  );
}

function InfoRow({ k, v, mono }: { k: string; v: string; mono?: boolean }) {
  return (
    <div className="flex items-baseline justify-between py-2 gap-3 border-b border-stone-100 last:border-0">
      <span className="text-stone-500 shrink-0" style={{ fontSize: 12 }}>{k}</span>
      <span className={`text-stone-800 text-right ${mono ? "font-mono" : ""}`} style={{ fontSize: 13 }}>{v}</span>
    </div>
  );
}
