from sectionproperties.analysis import Section
from sectionproperties.pre.library import rectangular_section
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import plotly.express as px

#------------- 1. CONFIGURATION & HELPERS -----------#

def get_pier_config():
    """
    Mengembalikan konfigurasi statis untuk setiap pier.
    """
    return {
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

@st.cache_resource
def get_cached_section(length, width):
    """
    Membuat dan me-return Section object.
    Di-cache menggunakan st.cache_resource karena object ini statis dan berat.
    """
    geom = rectangular_section(d=length, b=width)
    geom.create_mesh(mesh_sizes=[float(length)]) # Mesh size coarseness tuned to length
    sec = Section(geometry=geom)
    sec.calculate_geometric_properties()
    sec.calculate_warping_properties()
    return sec

def create_mesh_plot(x_coords, y_coords, values, nodes, elements, 
                     symbol, unit, title, strain_gauges=None, strain_gauge_values=None):
    """
    Create an interactive Plotly mesh plot.
    """
    fig = go.Figure()
    
    # Add scatter plot for nodes with values
    fig.add_trace(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='markers',
        marker=dict(
            size=8,
            color=values,
            colorscale='RdYlBu_r',
            colorbar=dict(
                title=dict(text=f"{symbol} ({unit})", side="right"),
                tickformat=".2f"
            ),
            showscale=True
        ),
        text=[f"{symbol}: {v:.2f} {unit}" for v in values],
        hovertemplate="<b>Koordinat</b><br>" +
                      "x: %{x:.1f} mm<br>" +
                      "y: %{y:.1f} mm<br>" +
                      "%{text}<extra></extra>",
        name=title
    ))
    
    # Add strain gauge annotations if provided
    if strain_gauges:
        for name, (sg_x, sg_y) in strain_gauges.items():
            text_content = name
            if strain_gauge_values and name in strain_gauge_values:
                val = strain_gauge_values[name]
                text_content += f"<br>{val:.2f} {unit}"
                
            fig.add_annotation(
                x=sg_x,
                y=sg_y,
                text=text_content,
                font=dict(color="black", size=10),
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="black",
                ax=0,
                ay=-30,
                bgcolor="yellow",
                bordercolor="black",
                borderwidth=1,
                opacity=0.8
            )
            # Add a marker for the SG position
            fig.add_trace(go.Scatter(
                x=[sg_x],
                y=[sg_y],
                mode='markers',
                marker=dict(symbol='circle', size=6, color='black'),
                name=name,
                hoverinfo='name+x+y'
            ))

    # Draw mesh edges for visualization
    for tri in elements:
        tri_nodes = nodes[tri]
        x_tri = list(tri_nodes[:, 0]) + [tri_nodes[0, 0]]
        y_tri = list(tri_nodes[:, 1]) + [tri_nodes[0, 1]]
        fig.add_trace(go.Scatter(
            x=x_tri,
            y=y_tri,
            mode='lines',
            line=dict(color='rgba(100,100,100,0.3)', width=0.5),
            hoverinfo='skip',
            showlegend=False
        ))

    # Update layout
    fig.update_layout(
        xaxis_title="x (mm)",
        yaxis_title="y (mm)",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        height=600,
        hovermode='closest',
        showlegend=False
    )
    
    return fig

def display_statistics(values, symbol, unit, title):
    st.subheader(title)
    col1, col2, col3 = st.columns(3)
    col1.metric(f"{symbol} Maksimum", f"{np.max(values):.2f} {unit}")
    col2.metric(f"{symbol} Minimum", f"{np.min(values):.2f} {unit}")
    col3.metric(f"{symbol} Rata-rata", f"{np.mean(values):.2f} {unit}")

def display_strain_gauge_stress_table(strain_gauges, stress_values, modulus_elastisitas, title="Tegangan pada Strain Gauge"):
    st.subheader(title)
    cols = st.columns(len(strain_gauges))
    for i, (sg_name, (x, y)) in enumerate(strain_gauges.items()):
        stress = stress_values[sg_name]
        strain = (stress / modulus_elastisitas) * 1e6
        with cols[i]:
            st.markdown(f"**{sg_name}**")
            st.caption(f"Posisi: ({x} mm, {y} mm)")
            st.metric("σzz", f"{stress:.2f} MPa")
            st.metric("ε", f"{strain:.2f} με")

@st.cache_data
def calculate_history(df_gaya, list_stage, _sections_data, modulus_elastisitas):
    """
    Calculate stress/strain history for all stages.
    """
    history_rows = []
    
    for stage_idx, s in enumerate(list_stage):
        for pier_name, data in _sections_data.items():
            sec = data['section']
            part_id = data['part']
            sgs = data['sgs']
            
            # Filter forces
            gaya_pier = df_gaya[(df_gaya['Part'] == part_id) & (df_gaya['Stage'] == s)]
            if len(gaya_pier) == 0:
                continue
                
            N = gaya_pier["Axial (kN)"].values[0]
            My = gaya_pier["Moment-y (kN·m)"].values[0]
            Mz = gaya_pier["Moment-z (kN·m)"].values[0]
            load_case = {"n": N * 1000, "mxx": Mz * 1000000, "myy": My * 1000000}
            
            # Calculate Stress
            pts = list(sgs.values())
            try:
                # Use get_stress_at_points (fast calculation)
                # Returns list of tuples [(sig_zz, ...), ...], one tuple per point
                results = sec.get_stress_at_points(pts=pts, **load_case)
                
                for i, (sg_name, _) in enumerate(sgs.items()):
                    sig_zz = results[i][0]
                    strain = (sig_zz / modulus_elastisitas) * 1e6
                    history_rows.append({
                        "Stage": s,
                        "Pier": pier_name,
                        "SG": sg_name,
                        "Stress (MPa)": sig_zz,
                        "Strain (με)": strain
                    })
            except Exception as e:
                pass 

    return pd.DataFrame(history_rows)

def render_pier_analysis(pier_name, section, load_data, strain_gauges, modulus_elastisitas):
    """
    Fungsi utama untuk merender dashboard analisis per pier.
    """
    # 1. Prepare Load Case
    N = load_data["Axial (kN)"].values[0]
    My = load_data["Moment-y (kN·m)"].values[0]
    Mz = load_data["Moment-z (kN·m)"].values[0]
    load_case = {"n": N * 1000, "mxx": Mz * 1000000, "myy": My * 1000000}

    # 2. Display Info
    st.subheader("Informasi Umum")
    col1, col2 = st.columns(2)
    col1.metric("Stage", f"{load_data['Stage'].values[0]}")
    col2.metric("Part", f"{load_data['Part'].values[0]}")
    
    st.subheader("Parameter Beban")
    col1, col2, col3 = st.columns(3)
    col1.metric("Gaya Aksial (N)", f"{N:.2f} kN")
    col2.metric("Momen My", f"{My:.2f} kN·m")
    col3.metric("Momen Mz", f"{Mz:.2f} kN·m")

    # 3. Calculate Stress (Full Mesh)
    case_res = section.calculate_stress(**load_case)
    sig_zz = case_res.material_groups[0].stress_result.sig_zz
    strain_zz = (sig_zz / modulus_elastisitas) * 1e6
    
    # Mesh Coordinates
    nodes = section.mesh["vertices"]
    elements = section.mesh["triangles"]
    x_coords = nodes[:, 0]
    y_coords = nodes[:, 1]

    # 4. Calculate SG Values for Annotation
    sg_pts = list(strain_gauges.values())
    sg_res_arr = section.get_stress_at_points(pts=sg_pts, **load_case)
    sg_stress_vals = {name: sg_res_arr[i][0] for i, name in enumerate(strain_gauges.keys())}
    sg_strain_vals = {name: (sg_res_arr[i][0] / modulus_elastisitas) * 1e6 for i, name in enumerate(strain_gauges.keys())}

    # 5. Interactive Plots
    col_stress, col_strain = st.columns(2)
    with col_stress:
        st.subheader("Diagram Tegangan (σzz)")
        fig = create_mesh_plot(x_coords, y_coords, sig_zz, nodes, elements, "σzz", "MPa", "Tegangan", strain_gauges, sg_stress_vals)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_strain:
        st.subheader("Diagram Regangan (ε)")
        fig = create_mesh_plot(x_coords, y_coords, strain_zz, nodes, elements, "ε", "με", "Regangan", strain_gauges, sg_strain_vals)
        st.plotly_chart(fig, use_container_width=True)

    # 6. Statistics & Table
    display_statistics(sig_zz, "σzz", "MPa", "Statistik Tegangan")
    display_statistics(strain_zz, "ε", "με", "Statistik Regangan")
    display_strain_gauge_stress_table(strain_gauges, sg_stress_vals, modulus_elastisitas, "Tegangan Aksial pada Strain Gauge")

#------------- 2. MAIN APP FLOW -----------#

st.set_page_config(page_title="Dashboard Tegangan", layout="wide")
st.title("Dashboard Tegangan Teoritis Jembatan Sedyatmo Ramp 1")

# Load Data
df_gaya_all = pd.read_csv('data/data_gaya.csv')
list_stage = df_gaya_all['Stage'].unique().tolist()
PIER_CONFIG = get_pier_config()

# Sidebar
st.sidebar.header("Input Parameter")
kuat_tekan_beton = st.sidebar.number_input("Kuat Tekan Beton", value=40)
stage = st.sidebar.selectbox("Stage", list_stage, index=58 if 58 < len(list_stage) else 0)
modulus_elastisitas = 4700 * np.sqrt(kuat_tekan_beton)

# Pre-calculate Sections (Cached)
with st.spinner("Memuat model geometri..."):
    sections_runtime_data = {}
    for pier_name, cfg in PIER_CONFIG.items():
        sec_obj = get_cached_section(cfg["length"], cfg["width"])
        sections_runtime_data[pier_name] = {
            "section": sec_obj,
            "part": cfg["part_id"],
            "sgs": cfg["sgs"]
        }

# Render Dashboards per Pier
for pier_name, cfg in PIER_CONFIG.items():
    st.header(pier_name, divider=True)
    
    # Get Force Data
    part_id = cfg["part_id"]
    gaya_current = df_gaya_all[(df_gaya_all['Part'] == part_id) & (df_gaya_all['Stage'] == stage)]
    
    if len(gaya_current) > 0:
        render_pier_analysis(
            pier_name=pier_name,
            section=sections_runtime_data[pier_name]["section"],
            load_data=gaya_current,
            strain_gauges=cfg["sgs"],
            modulus_elastisitas=modulus_elastisitas
        )
    else:
        st.warning(f"Data gaya tidak ditemukan untuk {pier_name} pada stage {stage}")

# Trend Analysis
st.header("Analisis Tren", divider=True)
with st.spinner("Menghitung data historis..."):
    df_history = calculate_history(df_gaya_all, list_stage, sections_runtime_data, modulus_elastisitas)

    tab1, tab2 = st.tabs(["Tegangan (Stress)", "Regangan (Strain)"])
    with tab1:
        st.subheader("Tren Tegangan Aksial (σzz)")
        fig_stress = px.line(df_history, x="Stage", y="Stress (MPa)", color="SG", facet_col="Pier", facet_col_wrap=2, markers=True)
        fig_stress.update_layout(height=800)
        st.plotly_chart(fig_stress, use_container_width=True)
    with tab2:
        st.subheader("Tren Regangan (ε)")
        fig_strain = px.line(df_history, x="Stage", y="Strain (με)", color="SG", facet_col="Pier", facet_col_wrap=2, markers=True)
        fig_strain.update_layout(height=800)
        st.plotly_chart(fig_strain, use_container_width=True)
    
    st.download_button("Download Data Historis (CSV)", df_history.to_csv(index=False), "stress_strain_history.csv", "text/csv")
