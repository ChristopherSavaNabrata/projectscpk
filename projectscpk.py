import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# KONFIGURASI HALAMAN UTAMA STREAMLIT
# ==========================================
st.set_page_config(page_title="SPK Pemilihan Komoditas Tanam", layout="wide")

# 1. LOAD DATASET
@st.cache_data
def load_data():
    df = pd.read_csv('Crop_recommendation.csv')
    return df

df = load_data()

# 2. SIDEBAR NAVIGASI STANDARD
st.sidebar.title("Navigasi")
page = st.sidebar.selectbox("Pilih Halaman:", ["Dataset & Analisis", "Perhitungan SAW", "Profil Kelompok"])


# ==========================================
# --- HALAMAN 1: DATASET & ANALISIS ---
# ==========================================
if page == "Dataset & Analisis":
    st.title("📊 Dataset & Analisis Data")
    st.write("Menampilkan data awal karakteristik lahan untuk berbagai komoditas tanam.")
    
    # Tampilan Dataset Utama
    st.subheader("Raw Data")
    st.dataframe(df.head(2200), use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Analisis Data Menggunakan 3 Grafik Utama")
    
    # --- GRAFIK 1: GROUPED BAR CHART ---
    st.subheader("1. Rata-Rata Kebutuhan Unsur Hara (N, P, K) per Komoditas Tanam")
    st.write("Grafik batang kelompok ini membandingkan rata-rata nilai kandungan hara Nitrogen, Fosfor, dan Kalium untuk seluruh alternatif tanaman.")
    
    df_summary = df.groupby('label')[['N', 'P', 'K']].mean().reset_index()
    # Mengubah struktur data agar format kolom mencocokkan visualisasi grouped bar
    df_melted = pd.melt(df_summary, id_vars=['label'], value_vars=['N', 'P', 'K'], 
                        var_name='Unsur Hara', value_name='Nilai Rata-rata')
    
    fig1, ax1 = plt.subplots(figsize=(14, 6))
    sns.barplot(x='label', y='Nilai Rata-rata', hue='Unsur Hara', data=df_melted, palette='Set2', ax=ax1)
    plt.xticks(rotation=90)
    ax1.set_xlabel("Jenis Komoditas Tanaman")
    ax1.set_ylabel("Nilai Kandungan")
    st.pyplot(fig1)

    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # Grafik 2: Heatmap Hubungan Multivariat (Korelasi antar kriteria)
        st.subheader("2. Korelasi Antar Kriteria (Heatmap)")
        fig2, ax2 = plt.subplots()
        sns.heatmap(df.drop('label', axis=1).corr(), annot=True, cmap='coolwarm', ax=ax2)
        ax2.xaxis.tick_top()
        ax2.tick_params(axis='x', rotation=90)
        st.pyplot(fig2)

    with col2:
        # Grafik 3: Histogram Sebaran Univariat (Curah Hujan)
        st.subheader("3. Sebaran Distribusi Curah Hujan (Histogram)")
        fig3, ax3 = plt.subplots()
        sns.histplot(df['rainfall'], kde=True, color='teal', ax=ax3)
        ax3.set_xlabel("Curah Hujan (mm)")
        ax3.set_ylabel("Frekuensi")
        st.pyplot(fig3)


# ==========================================
# --- HALAMAN 2: PERHITUNGAN SAW ---
# ==========================================
elif page == "Perhitungan SAW":
    st.title("🧮 Perhitungan Metode SAW")
    
    # Pengaturan Bobot di Halaman Utama
    st.subheader("⚖️ Pengaturan Bobot Kriteria")
    st.write("Tentukan bobot prioritas untuk masing-masing kriteria. **Total keseluruhan bobot harus bernilai 1.0.**")
    
    with st.container(border=True):
        bw1, bw2, bw3, bw4 = st.columns(4)
        with bw1:
            w_n = st.number_input("Bobot Nitrogen (N)", 0.0, 1.0, 0.15, step=0.05)
            w_p = st.number_input("Bobot Fosfor (P)", 0.0, 1.0, 0.15, step=0.05)
        with bw2:
            w_k = st.number_input("Bobot Kalium (K)", 0.0, 1.0, 0.15, step=0.05)
            w_temp = st.number_input("Bobot Suhu", 0.0, 1.0, 0.15, step=0.05)
        with bw3:
            w_hum = st.number_input("Bobot Kelembapan", 0.0, 1.0, 0.15, step=0.05)
            w_ph = st.number_input("Bobot pH", 0.0, 1.0, 0.10, step=0.05)
        with bw4:
            w_rain = st.number_input("Bobot Curah Hujan", 0.0, 1.0, 0.15, step=0.05)
            
            total_bobot = round(w_n + w_p + w_k + w_temp + w_hum + w_ph + w_rain, 2)
            if total_bobot == 1.0:
                st.markdown(f"**Total Bobot Saat Ini:** :green[{total_bobot}] (Siap)")
            else:
                st.markdown(f"**Total Bobot Saat Ini:** :red[{total_bobot}] (Harus 1.0)")

    st.markdown("---")

    # Input Karakteristik Lahan Aktual (Widget Sinkron)
    st.subheader("🌱 Input Kondisi Lahan Aktual")
    st.write("Gunakan slider atau isi angka di bawahnya. Keduanya akan otomatis berubah bersamaan!")

    if 'n' not in st.session_state: st.session_state['n'] = 80
    if 'p' not in st.session_state: st.session_state['p'] = 45
    if 'k' not in st.session_state: st.session_state['k'] = 40
    if 'temp' not in st.session_state: st.session_state['temp'] = 25.0
    if 'hum' not in st.session_state: st.session_state['hum'] = 80.0
    if 'ph' not in st.session_state: st.session_state['ph'] = 6.5
    if 'rain' not in st.session_state: st.session_state['rain'] = 200.0

    def sync_widgets(from_key, to_key):
        st.session_state[to_key] = st.session_state[from_key]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### Nitrogen (N) & Fosfor (P)")
        st.slider("Slider Kandungan Nitrogen (N)", 0, 150, key="slider_n", value=st.session_state['n'], on_change=sync_widgets, args=("slider_n", "n"))
        in_n = st.number_input("Number Input Kandungan Nitrogen (N)", min_value=0, max_value=150, key="n", on_change=sync_widgets, args=("n", "slider_n"))
        st.write("") 
        st.slider("Slider Kandungan Fosfor (P)", 5, 145, key="slider_p", value=st.session_state['p'], on_change=sync_widgets, args=("slider_p", "p"))
        in_p = st.number_input("Number Input Kandungan Fosfor (P)", min_value=5, max_value=145, key="p", on_change=sync_widgets, args=("p", "slider_p"))

    with c2:
        st.markdown("### Kalium (K) & Suhu")
        st.slider("Slider Kandungan Kaluim (K)", 5, 205, key="slider_k", value=st.session_state['k'], on_change=sync_widgets, args=("slider_k", "k"))
        in_k = st.number_input("Number Input Kandungan Kalium (K)", min_value=5, max_value=205, key="k", on_change=sync_widgets, args=("k", "slider_k"))
        st.write("")
        st.slider("Slider Suhu (°C)", 8.0, 45.0, key="slider_temp", value=st.session_state['temp'], on_change=sync_widgets, args=("slider_temp", "temp"))
        in_temp = st.number_input("Number Input Suhu (°C)", min_value=8.0, max_value=45.0, key="temp", on_change=sync_widgets, args=("temp", "slider_temp"))

    with c3:
        st.markdown("### Kelembapan & pH")
        st.slider("Slider Kelembapan (%)", 14.0, 100.0, key="slider_hum", value=st.session_state['hum'], on_change=sync_widgets, args=("slider_hum", "hum"))
        in_hum = st.number_input("Number Input Kelembapan (%)", min_value=14.0, max_value=100.0, key="hum", on_change=sync_widgets, args=("hum", "slider_hum"))
        st.write("")
        st.slider("Slider pH Tanah", 3.5, 10.0, key="slider_ph", value=st.session_state['ph'], on_change=sync_widgets, args=("slider_ph", "ph"))
        in_ph = st.number_input("Number Input pH Tanah", min_value=3.5, max_value=10.0, key="ph", on_change=sync_widgets, args=("ph", "slider_ph"))

    st.markdown("---")
    st.slider("Slider Curah Hujan (mm)", 20.0, 300.0, key="slider_rain", value=st.session_state['rain'], on_change=sync_widgets, args=("slider_rain", "rain"))
    in_rain = st.number_input("Number Input Curah Hujan (mm)", min_value=20.0, max_value=300.0, key="rain", on_change=sync_widgets, args=("rain", "slider_rain"))

    # Tombol Hitung Rumus SAW
    if st.button("Hitung Rekomendasi"):
        if not np.isclose(total_bobot, 1.0):
            st.error(f"❌ Perhitungan Gagal! Total bobot harus 1.0 (Total saat ini: {total_bobot}).")
        else:
            ideal_profile = df.groupby('label').mean()
            user_input = np.array([in_n, in_p, in_k, in_temp, in_hum, in_ph, in_rain])
            decision_matrix = np.clip(abs(ideal_profile - user_input), 0.0001, None)
            min_values = decision_matrix.min()
            normalized_matrix = min_values / decision_matrix
            weights = np.array([w_n, w_p, w_k, w_temp, w_hum, w_ph, w_rain])
            final_scores = normalized_matrix.dot(weights)
            ranking = final_scores.sort_values(ascending=False).reset_index()
            ranking.columns = ['Alternatif Tanaman', 'Skor Akhir (V)']

            st.success("Berhasil menghitung rekomendasi!")
            st.subheader("🏆 Hasil Perangkingan")
            st.table(ranking.head(10))

            st.subheader("Visualisasi Skor Alternatif Top 10")
            fig4, ax4 = plt.subplots()
            sns.barplot(x='Skor Akhir (V)', y='Alternatif Tanaman', data=ranking.head(10), palette='viridis', ax=ax4)
            st.pyplot(fig4)


# ==========================================
# --- HALAMAN 3: PROFIL KELOMPOK ---
# ==========================================
elif page == "Profil Kelompok":
    st.title("👥 Profil Kelompok")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Nama:** Daniel Requel")
        st.markdown("**NIM:** 123240134")
        st.markdown("**Kelas:** IF-A Informatika")

    with col2:
        st.markdown("**Nama:** Christopher Sava Nabrata")
        st.markdown("**NIM:** 123240140")
        st.markdown("**Kelas:** IF-A Informatika")