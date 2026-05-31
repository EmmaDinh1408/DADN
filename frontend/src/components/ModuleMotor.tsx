import { useState, useEffect } from "react";
import { Header } from "./Header";
import { Card, Badge, Result } from "./ui-bits";
import { Zap, Check, ArrowRight, X, AlertCircle, Search, Lollipop } from "lucide-react";
import { createClient } from "@/utils/supabase/client";

export function ModuleMotor({ onGoto, aiResult, currentScheme }: { onGoto?: (k: any) => void; aiResult?: any; currentScheme?: { projectID: number; schemeNo: number } | null }) {
  const [picked, setPicked] = useState<string | null>(null);
  const [stdMotors, setStdMotors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const supabase = createClient();

  const disc = aiResult?.physics_details?.discretization?.discretized || { P_yc: 4.5, n_yc: 50, u_total: 22.2 };
  
  const eta_total = 0.85;
  const P_ct = +(disc.P_yc / eta_total).toFixed(2);
  const n_sb = +(disc.n_yc * disc.u_total).toFixed(0);

  useEffect(() => {
    async function loadMotors() {
      const { data, error } = await supabase.from("STD_MOTOR").select("*").order("P_dm", { ascending: true });
      console.log("[ModuleMotor] STD_MOTOR query:", { data, error });
      if (error) {
        console.error("[ModuleMotor] Lỗi fetch STD_MOTOR:", error.message, error);
      }
      if (data) setStdMotors(data);
      setLoading(false);
    }
    loadMotors();
  }, []);

  const saveMotor = async () => {
    if (picked && currentScheme) {
      setSaving(true);
      await supabase.from("DESIGN_SCHEME").update({ motorCode: picked }).eq("projectID", currentScheme.projectID).eq("schemeNo", currentScheme.schemeNo);
      setSaving(false);
    }
    if (onGoto) onGoto("chain");
  };

  return (
    <div className="flex-1 overflow-y-auto">
      <Header
        title="Chọn động cơ"
        desc="Tự động tính P_ct, n_sb · Tra catalog STD_MOTOR"
        stepKey="motor"
        onGoto={onGoto}
        onRun={saveMotor}
      />
      <div className="p-8 space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card title="Kế thừa từ Bước 1">
            <Result label="P_yc" value={disc.P_yc.toString()} unit="kW" />
            <Result label="n_yc" value={disc.n_yc.toString()} unit="vg/ph" />
            <Result label="u_total" value={disc.u_total.toString()} />
          </Card>
          <Card title="Hiệu suất sơ bộ">
            <Result label="η_total" value={eta_total.toFixed(2)} />
            <div className="mt-3 text-stone-500" style={{ fontSize: 12, lineHeight: 1.7 }}>
              η<sub>ch</sub>·η<sub>brc</sub>·η<sub>brt</sub>·η<sub>ol</sub>⁴ ≈ 0.85
            </div>
          </Card>
          <Card accent title="Tính tự động">
            <Result label="P_ct = P_yc / η" value={P_ct.toString()} unit="kW" hi />
            <Result label="n_sb = n_yc · u_total" value={n_sb.toString()} unit="vg/ph" hi />
          </Card>
        </div>

        <Card title={`Catalog STD_MOTOR · Chọn 1 dòng (P_dm ≥ ${P_ct} kW · n_dm ≈ ${n_sb} vg/ph)`}>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-stone-500 border-b border-stone-200" style={{ fontSize: 13, letterSpacing: '0.04em' }}>
                  <th className="text-left py-3 px-2 whitespace-nowrap">MOTOR CODE</th>
                  <th className="text-right py-3 px-2 whitespace-nowrap">P_ĐM (KW)</th>
                  <th className="text-right py-3 px-2 whitespace-nowrap">N_ĐM (VG/PH)</th>
                  <th className="text-right py-3 px-2 whitespace-nowrap">T_MAX/T_DN</th>
                  <th className="text-right py-3 px-2 whitespace-nowrap">ĐÁNH GIÁ</th>
                  <th className="py-3 px-2"></th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={6} className="py-10 text-center text-stone-400"><Lollipop className="animate-spin inline mr-2 text-pink-400" size={16} />Đang tải dữ liệu động cơ...</td></tr>
                ) : stdMotors.length === 0 ? (
                  <tr><td colSpan={6} className="py-10 text-center text-stone-400">Không có dữ liệu động cơ trong bảng STD_MOTOR.</td></tr>
                ) : (
                  stdMotors.map((m) => {
                    const ok = m.P_dm >= P_ct;
                    const isPicked = m.motorCode === picked;
                    return (
                      <tr
                        key={m.motorCode}
                        onClick={() => ok && setPicked(m.motorCode)}
                        className={`border-b border-stone-100 cursor-pointer ${
                          isPicked ? "bg-gradient-to-r from-yellow-50 to-pink-50" : "hover:bg-stone-50"
                        } ${!ok ? "opacity-50 cursor-not-allowed" : ""}`}
                      >
                        <td className="py-3 px-2 text-stone-800 font-mono">{m.motorCode}</td>
                        <td className="py-3 px-2 text-right text-stone-700 font-mono">{m.P_dm}</td>
                        <td className="py-3 px-2 text-right text-stone-700 font-mono">{m.n_dm}</td>
                        <td className="py-3 px-2 text-right text-stone-700 font-mono">{m.torqueRatio}</td>
                        <td className="py-3 px-2 text-right">
                          <Badge tone={ok ? "green" : "rose"}>{ok ? "Đạt" : "Thiếu công suất"}</Badge>
                        </td>
                        <td className="py-3 px-2 text-right">
                          {isPicked && <Check size={14} className="inline text-stone-700" />}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
          {picked && (
            <div className="mt-4 p-3 rounded-xl bg-gradient-to-r from-yellow-50 to-pink-50 text-stone-700" style={{ fontSize: 13 }}>
              Đã chọn động cơ <b className="font-mono">{picked}</b> — bấm "Tính & hoàn thành" để khoá lựa chọn.
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
