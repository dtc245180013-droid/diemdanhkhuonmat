# Điểm danh bằng khuôn mặt (DeepFace + OpenCV + Streamlit)

Hệ thống điểm danh dùng mô hình nhận diện khuôn mặt ArcFace qua thư viện DeepFace.
Tích hợp giao diện Dashboard Web Streamlit, tự động đối soát danh sách lớp (ai có mặt, ai vắng mặt)
và xuất báo cáo Excel/CSV chỉ với 1 cú nhấp chuột.

## Cài đặt

Dùng Python 3.9 đến 3.12.

```bash
pip install -r requirements.txt
```

Lần chạy đầu DeepFace tự tải trọng số model nên cần có mạng (trọng số đã được nạp sẵn offline).

## Cách dùng

### 1. Đăng ký khuôn mặt sinh viên
Chụp 10 ảnh mẫu cho mỗi sinh viên:
```bash
python diem_danh.py dang-ky --ten Tranthithuhuyen
```
*(SPACE: chụp ảnh | Q: thoát)*

### 2. Điểm danh thời gian thực qua webcam
```bash
python diem_danh.py chay
```
Thêm cờ `--chong-gia` để bật chống giả mạo bằng ảnh in/màn hình:
```bash
python diem_danh.py chay --chong-gia
```
Kết quả được tự động ghi nhận vào `diem_danh/diem_danh_<ngày>.csv`.

### 3. Mở Giao diện Web Dashboard (Điểm cộng đồ án)
Khởi chạy trang quản trị điểm danh sinh viên:
```bash
streamlit run app.py
```
- Tự động đối soát với `danh_sach_lop.csv` để thống kê ai Có mặt, ai Vắng mặt.
- Xem tỉ lệ chuyên cần (%), biểu đồ trực quan.
- Tải báo cáo danh sách điểm danh ra file **Excel (.xlsx)** hoặc **CSV**.

### 4. Đánh giá mô hình để lấy số liệu cho Báo cáo
```bash
python diem_danh.py danh-gia --test test
```

## Cấu trúc thư mục

```
danh_sach_lop.csv                 danh sách sinh viên cả lớp (MSSV, Họ tên, Tên đăng ký)
app.py                            giao diện Web Dashboard Streamlit
diem_danh.py                      mã nguồn điểm danh, đăng ký, đánh giá
my_db/
  Tranthithuhuyen/ 1.jpg ...      ảnh đăng ký của sinh viên
test/                             dùng cho lệnh danh-gia
  Tranthithuhuyen/ t1.jpg ...     ảnh kiểm thử (KHÔNG trùng ảnh trong my_db)
  nguoi_la/        x1.jpg ...     ảnh người chưa đăng ký (đo FAR)
diem_danh/
  diem_danh_2026-11-12.csv        nhật ký điểm danh theo ngày
```
