# Sedyatmo Strain Gauge Monitoring Dashboard

Dashboard interaktif untuk memonitor tegangan (stress) dan regangan (strain) aktual maupun teoritis pada proyek jembatan IC Tol Sedyatmo - Kartaraja. Aplikasi ini dibangun menggunakan Python dan Streamlit.

## Fitur Utama

-   **Analisis Per Pier**: Visualisasi distribusi tegangan dan regangan pada penampang pier (Pilar 3A, 3B, 4A, 4B).
-   **Mesh Visualization**: Plot interaktif penampang beton menggunakan `plotly` dan `sectionproperties`.
-   **Strain Gauge Monitoring**: Menampilkan posisi dan nilai teoritis strain gauge pada penampang.
-   **Analisis Tren**: Grafik historis tegangan dan regangan berdasarkan data stage pengerjaan.
-   **Data Export**: Kemampuan untuk mengunduh data historis dalam format CSV.

## Struktur Direktori

```
sedyatmo_strain_gauge_monitoring_dashboard/
├── data/
│   └── data_gaya.csv       # File input data gaya dan momen
├── .conda/                 # (Opsional) Environment conda
├── main_app.py             # File utama aplikasi Streamlit
├── requirements.txt        # Daftar dependensi Python
└── README.md               # Dokumentasi proyek
```

## Persyaratan Sistem

-   Python 3.8 atau lebih baru
-   PIP (Python Package Installer)

## Instalasi

1.  **Clone atau Download** repositori ini ke komputer lokal Anda.

2.  **Buat Virtual Environment** (disarankan):
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependensi**:
    Jalankan perintah berikut untuk menginstall semua library yang dibutuhkan:
    ```bash
    pip install -r requirements.txt
    ```

## Cara Menjalankan Aplikasi

Setelah semua dependensi terinstall, jalankan aplikasi dengan perintah:

```bash
streamlit run main_app.py
```

Browser default Anda akan otomatis terbuka dan menampilkan dashboard di alamat `http://localhost:8501`.

## Troubleshooting

-   **Error `ModuleNotFoundError`**: Pastikan Anda telah mengaktifkan virtual environment dan menjalankan `pip install -r requirements.txt`.
-   **Masalah Ukuran Memori**: Perhitungan penampang (`sectionproperties`) bisa memakan memori cukup besar untuk mesh yang sangat halus. Jika aplikasi terasa lambat, coba kurangi kompleksitas mesh di kode `main_app.py`.
