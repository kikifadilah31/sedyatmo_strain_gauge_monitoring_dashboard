# Dashboard Monitoring SHMS - Jembatan Sedyatmo (Ramp 1)

Platform monitoring kesehatan struktur (Structural Health Monitoring System) untuk Jembatan IC Sedyatmo - Kartaraja. Aplikasi ini dirancang untuk memantau integritas struktur Pier dan Box Girder melalui visualisasi data sensor strain gauge, baik secara aktual (real-time/historis) maupun teoritis (analisis elemen hingga).

## 🚀 Fitur Utama

### 1. Multi-Page Application
Aplikasi menggunakan arsitektur modern dengan navigasi intuitif:
- **Home (`Home.py`)**: Landing page profesional sebagai pusat kendali.
- **Monitoring Pier (`pages/1_Monitoring_Pier.py`)**: Dashboard analisis mendalam untuk pilar jembatan.
- **Monitoring Box Girder (`pages/2_Monitoring_Box_Girder.py`)**: (Dalam Pengembangan) Modul untuk struktur bentang atas.

### 2. Analisis Per Pier
Dashboard mendetail untuk **Pier 3A, 3B, 4A, dan 4B**:
- **Visualisasi Geometri**: Menampilkan penampang pier menggunakan mesh elements (`sectionproperties`).
- **Peta Panas (Heatmap)**: Distribusi tegangan ($\sigma_{zz}$) dan regangan ($\epsilon$) teoritis akibat beban aksial dan momen.
- **Data Sensor Aktual vs Teoritis**:
    - Perbandingan side-by-side antara kalkulasi FEA dan pembacaan sensor lapangan.
    - Konversi otomatis dari data Raw ($\mu\epsilon$) ke Tegangan Aktual (MPa).
- **Tabel Data**: Rincian nilai strain gauge dengan label yang jelas (Teoritis vs Aktual).

### 3. Analisis Tren Historis
- Visualisasi grafik garis interaktif menggunakan `Plotly`.
- Melacak perubahan tegangan dan regangan di setiap tahap konstruksi (Stage).
- **Ekspor Data**: Fitur unduh data riwayat analisis ke format CSV (`analisis_tren_teoritis.csv`).

---

## 📂 Struktur Direktori

```plaintext
sedyatmo_strain_gauge_monitoring_dashboard/
├── Home.py                     # Entry point (Landing Page)
├── pages/
│   ├── 1_Monitoring_Pier.py    # Logika Dashboard Pier
│   └── 2_Monitoring_Box_Girder.py # Placeholder Box Girder
├── data/
│   ├── data_gaya.csv           # Input data beban (Gaya & Momen) per Stage
│   └── data_gaya_aktual.csv    # Input data pembacaan sensor aktual
├── requirements.txt            # Dependensi Python
└── README.md                   # Dokumentasi
```

---

## 🛠️ Instalasi & Penggunaan

### Prasyarat
- Python 3.9+
- PIP (Python Package Manager)

### Langkah Instalasi
1.  **Clone Repositori** atau unduh source code.
2.  **Buat Virtual Environment** (Rekomendasi):
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```
3.  **Install Library**:
    ```bash
    pip install -r requirements.txt
    ```

### Menjalankan Aplikasi
Gunakan perintah berikut untuk memulai server Streamlit:

```bash
streamlit run Home.py
```

Aplikasi akan otomatis terbuka di browser pada `http://localhost:8501`.

---

## ℹ️ Catatan Teknis

- **Baseline Config**: Nilai awal (raw) sensor disimpan dalam konfigurasi statis (`BASELINE_CONFIG`) untuk perhitungan nilai aktual yang akurat.
- **Mesh Optimization**: Skala mesh dioptimalkan untuk performa rendering web tanpa mengurangi akurasi visual yang signifikan.
- **Refactoring**: Kode telah direfaktor menggunakan standar PEP8, dengan pemisahan fungsi logika, UI, dan data helpers untuk kemudahan pemeliharaan (maintainability).

---

**Dikembangkan oleh KFT**
