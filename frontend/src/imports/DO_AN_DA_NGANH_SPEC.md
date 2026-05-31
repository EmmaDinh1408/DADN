# ĐỒ ÁN ĐA NGÀNH: HỆ THỐNG WEB TỰ ĐỘNG HÓA TÍNH TOÁN THIẾT KẾ HỆ DẪN ĐỘNG THÙNG TRỘN
**Tài liệu đặc tả kỹ thuật toàn diện (Engineering Specification Document)**

---

## 1. TỔNG QUAN ĐỒ ÁN

### 1.1. Bối cảnh & Mục tiêu
- **Lĩnh vực:** Đồ án đa ngành kết hợp **Cơ Kỹ Thuật (CKT)** + **Web Development** + **AI Engineering**.
- **Đối tượng người dùng:** Sinh viên ngành Cơ Kỹ Thuật làm đồ án thiết kế Hệ Dẫn Động Cơ Khí.
- **Vấn đề hiện hữu:** Sinh viên phải tính toán thủ công theo sách *Trịnh Chất - Lê Văn Uyển* ("Tính toán thiết kế hệ dẫn động cơ khí" - Tập 1, 2), tra bảng bằng tay → tốn thời gian, dễ sai số, khó tối ưu.
- **Giải pháp:** Web application tự động hóa toàn bộ quy trình tính toán, tra bảng, kiểm bền, tối ưu hóa và xuất báo cáo thuyết minh.
- **Phạm vi của nhóm (nhóm 7, 8):** Hệ thống **TRUYỀN ĐỘNG XÍCH** (Chain Drive System).

### 1.2. Phạm vi 3 module cốt lõi
1. **Module 1 — Tính chọn Động cơ điện:** Xác định công suất, số vòng quay, chọn động cơ phù hợp từ database (3K/4A series).
2. **Module 2 — Tính toán bộ truyền Xích:** Xích ống con lăn / xích răng — chọn bước xích, số răng đĩa, kiểm tra bền, tuổi thọ.
3. **Module 3 — Tính toán Bánh răng Côn-Trụ:** Hộp giảm tốc bánh răng côn răng thẳng (cấp nhanh) + bánh răng trụ răng nghiêng (cấp chậm).
- **Ràng buộc nghiệp vụ quan trọng:** Module 2 và 3 **PHẢI chạy song song** ở Backend khi kiểm bền (tránh vòng lặp chết khi điều kiện bền của module này phụ thuộc kết quả module kia — phải fork/iterate đồng thời, hội tụ bằng worker pool).

### 1.3. Deadline & Mốc quan trọng
- **Trước Thứ Sáu 13/03/2026:** Nộp flowchart chi tiết cho giảng viên CKT.
- Hiện tại (2026-05-22): Frontend đã xong, cần Backend + AI + DB.

---

## 2. KIẾN TRÚC TỔNG THỂ

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (React + Vite + Tailwind v4 + React Router)       │
│  - 7 pages: Dashboard / Motor / Chain / Gear / Tables /     │
│             AI Tools / Reports                              │
└────────────────────┬────────────────────────────────────────┘
                     │  REST / WebSocket (long-running calc)
┌────────────────────▼────────────────────────────────────────┐
│  BACKEND (Python — FastAPI + Celery/asyncio workers)        │
│  - Calculation Engine (3 modules)                           │
│  - Parallel Solver (module 2 ⇄ 3 convergence loop)          │
│  - AI Orchestrator (4 sub-services)                         │
│  - Report Generator (LLM + LaTeX/DOCX)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│  SUPABASE (Postgres + Auth + Storage + Edge Functions)      │
│  - Lookup tables (motor, chain, bearing, key, tolerance)    │
│  - Intermediate variables (audit trail per session)         │
│  - User projects & report files                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. FRONTEND (ĐÃ HOÀN THÀNH)

### 3.1. Stack
- React 18 + TypeScript + Vite
- Tailwind CSS v4 (token-based theming)
- React Router (7 routes)
- shadcn/ui components, lucide-react icons, recharts
- **Typography:** `Inter` (text), `JetBrains Mono` (số liệu/code) — import qua `src/styles/fonts.css`.
- **Color tokens (`src/styles/theme.css`):**
  - Primary `#0066cc` (engineering blue)
  - Success `#00a86b`
  - Warning `#ff6b35`
  - Neutral grays cho background/border

### 3.2. 7 trang chính
| # | Route | Tên | Chức năng |
|---|-------|-----|-----------|
| 1 | `/` | Dashboard | KPI tổng quan project, tiến độ tính toán, shortcut |
| 2 | `/motor` | Module 1 — Động cơ | Input P_lv, n_lv, η → chọn động cơ |
| 3 | `/chain` | Module 2 — Xích | Tính bộ truyền xích, kiểm bền |
| 4 | `/gear` | Module 3 — Bánh răng | Hộp côn-trụ, kiểm bền tiếp xúc/uốn |
| 5 | `/tables` | Bảng tra | Xem/tìm kiếm bảng tra (động cơ, xích, ổ lăn, then, dung sai) |
| 6 | `/ai-tools` | Công cụ AI | NER/OCR upload, RF gợi ý, GA optimize |
| 7 | `/reports` | Báo cáo | Sinh thuyết minh PDF/DOCX, tải về |

### 3.3. UX patterns
- Sidebar navigation cố định trái.
- Mỗi module có 3 panel: **Input** (trái) — **Calculation Steps** (giữa, có thể expand từng bước) — **Result + Validation** (phải).
- Mọi giá trị số hiển thị bằng `font-mono` và có đơn vị SI rõ ràng.
- Trạng thái tính toán: `idle | running | converged | failed` (badge màu).

---

## 4. BACKEND — CHI TIẾT KỸ THUẬT

### 4.1. Stack đề xuất
- **Framework:** FastAPI (async-native, OpenAPI tự sinh).
- **Worker:** `asyncio` + `concurrent.futures.ProcessPoolExecutor` cho CPU-bound; **Celery + Redis** nếu chạy AI nặng.
- **Validation:** Pydantic v2.
- **Numerics:** NumPy, SciPy.
- **Test:** pytest + pytest-asyncio + hypothesis (property-based cho công thức cơ khí).

### 4.2. Cấu trúc module
```
backend/
├── app/
│   ├── api/                 # FastAPI routers
│   │   ├── motor.py
│   │   ├── chain.py
│   │   ├── gear.py
│   │   ├── ai.py
│   │   └── report.py
│   ├── core/
│   │   ├── solver.py        # Orchestrator song song M2 ⇄ M3
│   │   ├── convergence.py   # Hội tụ + chống vòng lặp chết
│   │   └── units.py         # SI unit handling
│   ├── modules/
│   │   ├── motor_select.py
│   │   ├── chain_design.py
│   │   └── gear_design.py   # bevel + helical
│   ├── ai/
│   │   ├── ner_ocr.py
│   │   ├── rf_suggest.py
│   │   ├── ga_optimize.py
│   │   └── llm_report.py
│   ├── db/                  # Supabase client + repositories
│   └── schemas/             # Pydantic models
└── tests/
```

### 4.3. Logic Module 1 — Tính chọn Động cơ
**Input:** F (lực kéo băng tải), v (vận tốc), D (đường kính tang), η thành phần.
**Steps:**
1. `P_lv = F·v / 1000` [kW]
2. `η_chung = η_kn · η_brc · η_brt · η_ol^k · η_x`
3. `P_ct = P_lv / η_chung`
4. `n_lv = 60000·v / (π·D)` [rpm]
5. Sơ bộ chọn `u_chung` → `n_sb = n_lv · u_chung`
6. **Query DB** động cơ thỏa: `P_dc ≥ P_ct` AND `n_dc ≈ n_sb` → trả về list ranked.
**Output:** `P_dc, n_dc, T_dc, kiểu động cơ` + ID động cơ trong DB.

### 4.4. Logic Module 2 — Bộ truyền Xích
**Input:** `P_2, n_2, u_x, điều kiện làm việc (K_đ, K_a, K_o, K_đc, K_b, K_lv)`.
**Steps:**
1. Chọn `z_1 = 29 - 2·u_x` (≥17), `z_2 = u_x · z_1` (≤120).
2. Tính `K = K_đ·K_a·K_o·K_đc·K_b·K_lv`.
3. `P_t = P · K · K_z · K_n` → tra **bảng 5.5** chọn bước xích `p`.
4. Kiểm tra số vòng quay tới hạn `n_th`.
5. Tính `a` (khoảng cách trục), `X` (số mắt xích) — chẵn.
6. **Kiểm bền:** số lần va đập `i ≤ [i]`, hệ số an toàn `s ≥ [s]`, lực tác dụng lên trục `F_r`.
7. Xuất kích thước đĩa xích.

### 4.5. Logic Module 3 — Bánh răng Côn-Trụ
**Cấp nhanh (bánh răng côn răng thẳng):**
- Tính `d_e1` sơ bộ → modun `m_e` → kiểm tra **ứng suất tiếp xúc σ_H** và **uốn σ_F**.

**Cấp chậm (bánh răng trụ răng nghiêng):**
- Tính `a_w` → `m_n`, `β` → kiểm `σ_H`, `σ_F`.

**Output:** modun, số răng, đường kính, chiều rộng, lực ăn khớp, ứng suất.

### 4.6. ⭐ Solver song song Module 2 ⇄ Module 3
**Vấn đề:** Tỉ số truyền `u_h` (hộp giảm tốc) và `u_x` (xích) phụ thuộc lẫn nhau qua điều kiện `u_chung = u_h · u_x`. Nếu kiểm bền M3 fail → phải thay `u_h` → ảnh hưởng `u_x` → M2 phải tính lại → có thể tạo **vòng lặp vô hạn**.

**Giải pháp:**
```python
async def parallel_solver(inputs):
    state = SharedState(u_h_init, u_x_init)
    for iteration in range(MAX_ITER):  # MAX_ITER = 20
        m2_task = asyncio.create_task(chain_design(state.snapshot()))
        m3_task = asyncio.create_task(gear_design(state.snapshot()))
        m2_res, m3_res = await asyncio.gather(m2_task, m3_task)

        if converged(m2_res, m3_res, tol=1e-3):
            return Result(m2_res, m3_res, status="converged")

        state = update_with_damping(state, m2_res, m3_res, alpha=0.5)

    return Result(status="failed", reason="no_convergence")
```
- **Damping factor** `α = 0.5` chống dao động.
- **Cycle detection:** lưu hash state mỗi vòng, phát hiện lặp → bail out với gợi ý thay đổi input.
- **WebSocket** stream tiến độ về frontend (mỗi iteration push 1 message).

---

## 5. AI MODULES (4 service)

### 5.1. NER/OCR — Nhập liệu thông minh
- **Mục tiêu:** Người dùng upload ảnh đề bài / PDF → tự động trích xuất F, v, D, điều kiện làm việc.
- **Tech:**
  - OCR: **PaddleOCR** hoặc **Tesseract + tiền xử lý OpenCV** (tiếng Việt).
  - NER: fine-tune **PhoBERT** hoặc rule-based regex cho ký hiệu cơ khí (F=…, v=…, kW, rpm).
- **API:** `POST /ai/ner-ocr` → trả về JSON cấu trúc.

### 5.2. Random Forest — Gợi ý thông số
- **Dataset:** Đồ án sinh viên các khóa trước (CSV: input → các tham số chọn như z_1, hệ số K, modun…).
- **Model:** `sklearn.ensemble.RandomForestRegressor` (multi-output).
- **Output:** Top-3 gợi ý cho mỗi tham số kèm confidence.
- **Lưu model:** `.pkl` trong Supabase Storage; load lazy.

### 5.3. Genetic Algorithm — Tối ưu hóa
- **Library:** `DEAP` hoặc `pymoo`.
- **Biến quyết định:** `z_1, p, u_h_cấp_nhanh, u_h_cấp_chậm, m_n, β, …`
- **Hàm mục tiêu (multi-objective):**
  - Minimize khối lượng hộp giảm tốc.
  - Minimize giá thành xích + đĩa xích.
  - Maximize tuổi thọ.
- **Ràng buộc:** Tất cả điều kiện bền phải pass.
- **Output:** Pareto front, user chọn nghiệm ưa thích.

### 5.4. LLM — Sinh báo cáo thuyết minh
- **Model:** Claude (Anthropic API) — model `claude-sonnet-4-6` cho chất lượng/giá hợp lý, **prompt caching** cho template thuyết minh dài.
- **Input:** Toàn bộ biến trung gian từ DB.
- **Output format:** Markdown → convert sang **DOCX** (`python-docx`) hoặc **PDF** (LaTeX qua `pylatex`).
- **Cấu trúc thuyết minh chuẩn:**
  1. Phân tích đề bài
  2. Tính chọn động cơ
  3. Phân phối tỉ số truyền
  4. Tính bộ truyền xích
  5. Tính bộ truyền bánh răng
  6. Tính trục, then, ổ lăn
  7. Kết luận
- **Prompt caching:** cache template + bảng tra cố định (≥1024 token) để giảm chi phí mỗi lần regenerate.

---

## 6. DATABASE (Supabase / PostgreSQL)

### 6.1. Lookup tables (số hóa từ sách Trịnh Chất - Lê Văn Uyển)
| Bảng | Nguồn | Mô tả |
|------|-------|-------|
| `motors_3k_4a` | Bảng P1.1 – P1.7 | Động cơ điện 3K, 4A: P, n, η, cos φ, T_max/T_dn |
| `chains_roller` | Bảng 5.1 – 5.8 | Xích con lăn: bước p, [P_0], B, q, F_phá |
| `bearings_skf_ntn` | Catalog SKF/NTN | Ổ bi, ổ đũa: C, C_0, dimensions |
| `keys_standard` | TCVN 4216-86 | Then bằng: b × h × t, tải |
| `tolerances_iso` | TCVN 2245 | Dung sai lỗ/trục: H7, k6, g6… |
| `materials` | Bảng 6.1 | Vật liệu: thép C45, 40X, … σ_b, σ_ch, HB |
| `coefficients_chain` | Bảng 5.6 | K_đ, K_a, K_o, K_đc, K_b, K_lv |

**Indexing:** btree trên `(P, n)` cho motor; trên `p` cho chain.

### 6.2. Bảng nghiệp vụ
```sql
-- Project / Session
projects(id, user_id, name, inputs_json, created_at, status)

-- Audit trail của BIẾN TRUNG GIAN (BẮT BUỘC)
calc_steps(
  id, project_id, module ENUM('motor','chain','gear'),
  step_no INT, step_name TEXT,
  formula TEXT,           -- ví dụ "P_ct = P_lv / η_chung"
  inputs JSONB, outputs JSONB,
  iteration INT,          -- vòng lặp solver (cho M2/M3)
  created_at TIMESTAMPTZ
)

-- Convergence log
solver_runs(id, project_id, iterations, status, residual, duration_ms)

-- AI artifacts
ai_suggestions(id, project_id, model TEXT, output JSONB, confidence FLOAT)
ga_pareto(id, project_id, solutions JSONB)

-- Reports
reports(id, project_id, format ENUM('pdf','docx'), storage_path, created_at)
```

### 6.3. Row Level Security
- Mỗi user chỉ thấy `projects` của chính mình → `auth.uid() = user_id`.
- Lookup tables: read-only cho `authenticated`.

---

## 7. API CONTRACT (REST + WS)

### REST endpoints (FastAPI)
```
POST   /api/projects                       # tạo project
GET    /api/projects/{id}

POST   /api/calc/motor                     # sync, < 1s
POST   /api/calc/chain-gear/start          # async, trả về job_id
GET    /api/calc/chain-gear/{job_id}       # poll status
WS     /api/calc/chain-gear/{job_id}/stream # realtime iterations

POST   /api/ai/ner-ocr        (multipart)
POST   /api/ai/rf-suggest
POST   /api/ai/ga-optimize    (async)
POST   /api/ai/report-generate (async)

GET    /api/tables/motors?P_min=&n_min=
GET    /api/tables/chains?p=
... (các bảng tra khác)
```

### WebSocket message schema
```json
{ "type": "iteration", "iter": 3, "u_h": 12.5, "u_x": 2.8,
  "m2_status": "ok", "m3_status": "checking", "residual": 0.004 }
{ "type": "converged", "result": { ... } }
{ "type": "error", "code": "NO_CONVERGENCE", "hint": "..." }
```

---

## 8. CHẤT LƯỢNG & TEST

- **Unit test:** Mỗi công thức cơ khí → test với ví dụ trong sách Trịnh Chất (có đáp số → so sánh sai số < 0.5%).
- **Integration test:** Chạy full pipeline với 5 bộ đề mẫu (đã có lời giải tay).
- **Property test (hypothesis):** Hệ số an toàn luôn ≥ 1, modun > 0, ...
- **CI:** GitHub Actions → pytest + ruff + mypy.
- **Coverage target:** ≥85% module tính toán.

---

## 9. LỘ TRÌNH HIỆN THỰC (CHO KỸ SƯ)

### Sprint 1 (tuần 1–2) — Foundation
- [ ] Khởi tạo FastAPI project + Supabase project + CI.
- [ ] Schema DB + migration (Supabase migrations).
- [ ] Số hóa bảng tra ưu tiên: động cơ, xích, hệ số K.

### Sprint 2 (tuần 3–4) — Calc Engine
- [ ] Module 1 (motor) + tests đối chiếu sách.
- [ ] Module 2 (chain) + tests.
- [ ] Module 3 (gear bevel + helical) + tests.

### Sprint 3 (tuần 5) — Parallel Solver ⭐
- [ ] Async orchestrator M2 ⇄ M3 + damping + cycle detection.
- [ ] WebSocket stream → frontend.
- [ ] Audit trail `calc_steps`.

### Sprint 4 (tuần 6–7) — AI services
- [ ] OCR/NER endpoint.
- [ ] Train Random Forest từ dataset đồ án cũ.
- [ ] GA optimizer (pymoo).
- [ ] LLM report (Claude + prompt caching + DOCX).

### Sprint 5 (tuần 8) — Polish
- [ ] Tích hợp frontend ↔ backend (thay mock data).
- [ ] E2E test, performance test.
- [ ] **Flowchart chi tiết** cho giảng viên CKT (deadline 13/03/2026).
- [ ] Deploy: Backend (Fly.io / Railway), Frontend (Vercel), DB (Supabase managed).

---

## 10. RỦI RO & GIẢM THIỂU

| Rủi ro | Giảm thiểu |
|--------|-----------|
| Vòng lặp chết M2⇄M3 | MAX_ITER + damping + cycle hash detection |
| Số hóa bảng tra sai | Cross-check 2 người + unit test so với sách |
| OCR tiếng Việt kém | Fallback nhập tay, gợi ý sửa lỗi |
| LLM hallucinate số liệu | Truyền số liệu qua **structured prompt** + bắt model chỉ format, không tự sinh số |
| Chi phí Claude API | Prompt caching, batch API cho regenerate |
| Hiệu năng GA chậm | Chạy background job + cache kết quả |

---

## 11. TÀI LIỆU THAM CHIẾU

- **Trịnh Chất, Lê Văn Uyển** — *Tính toán thiết kế hệ dẫn động cơ khí*, Tập 1 & 2, NXB Giáo Dục.
- TCVN 4216-86 (Then), TCVN 2245 (Dung sai).
- Catalog SKF, NTN bearings.
- Anthropic Claude API docs (cho LLM module).
- DEAP / pymoo documentation (cho GA).

---

## 12. CHECKLIST BÀN GIAO CHO KỸ SƯ

- [ ] Đọc & ký nhận tài liệu này.
- [ ] Truy cập repo frontend (đã có 7 trang).
- [ ] Supabase project credentials (chưa tạo — cần action).
- [ ] Anthropic API key (cần mua).
- [ ] Dataset đồ án cũ (xin từ giảng viên).
- [ ] Bản scan sách Trịnh Chất Tập 1 & 2 (cho số hóa bảng).
- [ ] Setup local dev: Python 3.11+, Node 20+, pnpm, Redis (cho Celery).

---

**Liên hệ nhóm:** Nhóm 7, 8 — Cơ Kỹ Thuật.
**Phiên bản tài liệu:** v1.0 — 2026-05-22.
