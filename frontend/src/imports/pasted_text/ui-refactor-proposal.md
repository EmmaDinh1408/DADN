*(Khoanh tay trước ngực, nhìn thẳng vào sơ đồ phân chia các Tab trong thư mục `src` của cậu, khẽ lắc đầu)* Cậu định mang cái tư duy thiết kế "bảng phẳng" này đi thuyết phục Hội đồng chấm đồ án và người dùng thực tế à?

Thẳng thắn mà nói: **Cấu trúc Tab hiện tại của cậu đang bị rời rạc, chưa phản ánh đúng bản chất luồng tuyến tính (Linear Pipeline) của kỹ thuật cơ khí, và đặt Tab AI Optimizer ở dạng song song là một nước đi cực kỳ "bậy" về mặt trải nghiệm.**

Dưới góc độ của một người sẽ ngồi chấm bài Demo của cậu (Hội đồng) và một người trực tiếp sử dụng (Sinh viên/Kỹ sư), đây là những điểm bất hợp lý chí mạng và cách cậu phải sửa ngay lập tức:

---

### I. GÓC NHÌN NGƯỜI USER: "Sự hỗn loạn khi ép Luồng Tuyến Tính vào Tab Song Song"

Bản chất của đồ án thiết kế hệ dẫn động là **Luồng phụ thuộc dữ liệu 1 chiều (Data Dependency Cascade)**. Đầu ra của bước này là Đầu vào bắt buộc của bước sau:


$$\text{Đề bài} \rightarrow \text{AI Tối ưu (Chia tỉ số truyền)} \rightarrow \text{Chọn Động cơ} \rightarrow \text{Tính Xích} \rightarrow \text{Tính Hộp số (Bánh răng)}$$

Khi cậu dùng cấu trúc Tab độc lập ngang hàng trong `Sidebar.tsx` (`ModuleProjects`, `ModuleMotor`, `ModuleChain`, `ModuleGearbox`, `ModuleOptimizer`):

* **Lỗi logic của User:** Người dùng hoàn toàn có quyền click vào `ModuleChain` hoặc `ModuleGearbox` trước khi click vào `ModuleOptimizer`. Lúc đó, giao diện của cậu sẽ hiện cái gì? Một màn hình trống rỗng lỗi Null Pointer, hay một đống dữ liệu rác/mẫu? Người dùng sẽ cực kỳ bối rối vì không biết phải làm gì trước, làm gì sau.
* **Sự tù túng trong thao tác:** User phải nhảy qua nhảy lại giữa các Tab để xem con số AI gợi ý ở Tab này rồi lạch cạch nhập hoặc kiểm tra ở Tab khác.

### II. GÓC NHÌN NGƯỜI DEMO (HỘI ĐỒNG CHẤM): "Câu chuyện công nghệ bị gãy nửa chừng"

Khi cậu đứng trước Hội đồng để bảo vệ một đồ án "Ứng dụng AI", cậu cần một **Storytelling (Kịch bản trình diễn)** mượt mà để chứng minh con AI Q-Learning offline của cậu là **Trái tim dẫn dắt hệ thống**, chứ không phải là một tính năng "đính kèm cho sang".

* **Cái bẫy của Tab `ModuleOptimizer` lửng lơ:** Nếu cậu để `ModuleOptimizer` nằm riêng một Tab ngang hàng với các cấu phần, thầy cô sẽ vặn ngay: *"Tại sao tôi đã chọn động cơ xong rồi, tính xích xong rồi mới thấy cái Tab Optimizer? AI tối ưu cái gì khi mọi sự đã rồi?"*. Nếu cậu giải thích là "phải bấm Tab này trước", thầy cô sẽ bảo: *"Vậy sao anh không thiết kế giao diện bắt tôi làm bước đó trước? Thiết kế UI/UX quá tồi!"*.

---

### III. GIẢI PHÁP RE-ARCHITECT (SỬA LẠI UI LUỒNG CHO CHUẨN)

Để giải quyết triệt để sự "bậy" này, tôi yêu cầu cậu phải thay đổi cấu trúc hiển thị theo 1 trong 2 cách sau:

#### Cách 1: Chuyển dịch sang Kiến trúc Stepper (Quy trình từng bước - Khuyên dùng)

Thay vì dùng Sidebar để Switch các Tab tự do, cậu hãy biến khu vực làm việc chính thành một **Workflow Stepper** (Dùng component `VerticalStepper.tsx` hoặc một thanh tiến trình ngang ở Top).

Luồng dịch chuyển của các bước bắt buộc phải là:

1. **Step 1: Khởi tạo Dự án (`ModuleProjects`)** -> Nhập số liệu đầu vào ($P, n$).
2. **Step 2: Tối ưu hóa Hệ thống (`ModuleOptimizer`)** -> Đây phải là bước kế tiếp ngay lập tức! Ấn nút "AI Optimize", hệ thống chạy thuật toán $O(1)$ từ Q-Table offline, nhả ra bộ hạt giống: $u_{total}, u_d, u_x, \psi_{ba}, z_1$. User chốt phương án.
3. **Step 3: Chọn Động cơ (`ModuleMotor`)** -> Bước này kế thừa $u_{total}$ và hiệu suất từ Step 2 để tính công suất cần thiết và chọn mã động cơ từ `STD_MOTOR`.
4. **Step 4: Thiết kế Bộ truyền ngoài (`ModuleChain`)** -> Kế thừa $u_x, z_1$ từ AI để chạy luồng kiểm nghiệm xích.
5. **Step 5: Thiết kế Hộp giảm tốc (`ModuleGearbox`)** -> Kế thừa $u_d, \psi_{ba}$ từ AI để chạy luồng kiểm nghiệm bánh răng.
6. **Step 6: Xuất Báo cáo (`ReportPanel`)**.

*Các Step sau chỉ được Unlock khi Step trước đã hoàn thành (Success hoặc thông qua Fallback).*

#### Cách 2: Nếu khăng khăng giữ Sidebar Tabs (Thì phải Gom cụm Logic)

Nếu cậu vẫn muốn Sidebar có các Tab để User dễ nhảy font-end phục vụ mục đích khác, cậu phải gom cụm lại:

* **Tab 1: Tổng quan Dự án & Số liệu đầu vào** (`ModuleProjects`)
* **Tab 2: Trí tuệ nhân tạo & Phân phối hệ thống** (Đổi tên `ModuleOptimizer` thành **"AI System Design"** và đẩy nó lên vị trí số 2). Trong Tab này, hiển thị rõ sơ đồ động học tổng thể và các hạt giống AI nhả ra.
* **Tab 3: Chi tiết Thiết kế (Engineering Modules)** -> Khi bấm vào Tab này, bên trong nó mới chia thành các Sub-tabs con: `Động cơ` $\rightarrow$ `Truyền động Xích` $\rightarrow$ `Hộp số`.

---

### LỜI NHẬN XÉT THẲNG THẮN ĐỂ CẬU TỈNH NGỘ

Giao diện hiện tại của cậu trông rất hiện đại, dùng Shadcn UI, Tailwind bóng bẩy, nhưng **rỗng tuếch về mặt tư duy hệ thống cơ khí**. Cậu đang làm phần mềm cho kỹ sư dùng, chứ không phải làm web bán hàng thương mại điện tử để người dùng muốn click xem sản phẩm nào trước cũng được.

Hãy lôi file `Sidebar.tsx` và file cấu trúc luồng chính ra, đập lại theo kiến trúc Tuyến tính có khóa điều kiện (Conditional Stepper) ngay lập tức. Khi cậu Demo, cậu chỉ cần bấm "Next", dữ liệu chảy mượt mà từ AI sang Backend sang giao diện, Hội đồng sẽ không thể bẻ gãy được logic của cậu một câu nào cả.

Cậu chọn phương án sửa theo Stepper hay sửa theo Gom cụm Sidebar để tôi hướng dẫn cấu trúc lại State cho đồng bộ?