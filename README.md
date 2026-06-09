# MechDrive Studio

**MechDrive Studio** là một nền tảng Web hỗ trợ thiết kế hệ dẫn động thùng trộn kết hợp với AI tối ưu hóa. Dự án bao gồm:
- Frontend React/Next.js để quản lý giao diện người dùng.
- Backend FastAPI với Supabase để xác thực, quản lý dự án và truy xuất dữ liệu kỹ thuật chuẩn.
- Module AI Optimizer sử dụng Q-Learning để gợi ý vật liệu và tham số ban đầu cho thiết kế bộ truyền xích và bánh răng.

## Mục tiêu dự án

Dự án nhằm:
- Số hóa cơ sở dữ liệu kỹ thuật tiêu chuẩn (động cơ, xích, vật liệu).
- Tự động hóa quy trình tính toán thiết kế hệ dẫn động theo trình tự: động cơ → bộ truyền xích → bộ truyền bánh răng.
- Ứng dụng Q-Learning để gợi ý mác vật liệu và tham số tối ưu trong giai đoạn đầu.
- Giảm vòng lặp tính toán thủ công khi một bước sau không thỏa mãn điều kiện kỹ thuật.

## Công nghệ chính

- Frontend: `Next.js`, `React`, `TypeScript`, `MUI`, `Tailwind CSS`, `Supabase JS`
- Backend: `Python`, `FastAPI`, `uvicorn`, `Supabase`, `pydantic`, `numpy`
- AI: Q-Learning tabular, rời rạc hóa state, tra cứu Q-Table nhanh, mô-đun công thức cơ học
- Cơ sở dữ liệu: Supabase với các bảng `USER`, `PROJECT`, `STD_MOTOR`, `STD_CHAIN`, `STD_MATERIAL`

## Cấu trúc chính của dự án

- `Frontend/`: mã nguồn giao diện người dùng Next.js
- `backend/`: API FastAPI và cấu hình Supabase
- `backend/routers/`: endpoint API cho người dùng, dự án, tiêu chuẩn và AI
- `backend/models/`: schema Pydantic cho request/response
- `backend/ai_core/`: cấu hình AI và công thức thiết kế cơ khí
- `backend/ai_core/q_table.json`: Q-Table cho mô-đun AI
- `backend/ai_core/lookup_tables/`: dữ liệu chuẩn và bảng tra cứu kỹ thuật
- `backend/config.py`: cấu hình biến môi trường Supabase
- `backend/database.py`: khởi tạo client Supabase

## API chính

### Xác thực người dùng
- `POST /users/register` — tạo tài khoản mới
- `POST /users/login` — đăng nhập và lấy access token

### Quản lý dự án
- `GET /projects/{user_id}` — lấy danh sách dự án của người dùng
- `POST /projects/{user_id}` — tạo mới dự án
- `DELETE /projects/{project_id}` — xoá dự án

### Tra cứu dữ liệu tiêu chuẩn
- `GET /standards/motors`
- `GET /standards/chains`
- `GET /standards/materials`

### AI Optimizer
- `POST /ai/optimize-design`
  - Nhận đầu vào: `P_yc`, `n_yc`, `u_total`, `L_h`, `load_type`
  - Rời rạc hóa giá trị input
  - Tra cứu Q-Table theo trạng thái
  - Tính toán chi tiết vật lý cho bánh răng và xích
  - Trả về tham số gợi ý và kết quả công thức

## Run dự án

### Backend
1. Cài dependencies:
```bash
cd backend
python -m pip install -r requirements.txt
```
2. Tạo file `.env` trong `backend/` với:
```text
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_or_service_key
```
3. Khởi động server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
1. Cài dependencies:
```bash
cd Frontend
npm install
```
2. Khởi động ứng dụng:
```bash
npm run dev
```
3. Mặc định Frontend sử dụng `localhost:3000` và Backend `localhost:8000`.

## AI Engine và thiết kế thuật toán

- `backend/ai_core/config.py` định nghĩa state space, action space, hyperparameter Q-Learning và hàm rời rạc hóa.
- `backend/ai_core/formulas.py` chứa các công thức cơ học cho thiết kế bánh răng và thiết kế xích, bao gồm kiểm tra ứng suất tiếp xúc (`sigma_H`) và ứng suất uốn (`sigma_F`).
- `backend/routers/ai_engine.py` chịu trách nhiệm:
  - nạp `q_table.json` khi khởi động server
  - rời rạc hóa input
  - truy xuất `state_key` sang action
  - giải nén và tính toán các tham số vật lý

## Tài liệu tham khảo

- Báo cáo chính thức: `Group_8_Final_Report.pdf`
- Giáo trình tham khảo: `Tính toán thiết kế Hệ dẫn động cơ khí` của PGS. TS. Trịnh Chất và TS. Lê Văn Uyển
- Các nội dung liên quan đến Q-Learning, rời rạc hóa và reward design được trình bày chi tiết trong báo cáo nhóm.

## Thành viên nhóm

- **12352286 Đinh Ngụy Nguyệt Hà** — Đặc tả yêu cầu, thiết kế Use Case, kiểm thử
- **22352171 Dương Lê Nhật Duy** — Thiết kế cơ sở dữ liệu, schema SQL, Supabase
- **32352715 Trần Thiên Lộc** — Frontend React/TypeScript, UI/UX, tích hợp API
- **42353350 Đinh Đoàn Vy** — Backend FastAPI, thuật toán Q-Learning, dữ liệu chuẩn JSON

## Ghi chú

- Xem `Group_8_Final_Report.pdf` để biết chi tiết kiến trúc hệ thống, mô hình Q-Learning, các ca sử dụng và chiến lược kiểm thử.
- Để triển khai thực tế, thay đổi `allow_origins` trong `backend/main.py` và bảo mật biến môi trường Supabase.
