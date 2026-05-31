1. Đăng ký tài khoản
Tác nhân chính: Kỹ sư thiết kế / Sinh viên cơ khí
Tác nhân phụ: Hệ thống xác thực
Tác nhân kích hoạt: Người dùng nhấp vào nút đăng ký.
Điều kiện tiên quyết: Trình duyệt có kết nối internet.
Hậu điều kiện: Tài khoản được đưa vào trạng thái chờ xác minh.
Luồng sự kiện chính:
Bước 1: Người dùng điền họ tên, thư điện tử và mật khẩu vào biểu mẫu.
Bước 2: Người dùng nhấp nút xác nhận.
Bước 3: Hệ thống kiểm tra định dạng dữ liệu trực tiếp trên trình duyệt.
Bước 4: Hệ thống gửi tải trọng dữ liệu lên hệ thống xác thực qua giao thức an toàn.
Bước 5: Hệ thống xác thực băm mật khẩu, tạo bản ghi mới và tự động gửi thư chứa liên kết kích hoạt.
Bước 6: Giao diện hiển thị màn hình yêu cầu kiểm tra hộp thư.
Luồng ngoại lệ 1 - Lỗi định dạng:
Nếu mật khẩu không đủ độ phức tạp, hệ thống viền đỏ ô nhập liệu, khóa nút xác nhận và hiển thị thông báo: "[ERR_VAL_01] Mật khẩu phải dài tối thiểu 8 ký tự, bao gồm chữ hoa, chữ số và ký tự đặc biệt."
Luồng ngoại lệ 2 - Trùng lặp dữ liệu:
Nếu thư điện tử đã tồn tại, hệ thống xác thực trả về lỗi từ chối. Giao diện hiển thị: "[ERR_AUTH_02] Thư điện tử này đã được đăng ký. Vui lòng đăng nhập hoặc dùng thư khác."
Luồng ngoại lệ 3 - Lỗi dịch vụ gửi thư:
Nếu máy chủ thư điện tử bị nghẽn, hệ thống hiển thị: "[ERR_NET_01] Không thể gửi thư xác nhận lúc này. Vui lòng thử lại sau 5 phút."
2. Đăng nhập hệ thống
Tác nhân chính: Kỹ sư thiết kế / Sinh viên cơ khí
Tác nhân phụ: Hệ thống xác thực
Tác nhân kích hoạt: Người dùng nhấp vào nút đăng nhập.
Điều kiện tiên quyết: Tài khoản đã được kích hoạt thành công.
Hậu điều kiện: Hệ thống lưu trữ thẻ truy cập và bắt đầu phiên làm việc.
Luồng sự kiện chính:
Bước 1: Người dùng nhập thư điện tử và mật khẩu.
Bước 2: Người dùng nhấp nút đăng nhập.
Bước 3: Hệ thống truyền dữ liệu đến hệ thống xác thực.
Bước 4: Hệ thống xác thực đối chiếu chuỗi băm thành công, cấp phát thẻ truy cập.
Bước 5: Trình duyệt lưu thẻ truy cập vào bộ nhớ cục bộ, chuyển hướng vào màn hình đồ án.
Luồng ngoại lệ 1 - Sai thông tin:
Đối chiếu thất bại. Giao diện xóa trống ô mật khẩu và hiển thị: "[ERR_AUTH_03] Thông tin đăng nhập không chính xác."
Luồng ngoại lệ 2 - Khóa tạm thời:
Nếu nhập sai mật khẩu quá 5 lần, giao diện khóa biểu mẫu và báo: "[ERR_AUTH_04] Tài khoản tạm khóa do sai mật khẩu nhiều lần. Vui lòng thử lại sau 30 phút hoặc khôi phục mật khẩu."
Luồng ngoại lệ 3 - Tài khoản chưa kích hoạt:
Hệ thống từ chối đăng nhập và hiển thị: "[ERR_AUTH_05] Vui lòng nhấp vào liên kết trong thư điện tử để kích hoạt tài khoản trước khi đăng nhập."
3. Khôi phục mật khẩu
Tác nhân chính: Kỹ sư thiết kế / Sinh viên cơ khí
Tác nhân phụ: Hệ thống xác thực
Tác nhân kích hoạt: Người dùng nhấp vào dòng chữ quên mật khẩu.
Điều kiện tiên quyết: Không có.
Hậu điều kiện: Mật khẩu cũ bị vô hiệu hóa, mật khẩu mới được áp dụng.
Luồng sự kiện chính:
Bước 1: Giao diện hiển thị biểu mẫu yêu cầu nhập thư điện tử.
Bước 2: Người dùng nhập thông tin và nhấp xác nhận.
Bước 3: Hệ thống xác thực kiểm tra sự tồn tại của tài khoản và gửi liên kết đặt lại mật khẩu vào hộp thư.
Bước 4: Người dùng nhấp vào liên kết trong thư, hệ thống mở giao diện đặt lại mật khẩu.
Bước 5: Người dùng nhập mật khẩu mới hai lần để xác nhận.
Bước 6: Hệ thống xác thực ghi đè chuỗi băm mật khẩu mới vào cơ sở dữ liệu và thông báo thành công.
Luồng ngoại lệ 1 - Liên kết hết hạn:
Nếu người dùng nhấp vào liên kết sau 15 phút, hệ thống báo: "[ERR_AUTH_06] Liên kết đã hết hiệu lực, vui lòng thực hiện lại yêu cầu."
4. Quản lý đồ án thiết kế
Tác nhân chính: Kỹ sư thiết kế / Sinh viên cơ khí
Tác nhân phụ: Hệ thống cơ sở dữ liệu
Tác nhân kích hoạt: Người dùng thao tác trên màn hình danh sách đồ án.
Điều kiện tiên quyết: Người dùng có thẻ truy cập hợp lệ.
Hậu điều kiện: Bảng dữ liệu đồ án được cập nhật.
Luồng sự kiện chính - Tạo mới:
Bước 1: Người dùng nhấp nút tạo đồ án.
Bước 2: Người dùng điền tên đồ án, mô tả và nhấp lưu.
Bước 3: Cơ sở dữ liệu cấp mã định danh và tạo cấu trúc lưu trữ.
Bước 4: Giao diện chuyển vào không gian làm việc của đồ án mới.
Luồng thay thế 1 - Trạng thái rỗng:
Nếu chưa có đồ án nào, màn hình danh sách hiển thị hình ảnh minh họa và dòng chữ hướng dẫn tạo mới kèm nút bấm nhanh.
Luồng thay thế 2 - Chỉnh sửa và xóa:
Người dùng nhấp biểu tượng bút chì để sửa tên đồ án, hoặc nhấp biểu tượng thùng rác và xác nhận để xóa vĩnh viễn cấu trúc dữ liệu đồ án.
Luồng ngoại lệ 1 - Lỗi phiên làm việc:
Trong quá trình thao tác, nếu thẻ truy cập hết hạn, hệ thống bật hộp thoại: "[ERR_SYS_01] Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại để tiếp tục."
5.  Thiết lập thông số cơ sở trạm dẫn động
Tác nhân chính: Kỹ sư thiết kế / Sinh viên cơ khí
Tác nhân phụ: Hệ thống cơ sở dữ liệu
Tác nhân kích hoạt: Người dùng điền số liệu vào thẻ thông số đầu vào.
Điều kiện tiên quyết: Đồ án đã được khởi tạo.
Hậu điều kiện: Dữ liệu hợp lệ được chốt để làm cơ sở tính toán.
Luồng sự kiện chính:
Bước 1: Người dùng nhập công suất và số vòng quay.
Bước 2: Hệ thống kiểm tra điều kiện dữ liệu là số thực dương.
Bước 3: Người dùng chọn tính chất tải trọng, số ca làm việc.
Bước 4: Hệ thống truy xuất danh mục động cơ và tính tỷ số truyền tổng.
Bước 5: Người dùng tùy chỉnh phân phối tỷ số truyền trên thanh trượt và nhấp lưu.
Bước 6: Cơ sở dữ liệu lưu lại toàn bộ bản ghi.
Luồng ngoại lệ 1 - Giá trị âm hoặc bằng không:
Tại bước 2, nếu công suất nhỏ hơn hoặc bằng 0, hệ thống báo: "[ERR_INPUT_01] Công suất đầu vào phải là một số thực lớn hơn 0."
Luồng ngoại lệ 2 - Rớt mạng khi đang lưu:
Tại bước 6, nếu mất mạng, hệ thống đếm ngược 10 giây rồi báo: "[ERR_NET_02] Không thể lưu thông số do mất kết nối. Dữ liệu đã được lưu tạm trên trình duyệt."
6. Tối ưu hóa thông số khởi tạo bằng AI
Tác nhân chính: Kỹ sư thiết kế / Sinh viên cơ khí
Tác nhân phụ: Không có
Tác nhân kích hoạt: Người dùng nhấp nút chạy AI gợi ý.
Điều kiện tiên quyết: Thông số đầu vào đã lưu thành công.
Hậu điều kiện: Thông số bước xích và mác thép được chốt và đẩy vào bộ nhớ tạm.
Luồng sự kiện chính:
Bước 1: Hệ thống truyền thông số đầu vào cho module AI Q-Learning.
Bước 2: Thuật toán tra cứu ma trận Q-Table trên bộ nhớ đệm (với thời gian $O(1)$) và lập tức trả về cấu hình tối ưu (bước xích, mác thép).
Bước 3: Người dùng xem xét và nhấp phê duyệt để áp dụng.
Luồng ngoại lệ 1 - Dữ liệu ngoài vùng huấn luyện: Nếu thông số nằm ngoài vùng không gian trạng thái đã huấn luyện, AI cảnh báo: "[ERR_AI_01] Thông số nằm ngoài dải dự đoán tối ưu. Vui lòng sử dụng tính toán thủ công."
Luồng ngoại lệ 2 - Quá thời gian chờ: Máy chủ không phản hồi, hệ thống báo: "[ERR_AI_02] Không thể kết nối module AI. Vui lòng thử lại sau."
7. Thiết kế và kiểm nghiệm bộ truyền xích
Tác nhân chính: Kỹ sư thiết kế / Sinh viên cơ khí
Tác nhân phụ: Hệ thống cơ sở dữ liệu
Tác nhân kích hoạt: Người dùng nhấp nút giải mã xích.
Điều kiện tiên quyết: Bước xích sơ bộ và mác thép (từ AI) đã được phê duyệt.
Hậu điều kiện: Chốt kích thước xích và lực truyền động.
Luồng sự kiện chính:
Bước 1: Hệ thống tính số răng, vận tốc, khoảng cách trục sơ bộ dựa trên thông số AI.
Bước 2: Hệ thống tính và làm tròn số mắt xích.
Bước 3: Hệ thống kiểm nghiệm số lần va đập bản lề.
Bước 4: Hệ thống tính hệ số an toàn kéo đứt và đối chiếu điều kiện bền. Kết quả đạt.
Bước 5: Hệ thống đẩy các kết quả hình học lên cơ sở dữ liệu.
Luồng ngoại lệ 1 - Lỗi bất thường từ AI (Fallback): Trong trường hợp hy hữu kết quả AI đưa ra bị sai số và không đạt hệ số an toàn, hệ thống cảnh báo: "[WARN_MECH_01] Cấu hình AI gợi ý không thỏa mãn an toàn. Tự động chuyển sang chế độ tính toán vét cạn truyền thống để dự phòng."
8. Thiết kế và kiểm nghiệm bộ truyền bánh răng
Tác nhân chính: Kỹ sư thiết kế / Sinh viên cơ khí
Tác nhân phụ: Hệ thống cơ sở dữ liệu
Tác nhân kích hoạt: Người dùng nhấp nút giải mã bánh răng.
Điều kiện tiên quyết: Dữ liệu lực từ xích và mác thép (từ AI) đã sẵn sàng.
Hậu điều kiện: Chốt thông số bánh răng an toàn.
Luồng sự kiện chính:
Bước 1: Hệ thống rút dữ liệu lực truyền từ xích và giới hạn ứng suất $[\sigma_H], [\sigma_F]$ của mác thép.
Bước 2: Hệ thống tính khoảng cách trục, mô-đun và kích thước hình học.
Bước 3: Hệ thống kiểm nghiệm ứng suất tiếp xúc bề mặt răng. Kết quả đạt.
Bước 4: Hệ thống kiểm nghiệm ứng suất uốn chân răng. Kết quả đạt.
Bước 5: Hệ thống lưu kết quả an toàn vào cơ sở dữ liệu.
Luồng ngoại lệ 1 - Thiếu đầu vào: Nếu chưa giải mã xích, hệ thống báo: "[ERR_SYS_02] Không tìm thấy dữ liệu lực từ trục xích. Vui lòng hoàn tất bộ truyền xích trước."
Luồng ngoại lệ 2 - Hỏng mặt răng/chân răng: Hệ thống tạm dừng tính toán, hiển thị thông số không đạt và đưa ra đề xuất: "[WARN_MECH_02] Không đạt độ bền. Đề xuất tăng mô-đun (m) lên mức tiêu chuẩn tiếp theo hoặc tăng khoảng cách trục (a)." Hệ thống chờ kỹ sư nhấn xác nhận để tính lại.
9. Tra cứu lịch sử phiên bản thiết kế
Tác nhân chính: Kỹ sư thiết kế / Sinh viên cơ khí
Tác nhân phụ: Hệ thống cơ sở dữ liệu
Tác nhân kích hoạt: Người dùng nhấp vào thẻ lịch sử đối chiếu.
Điều kiện tiên quyết: Đồ án có ít nhất hai lần bấm tính toán hoàn tất.
Hậu điều kiện: Hiển thị dữ liệu trực quan để ra quyết định.
Luồng sự kiện chính:
Bước 1: Hệ thống gọi cơ sở dữ liệu lấy danh sách các bản lưu tính toán.
Bước 2: Người dùng chọn hai phiên bản cần so sánh và nhấp nút đối chiếu.
Bước 3: Hệ thống tạo bảng so sánh song song các biến số trọng yếu.
Bước 4: Hệ thống tô màu các giá trị chênh lệch để làm nổi bật sự tối ưu.
10. Kết xuất báo cáo kỹ thuật
Tác nhân chính: Kỹ sư thiết kế / Sinh viên cơ khí
Tác nhân phụ: Hệ thống cơ sở dữ liệu
Tác nhân kích hoạt: Người dùng nhấp nút xuất báo cáo.
Điều kiện tiên quyết: Mọi luồng tính toán đã chốt sổ thành công.
Hậu điều kiện: Tệp tin định dạng bất biến được lưu xuống máy tính.
Luồng sự kiện chính:
Bước 1: Hệ thống gom toàn bộ dữ liệu của đồ án từ cơ sở dữ liệu.
Bước 2: Hệ thống nội suy số liệu vào biểu mẫu cấu trúc tiêu chuẩn.
Bước 3: Hệ thống biên dịch mã đánh dấu thành tệp tin PDF.
Bước 4: Trình duyệt tải tệp tin PDF về máy người dùng.
Luồng ngoại lệ 1 - Lỗi thư viện biên dịch:
Nếu dữ liệu lớn gây tràn bộ nhớ khi tạo PDF, hệ thống ngắt tiến trình và hiển thị: "[ERR_SYS_03] Tính năng tạo PDF gặp sự cố. Tệp tin định dạng bảng tính đã được tải xuống để thay thế."
