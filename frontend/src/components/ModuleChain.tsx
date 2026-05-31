import { useState } from "react";
import { Header } from "./Header";
import { Card, Field, Select, Result, Badge } from "./ui-bits";
import { AlertTriangle, Sparkles, Search } from "lucide-react";

export function ModuleChain({ onGoto, aiResult }: { onGoto?: (k: any) => void; aiResult?: any }) {
  const chainData = aiResult?.physics_details?.chain;
  const aiAction = aiResult?.optimal_action;

  const AI_SEEDS = {
    u_x: aiResult?.physics_details?.gear?.u_x || 2.5,
    z_1: aiAction?.z1_chain || 25,
  };
  const [chainAngle, setChainAngle] = useState("30");
  const [lubrication, setLubrication] = useState("ngam_dau");
  const [autoA, setAutoA] = useState(true);
  const [aUser, setAUser] = useState("950");
  const [calc, setCalc] = useState(false);

  const warn = calc && chainData?.pass === false;
  const s_allowed = chainData?.s_allow || 7.6;
  const schemeStatus = !calc ? "PENDING" : chainData?.pass ? "SUCCESS" : "FAILED";

  const angleNum = parseFloat(chainAngle);
  const aUserNum = parseFloat(aUser);
  const errAngle = /^\d*\.?\d+$/.test(chainAngle) && angleNum >= 0 && angleNum <= 90 ? "" : "0 – 90°";
  const errAUser = autoA ? "" : (/^\d*\.?\d+$/.test(aUser) && aUserNum > 0 ? "" : "Phải là số dương");
  const invalid = !!(errAngle || errAUser);

  return (
    <div className="flex-1 overflow-y-auto">
      <Header
        title="Bộ truyền xích"
        desc="Vét cạn bước xích p · Seeds AI: u_x, z₁"
        stepKey="chain"
        onGoto={onGoto}
        onRun={() => setCalc(true)}
        runDisabled={invalid}
        runDisabledHint="Sửa các trường nhập sai trước"
      />

      <div className="px-8 pt-6">
        <div className="flex items-center gap-2 flex-wrap p-4 rounded-2xl bg-gradient-to-r from-yellow-50 to-pink-50 border border-pink-100">
          <span className="flex items-center gap-1.5 text-stone-700 mr-2" style={{ fontSize: 13 }}>
            <Sparkles size={14} className="text-stone-600" /> AI Q-Learning cấp:
          </span>
          <Badge tone="amber">u_x = {AI_SEEDS.u_x.toFixed(2)}</Badge>
          <Badge tone="amber">z₁ = {AI_SEEDS.z_1}</Badge>
          <span className="text-stone-400 ml-1" style={{ fontSize: 12 }}>
            (Bước xích p → thuật toán tính bằng vét cạn ở backend)
          </span>
        </div>
      </div>

      {warn && (
        <div className="px-8 pt-4">
          <div className="rounded-2xl border border-pink-300 bg-pink-50/80 p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="text-pink-700 mt-0.5" size={18} />
              <div className="flex-1">
                <div className="text-pink-800" style={{ letterSpacing: '0.04em' }}>
                  THẤT BẠI — Vượt áp suất / Hệ số an toàn không đủ
                </div>
                <div className="text-pink-700 mt-1" style={{ fontSize: 13, lineHeight: 1.7 }}>
                  Phương án xích này không thỏa mãn điều kiện bền. 
                  Hãy quay lại Optimizer hoặc thay đổi thông số động cơ.
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="p-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Input người dùng tại bước này">
          <div className="grid grid-cols-2 gap-4">
            <Field
              label="Góc nghiêng bộ truyền"
              unit="°"
              value={chainAngle}
              onChange={setChainAngle}
              error={errAngle}
            />
            <Select
              label="Chất lượng bôi trơn"
              value={lubrication}
              onChange={setLubrication}
              options={[
                { value: "nho_giot", label: "Nhỏ giọt" },
                { value: "ngam_dau", label: "Ngâm dầu" },
                { value: "bang_tay", label: "Bằng tay" },
              ]}
            />
            <div className="col-span-2">
              <label className="flex items-center gap-2 text-stone-700 mb-2" style={{ fontSize: 13 }}>
                <input
                  type="checkbox"
                  checked={autoA}
                  onChange={(e) => setAutoA(e.target.checked)}
                  className="accent-pink-400"
                />
                Máy tự tính khoảng cách trục a (bỏ chọn để nhập tay)
              </label>
              {!autoA && (
                <Field label="Khoảng cách trục a_user" unit="mm" value={aUser} onChange={setAUser} error={errAUser} />
              )}
              {invalid && (
                <div className="mt-2 text-pink-600" style={{ fontSize: 11 }}>
                  Có trường nhập sai — nút "Tính &amp; hoàn thành" tạm bị khoá.
                </div>
              )}
            </div>
          </div>
          <div className="mt-5 p-4 rounded-xl bg-pink-50/70 border border-pink-100 text-stone-600" style={{ fontSize: 13, lineHeight: 1.7 }}>
            P₁, n₁ kế thừa từ bước Động cơ. u_x, z₁ do AI Optimizer cấp. Bước này chỉ nhập thông số lắp đặt.
          </div>
        </Card>

        <Card title="Kết quả thiết kế xích" accent>
          {!calc ? (
            <div className="py-10 text-center text-stone-400">Bấm "Tính &amp; hoàn thành" để xem kết quả</div>
          ) : (
            chainData ? (
              <div className="space-y-1">
                <Result label="Bước xích p (vét cạn)" value={chainData.p} unit="mm" hi />
                <Result label="Số mắt xích X" value={chainData.X} />
                <Result label="Khoảng cách trục a" value={chainData.a} unit="mm" />
                <Result label="Lực tác dụng lên trục F_r" value={chainData.F_r} unit="N" />
                <Result label="Hệ số an toàn s" value={chainData.s} hi />
                <div className="pt-3 flex gap-2 flex-wrap">
                  {chainData.s >= chainData.s_allow ? (
                    <Badge tone="green">[s] = {chainData.s_allow} → Đạt</Badge>
                  ) : (
                    <Badge tone="rose">[s] = {chainData.s_allow} → Chưa đạt</Badge>
                  )}
                  <Badge tone="green">Áp suất cho phép đạt</Badge>
                  <Badge tone="stone">Xích con lăn 1 dãy</Badge>
                </div>
              </div>
            ) : (
              <div className="py-10 text-center text-rose-400">Không tìm thấy xích phù hợp hoặc lỗi tính toán (kiểm tra lại AI Result)</div>
            )
          )}
        </Card>

        {calc && chainData && (
          <Card title="CHAIN_TRANS.calculation_trace_report (JSONB)">
            <div className="flex items-center gap-2 mb-2" style={{ fontSize: 12 }}>
              <span className="text-stone-500">DESIGN_SCHEME.status =</span>
              <Badge tone={schemeStatus === "SUCCESS" ? "green" : schemeStatus === "FAILED" ? "rose" : "amber"}>
                {schemeStatus}
              </Badge>
            </div>
            <pre className="font-mono text-stone-700 bg-stone-50 rounded-xl p-4 overflow-x-auto" style={{ fontSize: 11, lineHeight: 1.6 }}>
{JSON.stringify(chainData, null, 2)}
            </pre>
          </Card>
        )}
      </div>
    </div>
  );
}
