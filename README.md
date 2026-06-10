# MechDrive Studio

Truy cập trực tuyến: https://mechdrive.vercel.app/

## 1. Thành viên nhóm

| MSSV | Họ và tên | Vai trò / Phân công |
| --- | --- | --- |
| 2352286 | Đinh Ngụy Nguyệt Hà | Đặc tả yêu cầu, phân tích ca sử dụng (Use case) và kiểm thử hệ thống |
| 2352171 | Dương Lê Nhật Duy | Thiết kế kiến trúc cơ sở dữ liệu, schema SQL và phân quyền an toàn trên Supabase |
| 2352715 | Trần Thiên Lộc | Phát triển giao diện người dùng (Frontend), thiết kế trải nghiệm UI/UX và xử lý tương tác API |
| 2353350 | Đinh Đoàn Vy | Xây dựng máy chủ (Backend API), lập trình thuật toán Q-Learning và số hóa dữ liệu cơ khí |

**MechDrive Studio** là một nền tảng Web hỗ trợ thiết kế hệ dẫn động thùng trộn kết hợp với AI tối ưu hóa. Dự án bao gồm:
- Frontend React/Next.js quản lý giao diện người dùng tương tác cao.
- Supabase (BaaS) để quản lý xác thực, lưu trữ trạng thái dự án và truy xuất dữ liệu kỹ thuật chuẩn.
- Backend FastAPI (Microservice) vận hành mô-đun AI Optimizer sử dụng thuật toán Q-Learning để gợi ý vật liệu và tham số ban đầu cho thiết kế bộ truyền xích và bánh răng.

## 2. Mục tiêu dự án

Dự án nhằm:
- Số hóa cơ sở dữ liệu kỹ thuật tiêu chuẩn (động cơ, xích, vật liệu).
- Tự động hóa quy trình tính toán thiết kế hệ dẫn động theo trình tự: động cơ -> bộ truyền xích -> bộ truyền bánh răng.
- Ứng dụng Q-Learning để gợi ý mác vật liệu và tham số tối ưu trong giai đoạn đầu.
- Giảm vòng lặp tính toán thủ công khi một bước sau không thỏa mãn điều kiện kỹ thuật.

## 3. Công nghệ chính

- Frontend: Next.js, React, TypeScript, Tailwind CSS, Supabase JS
- Backend: Python, FastAPI, uvicorn, pydantic, numpy
- AI: Q-Learning tabular, rời rạc hóa state, tra cứu Q-Table nhanh ở độ phức tạp O(1), mô-đun công thức cơ học
- Cơ sở dữ liệu: Supabase PostgreSQL với các bảng USER_ACCOUNT, PROJECT, DESIGN_SCHEME, TRANSMISSION, STD_MOTOR, STD_CHAIN, STD_MATERIAL...

## 4. Cấu trúc chính của dự án

- frontend/: mã nguồn giao diện người dùng Next.js
- backend/: API FastAPI làm engine tính toán AI
- backend/routers/: endpoint kích hoạt mô phỏng và AI
- backend/models/: schema Pydantic cho dữ liệu tính toán
- backend/ai_core/: cấu hình AI và các công thức thiết kế cơ khí lõi
- backend/ai_core/q_table.json: Bộ não Q-Table đã train sẵn cho mô-đun AI
- backend/config.py & database.py: cấu hình kết nối Backend

## 5. Luồng hoạt động & API (Data Flow)

### Quản lý Dự án & Tiêu chuẩn (Direct BaaS)
Frontend sử dụng Supabase Client SDK để tương tác trực tiếp với Database cho các tác vụ:
- Xác thực người dùng (Auth)
- Tạo mới, truy xuất và xóa Dự án / Design Scheme
- Truy xuất các danh mục tiêu chuẩn (Động cơ, Xích, Vật liệu...)

### AI Optimizer Engine (FastAPI Microservice)
- POST /ai/optimize-design
  - Nhận đầu vào: P_yc, n_yc, u_total, L_h, load_type
  - Rời rạc hóa giá trị input
  - Tra cứu trực tiếp trên RAM file q_table.json theo State
  - Tính toán chi tiết vật lý, giải nén Action thành tham số thực
  - Trả về tham số gợi ý tối ưu và báo cáo kỹ thuật.

## 6. Run dự án

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
3. Khởi động server (Port mặc định 8000):
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
1. Cài dependencies:
```bash
cd frontend
npm install
```
2. Khởi động ứng dụng (Port mặc định 3000):
```bash
npm run dev
```

## 7. AI Engine và thiết kế thuật toán

- backend/ai_core/config.py định nghĩa state space, action space, hyperparameter Q-Learning và hàm rời rạc hóa.
- backend/ai_core/formulas.py chứa các công thức cơ học cho thiết kế bánh răng và thiết kế xích, bao gồm kiểm tra ứng suất tiếp xúc (sigma_H) và ứng suất uốn (sigma_F).
- backend/routers/ai_engine.py chịu trách nhiệm:
  - nạp q_table.json thẳng vào RAM khi khởi động server
  - rời rạc hóa input
  - truy xuất state_key sang action
  - giải nén và tính toán các tham số vật lý

## 8. Tài liệu tham khảo

[1] Trịnh Chất & Lê Văn Uyển (2006). Tính toán thiết kế hệ dẫn động cơ khí (Tập 1 & Tập 2). Nhà xuất bản Giáo dục, Việt Nam.

[2] Watkins, C. J., & Dayan, P. (1992). Q-learning. Machine learning, 8(3), 279-292.

[3] Sutton, R. S., & Barto, A. G. (2018). Reinforcement learning: An introduction. MIT press.

[4] Tài liệu dự án nội bộ: Group_8_Final_Report.pdf (Khoa Cơ khí, Đại học Bách khoa ĐHQG-HCM).

## 9. Ghi chú

- Xem Group_8_Final_Report.pdf để biết chi tiết kiến trúc hệ thống, mô hình Q-Learning, các ca sử dụng và chiến lược kiểm thử.
- Giao diện người dùng sử dụng file .env.local ở frontend để liên kết Supabase.
