import streamlit as st

# ---- 1. SETUP PAGE CONFIGURATION ----
st.set_page_config(
    page_title="SHMS Jembatan Sedyatmo - Kartaraja Ramp 1",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- 2. CUSTOM STYLES (CSS) ----
def apply_custom_styles():
    st.markdown("""
    <style>
        /* Global Styles */
        .main {
            background-color: #0E1117;
        }
        h1, h2, h3 {
            font-family: 'Segoe UI', sans-serif;
            color: #FAFAFA;
        }
        
        /* Hero Section */
        .hero-container {
            text-align: center;
            padding: 4rem 2rem;
            background: linear-gradient(180deg, rgba(14,17,23,0) 0%, rgba(38,39,48,0.5) 100%);
            border-radius: 20px;
            margin-bottom: 3rem;
        }
        .hero-title {
            font-size: 3.5rem;
            font-weight: 700;
            background: -webkit-linear-gradient(120deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        .hero-subtitle {
            font-size: 1.5rem;
            color: #A0AEC0;
            margin-bottom: 2rem;
        }
        
        /* Card Styles */
        .card-container {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 2rem;
        }
        .feature-card {
            background-color: #1F2937; /* Dark gray */
            border: 1px solid #374151;
            border-radius: 16px;
            padding: 2rem;
            text-align: left;
            transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
            height: 100%;
            color: white;
        }
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            border-color: #60A5FA;
        }
        .card-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .card-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #F3F4F6;
        }
        .card-desc {
            color: #9CA3AF;
            font-size: 1rem;
            line-height: 1.5;
            margin-bottom: 1.5rem;
        }
        
        /* Button Styling Override */
        div.stButton > button {
            width: 100%;
            background-color: #2563EB;
            color: white;
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            font-weight: 600;
        }
        div.stButton > button:hover {
            background-color: #1D4ED8;
        }
    </style>
    """, unsafe_allow_html=True)

# ---- 3. UI SECTIONS ----
def render_hero_section():
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Dashboard Monitoring SHMS</div>
        <div class="hero-subtitle">Jembatan IC Sedyatmo Kartaraja (Ramp 1)</div>
    </div>
    """, unsafe_allow_html=True)

def render_navigation_cards():
    col1, col2 = st.columns(2, gap="large")
    
    # -- Card 1: Pier Monitoring --
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="card-icon">🏗️</div>
            <div class="card-title">Monitoring Pier</div>
            <div class="card-desc">
                Analisis detail integritas struktur Pier (3A, 3B, 4A, 4B) meliputi:
                <ul>
                    <li>Monitoring Tegangan & Regangan Aktual</li>
                    <li>Perbandingan dengan Data Teoritis (FEA)</li>
                    <li>Analisis Tren Historis</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Buka Dashboard Pier", icon="👉", use_container_width=True):
            st.switch_page("pages/1_Monitoring_Pier.py")
    
    # -- Card 2: Box Girder Monitoring --
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="card-icon">📦</div>
            <div class="card-title">Monitoring Box Girder</div>
            <div class="card-desc">
                Sistem pengawasan struktur Box Girder (Dalam Pengembangan):
                <ul>
                    <li>Visualisasi Geometri 3D</li>
                    <li>Mapping Sensor Strain Gauge</li>
                    <li>Analisis Performansi Penampang</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Buka Dashboard Box Girder", icon="👉", use_container_width=True):
            st.switch_page("pages/2_Monitoring_Box_Girder.py")

def render_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
        © 2026 KFT | Developed for Sedyatmo - Kartaraja Ramp 1 Project
    </div>
    """, unsafe_allow_html=True)

# ---- 4. MAIN APP LOGIC ----
def main():
    apply_custom_styles()
    render_hero_section()
    render_navigation_cards()
    render_footer()

if __name__ == "__main__":
    main()
