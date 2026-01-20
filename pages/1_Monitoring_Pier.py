import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sectionproperties.analysis import Section
from sectionproperties.pre.library import rectangular_section

# ==========================================
# 1. KONFIGURASI DAN KONSTANTA (CONSTANTS)
# ==========================================

# Konfigurasi Geometri dan Sensor Pier
PIER_CONFIG = {
    "Pier 3A": {
        "length": 5000, "width": 2000, "part_id": "I[3111]",
        "sgs": {"SG-1": (0, 2500), "SG-2": (1000, 5000), "SG-3": (2000, 2500), "SG-4": (1000, 0)}
    },
    "Pier 3B": {
        "length": 5000, "width": 2000, "part_id": "I[3211]",
        "sgs": {"SG-5": (0, 2500), "SG-6": (1000, 5000), "SG-7": (2000, 2500), "SG-8": (1000, 0)}
    },
    "Pier 4A": {
        "length": 5000, "width": 2000, "part_id": "I[4110]",
        "sgs": {"SG-25": (0, 2500), "SG-26": (1000, 5000), "SG-27": (2000, 2500), "SG-28": (1000, 0)}
    },
    "Pier 4B": {
        "length": 5000, "width": 2000, "part_id": "I[4210]",
        "sgs": {"SG-29": (0, 2500), "SG-30": (1000, 5000), "SG-31": (2000, 2500), "SG-32": (1000, 0)}
    }
}

# Nilai Baseline Konfigurasi (Nilai awal untuk kalibrasi)
BASELINE_CONFIG = {
    "P3A": {"SG-1": 1826.46, "SG-2": 2007.78, "SG-3": 1814.90, "SG-4": 2196.52},
    "P3B": {"SG-5": 1505.90, "SG-6": 1709.25, "SG-7": 1735.80, "SG-8": 1852.26},
    "P4A": {"SG-25": 3005.54, "SG-26": 2546.30, "SG-27": 2785.18, "SG-28": 2580.93},
    "P4B": {"SG-29": 2861.34, "SG-30": 2740.62, "SG-31": 3150.29, "SG-32": 2920.12}
}

# Mapping Nama Pier
PIER_MAP_SHORT = {
    "Pier 3A": "P3A", "Pier 3B": "P3B",
    "Pier 4A": "P4A", "Pier 4B": "P4B"
}

# ==========================================
# 2. FUNGSI UTILITAS DATA (HELPER FUNCTIONS)
# ==========================================

@st.cache_data
def load_actual_strain_data(csv_path):
    """
    Memuat data strain gauge aktual dari file CSV.
    Melakukan pembersihan data dan konversi tipe data.
    """
    try:
        df = pd.read_csv(csv_path)
        # Konversi kolom DATE, dayfirst=False untuk asumsi format MM/DD/YYYY
        df['DATE'] = pd.to_datetime(df['DATE'], dayfirst=False, errors='coerce')
        
        # Pastikan kolom sensor numerik
        cols_to_numeric = ['SGA', 'SGB', 'SGC', 'SGD']
        for c in cols_to_numeric:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')
                
        # Hapus baris dengan tanggal tidak valid
        return df.dropna(subset=['DATE'])
    except Exception as e:
        st.error(f"Gagal memuat data aktual: {e}")
        return pd.DataFrame()

def get_actual_values_by_date(df, pier_short_name, selected_date, baseline_cfg):
    """
    Mengambil nilai strain aktual untuk pier dan tanggal tertentu,
    kemudian mengurangi dengan nilai baseline.
    """
    if df.empty:
        return None
        
    # Filter berdasarkan Pier dan Tanggal
    row = df[(df['PIER'] == pier_short_name) & (df['DATE'] == selected_date)]
    if row.empty:
        return None
    
    vals = row.iloc[0]
    
    # Mapping kolom generik CSV (SGA...) ke nama sensor spesifik (SG-1...)
    sg_map_generic = {
        "P3A": ["SG-1", "SG-2", "SG-3", "SG-4"],
        "P3B": ["SG-5", "SG-6", "SG-7", "SG-8"],
        "P4A": ["SG-25", "SG-26", "SG-27", "SG-28"],
        "P4B": ["SG-29", "SG-30", "SG-31", "SG-32"]
    }
    
    target_sgs = sg_map_generic.get(pier_short_name)
    if not target_sgs:
        return None

    csv_cols = ["SGA", "SGB", "SGC", "SGD"]
    result = {}
    
    for i, sg_key in enumerate(target_sgs):
        if i < len(csv_cols):
            raw_val = vals[csv_cols[i]]
            base_val = baseline_cfg.get(sg_key, 0)
            # Hitung Nilai Aktual = Raw - Baseline
            result[sg_key] = raw_val - base_val
        
    return result

@st.cache_data
def calculate_stress_history(df_gaya, list_stage, _sections_data, modulus_elastisitas):
    """
    Menghitung riwayat tegangan dan regangan teoritis untuk semua stage.
    """
    history_rows = []
    
    for stage in list_stage:
        for pier_name, data in _sections_data.items():
            sec = data['section']
            part_id = data['part']
            sgs = data['sgs']
            
            # Filter gaya berdasarkan part dan stage
            gaya_pier = df_gaya[(df_gaya['Part'] == part_id) & (df_gaya['Stage'] == stage)]
            if len(gaya_pier) == 0:
                continue
                
            N = gaya_pier["Axial (kN)"].values[0]
            My = gaya_pier["Moment-y (kN·m)"].values[0]
            Mz = gaya_pier["Moment-z (kN·m)"].values[0]
            
            # Konversi satuan ke N dan Nmm
            load_case = {"n": N * 1000, "mxx": Mz * 1e6, "myy": My * 1e6}
            
            pts = list(sgs.values())
            try:
                # Hitung tegangan di titik sensor
                results = sec.get_stress_at_points(pts=pts, **load_case)
                
                for i, (sg_name, _) in enumerate(sgs.items()):
                    sig_zz = results[i][0]
                    strain = (sig_zz / modulus_elastisitas) * 1e6
                    history_rows.append({
                        "Stage": stage,
                        "Pier": pier_name,
                        "SG": sg_name,
                        "Stress (MPa)": sig_zz,
                        "Strain (με)": strain
                    })
            except Exception:
                continue

    return pd.DataFrame(history_rows)

# ==========================================
# 3. FUNGSI VISUALISASI (PLOTTING)
# ==========================================

@st.cache_resource
def get_cached_section_geometry(length, width, mesh_scale):
    """
    Membuat objek SectionProperties dengan mesh.
    Di-cache untuk performa karena proses meshing cukup berat.
    """
    geom = rectangular_section(d=length, b=width)
    geom.create_mesh(mesh_sizes=[float(length) * mesh_scale]) 
    sec = Section(geometry=geom)
    sec.calculate_geometric_properties()
    sec.calculate_warping_properties()
    return sec

def create_mesh_plot(x_coords, y_coords, values, nodes, elements, 
                     symbol, unit, title, strain_gauges=None, strain_gauge_values=None):
    """
    Membuat plot interaktif Heatmap Mesh menggunakan Plotly.
    """
    fig = go.Figure()
    
    # Heatmap titik-titik node
    fig.add_trace(go.Scatter(
        x=x_coords, y=y_coords, mode='markers',
        marker=dict(
            size=8,
            color=values,
            colorscale='RdYlBu_r',
            colorbar=dict(title=dict(text=f"{symbol} ({unit})", side="right"), tickformat=".2f"),
            showscale=True
        ),
        text=[f"{symbol}: {v:.2f} {unit}" for v in values],
        hovertemplate="<b>Coord</b>: (%{x:.1f}, %{y:.1f})<br>%{text}<extra></extra>",
        name=title
    ))
    
    # Anotasi Sensor
    if strain_gauges:
        for name, (sg_x, sg_y) in strain_gauges.items():
            text_content = name
            if strain_gauge_values and name in strain_gauge_values:
                val = strain_gauge_values[name]
                text_content += f"<br>{val:.2f} {unit}"
                
            fig.add_annotation(
                x=sg_x, y=sg_y, text=text_content,
                font=dict(color="black", size=10),
                showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="yellow",
                ax=0, ay=-30, bgcolor="yellow", bordercolor="black", borderwidth=1, opacity=0.8
            )
            # Marker Posisi Sensor
            fig.add_trace(go.Scatter(
                x=[sg_x], y=[sg_y], mode='markers',
                marker=dict(symbol='circle', size=6, color='black'),
                name=name, hoverinfo='name+x+y'
            ))

    # Garis Mesh (Wireframe) - Dioptimalkan menjadi trace tunggal
    x_lines, y_lines = [], []
    for tri in elements:
        tri_nodes = nodes[tri]
        # Loop segitiga: 0->1->2->0
        x_tri = [tri_nodes[0, 0], tri_nodes[1, 0], tri_nodes[2, 0], tri_nodes[0, 0], None]
        y_tri = [tri_nodes[0, 1], tri_nodes[1, 1], tri_nodes[2, 1], tri_nodes[0, 1], None]
        x_lines.extend(x_tri)
        y_lines.extend(y_tri)

    fig.add_trace(go.Scatter(
        x=x_lines, y=y_lines, mode='lines',
        line=dict(color='rgba(100,100,100,0.3)', width=0.5),
        hoverinfo='skip', showlegend=False
    ))

    fig.update_layout(
        xaxis_title="x (mm)", yaxis_title="y (mm)",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        height=600, hovermode='closest', showlegend=False
    )
    return fig

def create_actual_pier_plot(config, actual_values_dict, unit, title):
    """
    Membuat visualisasi sederhana geometri pier dan lokasi sensor untuk data aktual.
    """
    length = config['length']
    width = config['width']
    sgs = config['sgs']
    
    fig = go.Figure()
    
    # Gambar Body Pier
    fig.add_shape(type="rect",
        x0=0, y0=0, x1=width, y1=length,
        line=dict(color="black", width=2),
        fillcolor="lightgrey", opacity=0.3, layer="below"
    )
    
    # Plot Lokasi Sensor
    x_vals, y_vals = [], []
    
    for sg_name, coords in sgs.items():
        if sg_name in actual_values_dict:
            val = actual_values_dict[sg_name]
            if pd.isna(val): continue
            
            x, y = coords
            x_vals.append(x)
            y_vals.append(y)
            
            # Label Anotasi
            fig.add_annotation(
                x=x, y=y,
                text=f"<b>{sg_name}</b><br>{val:.2f} {unit}",
                showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="red",
                ax=20, ay=-20, bgcolor="white", bordercolor="red", borderwidth=1, opacity=0.9,
                font=dict(size=10, color="black")
            )

    # Scatter points sensor
    if x_vals:
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals, mode='markers',
            marker=dict(color='red', size=10, line=dict(width=1, color='black')),
            hoverinfo='skip', showlegend=False
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        xaxis=dict(visible=False, range=[-800, width + 1200]),
        yaxis=dict(visible=False, range=[-500, length + 500], scaleanchor="x", scaleratio=1),
        height=500, margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        dragmode='pan'
    )
    return fig

def display_strain_gauge_table(strain_gauges, stress_values, modulus_elastisitas, title, baseline_values=None):
    """
    Menampilkan tabel metrik untuk setiap Strain Gauge (Kartu Kecil).
    """
    st.subheader(title)
    cols = st.columns(len(strain_gauges))
    
    for i, (sg_name, (x, y)) in enumerate(strain_gauges.items()):
        stress = stress_values.get(sg_name, 0)
        strain = (stress / modulus_elastisitas) * 1e6
        
        with cols[i]:
            st.markdown(f"**{sg_name}**")
            st.caption(f"Posisi: ({x}, {y}) mm")
            
            if baseline_values and sg_name in baseline_values:
                # Mode Data Aktual
                base_val = baseline_values[sg_name]
                raw_val = strain + base_val
                st.metric("Nilai Raw", f"{raw_val:.2f} με")
                st.metric("Baseline", f"{base_val:.2f} με")
                lbl_stress = "σzz (Aktual)"
                lbl_strain = "ε (Aktual)"
            else:
                # Mode Data Teoritis
                lbl_stress = "σzz (Teoritis)"
                lbl_strain = "ε (Teoritis)"
                
            st.metric(lbl_stress, f"{stress:.2f} MPa")
            st.metric(lbl_strain, f"{strain:.2f} με")

# ==========================================
# 4. KOMPONEN RENDER (RENDER COMPONENT)
# ==========================================

def render_pier_analysis(pier_name, section, load_data, strain_gauges, modulus_elastisitas, df_actual, selected_actual_date):
    """
    Merender seluruh analisis untuk satu Pier (Teoritis vs Aktual).
    """
    # [A] Analisis Teoritis (Load Case)
    N = load_data["Axial (kN)"].values[0]
    My = load_data["Moment-y (kN·m)"].values[0]
    Mz = load_data["Moment-z (kN·m)"].values[0]
    load_case = {"n": N * 1000, "mxx": Mz * 1e6, "myy": My * 1e6}

    # Hitung Stress Mesh
    case_res = section.calculate_stress(**load_case)
    sig_zz = case_res.material_groups[0].stress_result.sig_zz
    strain_zz = (sig_zz / modulus_elastisitas) * 1e6
    
    # Mesh Data
    nodes = section.mesh["vertices"]
    elements = section.mesh["triangles"]
    x_coords, y_coords = nodes[:, 0], nodes[:, 1]

    # Hitung Nilai di Titik Sensor (Teoritis)
    sg_pts = list(strain_gauges.values())
    sg_res_arr = section.get_stress_at_points(pts=sg_pts, **load_case)
    sg_stress_vals = {name: sg_res_arr[i][0] for i, name in enumerate(strain_gauges.keys())}
    sg_strain_vals = {name: (val / modulus_elastisitas) * 1e6 for name, val in sg_stress_vals.items()}

    # --- Tampilan Header & Info ---
    st.subheader("Informasi Beban & Struktur")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Stage", f"{load_data['Stage'].values[0]}")
    col2.metric("Part ID", f"{load_data['Part'].values[0]}")
    col3.metric("Gaya Aksial", f"{N:.2f} kN")
    col4.metric("Momen My", f"{My:.2f} kN·m")
    col5.metric("Momen Mz", f"{Mz:.2f} kN·m")

    # --- Visualisasi Teoritis ---
    st.markdown("#### Analisis Teoritis (Finite Element)")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Diagram Tegangan (σzz)**")
        fig = create_mesh_plot(x_coords, y_coords, sig_zz, nodes, elements, "σzz", "MPa", "Tegangan", strain_gauges, sg_stress_vals)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.write("**Diagram Regangan (ε)**")
        fig = create_mesh_plot(x_coords, y_coords, strain_zz, nodes, elements, "ε", "με", "Regangan", strain_gauges, sg_strain_vals)
        st.plotly_chart(fig, use_container_width=True)
        
    display_strain_gauge_table(strain_gauges, sg_stress_vals, modulus_elastisitas, "Detail Sensor (Teoritis)")
   
    # --- Visualisasi Aktual ---
    st.divider()
    
    if selected_actual_date and not df_actual.empty:
        short_name = PIER_MAP_SHORT.get(pier_name)
        baseline_cfg = BASELINE_CONFIG.get(short_name, {})
        actual_strain_data = get_actual_values_by_date(df_actual, short_name, selected_actual_date, baseline_cfg)
        
        if actual_strain_data:
            st.markdown(f"#### Analisis Data Aktual ({selected_actual_date.strftime('%d %b %Y %H:%M')})")
            
            # Konversi Strain Aktual ke Stress Aktual
            actual_stress_data = {k: (v / 1e6) * modulus_elastisitas for k, v in actual_strain_data.items()}
            
            ac1, ac2 = st.columns(2)
            with ac1:
                fig_stress = create_actual_pier_plot(PIER_CONFIG[pier_name], actual_stress_data, "MPa", "Tegangan Aktual (σzz)")
                st.plotly_chart(fig_stress, use_container_width=True)
            with ac2:
                fig_strain = create_actual_pier_plot(PIER_CONFIG[pier_name], actual_strain_data, "με", "Regangan Aktual (ε)")
                st.plotly_chart(fig_strain, use_container_width=True)
            
            # Filter hanya sensor yang ada datanya
            sgs_present = {k: v for k, v in strain_gauges.items() if k in actual_stress_data}
            if sgs_present:
                 display_strain_gauge_table(sgs_present, actual_stress_data, modulus_elastisitas, "Detail Sensor (Aktual)", baseline_values=baseline_cfg)
        else:
            st.warning(f"Data aktual tidak ditemukan untuk {pier_name} pada tanggal tersebut.")
    else:
        st.info("Silakan pilih Tanggal Data Aktual di sidebar untuk melihat perbandingan.")

# ==========================================
# 5. FUNGSI UTAMA (MAIN APP)
# ==========================================

def main():
    st.set_page_config(page_title="Monitoring Pier - Jembatan Sedyatmo - Kartaraja Ramp 1", layout="wide")
    st.title("Monitoring Pier - Jembatan Sedyatmo - Kartaraja Ramp 1")
    
    # --- Load Data Master ---
    try:
        df_gaya_all = pd.read_csv('data/data_gaya.csv')
        list_stage = df_gaya_all['Stage'].unique().tolist()
    except FileNotFoundError:
        st.error("File 'data/data_gaya.csv' tidak ditemukan.")
        st.stop()
        
    # --- Sidebar Configuration ---
    st.sidebar.header("Parameter Input")
    kuat_tekan_beton = st.sidebar.number_input("Kuat Tekan Beton (MPa)", value=40)
    # Default stage
    default_idx = 58 if 58 < len(list_stage) else 0
    stage = st.sidebar.selectbox("Pilih Stage Konstruksi", list_stage, index=default_idx)
    mesh_scale = st.sidebar.number_input("Mesh Scale (Resolusi)", value=50, help="Semakin kecil semakin detail tapi lambat")
    
    # Hitung E
    modulus_elastisitas = 4700 * np.sqrt(kuat_tekan_beton)
    
    st.sidebar.markdown("---")
    st.sidebar.header("Data Aktual")
    df_actual = load_actual_strain_data('data/data_gaya_aktual.csv')
    
    selected_actual_date = None
    if not df_actual.empty:
        available_dates = df_actual['DATE'].sort_values(ascending=False).unique()
        selected_actual_date = st.sidebar.selectbox("Pilih Tanggal Data Aktual", available_dates)

    # --- Persiapan Model Geometri (Cached) ---
    with st.spinner("Menyiapkan model geometri dan mesh..."):
        sections_runtime_data = {}
        for pier_name, cfg in PIER_CONFIG.items():
            sec_obj = get_cached_section_geometry(cfg["length"], cfg["width"], mesh_scale)
            sections_runtime_data[pier_name] = {
                "section": sec_obj,
                "part": cfg["part_id"],
                "sgs": cfg["sgs"]
            }

    # --- Render Tabs ---
    tab_names = list(PIER_CONFIG.keys()) + ["📈 Analisis Tren"]
    tabs = st.tabs(tab_names)
    
    # Render Pier Tabs
    for i, (pier_name, cfg) in enumerate(PIER_CONFIG.items()):
        with tabs[i]:
            st.header(f"Analisis Struktur - {pier_name}", divider="gray")
            
            # Ambil data gaya beban
            part_id = cfg["part_id"]
            gaya_current = df_gaya_all[(df_gaya_all['Part'] == part_id) & (df_gaya_all['Stage'] == stage)]
            
            if not gaya_current.empty:
                render_pier_analysis(
                    pier_name=pier_name,
                    section=sections_runtime_data[pier_name]["section"],
                    load_data=gaya_current,
                    strain_gauges=cfg["sgs"],
                    modulus_elastisitas=modulus_elastisitas,
                    df_actual=df_actual,
                    selected_actual_date=selected_actual_date
                )
            else:
                st.warning(f"Data beban tidak ditemukan untuk {pier_name} pada stage {stage}")
    
    # Render Tab Analisis Tren
    with tabs[-1]:
        st.header("Analisis Tren Historis (Teoritis)", divider="gray")
        
        with st.spinner("Menghitung data historis seluruh stage..."):
            df_history = calculate_stress_history(df_gaya_all, list_stage, sections_runtime_data, modulus_elastisitas)
            
            if not df_history.empty:
                # Plotting
                tabs_trend = st.tabs(["Grafik Tegangan", "Grafik Regangan"])
                
                with tabs_trend[0]:
                    fig_stress = px.line(df_history, x="Stage", y="Stress (MPa)", color="SG", 
                                        facet_col="Pier", facet_col_wrap=2, markers=True,
                                        title="Riwayat Tegangan Teoritis per Stage")
                    fig_stress.update_layout(height=800)
                    st.plotly_chart(fig_stress, use_container_width=True)
                    
                with tabs_trend[1]:
                    fig_strain = px.line(df_history, x="Stage", y="Strain (με)", color="SG", 
                                        facet_col="Pier", facet_col_wrap=2, markers=True,
                                        title="Riwayat Regangan Teoritis per Stage")
                    fig_strain.update_layout(height=800)
                    st.plotly_chart(fig_strain, use_container_width=True)
                    
                # Download Button
                csv = df_history.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Data Historis (CSV)",
                    data=csv,
                    file_name="analisis_tren_teoritis.csv",
                    mime="text/csv",
                    type="primary"
                )
            else:
                st.warning("Gagal menghitung data historis.")

if __name__ == "__main__":
    main()
