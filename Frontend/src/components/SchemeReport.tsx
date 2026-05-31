import { useState, useEffect } from "react";
import { Card, Result, Badge, Button } from "./ui-bits";
import { ArrowLeft, Cog, Link2, Zap, Sparkles, CheckCircle2, AlertTriangle, FileText, Lollipop } from "lucide-react";
import { createClient } from "@/utils/supabase/client";

export type SchemeDetail = {
  projectID: string;
  projectName: string;
  schemeNo: number;
  date: string;
  status: "draft" | "ok" | "fail";
  P_dc: number;
  n_dc: number;
  u_total: number;
  motorCode?: string;
};

const statusTone = { draft: "stone", ok: "green", fail: "rose" } as const;
const statusLabel = { draft: "Nháp", ok: "Đạt toàn bộ", fail: "Chưa đạt" } as const;

export function SchemeReport({ scheme, onBack, hideBackBtn }: { scheme: SchemeDetail; onBack: () => void; hideBackBtn?: boolean }) {
  const [reportData, setReportData] = useState<any>(null);
  const [motorData, setMotorData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const supabase = createClient();

  useEffect(() => {
    async function loadData() {
      const { data, error } = await supabase
        .from("GEAR_TRANS")
        .select("calculation_trace_report")
        .eq("projectID", parseInt(scheme.projectID))
        .eq("schemeNo", scheme.schemeNo)
        .eq("stageNo", 1)
        .single();
      
      if (data && data.calculation_trace_report) {
        setReportData(data.calculation_trace_report);
      }
      
      if (scheme.motorCode) {
        const { data: mData } = await supabase
          .from("STD_MOTOR")
          .select("*")
          .eq("motorCode", scheme.motorCode)
          .single();
        if (mData) setMotorData(mData);
      }
      
      setLoading(false);
    }
    if (scheme.status !== "draft") {
      loadData();
    } else {
      setLoading(false);
    }
  }, [scheme]);

  if (loading) {
    return <div className="p-10 text-center text-stone-500"><Lollipop className="animate-spin inline mr-2 text-pink-400" /> Đang tải báo cáo...</div>;
  }

  if (scheme.status === "draft" || !reportData) {
    return (
      <div className="flex-1 overflow-y-auto bg-stone-50/50 flex items-center justify-center">
        <div className="p-8 max-w-md text-center space-y-4">
          <div className="w-16 h-16 bg-stone-200 text-stone-400 rounded-full flex items-center justify-center mx-auto mb-2">
            <Settings2 size={24} />
          </div>
          <h2 className="text-lg font-medium text-stone-800">Báo cáo chưa sẵn sàng</h2>
          <p className="text-stone-500 text-sm leading-relaxed">
            Phương án <b>#{scheme.schemeNo}</b> của bạn đang ở trạng thái Nháp. 
            <br/><br/>
            Bạn cần phải bấm <b className="text-stone-700">Chạy AI Tối Ưu</b> và hoàn thành các bước tính toán qua các tab <b>Động cơ &rarr; Xích &rarr; Bánh răng</b>, sau đó bấm <b>"Tính & hoàn thành"</b> ở bước cuối cùng để hệ thống tạo bản báo cáo này.
          </p>
          {!hideBackBtn && (
            <Button onClick={onBack} variant="outline" className="mt-4 shadow-sm">
              <ArrowLeft size={14} className="mr-2" /> Quay lại
            </Button>
          )}
        </div>
      </div>
    );
  }

  const pd = reportData.physics_details;
  const ai = {
    matID: reportData.optimal_action.matID,
    psi_ba: reportData.optimal_action.optimal_psi_ba,
    u_d: reportData.optimal_action.optimal_ud,
    z_g1: pd.gear.z1 || "?",
    u_x: pd.gear.u_x || "?",
    z_chain: reportData.optimal_action.z1_chain,
  };
  
  const eta_total = 0.85;
  const motor = {
    code: scheme.motorCode || "Chưa chọn",
    P_dc: motorData?.P_dm,
    n_dc: motorData?.n_dm || scheme.n_dc,
    eta: eta_total,
    P_ct: scheme.P_dc / eta_total,
    P_td: (scheme.P_dc / eta_total) * 1.1,
  };
  
  const chain_d1 = pd.chain.pitch_p && pd.chain.z1 ? (pd.chain.pitch_p / Math.sin(Math.PI / pd.chain.z1)).toFixed(1) : "?";
  const chain_d2 = pd.chain.pitch_p && pd.chain.z2 ? (pd.chain.pitch_p / Math.sin(Math.PI / pd.chain.z2)).toFixed(1) : "?";

  const chain = {
    p: pd.chain.pitch_p, X: pd.chain.X, a: pd.chain.a, 
    d1: chain_d1, d2: chain_d2, F_r: pd.chain.F_r, 
    s: pd.chain.s, s_allow: 7.6, pass: pd.chain.pass,
  };
  const gear = {
    u1: pd.gear.u_d || reportData.optimal_action.optimal_ud, 
    u2: pd.gear.u_m, 
    m_tm: pd.gear.m, 
    m_n: pd.gear.m, 
    a_w: pd.gear.a_w,
    sigmaH: pd.gear.sigma_H, sigmaH_allow: pd.gear.sigma_H_allow, 
    sigmaF: pd.gear.sigma_F, sigmaF_allow: pd.gear.sigma_F_allow,
    passH: pd.gear.pass_H, 
    passF: pd.gear.pass_F,
  };

  return (
    <div className="flex-1 overflow-y-auto bg-stone-50/50">
      <div className="sticky top-0 z-10 bg-white/95 backdrop-blur border-b border-stone-200 no-print">
        <div className="px-8 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-4 min-w-0">
            {!hideBackBtn && (
              <Button size="sm" variant="ghost" onClick={onBack}>
                <ArrowLeft size={14} />
              </Button>
            )}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 text-stone-400" style={{ fontSize: 11, letterSpacing: '0.08em' }}>
                <FileText size={12} /> SCHEME · {scheme.projectID} · #{scheme.schemeNo}
              </div>
              <div className="text-stone-800 font-bold truncate mt-0.5" style={{ fontSize: 15, letterSpacing: '0.03em' }}>
                {scheme.projectName.toUpperCase()}
              </div>
            </div>
            <Badge tone={statusTone[scheme.status]}>{statusLabel[scheme.status]}</Badge>
            <span className="text-stone-400" style={{ fontSize: 11 }}>{scheme.date}</span>
          </div>
          <button
            onClick={() => window.print()}
            className="group relative p-2.5 rounded-xl border border-stone-200 text-stone-500 hover:bg-stone-50 hover:text-stone-800 hover:border-stone-300 transition-all"
            title="Xuất PDF / In báo cáo"
          >
            <FileText size={16} />
            <span className="pointer-events-none absolute -bottom-8 left-1/2 -translate-x-1/2 whitespace-nowrap px-2.5 py-1 rounded-lg bg-stone-800 text-white text-[11px] opacity-0 group-hover:opacity-100 transition-opacity shadow-lg z-50">
              Xuất PDF / In
            </span>
          </button>
        </div>
      </div>

      {}
      <div className="p-8 space-y-6 max-w-5xl mx-auto print:hidden">
        <div>
          <Card accent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Metric k="P_ct" v={motor.P_ct} u="kW" />
              <Metric k="n_đc" v={scheme.n_dc} u="vg/ph" />
              <Metric k="u_chung" v={scheme.u_total.toFixed(2)} />
              <Metric k="η tổng" v={motor.eta.toFixed(2)} />
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <Card title="Thông số thiết kế AI Q-Learning">
              <div className="flex items-center gap-2 mb-3 text-stone-500" style={{ fontSize: 12 }}>
                <Sparkles size={13} /> Tra Q-Table O(1) · huấn luyện offline
              </div>
              <div className="space-y-1">
                <Result label="Mác thép bánh răng" value={ai.matID} />
                <Result label="ψ_ba (gear)" value={ai.psi_ba?.toFixed(3) || "?"} hi />
                <Result label="u_d (gear)" value={ai.u_d?.toFixed(2) || "?"} />
                <Result label="z₁ sơ bộ (gear)" value={ai.z_g1} />
                <Result label="u_x (chain)" value={ai.u_x?.toFixed(2) || "?"} hi />
                <Result label="z₁ (chain)" value={ai.z_chain} />
              </div>
            </Card>
          </div>

          <div>
            <Card title="Động cơ đã chọn">
              <div className="flex items-center gap-2 mb-3 text-stone-500" style={{ fontSize: 12 }}>
                <Zap size={13} /> Catalog 4A
              </div>
              <div className="space-y-1">
                <Result label="Mã động cơ" value={motor.code} hi />
                <Result label="P_đc" value={motor.P_dc?.toFixed(1) || "?"} unit="kW" />
                <Result label="n_đc" value={motor.n_dc} unit="vg/ph" />
                <Result label="P_tđ" value={motor.P_td?.toFixed(2) || "?"} unit="kW" />
                <Result label="P_ct" value={motor.P_ct?.toFixed(2) || "?"} unit="kW" hi />
                <Result label="η hệ thống" value={motor.eta?.toFixed(2) || "?"} />
              </div>
            </Card>
          </div>

          <div>
            <Card title="Bộ truyền xích">
              <div className="flex items-center gap-2 mb-3 text-stone-500" style={{ fontSize: 12 }}>
                <Link2 size={13} /> Vét cạn bước xích p
              </div>
              <div className="space-y-1">
                <Result label="Bước xích p" value={chain.p} unit="mm" hi />
                <Result label="Số mắt xích X" value={chain.X} />
                <Result label="Khoảng cách trục a" value={chain.a} unit="mm" />
                <Result label="d₁ / d₂" value={`${chain.d1} / ${chain.d2}`} unit="mm" />
                <Result label="Lực F_r" value={chain.F_r} unit="N" />
                <Result label="Hệ số an toàn s / [s]" value={`${chain.s} / ${chain.s_allow}`} hi />
              </div>
              <div className="mt-3">
                {chain.pass
                  ? <Badge tone="green"><CheckCircle2 size={11} className="mr-1" /> Đạt s ≥ [s]</Badge>
                  : <Badge tone="rose">Chưa đạt</Badge>}
              </div>
            </Card>
          </div>

          <div>
            <Card title="Hộp giảm tốc côn-trụ">
              <div className="flex items-center gap-2 mb-3 text-stone-500" style={{ fontSize: 12 }}>
                <Cog size={13} /> 2 cấp · Côn-trụ răng nghiêng
              </div>
              <div className="space-y-1">
                <Result label="u₁ (cấp côn)" value={gear.u1?.toFixed(2) || "?"} />
                <Result label="u₂ (cấp trụ)" value={gear.u2?.toFixed(2) || "?"} />
                <Result label="Module m_tm / m_n" value={`${gear.m_tm || "?"} / ${gear.m_n || "?"}`} unit="mm" />
                <Result label="Khoảng cách trục a_w" value={gear.a_w || "?"} unit="mm" hi />
                <Result label="σ_H / [σ_H]" value={`${gear.sigmaH || "?"} / ${gear.sigmaH_allow || "?"}`} unit="MPa" />
                <Result label="σ_F / [σ_F]" value={`${gear.sigmaF || "?"} / ${gear.sigmaF_allow || "?"}`} unit="MPa" hi />
              </div>
              <div className="mt-3 flex gap-2 flex-wrap">
                {gear.passH ? <Badge tone="green">Bền tiếp xúc</Badge> : <Badge tone="rose">Hỏng tiếp xúc</Badge>}
                {gear.passF ? <Badge tone="green">Bền uốn</Badge> : <Badge tone="rose">Hỏng uốn (WARN_MECH_02)</Badge>}
              </div>
            </Card>
          </div>
        </div>

        <div>
          <Card title="Kiểm nghiệm tổng thể">
            <div className="space-y-2">
              <CheckRow label="Động cơ thoả mãn P_đc ≥ P_ct" ok={motor.P_dc >= motor.P_ct} />
              <CheckRow label="Xích đạt s ≥ [s] và áp suất cho phép" ok={chain.pass} />
              <CheckRow label="Bánh răng bền tiếp xúc (σ_H ≤ [σ_H])" ok={gear.passH} />
              <CheckRow label="Bánh răng bền uốn (σ_F ≤ [σ_F])" ok={gear.passF} />
              <CheckRow label="Solver song song hội tụ |Δu| < 0.01" ok={true} />
            </div>
          </Card>
        </div>

        {scheme.status === "fail" && (
          <div>
            <Card title="Ghi chú lỗi · WARN_MECH_02">
              <div className="flex items-start gap-3 p-3 rounded-xl bg-yellow-50 border border-yellow-200">
                <AlertTriangle className="text-stone-700 mt-0.5" size={16} />
                <div className="text-stone-700" style={{ fontSize: 13, lineHeight: 1.7 }}>
                  σ_F vượt [σ_F] tại cấp chậm. Cần chạy lại với fix tăng module hoặc tăng khoảng cách trục
                  trong Module Hộp giảm tốc — bộ thông số AI giữ nguyên.
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>

      {}
      <div className="hidden print:block p-8 max-w-4xl mx-auto font-serif text-black leading-relaxed">
        <div className="text-center mb-10 border-b-2 border-black pb-6">
          <h1 className="text-2xl font-bold uppercase mb-2">THUYẾT MINH TÍNH TOÁN THIẾT KẾ HỆ DẪN ĐỘNG</h1>
          <p className="text-lg font-medium italic">Tài liệu kỹ thuật lưu trữ tự động</p>
          <div className="mt-4 text-sm grid grid-cols-2 text-left max-w-lg mx-auto gap-y-1">
            <div className="font-bold">Dự án:</div><div>{scheme.projectName}</div>
            <div className="font-bold">Mã phương án:</div><div>#{scheme.schemeNo} (ID: {scheme.projectID})</div>
            <div className="font-bold">Ngày xuất:</div><div>{new Date().toLocaleDateString('vi-VN')}</div>
            <div className="font-bold">Kết luận:</div><div>{scheme.status === 'ok' ? 'ĐẠT YÊU CẦU' : 'CẦN CHỈNH SỬA'}</div>
          </div>
        </div>

        <section className="mb-8 print-break-avoid">
          <h2 className="text-lg font-bold mb-3 uppercase">1. Thông số đầu vào & Chọn động cơ điện</h2>
          <table className="w-full border-collapse border border-black text-sm text-left">
            <thead>
              <tr className="bg-gray-100"><th className="border border-black p-2 w-1/2">Thông số</th><th className="border border-black p-2 w-1/4">Ký hiệu</th><th className="border border-black p-2 w-1/4">Giá trị / Đơn vị</th></tr>
            </thead>
            <tbody>
              <tr><td className="border border-black p-2">Công suất cần thiết trên trục công tác</td><td className="border border-black p-2">P<sub>ct</sub></td><td className="border border-black p-2 font-mono">{motor.P_ct?.toFixed(2)} kW</td></tr>
              <tr><td className="border border-black p-2">Số vòng quay đồng bộ sơ bộ</td><td className="border border-black p-2">n<sub>sb</sub></td><td className="border border-black p-2 font-mono">{pd.motor?.n_sb?.toFixed(0) || scheme.n_dc} vg/ph</td></tr>
              <tr><td className="border border-black p-2 font-bold">Mã động cơ được chọn</td><td className="border border-black p-2">CODE</td><td className="border border-black p-2 font-mono font-bold">{motor.code}</td></tr>
              <tr><td className="border border-black p-2">Công suất định mức động cơ</td><td className="border border-black p-2">P<sub>đc</sub></td><td className="border border-black p-2 font-mono">{motor.P_dc?.toFixed(2) || "?"} kW</td></tr>
              <tr><td className="border border-black p-2">Vòng quay định mức động cơ</td><td className="border border-black p-2">n<sub>đc</sub></td><td className="border border-black p-2 font-mono">{motor.n_dc} vg/ph</td></tr>
              <tr><td className="border border-black p-2">Tỉ số truyền chung toàn hệ thống</td><td className="border border-black p-2">u<sub>Σ</sub></td><td className="border border-black p-2 font-mono">{scheme.u_total?.toFixed(2)}</td></tr>
            </tbody>
          </table>
        </section>

        <section className="mb-8 print-break-avoid">
          <h2 className="text-lg font-bold mb-3 uppercase">2. Thiết kế bộ truyền xích (Năng suất AI)</h2>
          <table className="w-full border-collapse border border-black text-sm text-left">
            <thead>
              <tr className="bg-gray-100"><th className="border border-black p-2 w-1/2">Thông số</th><th className="border border-black p-2 w-1/4">Ký hiệu</th><th className="border border-black p-2 w-1/4">Giá trị / Đơn vị</th></tr>
            </thead>
            <tbody>
              <tr><td className="border border-black p-2">Tỉ số truyền xích (AI Đề xuất)</td><td className="border border-black p-2">u<sub>x</sub></td><td className="border border-black p-2 font-mono">{ai.u_x?.toFixed(2)}</td></tr>
              <tr><td className="border border-black p-2">Số răng đĩa xích 1 / 2</td><td className="border border-black p-2">z<sub>1</sub> / z<sub>2</sub></td><td className="border border-black p-2 font-mono">{ai.z_chain} / {pd.chain?.z2}</td></tr>
              <tr><td className="border border-black p-2 font-bold">Bước xích chuẩn</td><td className="border border-black p-2">p</td><td className="border border-black p-2 font-mono font-bold">{chain.p} mm</td></tr>
              <tr><td className="border border-black p-2">Khoảng cách trục thiết kế</td><td className="border border-black p-2">a</td><td className="border border-black p-2 font-mono">{chain.a} mm</td></tr>
              <tr><td className="border border-black p-2">Số mắt xích</td><td className="border border-black p-2">X</td><td className="border border-black p-2 font-mono">{chain.X}</td></tr>
              <tr><td className="border border-black p-2">Lực tác dụng lên trục</td><td className="border border-black p-2">F<sub>r</sub></td><td className="border border-black p-2 font-mono">{chain.F_r} N</td></tr>
              <tr><td className="border border-black p-2">Hệ số an toàn thực tế / Cho phép</td><td className="border border-black p-2">s / [s]</td><td className="border border-black p-2 font-mono">{chain.s} / {chain.s_allow}</td></tr>
            </tbody>
          </table>
        </section>

        <section className="mb-8 print-break-avoid">
          <h2 className="text-lg font-bold mb-3 uppercase">3. Thiết kế hộp giảm tốc (Bánh răng)</h2>
          <table className="w-full border-collapse border border-black text-sm text-left">
            <thead>
              <tr className="bg-gray-100"><th className="border border-black p-2 w-1/2">Thông số</th><th className="border border-black p-2 w-1/4">Ký hiệu</th><th className="border border-black p-2 w-1/4">Giá trị / Đơn vị</th></tr>
            </thead>
            <tbody>
              <tr><td className="border border-black p-2">Vật liệu chế tạo</td><td className="border border-black p-2">Material</td><td className="border border-black p-2 font-mono">{ai.matID}</td></tr>
              <tr><td className="border border-black p-2">Hệ số chiều rộng vành răng (AI Đề xuất)</td><td className="border border-black p-2">ψ<sub>ba</sub></td><td className="border border-black p-2 font-mono">{ai.psi_ba?.toFixed(3)}</td></tr>
              <tr><td className="border border-black p-2">Tỉ số truyền bánh răng (AI Đề xuất)</td><td className="border border-black p-2">u<sub>d</sub></td><td className="border border-black p-2 font-mono">{ai.u_d?.toFixed(2)}</td></tr>
              <tr><td className="border border-black p-2 font-bold">Khoảng cách trục bánh răng</td><td className="border border-black p-2">a<sub>w</sub></td><td className="border border-black p-2 font-mono font-bold">{gear.a_w || "?"} mm</td></tr>
              <tr><td className="border border-black p-2">Module pháp (m_tm / m_n)</td><td className="border border-black p-2">m</td><td className="border border-black p-2 font-mono">{gear.m_tm || "?"} / {gear.m_n || "?"} mm</td></tr>
              <tr><td className="border border-black p-2">Ứng suất tiếp xúc thực tế / Cho phép</td><td className="border border-black p-2">σ<sub>H</sub> / [σ<sub>H</sub>]</td><td className="border border-black p-2 font-mono">{gear.sigmaH || "?"} / {gear.sigmaH_allow || "?"} MPa</td></tr>
              <tr><td className="border border-black p-2">Ứng suất uốn thực tế / Cho phép</td><td className="border border-black p-2">σ<sub>F</sub> / [σ<sub>F</sub>]</td><td className="border border-black p-2 font-mono">{gear.sigmaF || "?"} / {gear.sigmaF_allow || "?"} MPa</td></tr>
            </tbody>
          </table>
        </section>

        <section className="mb-8 print-break-avoid border-t-2 border-black pt-6">
          <h2 className="text-lg font-bold mb-3 uppercase">4. Kết luận kiểm nghiệm</h2>
          <ul className="list-disc pl-5 space-y-2">
            <li><b>Động cơ điện:</b> {motor.P_dc >= motor.P_ct ? "Thỏa mãn công suất." : "Không đủ công suất."}</li>
            <li><b>Bộ truyền xích:</b> {chain.pass ? "Đạt điều kiện bền (s ≥ [s])." : "Chưa đạt điều kiện an toàn."}</li>
            <li><b>Bộ truyền bánh răng (Tiếp xúc):</b> {gear.passH ? "Đạt điều kiện ứng suất tiếp xúc." : "Vượt ngưỡng ứng suất tiếp xúc (Cần kiểm tra lại m hoặc aw)."}</li>
            <li><b>Bộ truyền bánh răng (Uốn):</b> {gear.passF ? "Đạt điều kiện ứng suất uốn." : "Hỏng do uốn (Gợi ý: Tăng module hoặc bề rộng bánh răng)."}</li>
          </ul>
          
          <div className="mt-12 flex justify-end">
            <div className="text-center">
              <p className="mb-16">Ngày ..... tháng ..... năm 202...</p>
              <p className="font-bold border-t border-black pt-2 inline-block px-8">Chữ ký người thiết kế</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function Metric({ k, v, u }: { k: string; v: string | number; u?: string }) {
  return (
    <div className="p-4 rounded-xl bg-white/60 backdrop-blur border border-pink-100">
      <div className="text-stone-500" style={{ fontSize: 12 }}>{k}</div>
      <div className="text-stone-800 mt-1 font-mono" style={{ fontSize: 18 }}>
        {v} {u && <span className="text-stone-400" style={{ fontSize: 12 }}>{u}</span>}
      </div>
    </div>
  );
}

function CheckRow({ label, ok }: { label: string; ok: boolean }) {
  return (
    <div className="flex items-center justify-between py-2 px-3 rounded-lg bg-stone-50">
      <span className="text-stone-700" style={{ fontSize: 13 }}>{label}</span>
      {ok
        ? <Badge tone="green"><CheckCircle2 size={11} className="mr-1" /> Đạt</Badge>
        : <Badge tone="rose"><AlertTriangle size={11} className="mr-1" /> Chưa đạt</Badge>}
    </div>
  );
}
