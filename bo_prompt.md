# Bộ prompt dùng với AI cho đồ án Điểm danh bằng khuôn mặt

Thay phần trong `[ ]` bằng nội dung thật của bạn rồi dán vào AI.
Ở mọi prompt, hãy dán số liệu thật và giữ câu "không tự bịa số", vì mẫu báo cáo yêu cầu mọi chỉ số phải lấy từ thực nghiệm.

---

### 1. Chạy thử và sửa lỗi code

```
Mình có script điểm danh bằng khuôn mặt dùng DeepFace + OpenCV (file diem_danh.py, đính kèm).
Môi trường: [Windows/Mac/Linux], Python [phiên bản], có webcam [có/không].
Khi chạy lệnh [python diem_danh.py chay] mình gặp lỗi sau:
[dán nguyên văn lỗi]
Hãy giải thích nguyên nhân, sửa đúng chỗ lỗi và chỉ đưa phần code thay đổi. Không viết lại toàn bộ file.
```

### 2. Viết Chương 3 (Dataset và Pre-processing)

```
Viết Chương 3 báo cáo Capstone (Samsung Innovation Campus) bằng tiếng Anh học thuật cho đề tài
"Face Recognition Attendance System".
Dữ liệu thật của nhóm: [số người], [số ảnh mỗi người], [tổng ảnh], [độ phân giải], [điều kiện ánh sáng/góc chụp],
[tập đăng ký / tập test / tập người lạ gồm bao nhiêu ảnh], thu thập bằng [webcam/điện thoại].
Gồm các mục: nguồn dữ liệu, thu thập, thống kê, tiền xử lý (detect, align, resize), xử lý ảnh lỗi/không thấy mặt, đạo đức dữ liệu.
Chỉ dùng số liệu mình cung cấp. Chỗ nào thiếu thì ghi [CẦN BỔ SUNG], tuyệt đối không tự bịa số.
```

### 3. Viết Chương 4 (Model Configuration)

```
Viết Chương 4 báo cáo Capstone cho hệ thống điểm danh khuôn mặt dùng DeepFace.
Cấu hình thật: model [ArcFace], detector [opencv], độ đo [cosine distance], ngưỡng [0.55],
xác nhận [2] lần liên tiếp mới ghi điểm danh, xử lý mỗi [10] frame.
Giải thích pipeline detect → align → embedding → so khớp, vì sao chọn model và ngưỡng này,
kèm công thức cosine distance bằng LaTeX và một bảng tham số.
Nói rõ mô hình dùng trọng số pretrained, không train từ đầu. Không bịa thông số.
```

### 4. Viết Chương 5 (Kết quả) từ file CSV

```
Đây là kết quả đánh giá thật của hệ thống điểm danh khuôn mặt (file ket_qua_danh_gia.csv):
[dán nội dung CSV]
Hãy viết Chương 5: bảng kết quả theo ngưỡng (Accuracy, FRR, FAR, tổng lỗi), phân tích đánh đổi giữa FAR và FRR,
chọn ngưỡng tối ưu và giải thích, rồi phân tích lỗi (ánh sáng, góc mặt, khẩu trang, ảnh mờ) dựa trên
[mô tả các ca sai trong chi_tiet_danh_gia.csv]. Thêm phần hạn chế và hướng phát triển (anti-spoofing, nhiều camera).
Chỉ dùng số trong CSV, không thêm số nào khác.
```

### 5. So sánh nhiều model

```
Mình đã chạy so sánh 3 model nhận diện khuôn mặt trên cùng tập test:
[ArcFace: acc, FAR, FRR, FPS], [Facenet512: ...], [SFace: ...].
Hãy tạo bảng so sánh, viết đoạn phân tích chọn model nào cho điểm danh lớp học
(cân bằng độ chính xác và tốc độ), và gợi ý biểu đồ phù hợp. Chỉ dùng số mình đưa.
```

### 6. Tài liệu tham khảo và phụ lục

```
Soạn danh sách References (IEEE) cho đề tài điểm danh bằng khuôn mặt, gồm: DeepFace (Serengil & Ozpinar),
ArcFace (Deng et al., 2019), FaceNet (Schroff et al., 2015), InsightFace, RetinaFace,
và Silent-Face-Anti-Spoofing. Xuất ra file .bib hợp lệ và cho biết nên trích dẫn ở mục nào của báo cáo.
Với tài liệu nào bạn không chắc về chi tiết xuất bản, hãy đánh dấu để mình tự kiểm tra, đừng đoán.
```

### 7. Chuẩn bị thuyết trình

```
Tạo dàn ý slide 10 phút cho đồ án "Face Recognition Attendance System" (Samsung Innovation Campus).
Thông tin: [vấn đề], [giải pháp], [kết quả chính: acc, FAR, FRR, FPS], [demo], [hạn chế].
Mỗi slide cho tiêu đề, 3-4 ý chính và lời thuyết trình ngắn. Cuối cùng đưa 8 câu hỏi giảng viên có thể hỏi
kèm gợi ý trả lời.
```
