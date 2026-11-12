import io
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

# Cấu hình trang
st.set_page_config(
    page_title="Hệ Thống Điểm Danh Bằng Khuôn Mặt",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

THU_MUC_LOG = Path("diem_danh")
THU_MUC_DB = Path("my_db")
FILE_DANH_SACH_LOP = Path("danh_sach_lop.csv")

st.markdown("""
<style>
    .main-title {
        font-size: 26px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 4px;
    }
    .sub-title {
        font-size: 14px;
        color: #4B5563;
        margin-bottom: 18px;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎓 HỆ THỐNG ĐIỂM DANH SINH VIÊN BẰNG KHUÔN MẶT</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Đồ án Capstone AI - Samsung Innovation Campus (SIC) | DeepFace & ArcFace</div>', unsafe_allow_html=True)


def load_danh_sach_lop():
    if FILE_DANH_SACH_LOP.exists():
        try:
            return pd.read_csv(FILE_DANH_SACH_LOP, encoding="utf-8")
        except Exception:
            return pd.read_csv(FILE_DANH_SACH_LOP, encoding="utf-8-sig")
    return pd.DataFrame(columns=["mssv", "ho_ten", "ten_dang_ky"])


def load_nhat_ky_diem_danh(ngay_str):
    file_path = THU_MUC_LOG / f"diem_danh_{ngay_str}.csv"
    if file_path.exists():
        try:
            return pd.read_csv(file_path, encoding="utf-8-sig")
        except Exception:
            try:
                return pd.read_csv(file_path, encoding="utf-8")
            except Exception:
                return pd.DataFrame(columns=["ten", "thoi_gian", "khoang_cach"])
    return pd.DataFrame(columns=["ten", "thoi_gian", "khoang_cach"])


# Sidebar
st.sidebar.header("⚙️ Tuỳ chọn & Ngày điểm danh")
hom_nay = datetime.now().strftime("%Y-%m-%d")

# Tìm các ngày đã có log
ds_ngay = []
if THU_MUC_LOG.exists():
    for f in sorted(THU_MUC_LOG.glob("diem_danh_*.csv"), reverse=True):
        ten_ngay = f.stem.replace("diem_danh_", "")
        if ten_ngay not in ds_ngay:
            ds_ngay.append(ten_ngay)

if hom_nay not in ds_ngay:
    ds_ngay.insert(0, hom_nay)

ngay_chon = st.sidebar.selectbox("📅 Chọn ngày xem báo cáo:", ds_ngay, index=0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Lệnh điều khiển nhanh")
st.sidebar.code("python diem_danh.py chay", language="powershell")
st.sidebar.code("python diem_danh.py chay --chong-gia", language="powershell")

tab1, tab2, tab3 = st.tabs(["📋 Báo Cáo & Đối Soát Điểm Danh", "📊 Đánh Giá Mô Hình AI", "👥 Quản Lý Danh Sách & Khuôn Mặt"])

# TAB 1: BÁO CÁO & ĐỐI SOÁT
with tab1:
    col_left, col_right = st.columns([3, 1])
    with col_left:
        st.subheader(f"📌 Bảng điểm danh ngày: `{ngay_chon}`")
    with col_right:
        if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
            st.rerun()

    df_lop = load_danh_sach_lop()
    df_log = load_nhat_ky_diem_danh(ngay_chon)

    if df_lop.empty:
        st.warning("⚠️ Chưa có danh sách lớp! Vui lòng kiểm tra file `danh_sach_lop.csv`.")
    else:
        # Đối soát danh sách lớp với nhật ký điểm danh
        ds_da_diem_danh = {}
        if not df_log.empty and "ten" in df_log.columns:
            for _, r in df_log.iterrows():
                ds_da_diem_danh[str(r["ten"])] = {
                    "thoi_gian": r.get("thoi_gian", "--"),
                    "khoang_cach": r.get("khoang_cach", "--")
                }

        ket_qua = []
        for i, row in df_lop.iterrows():
            ten_dk = str(row["ten_dang_ky"])
            co_mat = ten_dk in ds_da_diem_danh
            info = ds_da_diem_danh.get(ten_dk, {})
            tg = str(info.get("thoi_gian", "--")) if co_mat else "--"
            kc_val = info.get("khoang_cach", "--")
            kc_str = f"{float(kc_val):.3f}" if (co_mat and str(kc_val) != "--") else "--"

            ket_qua.append({
                "STT": i + 1,
                "MSSV": str(row["mssv"]),
                "Họ và Tên": str(row["ho_ten"]),
                "Tên Đăng Ký": ten_dk,
                "Trạng Thái": "✅ Có mặt" if co_mat else "❌ Vắng mặt",
                "Thời Gian": tg,
                "Khoảng Cách (Cosine)": kc_str,
            })

        df_kq = pd.DataFrame(ket_qua)
        df_kq = df_kq.astype(str)
        df_kq["STT"] = pd.to_numeric(df_kq["STT"])
        tong_sv = len(df_kq)
        co_mat_count = sum(1 for r in ket_qua if "Có mặt" in r["Trạng Thái"])
        vang_count = tong_sv - co_mat_count
        ti_le = (co_mat_count / tong_sv * 100) if tong_sv > 0 else 0

        # Thống kê số liệu nhanh
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tổng số sinh viên", f"{tong_sv}")
        m2.metric("Số lượng có mặt", f"{co_mat_count}", delta=f"{co_mat_count} SV")
        m3.metric("Số lượng vắng mặt", f"{vang_count}", delta=f"-{vang_count} SV" if vang_count > 0 else "0", delta_color="inverse")
        m4.metric("Tỉ lệ chuyên cần", f"{ti_le:.1f}%")

        # Hiển thị biểu đồ Có mặt vs Vắng mặt
        st.markdown("##### 📈 Tỷ lệ chuyên cần trực quan")
        df_chart = pd.DataFrame({
            "Trạng thái": ["Có mặt", "Vắng mặt"],
            "Số lượng": [co_mat_count, vang_count]
        })
        st.bar_chart(df_chart.set_index("Trạng thái"), color="#2563EB")

        # Tô màu trạng thái bảng
        def highlight_status(val):
            if "Có mặt" in str(val):
                return "background-color: #D1FAE5; color: #065F46; font-weight: bold;"
            elif "Vắng mặt" in str(val):
                return "background-color: #FEE2E2; color: #991B1B; font-weight: bold;"
            return ""

        st.dataframe(
            df_kq.style.map(highlight_status, subset=["Trạng Thái"]),
            use_container_width=True,
            hide_index=True,
        )

        # Xuất file Excel / CSV
        st.markdown("### 📥 Xuất báo cáo điểm danh")
        c_exp1, c_exp2 = st.columns(2)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_kq.to_excel(writer, index=False, sheet_name=f"DiemDanh_{ngay_chon}")
        buffer.seek(0)

        with c_exp1:
            st.download_button(
                label="📗 Tải về file Excel (.xlsx)",
                data=buffer,
                file_name=f"Bao_Cao_Diem_Danh_{ngay_chon}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with c_exp2:
            csv_data = df_kq.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📄 Tải về file CSV",
                data=csv_data,
                file_name=f"Bao_Cao_Diem_Danh_{ngay_chon}.csv",
                mime="text/csv",
                use_container_width=True
            )

# TAB 2: ĐÁNH GIÁ MÔ HÌNH AI
with tab2:
    st.subheader("📊 Kết Quả Đánh Giá & Thử Nghiệm Mô Hình (Model Evaluation)")
    file_eval = Path("ket_qua_danh_gia.csv")
    file_detail = Path("chi_tiet_danh_gia.csv")

    if file_eval.exists():
        df_eval = pd.read_csv(file_eval, encoding="utf-8-sig")

        # Metrics tổng quan mô hình tối ưu
        best_row = df_eval.loc[df_eval["tong_loi"].idxmin()]
        opt_nguong = best_row["nguong"]
        opt_acc = best_row["accuracy"] * 100
        opt_far = best_row["FAR"] * 100
        opt_frr = best_row["FRR"] * 100
        opt_err = best_row["tong_loi"] * 100

        st.success(f"🎯 **Cấu hình tối ưu đề xuất:** Model **ArcFace** | Ngưỡng Cosine: **{opt_nguong}** | Độ chính xác đạt **{opt_acc:.1f}%** | Tổng lỗi thấp nhất: **{opt_err:.1f}%**")

        e1, e2, e3, e4 = st.columns(4)
        e1.metric("Độ chính xác (Accuracy)", f"{opt_acc:.1f}%")
        e2.metric("Tỉ lệ từ chối sai (FRR)", f"{opt_frr:.1f}%")
        e3.metric("Tỉ lệ nhận nhầm (FAR)", f"{opt_far:.1f}%")
        e4.metric("Ngưỡng tối ưu", f"{opt_nguong}")

        st.markdown("##### 📈 Biểu đồ đánh đổi giữa FAR, FRR và Độ chính xác (Accuracy) theo Ngưỡng")
        chart_data = df_eval.set_index("nguong")[["accuracy", "FRR", "FAR", "tong_loi"]]
        st.line_chart(chart_data)

        st.markdown("##### 📋 Bảng số liệu chi tiết theo từng ngưỡng đo:")
        df_display = df_eval.copy()
        for col in ["accuracy", "FRR", "nhan_nham_nguoi", "FAR", "tong_loi"]:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: f"{x*100:.1f}%")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        if file_detail.exists():
            st.markdown("##### 🔍 Chi tiết các mẫu kiểm thử (chi_tiet_danh_gia.csv)")
            df_det = pd.read_csv(file_detail, encoding="utf-8-sig").fillna("").astype(str)
            st.dataframe(df_det.head(15), use_container_width=True, hide_index=True)
    else:
        st.info("💡 Bạn chưa có file kết quả đánh giá.")

# TAB 3: QUẢN LÝ
with tab3:
    st.subheader("👥 Quản Lý Danh Sách & Khuôn Mặt")
    c_m1, c_m2 = st.columns(2)

    with c_m1:
        st.markdown("#### 📁 Dữ liệu khuôn mặt đã đăng ký (`my_db/`)")
        if THU_MUC_DB.exists():
            nguoi_list = [d.name for d in THU_MUC_DB.iterdir() if d.is_dir()]
            for n in nguoi_list:
                so_anh = len(list((THU_MUC_DB / n).glob("*.jpg")))
                st.write(f"- 👤 **{n}**: Đã lưu `{so_anh}` ảnh góc mặt")
        else:
            st.write("Chưa có thư mục `my_db`.")

    with c_m2:
        st.markdown("#### 📝 Danh sách sinh viên cả lớp (`danh_sach_lop.csv`)")
        st.dataframe(load_danh_sach_lop(), use_container_width=True, hide_index=True)
