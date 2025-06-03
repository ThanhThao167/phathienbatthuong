
import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import zscore
import matplotlib.pyplot as plt

st.set_page_config(page_title="Phát hiện điểm bất thường", layout="wide")
st.title("📊 Ứng dụng phát hiện học sinh có điểm bất thường")

# ===== Phần 1: File Studentscore.csv =====
st.header("1️⃣ Xử lý và phát hiện bất thường từ file Studentscore.csv")
uploaded_score = st.file_uploader("📥 Tải lên file Studentscore.csv", type=["csv"], key="score")
if uploaded_score:
    df_studentscore = pd.read_csv(uploaded_score)
    score_cols_stu = ["TX1", "TX2", "TX3", "GK", "CK"]
    st.write("✅ Các cột dữ liệu:", df_studentscore.columns.tolist())

    missing_before = df_studentscore[df_studentscore[score_cols_stu].isna().any(axis=1)]
    st.subheader("📋 Học sinh thiếu điểm trước xử lý")
    st.dataframe(missing_before)

    df_studentscore[score_cols_stu] = df_studentscore[score_cols_stu].apply(pd.to_numeric, errors="coerce")
    df_studentscore = df_studentscore.dropna(subset=score_cols_stu, how='all')
    df_studentscore[score_cols_stu] = df_studentscore[score_cols_stu].apply(lambda row: row.fillna(row.mean()), axis=1)

    df_studentscore["Diem_TB"] = df_studentscore[score_cols_stu].mean(axis=1)
    df_studentscore["zscore"] = zscore(df_studentscore["Diem_TB"])
    df_studentscore["BatThuong_Zscore"] = df_studentscore["zscore"].abs() > 2.0

    def tinh_lech_max(row):
        return max(abs(float(row[col]) - sum([row[c] for c in score_cols_stu if c != col]) / (len(score_cols_stu)-1)) for col in score_cols_stu)

    df_studentscore["Diem_Lech_Max"] = df_studentscore.apply(tinh_lech_max, axis=1)
    df_studentscore["BatThuong_LechDiem"] = df_studentscore["Diem_Lech_Max"] > 4.0
    df_studentscore["Anomaly"] = df_studentscore["BatThuong_Zscore"] | df_studentscore["BatThuong_LechDiem"]

    st.success(f"✅ Số học sinh bất thường: {df_studentscore['Anomaly'].sum()}")
    st.subheader("📋 Danh sách học sinh bất thường")
    st.dataframe(df_studentscore[df_studentscore["Anomaly"]][["MaHS", "lop"] + score_cols_stu + ["Diem_TB", "Diem_Lech_Max"]])

    st.subheader("📊 Biểu đồ số học sinh lệch điểm > 4 theo lớp")

    df_lech = df_studentscore[df_studentscore["Diem_Lech_Max"] > 4]
    if not df_lech.empty:
        fig1, ax1 = plt.subplots(figsize=(5, 3))  # nhỏ gọn
        df_lech.groupby("lop").size().sort_index().plot(kind="bar", ax=ax1, color="salmon")

        ax1.set_title("Học sinh lệch điểm > 4 theo lớp", fontsize=12)
        ax1.set_xlabel("Lớp", fontsize=10)
        ax1.set_ylabel("Số học sinh", fontsize=10)
        ax1.tick_params(axis='x', labelrotation=30, labelsize=9)
        ax1.tick_params(axis='y', labelsize=9)
        plt.tight_layout()

        col1, _ = st.columns([1, 3])  # 👈 giới hạn không gian
        with col1:
            st.pyplot(fig1)

# ===== Phần 2: File Diemtonghoplop.csv =====
st.header("2️⃣ Xử lý và phát hiện bất thường từ file Diemtonghoplop.csv")
uploaded_tonghop = st.file_uploader("📥 Tải lên file Diemtonghoplop.csv", type=["csv"], key="tonghop")
if uploaded_tonghop:
    df_diem = pd.read_csv(uploaded_tonghop)
    score_cols_diem = ["Toan", "Van", "Ly", "Hoa", "Ngoaingu", "Su", "Tin", "Sinh", "Dia"]
    st.write("✅ Các cột dữ liệu:", df_diem.columns.tolist())

    missing_before_diem = df_diem[df_diem[score_cols_diem].isna().any(axis=1)]
    st.subheader("📋 Học sinh thiếu điểm trước xử lý (Diemtonghoplop)")
    st.dataframe(missing_before_diem)

    df_diem[score_cols_diem] = df_diem[score_cols_diem].apply(pd.to_numeric, errors="coerce")
    df_diem = df_diem.dropna(subset=score_cols_diem, how='all')
    df_diem[score_cols_diem] = df_diem[score_cols_diem].apply(lambda row: row.fillna(row.mean()), axis=1)

    df_diem["Diem_TB"] = df_diem[score_cols_diem].mean(axis=1)
    df_diem["zscore"] = zscore(df_diem["Diem_TB"])
    df_diem["BatThuong_Zscore"] = df_diem["zscore"].abs() > 2.0

    def tinh_lech_max_diem(row):
        return max(abs(float(row[col]) - sum([row[c] for c in score_cols_diem if c != col]) / (len(score_cols_diem)-1)) for col in score_cols_diem)

    df_diem["Diem_Lech_Max"] = df_diem.apply(tinh_lech_max_diem, axis=1)
    df_diem["BatThuong_LechDiem"] = df_diem["Diem_Lech_Max"] > 4.0
    df_diem["Anomaly"] = df_diem["BatThuong_Zscore"] | df_diem["BatThuong_LechDiem"]

    st.success(f"✅ Số học sinh bất thường: {df_diem['Anomaly'].sum()}")
    st.subheader("📋 Danh sách học sinh bất thường (Diemtonghoplop)")
    st.dataframe(df_diem[df_diem["Anomaly"]][["MaHS", "lop"] + score_cols_diem + ["Diem_TB", "Diem_Lech_Max"]])
    
    st.subheader("📊 Biểu đồ số học sinh lệch điểm > 4 theo môn học")

    def mon_lech_nhat_diem(row):
        diffs = {
            col: abs(float(row[col]) - sum([row[c] for c in score_cols_diem if c != col]) / (len(score_cols_diem)-1))
            for col in score_cols_diem
        }
        return max(diffs, key=diffs.get)

    df_diem["Mon_Lech_Max"] = df_diem.apply(mon_lech_nhat_diem, axis=1)
    df_lech_cao_diem = df_diem[df_diem["Diem_Lech_Max"] > 4]

    if not df_lech_cao_diem.empty:
        fig2, ax2 = plt.subplots(figsize=(5, 3))  # 👈 nhỏ gọn hơn
        df_lech_cao_diem["Mon_Lech_Max"].value_counts().sort_index().plot(kind="bar", color="orange", ax=ax2)
        ax2.set_xlabel("Môn học", fontsize=10)
        ax2.set_ylabel("Số học sinh", fontsize=10)
        ax2.set_title("Học sinh lệch điểm > 4 theo môn học", fontsize=12)
        ax2.tick_params(axis='x', labelrotation=30, labelsize=9)
        ax2.tick_params(axis='y', labelsize=9)
        plt.tight_layout()
        col2, _ = st.columns([1, 3])  # 👈 giới hạn không gian hiển thị
        with col2:
            st.pyplot(fig2)

    