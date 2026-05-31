import { useState, useEffect } from "react";
import { Header } from "./Header";
import { Card, Badge, Button, Field } from "./ui-bits";
import { Plus, FolderOpen, Trash2, ChevronRight, Pencil, X, ArrowUpRight, AlertCircle } from "lucide-react";
import { SchemeReport, SchemeDetail } from "./SchemeReport";
import { ProjectWorkspace, Project, Scheme } from "./ProjectWorkspace";
import { createClient } from "@/utils/supabase/client";

const statusTone = { draft: "stone", ok: "green", fail: "rose" } as const;
const statusLabel = { draft: "Nháp", ok: "Đạt", fail: "Chưa đạt" } as const;

export function ModuleProjects({ onGoto, user, onSetScheme }: { onGoto?: (k: any) => void; user?: any; onSetScheme?: (s: {projectID: number; schemeNo: number} | null) => void }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [creating, setCreating] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDesc, setEditDesc] = useState("");
  const [openProjectId, setOpenProjectId] = useState<string | null>(null);
  const [viewing, setViewing] = useState<SchemeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const supabase = createClient();

  useEffect(() => {
    if (!user?.id) return;
    const fetchProjects = async () => {
      setLoading(true);
      const { data, error } = await supabase
        .from("PROJECT")
        .select(`
          *,
          DESIGN_SCHEME (*)
        `)
        .eq("userID", user.id)
        .order("createdDate", { ascending: false });

      if (error) {
        setError("Lỗi tải dự án: " + error.message);
      } else if (data) {
        setProjects(
          data.map((row) => ({
            projectID: row.projectID,
            projectName: row.projectName,
            projectDescription: row.projectDescription || "",
            createdDate: row.createdDate.slice(0, 10),
            schemes: row.DESIGN_SCHEME ? row.DESIGN_SCHEME.map((s: any) => ({
              schemeNo: s.schemeNo,
              date: s.date,
              status: s.status === "PENDING" ? "draft" : s.status === "SUCCESS" ? "ok" : "fail",
              P_dc: parseFloat(s.P_dc),
              n_dc: parseFloat(s.n_dc),
              u_total: parseFloat(s.u_total),
              L_h: s.L_h,
              shiftNum: s.shiftNum,
              load_type: s.load_type,
              motorCode: s.motorCode,
            })) : [], 
          }))
        );
      }
      setLoading(false);
    };
    fetchProjects();
  }, [user]);

  const create = async () => {
    if (!editName.trim() || !user?.id) return;
    setError("");

    const { data, error } = await supabase
      .from("PROJECT")
      .insert({
        userID: user.id,
        projectName: editName.trim(),
        projectDescription: editDesc.trim(),
      })
      .select()
      .single();

    if (error) {
      setError("Lỗi tạo dự án: " + error.message);
      return;
    }

    if (data) {
      const p: Project = {
        projectID: data.projectID,
        projectName: data.projectName,
        projectDescription: data.projectDescription || "",
        createdDate: data.createdDate.slice(0, 10),
        schemes: [],
      };
      setProjects([p, ...projects]);
      setEditName("");
      setEditDesc("");
      setCreating(false);
      setOpenProjectId(p.projectID);
    }
  };

  const remove = async (id: string) => {
    const { error } = await supabase.from("PROJECT").delete().eq("projectID", id);
    if (error) {
      setError("Lỗi xoá dự án: " + error.message);
    } else {
      setProjects(projects.filter((p) => p.projectID !== id));
    }
  };

  const addScheme = async (projectID: string, s: Scheme) => {
    const { error } = await supabase.from("DESIGN_SCHEME").insert({
      projectID: parseInt(projectID),
      schemeNo: s.schemeNo,
      operation_mode: "Liên tục",
      L_h: s.L_h,
      shiftNum: s.shiftNum,
      status: s.status === "draft" ? "PENDING" : s.status === "ok" ? "SUCCESS" : "FAILED",
      P_dc: s.P_dc,
      n_dc: s.n_dc,
      u_total: s.u_total,
      load_type: s.load_type === "tinh" ? "Tĩnh" : s.load_type === "va_nhe" ? "Va đập nhẹ" : "Va đập mạnh",
    });

    if (error) {
      console.error("Lỗi khi tạo Scheme:", error);
      let errMsg = error.message;
      if (typeof error === "object") errMsg = JSON.stringify(error);
      alert("Lỗi khi tạo Scheme: " + errMsg);
      return;
    }

    setProjects((prev) =>
      prev.map((p) =>
        p.projectID === projectID ? { ...p, schemes: [...p.schemes, s] } : p
      )
    );
  };

  if (viewing) {
    return <SchemeReport scheme={viewing} onBack={() => setViewing(null)} />;
  }

  if (openProjectId) {
    const p = projects.find((x) => x.projectID === openProjectId);
    if (p) {
      return (
        <ProjectWorkspace
          project={p}
          onBack={() => setOpenProjectId(null)}
          onAddScheme={(s) => addScheme(p.projectID, s)}
          onOpenScheme={(s) =>
            setViewing({
              projectID: p.projectID,
              projectName: p.projectName,
              schemeNo: s.schemeNo,
              date: s.date,
              status: s.status,
              P_dc: s.P_dc,
              n_dc: s.n_dc,
              u_total: s.u_total,
              motorCode: s.motorCode,
            })
          }
          onRunPipeline={(s) => {
            if (onSetScheme) onSetScheme({ projectID: parseInt(p.projectID), schemeNo: s.schemeNo });
            if (onGoto) onGoto("optimizer");
          }}
        />
      );
    }
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <Header
        title="Quản lý dự án"
        desc="Bấm vào một dự án để nhập số liệu và tạo Design Scheme mới"
        stepKey="projects"
        onGoto={onGoto}
        onRun={() => {  }}
      />

      <div className="p-8 space-y-6">
        <Card
          title={`Danh sách dự án · ${projects.length}`}
          action={
            !creating ? (
              <Button size="sm" onClick={() => setCreating(true)}>
                <Plus size={14} /> Dự án mới
              </Button>
            ) : null
          }
        >
          {creating && (
            <div className="mb-4 p-4 rounded-xl border border-pink-200 bg-gradient-to-br from-yellow-50 to-pink-50">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <Field label="Tên dự án" type="text" value={editName} onChange={setEditName} placeholder="VD: Thùng trộn 3 kW" />
                <Field label="Mô tả" type="text" value={editDesc} onChange={setEditDesc} placeholder="Ngắn gọn 1 dòng" />
              </div>
              <div className="mt-3 flex items-center justify-end gap-2">
                <Button size="sm" variant="ghost" onClick={() => { setCreating(false); setEditName(""); setEditDesc(""); }}>
                  <X size={14} /> Huỷ
                </Button>
                <Button size="sm" onClick={create}>Tạo</Button>
              </div>
            </div>
          )}

          {error && (
            <div className="mb-4 flex items-center gap-2 p-3 rounded-xl bg-pink-50 text-pink-700 text-sm">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          {loading ? (
            <div className="py-10 text-center text-stone-400" style={{ fontSize: 13 }}>
              Đang tải dự án từ máy chủ...
            </div>
          ) : projects.length === 0 ? (
            <div className="py-10 text-center text-stone-400" style={{ fontSize: 13 }}>
              Chưa có dự án nào. Bấm "Dự án mới" để bắt đầu.
            </div>
          ) : (
            <div className="space-y-2">
              {projects.map((p) => (
                <div
                  key={p.projectID}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl border border-stone-200 hover:bg-gradient-to-r hover:from-yellow-50 hover:to-pink-50 cursor-pointer transition-colors"
                  onClick={() => setOpenProjectId(p.projectID)}
                >
                  <FolderOpen size={15} className="text-stone-500 shrink-0" />
                  <div className="min-w-0 flex-1">
                    <div className="text-stone-800 truncate" style={{ fontSize: 14 }}>{p.projectName}</div>
                    <div className="text-stone-500 truncate" style={{ fontSize: 12 }}>{p.projectDescription}</div>
                  </div>
                  <Badge tone="stone">{p.schemes.length} scheme</Badge>
                  <span className="text-stone-400 hidden md:inline" style={{ fontSize: 12 }}>{p.createdDate}</span>
                  <button
                    onClick={(e) => { e.stopPropagation(); remove(p.projectID); }}
                    className="p-1.5 rounded-md text-stone-400 hover:bg-stone-100 hover:text-stone-600"
                    aria-label="Xoá"
                  >
                    <Trash2 size={13} />
                  </button>
                  <ChevronRight size={14} className="text-stone-400" />
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
