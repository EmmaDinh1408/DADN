import { useState } from "react";
import { Header } from "./Header";
import { Card, Result, Badge } from "./ui-bits";
import { AlertTriangle, Sparkles, Loader2 } from "lucide-react";
import { createClient } from "@/utils/supabase/client";

export function ModuleGearbox({ onGoto, aiResult, currentScheme }: { onGoto?: (k: any) => void; aiResult?: any, currentScheme?: { projectID: number; schemeNo: number } | null }) {
  const gearData = aiResult?.physics_details?.gear;
  const aiAction = aiResult?.optimal_action;
  
  const AI_SEEDS = {
    matID: aiAction?.matID || "40X",
    psi_ba: aiAction?.optimal_psi_ba || 0.315,
    u_d: aiAction?.optimal_ud || 3.15,
    z_g1: aiAction?.z1_gear || 21,
  };
  const [calc, setCalc] = useState(false);
  const [saving, setSaving] = useState(false);
  const supabase = createClient();

  const passed = gearData?.pass_H && gearData?.pass_F;
  const schemeStatus = !calc ? "PENDING" : passed ? "SUCCESS" : "FAILED";
  const failure = calc && !passed;

  const handleRun = async () => {
    if (!currentScheme) {
      setCalc(true);
      return;
    }
    setSaving(true);
    const newStatus = passed ? "SUCCESS" : "FAILED";
    
    const { error: err1 } = await supabase.from("DESIGN_SCHEME").update({
      status: newStatus
    }).eq("projectID", currentScheme.projectID).eq("schemeNo", currentScheme.schemeNo);
    
    setSaving(false);
    setCalc(true);
  };

  return (
    <div className="flex-1 overflow-y-auto">
      <Header
        title="Hộp giảm tốc"
        desc="Côn-trụ 2 cấp · Áp dụng seeds AI cho mác thép & ψ_ba"
        stepKey="gearbox"
        onGoto={onGoto}
        onRun={handleRun}
        saving={saving}
      />

      <div className="px-8 pt-6">
        <div className="flex items-center gap-2 flex-wrap p-4 rounded-2xl bg-gradient-to-r from-yellow-50 to-pink-50 border border-pink-100">
          <span className="flex items-center gap-1.5 text-stone-700 mr-2" style={{ fontSize: 13 }}>
            <Sparkles size={14} className="text-stone-600" /> AI Q-Learning cấp:
          </span>
          <Badge tone="amber">Mác Thép = {AI_SEEDS.matID}</Badge>
          <Badge tone="amber">ψ_ba = {AI_SEEDS.psi_ba.toFixed(3)}</Badge>
          <Badge tone="amber">u_d = {AI_SEEDS.u_d.toFixed(2)}</Badge>
          <Badge tone="amber">z₁ sơ bộ = {AI_SEEDS.z_g1}</Badge>
        </div>
      </div>

      {failure && (
        <div className="px-8 pt-4">
          <div className="rounded-2xl border border-pink-300 bg-pink-50/80 p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="text-pink-700 mt-0.5" size={18} />
              <div className="flex-1">
                <div className="text-pink-800" style={{ letterSpacing: '0.04em' }}>
                  THẤT BẠI — Kiểm bền không đạt
                </div>
                <div className="text-pink-700 mt-1" style={{ fontSize: 13, lineHeight: 1.7 }}>
                  {!gearData?.pass_H && `σ_H thực tế (${gearData?.sigma_H} MPa) vượt quá [σ_H] = ${gearData?.sigma_H_allow} MPa.`}
                  {!gearData?.pass_F && `σ_F thực tế (${gearData?.sigma_F} MPa) vượt quá [σ_F] = ${gearData?.sigma_F_allow} MPa.`}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="p-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Kế thừa hoàn toàn từ AI Optimizer">
          <div className="space-y-2">
            <Result label="Mác thép" value={AI_SEEDS.matID} />
            <Result label="ψ_ba" value={AI_SEEDS.psi_ba.toFixed(3)} />
            <Result label="u_d" value={AI_SEEDS.u_d.toFixed(2)} />
            <Result label="z₁ sơ bộ" value={AI_SEEDS.z_g1.toString()} />
          </div>
          <div className="mt-4 p-3 rounded-xl bg-stone-50 text-stone-500" style={{ fontSize: 12, lineHeight: 1.7 }}>
            Bước này KHÔNG nhập tay. Tất cả tham số đều do AI cấp. 
          </div>
        </Card>

        <Card title="Cấp nhanh — Bánh răng côn" accent>
          {!calc ? (
            <div className="py-8 text-center text-stone-400">Bấm "Tính &amp; hoàn thành" để xem kết quả</div>
          ) : (
            gearData ? (
              <div className="space-y-1">
                <Result label="u₁ (u_d)" value={gearData.u1?.toFixed(2) || AI_SEEDS.u_d.toFixed(2)} hi />
                <Result label="Module m_te" value={gearData.m_tm} unit="mm" />
                <Result label="Số răng z₁ / z₂" value={`${gearData.z1} / ${gearData.z2}`} />
                <Result label="Đường kính d_e1 / d_e2" value={`${gearData.d_w1} / ${gearData.d_w2}`} unit="mm" />
                <Result label="σ_H thực / [σ_H]" value={`${gearData.sigmaH} / ${gearData.sigmaH_allow}`} unit="MPa" />
                {(gearData.sigmaH && gearData.sigmaH_allow && gearData.sigmaH <= gearData.sigmaH_allow) || gearData.pass_H ? <Badge tone="green">Bền tiếp xúc</Badge> : <Badge tone="rose">Không bền tiếp xúc</Badge>}
              </div>
            ) : (
              <div className="py-8 text-center text-rose-400">Không tìm thấy thông số bánh răng</div>
            )
          )}
        </Card>

        <Card title="Cấp chậm — Bánh răng trụ răng nghiêng">
          {!calc ? (
            <div className="py-8 text-center text-stone-400">Bấm "Tính &amp; hoàn thành" để xem kết quả</div>
          ) : (
            gearData ? (
              <div className="space-y-1">
                <Result label="u₂" value={gearData.u2?.toFixed(2) || "2.82"} hi />
                <Result label="Khoảng cách trục a_w" value={gearData.a_w} unit="mm" />
                <Result label="Module m_n" value={gearData.m_n} unit="mm" />
                <Result label="Góc nghiêng β" value={gearData.beta_deg || "0"} unit="°" />
                <Result label="σ_F thực / [σ_F]" value={`${gearData.sigmaF} / ${gearData.sigmaF_allow}`} unit="MPa" />
                {(gearData.sigmaF && gearData.sigmaF_allow && gearData.sigmaF <= gearData.sigmaF_allow) || gearData.pass_F ? <Badge tone="green">Bền uốn</Badge> : <Badge tone="rose">Chưa bền uốn</Badge>}
              </div>
            ) : (
              <div className="py-8 text-center text-rose-400">Không tìm thấy thông số bánh răng</div>
            )
          )}
        </Card>

        {calc && gearData && (
          <Card title="GEAR_TRANS.calculation_trace_report (JSONB)">
            <div className="flex items-center gap-2 mb-2" style={{ fontSize: 12 }}>
              <span className="text-stone-500">DESIGN_SCHEME.status =</span>
              <Badge tone={schemeStatus === "SUCCESS" ? "green" : schemeStatus === "FAILED" ? "rose" : "amber"}>
                {schemeStatus}
              </Badge>
            </div>
            <pre className="font-mono text-stone-700 bg-stone-50 rounded-xl p-4 overflow-x-auto" style={{ fontSize: 11, lineHeight: 1.6 }}>
{JSON.stringify(gearData, null, 2)}
            </pre>
          </Card>
        )}

        <Card title="Phân phối tỉ số truyền (Solver song song)">
          <div className="grid grid-cols-3 gap-3 text-center">
            <div className="p-4 rounded-xl bg-gradient-to-br from-yellow-100 to-yellow-50">
              <div className="text-stone-500" style={{ fontSize: 12 }}>u_h (gearbox)</div>
              <div className="text-stone-800 mt-1">{gearData?.u_t?.toFixed(2) || "8.89"}</div>
            </div>
            <div className="p-4 rounded-xl bg-gradient-to-br from-pink-100 to-pink-50">
              <div className="text-stone-500" style={{ fontSize: 12 }}>u_x (xích)</div>
              <div className="text-stone-800 mt-1">{aiResult?.physics_details?.chain?.u?.toFixed(2) || "2.50"}</div>
            </div>
            <div className="p-4 rounded-xl bg-gradient-to-br from-pink-100 to-pink-50">
              <div className="text-stone-500" style={{ fontSize: 12 }}>u_chung</div>
              <div className="text-stone-800 mt-1">{aiResult?.physics_details?.discretization?.discretized?.u_total?.toFixed(2) || "22.23"}</div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
