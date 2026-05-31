import { useState } from "react";
import { Header } from "./Header";
import { Card, Badge, Button, Field } from "./ui-bits";
import { Sparkles, Brain, Cog, Link2, Play, ArrowRight, AlertCircle, Lollipop } from "lucide-react";
import { useWorkflow } from "./workflow";

import { createClient } from "@/utils/supabase/client";

export function ModuleOptimizer({ onGoto, onSuccess, currentScheme }: { onGoto?: (k: any) => void; onSuccess?: (data: any) => void; currentScheme?: { projectID: number; schemeNo: number } | null }) {
  const [ran, setRan] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { markDone, nextOf } = useWorkflow();
  const supabase = createClient();

  const [P_yc, setP_yc] = useState("4.5");
  const [n_yc, setN_yc] = useState("50");
  const [u_total, setU_total] = useState("28.5");
  const [L_h, setL_h] = useState("5");
  const [load_type, setLoad_type] = useState("1");

  const [aiResult, setAiResult] = useState<any>(null);

  const run = async () => {
    setLoading(true);
    setError("");
    try {
      if (!currentScheme) {
        throw new Error("Không tìm thấy Scheme hiện tại. Hãy tạo scheme từ màn hình Dự án trước.");
      }

      const res = await fetch("http://127.0.0.1:8000/ai/optimize-design", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          P_yc: parseFloat(P_yc),
          n_yc: parseFloat(n_yc),
          u_total: parseFloat(u_total),
          L_h: parseFloat(L_h),
          load_type: parseInt(load_type),
        }),
      });
      if (!res.ok) {
        const errData = await res.json();
        let errMsg = "Có lỗi xảy ra khi gọi AI";
        if (errData.detail) {
          if (typeof errData.detail === "string") {
            errMsg = errData.detail;
          } else {
            errMsg = JSON.stringify(errData.detail);
          }
        }
        throw new Error(errMsg);
      }
      const data = await res.json();

      const { error: errTrans1 } = await supabase.from("TRANSMISSION").upsert({
        projectID: currentScheme.projectID,
        schemeNo: currentScheme.schemeNo,
        stageNo: 1,
        transtype: "GEAR",
        u_real: data.optimal_action.optimal_ud,
      }, { onConflict: "projectID,schemeNo,stageNo" });
      if (errTrans1) throw errTrans1;

      const { error: errGear } = await supabase.from("GEAR_TRANS").upsert({
        projectID: currentScheme.projectID,
        schemeNo: currentScheme.schemeNo,
        stageNo: 1,
        optimal_ud: data.optimal_action.optimal_ud,
        gear_type: data.optimal_action.gear_type === "Răng thẳng" ? "straight" : "helical",
        optimal_zg1: data.optimal_action.z1_gear || 17,
        optimal_psi_ba: data.optimal_action.optimal_psi_ba,
        matID: data.optimal_action.matID,
        calculation_trace_report: data,
      }, { onConflict: "projectID,schemeNo,stageNo" });
      if (errGear) throw errGear;

      const { error: errTrans2 } = await supabase.from("TRANSMISSION").upsert({
        projectID: currentScheme.projectID,
        schemeNo: currentScheme.schemeNo,
        stageNo: 2,
        transtype: "CHAIN",
      }, { onConflict: "projectID,schemeNo,stageNo" });
      if (errTrans2) throw errTrans2;

      const computed_ux = parseFloat(u_total) / (data.optimal_action.optimal_ud || 1);

      const { error: errChain } = await supabase.from("CHAIN_TRANS").upsert({
        projectID: currentScheme.projectID,
        schemeNo: currentScheme.schemeNo,
        stageNo: 2,
        optimal_ux: +computed_ux.toFixed(3),
        optimal_z1: data.optimal_action.z1_chain || 25,
        calculation_trace_report: data,
      }, { onConflict: "projectID,schemeNo,stageNo" });
      if (errChain) throw errChain;

      setAiResult(data);
      if (onSuccess) onSuccess(data);
      setRan(true);
    } catch (err: any) {
      let msg = err.message || err.details || err.hint;
      if (!msg && typeof err === "object") msg = JSON.stringify(err);
      setError(msg || "Có lỗi xảy ra");
    } finally {
      setLoading(false);
    }
  };

  const approve = () => {
    markDone("optimizer");
    const next = nextOf("optimizer");
    if (next && onGoto) onGoto(next);
  };

  return (
    <div className="flex-1 overflow-y-auto">
      <Header
        title="AI Optimizer"
        desc="Q-Learning offline · Tra Q-Table O(1)"
        stepKey="optimizer"
        onGoto={onGoto}
      />
      <div className="p-8 space-y-6">
        {!ran && (
          <Card accent>
            <div className="flex flex-col items-center text-center gap-4 py-8">
              <div className="p-5 rounded-2xl bg-gradient-to-br from-yellow-200 to-pink-300 text-stone-800">
                <Sparkles size={32} />
              </div>
              <div className="max-w-md">
                <div className="text-stone-800" style={{ letterSpacing: '0.04em' }}>
                  THÔNG SỐ ĐẦU VÀO DỰ ÁN
                </div>
                <p className="text-stone-500 mt-2" style={{ fontSize: 13, lineHeight: 1.7 }}>
                  Nhập yêu cầu để AI tra Q-Table và đưa ra bộ thông số thiết kế tối ưu.
                </p>

                <div className="mt-6 grid grid-cols-2 gap-4 text-left">
                  <Field label="Công suất (kW)" type="number" value={P_yc} onChange={setP_yc} />
                  <Field label="Vòng quay (v/p)" type="number" value={n_yc} onChange={setN_yc} />
                  <Field label="Tỉ số truyền U" type="number" value={u_total} onChange={setU_total} />
                  <Field label="Tuổi thọ Lh (năm)" type="number" value={L_h} onChange={setL_h} />
                  <div className="col-span-2">
                    <label className="text-stone-700 block mb-1.5 font-medium" style={{ fontSize: 13 }}>Tải trọng</label>
                    <select 
                      value={load_type} 
                      onChange={(e) => setLoad_type(e.target.value)}
                      className="w-full px-3 py-2.5 rounded-xl bg-stone-50 border border-stone-200 focus:border-pink-300 outline-none"
                    >
                      <option value="0">Tải tĩnh</option>
                      <option value="1">Va đập nhẹ</option>
                      <option value="2">Va đập mạnh</option>
                    </select>
                  </div>
                </div>

                {error && (
                  <div className="mt-4 flex items-center gap-2 p-3 rounded-xl bg-pink-50 text-pink-700 text-sm text-left">
                    <AlertCircle size={16} />
                    <span>{error}</span>
                  </div>
                )}
              </div>
              <Button onClick={run} disabled={loading} className="mt-4">
                {loading ? <Lollipop size={14} className="animate-spin" /> : <Play size={14} />} 
                {loading ? "Đang tra cứu..." : "Chạy AI Tối Ưu"}
              </Button>
            </div>
          </Card>
        )}

        {ran && aiResult && (
          <>
            <Card accent>
              <div className="flex items-center gap-4">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-yellow-200 to-pink-300 text-stone-800">
                  <Sparkles size={28} />
                </div>
                <div className="flex-1">
                  <div className="text-stone-800">Thông số tối ưu đã sẵn sàng</div>
                  <div className="text-stone-500 mt-1" style={{ fontSize: 13, lineHeight: 1.7 }}>
                    Nhãn "Optimal" là kết quả đóng gói từ offline training (reward đã phạt phương án nặng & thưởng phương án gọn sát mép an toàn). Không phải kết luận runtime.
                  </div>
                </div>
                <Badge tone="green">AI Suggestion · Optimal</Badge>
              </div>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card title="Bộ thông số AI · Bánh răng">
                <div className="flex items-center gap-2 mb-4 text-stone-500" style={{ fontSize: 12 }}>
                  <Cog size={14} /> AI Suggestion (Optimal) · read-only
                </div>
                <div className="space-y-2">
                  <SeedRow k="Mác Thép" v={aiResult.optimal_action.matID} />
                  <SeedRow k="Hệ số ψ_ba" v={aiResult.optimal_action.optimal_psi_ba.toFixed(3)} />
                  <SeedRow k="Tỉ số truyền u_d" v={aiResult.optimal_action.optimal_ud.toFixed(2)} />
                  <SeedRow k="Số răng sơ bộ z₁" v={aiResult.optimal_action.z1_gear || "?"} />
                  <SeedRow k="Loại bánh răng" v={aiResult.optimal_action.gear_type} />
                </div>
              </Card>

              <Card title="Bộ thông số AI · Xích">
                <div className="flex items-center gap-2 mb-4 text-stone-500" style={{ fontSize: 12 }}>
                  <Link2 size={14} /> AI Suggestion (Optimal) · read-only
                </div>
                <div className="space-y-2">
                  <SeedRow k="Số răng đĩa nhỏ z₁" v={aiResult.optimal_action.z1_chain} />
                </div>
                <div className="mt-4 text-stone-400" style={{ fontSize: 11 }}>
                  * Bước xích p KHÔNG do AI chọn trực tiếp — vét cạn ở Module Xích.
                </div>
              </Card>
            </div>

            <Card title="Hộp Đen Minh Bạch · Reward Function">
              <div className="flex items-center gap-2 mb-3 text-stone-500" style={{ fontSize: 12 }}>
                <Brain size={14} /> Q-Learning reward
              </div>
              <pre className="font-mono text-stone-700 bg-stone-50 rounded-xl p-4 overflow-x-auto" style={{ fontSize: 12, lineHeight: 1.7 }}>
{`if (σH > [σH])  or  (σF > [σF])  or  (s < [s]):
    Reward = − Penalty

else:
    Reward = w₁ · (1 / Volume_gearbox)
           + w₂ · clip(SafetyFactor, 1.5, 2.0)
           + w₃ · η_total
           − w₄ · |u_d − u_d*|`}
              </pre>
            </Card>

            <div className="flex justify-between items-center mt-4">
              <Button variant="ghost" onClick={() => setRan(false)}>Nhập lại thông số</Button>
              <Button onClick={approve}>
                <ArrowRight size={14} /> Phê duyệt & Tiếp tục
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function SeedRow({ k, v }: { k: string; v: string | number }) {
  return (
    <div className="flex items-baseline justify-between py-2 px-3 rounded-lg bg-gradient-to-r from-yellow-50/70 to-pink-50/70">
      <span className="text-stone-600" style={{ fontSize: 13 }}>{k}</span>
      <span className="text-stone-900 font-mono">{v}</span>
    </div>
  );
}
