import { useState } from "react";
import { Mail, Lock, User, ArrowRight, AlertCircle } from "lucide-react";
import { GearLogo } from "./GearLogo";
import { createClient } from "@/utils/supabase/client";

export function AuthScreen({ onAuth }: { onAuth: (user: { id: string; name: string; email: string }) => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("vkee@hcmut.edu.vn");
  const [password, setPassword] = useState("vkee123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const supabase = createClient();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (mode === "register") {
        const { data: existing } = await supabase.from("USER_ACCOUNT").select("userID").eq("email", email).single();
        if (existing) {
          throw new Error("Email này đã được sử dụng. Vui lòng đăng nhập.");
        }

        const { error: signUpError } = await supabase.from("USER_ACCOUNT").insert({
          userName: name || "Sinh viên",
          email: email,
          password: password,
        });

        if (signUpError) throw signUpError;
        alert("Đăng ký thành công! Bạn có thể đăng nhập ngay.");
        setMode("login");
      } else {
        const { data: userRow, error: signInError } = await supabase
          .from("USER_ACCOUNT")
          .select("*")
          .eq("email", email)
          .eq("password", password)
          .single();

        if (signInError || !userRow) {
          throw new Error("Email hoặc mật khẩu không đúng.");
        }

        onAuth({ id: userRow.userID.toString(), name: userRow.userName, email: userRow.email });
      }
    } catch (err: any) {
      setError(err.message || "Đã có lỗi xảy ra");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-full grid grid-cols-1 lg:grid-cols-2 bg-white">
      {}
      <div className="relative hidden lg:flex flex-col justify-between p-12 overflow-hidden sticky top-0 h-screen">
        <video
          className="absolute inset-0 w-full h-full object-cover"
          autoPlay
          loop
          muted
          playsInline
          src="https://assets.mixkit.co/videos/preview/mixkit-engine-pistons-of-an-old-car-2459-large.mp4"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-yellow-200/30 via-pink-200/20 to-pink-300/30 mix-blend-screen" />
        <div className="absolute inset-0 bg-white/20" />
        <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-white/20 blur-3xl" />
        <div className="absolute -bottom-32 -right-20 w-[28rem] h-[28rem] rounded-full bg-yellow-200/25 blur-3xl" />

        <div className="relative flex items-center gap-3">
          <div className="w-14 h-14 flex items-center justify-center rounded-2xl bg-white/70 backdrop-blur shadow-md">
            <GearLogo size={28} />
          </div>
          <div>
            <div className="text-stone-900 font-serif" style={{ fontSize: 20 }}>MechDrive Studio</div>
            <div className="text-stone-800/70" style={{ fontSize: 12, letterSpacing: '0.1em' }}>HCMUT</div>
          </div>
        </div>

        <div className="relative">
          <h1 className="font-serif text-stone-900" style={{ fontSize: 32, lineHeight: 1.2, letterSpacing: '0.04em' }}>
            <b> Thiết kế hệ dẫn động</b>
          </h1>
          <p className="text-stone-600 mt-4 max-w-sm" style={{ fontSize: 13, lineHeight: 1.7 }}>
            Nền tảng tính toán và thiết kế hệ dẫn động cơ khí, hỗ trợ tối ưu hóa thông số bằng thuật toán AI.
          </p>

        </div>

        <div className="relative text-stone-600" style={{ fontSize: 12, letterSpacing: '0.08em' }}>
          MECHDRIVE STUDIO · HCMUT
        </div>
      </div>

      {}
      <div className="flex items-center justify-center p-6 lg:p-12">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="w-12 h-12 flex items-center justify-center rounded-xl bg-gradient-to-br from-yellow-200/50 to-pink-200/50 shadow-sm border border-pink-100">
              <GearLogo size={24} />
            </div>
            <div className="text-stone-900 font-serif" style={{ fontSize: 18 }}>MechDrive Studio</div>
          </div>

          <div className="inline-flex rounded-xl bg-white/70 backdrop-blur border border-pink-100 p-1 mb-6">
            {(["login", "register"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`px-4 py-1.5 rounded-lg transition ${mode === m ? "bg-gradient-to-r from-yellow-200 to-pink-200 text-stone-800" : "text-stone-500 hover:text-stone-700"
                  }`}
              >
                {m === "login" ? "Đăng nhập" : "Đăng ký"}
              </button>
            ))}
          </div>

          <h2 className="font-serif text-stone-900" style={{ fontSize: 24 }}>
            {mode === "login" ? "Chào mừng trở lại" : "Tạo tài khoản mới"}
          </h2>
          <p className="text-stone-500 mt-2" style={{ fontSize: 13 }}>
            {mode === "login"
              ? "Đăng nhập để tiếp tục"
              : ""}
          </p>

          <form onSubmit={submit} className="mt-6 space-y-4">
            {mode === "register" && (
              <div>
                <label className="text-stone-700 block mb-1.5">Họ và tên</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" size={16} />
                  <input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Nguyễn Văn A"
                    className="w-full pl-10 pr-3 py-3 rounded-xl bg-white border border-pink-100 focus:border-pink-300 focus:ring-2 focus:ring-pink-100 outline-none"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="text-stone-700 block mb-1.5">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" size={16} />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-3 py-3 rounded-xl bg-white border border-pink-100 focus:border-pink-300 focus:ring-2 focus:ring-pink-100 outline-none"
                />
              </div>
            </div>

            <div>
              <label className="text-stone-700 block mb-1.5">Mật khẩu</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" size={16} />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-3 py-3 rounded-xl bg-white border border-pink-100 focus:border-pink-300 focus:ring-2 focus:ring-pink-100 outline-none"
                />
              </div>
            </div>

            {mode === "login" && (
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-stone-600">
                  <input type="checkbox" className="accent-stone-600" defaultChecked /> Ghi nhớ
                </label>
                <button type="button" className="text-stone-700 hover:underline">Quên mật khẩu?</button>
              </div>
            )}

            {error && (
              <div className="flex items-center gap-2 p-3 rounded-xl bg-pink-50 text-pink-700 text-sm">
                <AlertCircle size={16} />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className={`w-full px-5 py-3 rounded-xl bg-gradient-to-r from-yellow-200 to-pink-300 text-stone-800 shadow-md flex items-center justify-center gap-2 transition ${loading ? "opacity-70 cursor-not-allowed" : "hover:shadow-lg"
                }`}
            >
              {loading ? "Đang xử lý..." : mode === "login" ? "Đăng nhập" : "Tạo tài khoản"}
              {!loading && <ArrowRight size={16} />}
            </button>

            <div className="flex items-center gap-3 text-stone-400">
              <div className="flex-1 h-px bg-pink-100" />
              <span style={{ fontSize: 12 }}>hoặc</span>
              <div className="flex-1 h-px bg-pink-100" />
            </div>

            <button
              type="button"
              onClick={() => onAuth({ id: "0", name: "Khách", email: "guest@demo" })}
              className="w-full px-5 py-3 rounded-xl bg-white border border-stone-200 text-stone-700 hover:bg-stone-50"
            >
              Vào nhanh chế độ demo
            </button>
          </form>

          <p className="text-stone-400 mt-8 text-center" style={{ fontSize: 11, letterSpacing: '0.08em' }}>
            © 2026 MECHDRIVE
          </p>
        </div>
      </div>
    </div>
  );
}
