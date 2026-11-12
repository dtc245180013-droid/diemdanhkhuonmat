#!/usr/bin/env python3
"""
ĐIỂM DANH BẰNG KHUÔN MẶT (DeepFace + OpenCV)

Ba lệnh:
  python diem_danh.py dang-ky --ten NguyenVanA      # chụp ảnh đăng ký bằng webcam
  python diem_danh.py chay                          # mở webcam và điểm danh
  python diem_danh.py danh-gia --test test          # đo độ chính xác, FAR/FRR theo ngưỡng

Thư mục dữ liệu:
  my_db/<TenSinhVien>/*.jpg      ảnh đăng ký (mỗi người một thư mục)
  test/<TenSinhVien>/*.jpg       ảnh kiểm thử của người đã đăng ký (KHÔNG trùng ảnh trong my_db)
  test/nguoi_la/*.jpg            ảnh của người chưa đăng ký (để đo FAR)
  diem_danh/diem_danh_<ngày>.csv kết quả điểm danh
"""
import argparse
import csv
import pickle
import sys
import time
import unicodedata
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from deepface import DeepFace

# ----------------------------- CẤU HÌNH -----------------------------
MODEL = "ArcFace"          # thử thêm: "Facenet512", "SFace", "VGG-Face"
DETECTOR = "opencv"        # nhanh nhất; chính xác hơn: "retinaface", "mtcnn" (chậm hơn)
NGUONG = 0.55              # khoảng cách cosine <= NGUONG thì nhận là người đã đăng ký
BO_QUA_FRAME = 10          # chỉ nhận diện mỗi N frame cho đỡ lag
SO_LAN_XAC_NHAN = 2        # phải nhận ra cùng một người >= N lần mới ghi điểm danh
THU_MUC_DB = Path("my_db")
THU_MUC_LOG = Path("diem_danh")
FILE_CACHE = Path("embeddings.pkl")
TEN_NGUOI_LA = "nguoi_la"
DUOI_ANH = {".jpg", ".jpeg", ".png", ".bmp"}
CHONG_GIA = False          # bật bằng cờ --chong-gia (cần DeepFace bản mới)
FONT = cv2.FONT_HERSHEY_SIMPLEX
# --------------------------------------------------------------------


def bo_dau(s):
    """OpenCV không vẽ được chữ có dấu, nên bỏ dấu khi hiển thị."""
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def lay_embedding(anh):
    """anh: đường dẫn hoặc mảng BGR. Trả về list[(vector, (x, y, w, h))]; rỗng nếu không thấy mặt."""
    tham_so = {"anti_spoofing": True} if CHONG_GIA else {}
    try:
        kq = DeepFace.represent(
            img_path=anh,
            model_name=MODEL,
            detector_backend=DETECTOR,
            enforce_detection=True,
            **tham_so,
        )
    except ValueError:  # không thấy mặt (hoặc bị coi là giả mạo khi bật --chong-gia)
        return []
    except TypeError:
        sys.exit("Bản DeepFace của bạn chưa hỗ trợ anti_spoofing. Chạy: pip install -U deepface")
    ra = []
    for k in kq:
        v = k["facial_area"]
        ra.append((np.array(k["embedding"], dtype=np.float32), (v["x"], v["y"], v["w"], v["h"])))
    return ra


def mat_lon_nhat(danh_sach):
    return max(danh_sach, key=lambda r: r[1][2] * r[1][3])


def khoang_cach_cosine(a, B):
    a = a / np.linalg.norm(a)
    B = B / np.linalg.norm(B, axis=1, keepdims=True)
    return 1.0 - B @ a


def nap_thu_vien():
    """Đọc ảnh trong my_db, tính embedding (có cache vào embeddings.pkl). Trả về (nhãn, ma trận vector)."""
    cache = {"meta": (MODEL, DETECTOR), "emb": {}}
    if FILE_CACHE.exists():
        try:
            with open(FILE_CACHE, "rb") as f:
                c = pickle.load(f)
            if c.get("meta") == (MODEL, DETECTOR):
                cache = c
        except Exception:
            pass
    emb = cache["emb"]

    files = [p for p in THU_MUC_DB.glob("*/*") if p.suffix.lower() in DUOI_ANH]
    hien_co = {str(p) for p in files}
    for k in list(emb):
        if k not in hien_co:
            del emb[k]

    can_tinh = [p for p in files if str(p) not in emb or emb[str(p)][0] != p.stat().st_mtime]
    if can_tinh:
        print(f"Đang tính embedding cho {len(can_tinh)} ảnh (lần đầu sẽ hơi lâu)...")
    for p in can_tinh:
        res = lay_embedding(str(p))
        if not res:
            print(f"  [bỏ qua] không thấy mặt: {p}")
            emb.pop(str(p), None)
            continue
        emb[str(p)] = (p.stat().st_mtime, mat_lon_nhat(res)[0])
    if can_tinh:
        with open(FILE_CACHE, "wb") as f:
            pickle.dump(cache, f)

    if not emb:
        return np.array([]), np.zeros((0, 1), dtype=np.float32)
    nhan = np.array([Path(k).parent.name for k in emb])
    vec = np.stack([v[1] for v in emb.values()])
    return nhan, vec


def nhan_dien_vector(v, nhan, vec):
    """Trả về (tên người gần nhất, khoảng cách)."""
    if len(nhan) == 0:
        return None, float("inf")
    d = khoang_cach_cosine(v, vec)
    i = int(np.argmin(d))
    return str(nhan[i]), float(d[i])


# --------------------------- GHI ĐIỂM DANH ---------------------------
def file_log():
    THU_MUC_LOG.mkdir(exist_ok=True)
    return THU_MUC_LOG / f"diem_danh_{datetime.now():%Y-%m-%d}.csv"


def da_diem_danh(path):
    if not path.exists():
        return set()
    with open(path, newline="", encoding="utf-8-sig") as f:
        return {row["ten"] for row in csv.DictReader(f)}


def ghi_diem_danh(path, ten, kc):
    moi = not path.exists()
    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if moi:
            w.writerow(["ten", "thoi_gian", "khoang_cach"])
        w.writerow([ten, datetime.now().strftime("%H:%M:%S"), f"{kc:.3f}"])


# ------------------------------ LỆNH ------------------------------
def lenh_dang_ky(args):
    ten = args.ten.strip()
    thu_muc = THU_MUC_DB / ten
    thu_muc.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        sys.exit("Không mở được camera.")
    print("SPACE: chụp ảnh | Q: thoát. Hãy xoay mặt nhẹ các góc, thay đổi ánh sáng giữa các lần chụp.")
    dem = 0
    while dem < args.so_anh:
        ok, frame = cap.read()
        if not ok:
            break
        hien = frame.copy()
        cv2.putText(hien, f"{bo_dau(ten)}: {dem}/{args.so_anh}", (10, 30), FONT, 0.8, (0, 255, 0), 2)
        cv2.imshow("Dang ky khuon mat", hien)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            break
        if k == ord(" "):
            if not lay_embedding(frame):
                print("Không thấy mặt, thử lại.")
                continue
            cv2.imwrite(str(thu_muc / f"{int(time.time() * 1000)}.jpg"), frame)
            dem += 1
            print(f"Đã lưu {dem}/{args.so_anh}")
    cap.release()
    cv2.destroyAllWindows()
    print(f"Xong. Ảnh nằm ở: {thu_muc}")


def lenh_chay(args):
    nhan, vec = nap_thu_vien()
    if len(nhan) == 0:
        sys.exit("Thư viện trống. Hãy đăng ký trước: python diem_danh.py dang-ky --ten TenSV")
    print(f"Đã nạp {len(nhan)} ảnh của {len(set(nhan))} người. Ngưỡng = {NGUONG}. Nhấn Q để thoát.")

    log = file_log()
    da = da_diem_danh(log)
    xac_nhan = defaultdict(int)

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        sys.exit("Không mở được camera.")
    dem, ket_qua = 0, []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if dem % BO_QUA_FRAME == 0:
            ket_qua = []
            for v, (x, y, w, h) in lay_embedding(frame):
                ten, kc = nhan_dien_vector(v, nhan, vec)
                if kc > NGUONG:
                    ten = None
                ket_qua.append(((x, y, w, h), ten, kc))
                if ten and ten not in da:
                    xac_nhan[ten] += 1
                    if xac_nhan[ten] >= SO_LAN_XAC_NHAN:
                        da.add(ten)
                        ghi_diem_danh(log, ten, kc)
                        print(f"[{datetime.now():%H:%M:%S}] Điểm danh: {ten} (khoảng cách {kc:.2f})")
        dem += 1

        for (x, y, w, h), ten, kc in ket_qua:
            mau = (0, 200, 0) if ten else (0, 0, 255)
            chu = f"{bo_dau(ten)} ({kc:.2f})" if ten else f"Nguoi la ({kc:.2f})"
            cv2.rectangle(frame, (x, y), (x + w, y + h), mau, 2)
            cv2.putText(frame, chu, (x, max(y - 8, 15)), FONT, 0.6, mau, 2)
        cv2.putText(frame, f"Da diem danh: {len(da)}", (10, 30), FONT, 0.8, (255, 255, 0), 2)
        cv2.imshow("Diem danh", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
    print(f"Kết quả lưu tại: {log}")


def lenh_danh_gia(args):
    nhan, vec = nap_thu_vien()
    if len(nhan) == 0:
        sys.exit("Thư viện trống, hãy đăng ký trước.")
    thu_muc = Path(args.test)
    mau = []  # (nhãn thật, tên dự đoán, khoảng cách, file)
    files = [p for p in sorted(thu_muc.glob("*/*")) if p.suffix.lower() in DUOI_ANH]
    if not files:
        sys.exit(f"Không có ảnh trong {thu_muc}/<ten>/ . Xem README để biết cấu trúc.")
    print(f"Đang đánh giá {len(files)} ảnh...")
    for p in files:
        that = p.parent.name
        res = lay_embedding(str(p))
        if not res:
            mau.append((that, None, float("inf"), str(p)))
            continue
        ten, kc = nhan_dien_vector(mat_lon_nhat(res)[0], nhan, vec)
        mau.append((that, ten, kc, str(p)))

    biet = [m for m in mau if m[0] != TEN_NGUOI_LA]
    la = [m for m in mau if m[0] == TEN_NGUOI_LA]
    print(f"Ảnh người đã đăng ký: {len(biet)} | ảnh người lạ: {len(la)}")

    hang = []
    for t in np.arange(0.20, 0.96, 0.05):
        dung = sum(1 for th, tn, kc, _ in biet if tn == th and kc <= t)
        tu_choi = sum(1 for _, _, kc, _ in biet if kc > t)
        nham = len(biet) - dung - tu_choi
        nhan_la = sum(1 for _, _, kc, _ in la if kc <= t)
        acc = dung / len(biet) if biet else 0.0
        frr = tu_choi / len(biet) if biet else 0.0
        far = nhan_la / len(la) if la else 0.0
        loi = (tu_choi + nham + nhan_la) / len(mau)
        hang.append((round(float(t), 2), acc, frr, nham / len(biet) if biet else 0.0, far, loi))

    print(f"\nModel: {MODEL} | Detector: {DETECTOR}")
    print(f"{'Nguong':>7} {'Acc':>7} {'FRR':>7} {'Nhan_nham':>10} {'FAR':>7} {'Tong_loi':>9}")
    for r in hang:
        print(f"{r[0]:>7.2f} {r[1]:>7.1%} {r[2]:>7.1%} {r[3]:>10.1%} {r[4]:>7.1%} {r[5]:>9.1%}")
    tot = min(hang, key=lambda r: r[5])
    print(f"\nNgưỡng cho tổng lỗi thấp nhất: {tot[0]} (hãy gán vào biến NGUONG)")

    with open("ket_qua_danh_gia.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["nguong", "accuracy", "FRR", "nhan_nham_nguoi", "FAR", "tong_loi"])
        w.writerows(hang)
    with open("chi_tiet_danh_gia.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["nhan_that", "du_doan", "khoang_cach", "file"])
        for th, tn, kc, p in mau:
            w.writerow([th, tn, "" if kc == float("inf") else f"{kc:.4f}", p])
    print("Đã lưu: ket_qua_danh_gia.csv, chi_tiet_danh_gia.csv")


def main():
    global NGUONG, CHONG_GIA
    ap = argparse.ArgumentParser(description="Điểm danh bằng khuôn mặt (DeepFace)")
    sub = ap.add_subparsers(dest="lenh", required=True)

    a = sub.add_parser("dang-ky", help="chụp ảnh đăng ký bằng webcam")
    a.add_argument("--ten", required=True, help="tên/MSSV, nên viết liền không dấu")
    a.add_argument("--so-anh", type=int, default=10)
    a.add_argument("--camera", type=int, default=0)

    b = sub.add_parser("chay", help="điểm danh bằng webcam")
    b.add_argument("--camera", type=int, default=0)
    b.add_argument("--nguong", type=float, default=NGUONG)

    c = sub.add_parser("danh-gia", help="đo accuracy, FAR, FRR theo ngưỡng")
    c.add_argument("--test", default="test")

    for p in (a, b, c):
        p.add_argument("--chong-gia", action="store_true", help="bật chống giả mạo (ảnh in/màn hình)")

    args = ap.parse_args()
    CHONG_GIA = args.chong_gia
    if args.lenh == "chay":
        NGUONG = args.nguong
    {"dang-ky": lenh_dang_ky, "chay": lenh_chay, "danh-gia": lenh_danh_gia}[args.lenh](args)


if __name__ == "__main__":
    main()
