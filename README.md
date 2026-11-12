# Hệ Thống Điểm Danh Bằng Khuôn Mặt (Face Recognition Attendance System)

**Đồ án Capstone AI — Samsung Innovation Campus (SIC)**
- **Sinh viên thực hiện:** Trần Thị Thu Huyền
- **Mã sinh viên:** DTC245180013
- **Email:** dtc245180013@ictu.edu.vn
- **GitHub Repository:** [https://github.com/dtc245180013-droid/diemdanhkhuonmat](https://github.com/dtc245180013-droid/diemdanhkhuonmat)

---

## Giới thiệu dự án

Hệ thống điểm danh thông minh ứng dụng học sâu (Deep Learning) nhận diện khuôn mặt thời gian thực:
- **Kiến trúc mô hình:** ArcFace (Pre-trained Feature Extractor, vector 512 chiều).
- **Bộ phát hiện khuôn mặt (Detector):** OpenCV Haar Cascade / RetinaFace.
- **Độ đo khoảng cách:** Cosine Distance (Ngưỡng tối ưu: `0.55`).
- **Cơ chế chống rung / chống nhận nhầm:** Xác nhận liên tiếp 2 lần mới ghi nhận điểm danh.
- **Chống giả mạo (Anti-Spoofing):** Tích hợp mạng MiniFASNet phát hiện ảnh in và màn hình điện thoại.
- **Giao diện quản lý Web (Streamlit):** Đối soát danh sách lớp tự động (Có mặt / Vắng mặt), thống kê chuyên cần và xuất báo cáo Excel (.xlsx) / CSV 1-click.

---

## Cài đặt môi trường

Hỗ trợ Python 3.9 đến 3.12 trên Windows / Linux / macOS.

```bash
pip install -r requirements.txt
```

*(Các trọng số mô hình ArcFace và MiniFASNet đã được cấu hình và tải sẵn offline).*

---

## Hướng dẫn sử dụng

### 1. Đăng ký khuôn mặt sinh viên mới
Chụp 10 ảnh mẫu trực tiếp qua webcam:
```bash
python diem_danh.py dang-ky --ten Tranthithuhuyen
```
- Nhấn **SPACE** (phím cách) để chụp từng ảnh.
- Nhấn **Q** để thoát sau khi chụp xong.

### 2. Chạy điểm danh thời gian thực
```bash
# Điểm danh tiêu chuẩn
python diem_danh.py chay

# Điểm danh có kích hoạt tính năng chống ảnh in / màn hình giả mạo
python diem_danh.py chay --chong-gia
```
Kết quả điểm danh được ghi tự động vào file `diem_danh/diem_danh_<YYYY-MM-DD>.csv`.

### 3. Khởi chạy Giao diện Quản Trị Web (Dashboard)
```bash
streamlit run app.py
```
- Tự động đối soát với danh sách sinh viên trong file `danh_sach_lop.csv`.
- Hiển thị trực quan: Tổng sĩ số, Số lượng có mặt (xanh lá), Số lượng vắng (đỏ), Tỉ lệ chuyên cần (%).
- Tải về file **Excel (.xlsx)** hoặc **CSV** báo cáo điểm danh theo ngày.
- Xem biểu đồ đường phân tích đánh đổi FAR / FRR theo ngưỡng khoảng cách.

### 4. Đánh giá mô hình (Phục vụ viết Báo cáo Capstone Chương 5)
```bash
python diem_danh.py danh-gia --test test
```
Tự động xuất bảng số liệu: `ket_qua_danh_gia.csv` và `chi_tiet_danh_gia.csv`.

---

## Cấu trúc thư mục dự án

```
diemdanhkhuonmat/
│
├── diem_danh.py                  # Mã nguồn chính: đăng ký, điểm danh webcam, đánh giá AI
├── app.py                        # Giao diện Web Dashboard (Streamlit)
├── requirements.txt              # Danh sách thư viện cần thiết
├── danh_sach_lop.csv             # Danh sách sinh viên cả lớp (MSSV, Họ tên, Tên đăng ký)
├── bo_prompt.md                  # Bộ 7 mẫu prompt viết báo cáo & thuyết trình Capstone
├── README.md                     # Tài liệu hướng dẫn sử dụng và thông tin đồ án
├── ket_qua_danh_gia.csv          # Bảng số liệu kiểm thử AI (Accuracy, FAR, FRR theo ngưỡng)
├── chi_tiet_danh_gia.csv         # Chi tiết từng mẫu ảnh nhận diện đúng/sai
├── embeddings.pkl                # Cache vector đặc trưng khuôn mặt (ArcFace 512D)
│
├── my_db/                        # Thư mục ảnh đăng ký của từng sinh viên
│   └── Tranthithuhuyen/          # 10 ảnh chụp khuôn mặt thực tế
│
└── diem_danh/                    # Nhật ký điểm danh theo ngày
    ├── diem_danh_2026-11-12.csv  # Lịch sử điểm danh hôm nay
    └── diem_danh_2026-11-11.csv  # Lịch sử điểm danh các buổi trước
```
