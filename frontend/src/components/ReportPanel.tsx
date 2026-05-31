import { useState, useEffect } from "react";
import { Header } from "./Header";
import { Button } from "./ui-bits";
import { FileText, Download, Share2, Sparkles, AlertCircle, Lollipop, ArrowRight } from "lucide-react";
import { createClient } from "@/utils/supabase/client";
import { SchemeReport, SchemeDetail } from "./SchemeReport";
import { ModuleKey } from "./Sidebar";

export function ReportPanel({ user, currentScheme, onGoto }: { user?: any, currentScheme?: any, onGoto?: (k: ModuleKey) => void }) {
  const [latestScheme, setLatestScheme] = useState<SchemeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const supabase = createClient();

  useEffect(() => {
    async function fetchLatest() {
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

      if (projects && projects.length > 0) {
        let allSchemes: SchemeDetail[] = [];
        projects.forEach((p: any) => {
          if (p.DESIGN_SCHEME) {
            p.DESIGN_SCHEME.forEach((s: any) => {
              allSchemes.push({
                projectID: p.projectID.toString(),
                projectName: p.projectName,
                schemeNo: s.schemeNo,
                date: new Date(s.date).toLocaleString("vi-VN"),
                status: s.status === "SUCCESS" ? "ok" : s.status === "FAILED" ? "fail" : "draft",
                P_dc: parseFloat(s.P_dc),
                n_dc: parseFloat(s.n_dc),
                u_total: parseFloat(s.u_total),
                motorCode: s.motorCode,
              });
            });
          }
        });
        
        if (allSchemes.length > 0) {
          allSchemes.sort((a, b) => {
            if (a.projectID !== b.projectID) return parseInt(b.projectID) - parseInt(a.projectID);
            return b.schemeNo - a.schemeNo;
          });
          
          let target = allSchemes.find(s => s.status !== "draft");
          if (currentScheme) {
            const exact = allSchemes.find(s => parseInt(s.projectID) === currentScheme.projectID && s.schemeNo === currentScheme.schemeNo);
            if (exact) target = exact;
          }
          
          if (target) setLatestScheme(target);
          else setLatestScheme(allSchemes[0]);
        }
      }
      setLoading(false);
    }
    
    fetchLatest();
  }, [user, currentScheme]);

  if (loading) {
    return (
      <div className="flex-1 overflow-y-auto flex items-center justify-center bg-stone-50/30">
        <div className="text-stone-400 flex flex-col items-center gap-3">
          <Lollipop className="animate-spin text-pink-400" size={24} />
          <span>Đang tìm báo cáo mới nhất...</span>
        </div>
      </div>
    );
  }

  if (!latestScheme) {
    return (
      <div className="flex-1 overflow-y-auto bg-stone-50/30">
        <Header title="Xuất Báo Cáo Thuyết Minh" desc="Trình bày tự động theo chuẩn đồ án môn học chi tiết máy" />
        <div className="p-10 flex flex-col items-center justify-center text-center mt-20">
          <div className="w-20 h-20 bg-stone-100 rounded-full flex items-center justify-center mb-4">
            <span className="text-3xl">📄</span>
          </div>
          <h2 className="text-lg font-medium text-stone-800 mb-2">Chưa có phương án nào</h2>
          <p className="text-stone-500 text-sm max-w-sm mb-6">Bạn cần tạo một dự án và thực hiện tính toán (chạy AI) trước khi có thể xem và xuất báo cáo PDF.</p>
          <Button onClick={() => onGoto && onGoto("projects")}>
            Đến tab Dự án <ArrowRight size={14} className="ml-2" />
          </Button>
        </div>
      </div>
    );
  }

  return <SchemeReport scheme={latestScheme} onBack={() => {}} hideBackBtn />;
}
