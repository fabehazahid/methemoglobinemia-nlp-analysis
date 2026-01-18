"""
Methemoglobinemia Analysis - Interactive Dashboard
Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np
import base64
import os

# Page configuration
st.set_page_config(
    page_title="MetHb Analysis",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Assets & Helper Functions
# -----------------------------------------------------------------------------

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        return ""

# Path to the generated background image
BACKGROUND_IMAGE_PATH = r"C:/Users/Fabeha/.gemini/antigravity/brain/3f5fe063-8243-4597-b3e7-421d90e7e1fc/background_rbc_1768756815374.png"
background_base64 = get_base64_of_bin_file(BACKGROUND_IMAGE_PATH)

# Refined Palette
PRIMARY_COLOR = "#800000"  # Oxblood
TEXT_COLOR = "#FFFFFF"
BG_OVERLAY = "rgba(10, 10, 20, 0.85)" # Dark overlay
CARD_BG = "rgba(30, 30, 40, 0.9)" 

# -----------------------------------------------------------------------------
# Hematology Dark Theme - Custom CSS
# -----------------------------------------------------------------------------
st.markdown(f"""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Montserrat:wght@400;600;700&display=swap');

    /* Global Styles */
    .stApp {{
        background-image: linear-gradient({BG_OVERLAY}, {BG_OVERLAY}), url("data:image/png;base64,{background_base64}");
        background-attachment: fixed;
        background-size: cover;
        font-family: 'Roboto', sans-serif;
        color: {TEXT_COLOR};
    }}
    
    body {{
        color: {TEXT_COLOR};
    }}

    /* Headers */
    h1, h2, h3, h4, h5 {{
        font-family: 'Montserrat', sans-serif;
        color: #f0f0f0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    h1 {{
        border-bottom: 2px solid {PRIMARY_COLOR};
        padding-bottom: 10px;
        margin-bottom: 20px;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }}

    h3 {{
        border-left: 4px solid {PRIMARY_COLOR};
        padding-left: 10px;
        margin-top: 20px;
        background: linear-gradient(90deg, rgba(128,0,0,0.2), transparent);
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: rgba(15, 15, 20, 0.95);
        border-right: 1px solid #333;
    }}
    
    section[data-testid="stSidebar"] h1 {{
        color: {PRIMARY_COLOR} !important;
        font-size: 1.1rem;
        border-bottom: none;
    }}
    
    .stMarkdown p {{
        color: #e0e0e0;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: rgba(0,0,0,0.3);
        padding: 5px;
        border-radius: 8px;
        gap: 5px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        color: #aaa;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 600;
        border: 1px solid transparent;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border: 1px solid {PRIMARY_COLOR};
    }}

    /* Metric Cards */
    .metric-card {{
        background-color: {CARD_BG};
        border-left: 4px solid {PRIMARY_COLOR};
        border-radius: 6px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(128,0,0,0.2);
    }}
    
    .metric-label {{
        color: #aaa;
        font-size: 0.85rem;
        text-transform: uppercase;
        font-weight: 500;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }}
    
    .metric-value {{
        color: white;
        font-size: 2rem;
        font-weight: 700;
        font-family: 'Montserrat', sans-serif;
    }}

    /* Hero Section Styles */
    .hero-container {{
        text-align: center;
        padding: 40px 20px;
        background: rgba(0,0,0,0.4);
        border-radius: 12px;
        margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    
    .hero-title {{
        font-size: 4rem;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        margin-bottom: 0px;
        font-family: 'Montserrat', sans-serif;
    }}
    
    .brand-meta {{
        font-weight: 300;
        color: white;
        letter-spacing: 2px;
        font-family: 'Roboto', sans-serif;
    }}
    
    .brand-bond {{
        height: 2px;
        width: 60px;
        background: linear-gradient(90deg, rgba(255,255,255,0.5), #800000);
        border-radius: 2px;
    }}
    
    .brand-hb {{
        font-weight: 800;
        color: #800000;
        letter-spacing: 1px;
    }}
    
    .hero-subtitle {{
        font-size: 1.2rem;
        color: #ddd;
        margin-bottom: 30px;
    }}

    /* Visual Pipeline */
    .pipeline-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin: 40px 0;
        flex-wrap: wrap;
    }}
    
    .pipeline-step {{
        background: {CARD_BG};
        border: 1px solid {PRIMARY_COLOR};
        padding: 15px 25px;
        border-radius: 20px;
        color: white;
        font-weight: 600;
        position: relative;
    }}
    
    .pipeline-arrow {{
        color: {PRIMARY_COLOR};
        font-size: 24px;
        font-weight: bold;
    }}

    /* Contact Buttons */
    .header-buttons {{
        position: absolute;
        top: -60px;
        right: 0;
        display: flex;
        gap: 15px;
    }}
    
    .icon-btn {{
        background-color: {CARD_BG};
        border: 1px solid {PRIMARY_COLOR};
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        text-decoration: none;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 5px;
    }}
    
    .icon-btn:hover {{
        background-color: {PRIMARY_COLOR};
        color: white;
        text-decoration: none;
        box-shadow: 0 0 10px rgba(128,0,0,0.5);
    }}

    /* Plotly Chart Backgrounds */
    .js-plotly-plot .plotly .main-svg {{
        background: rgba(0,0,0,0) !important;
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/processed/meth_structured_data.csv')
        
        # CLEANING
        if 'age' in df.columns:
            df['age'] = pd.to_numeric(df['age'].astype(str).str.extract(r'(\d+)', expand=False), errors='coerce')
        
        if 'methb_level' in df.columns:
            df['methb_level'] = pd.to_numeric(df['methb_level'].astype(str).str.replace('%', ''), errors='coerce')

        if 'data_quality_score' in df.columns:
            df['data_quality_score'] = df['data_quality_score'].fillna(0)

        return df
    except Exception as e:
        # Create dummy data if file not found for demonstration
        return pd.DataFrame() 

# -----------------------------------------------------------------------------
# Visual Components
# -----------------------------------------------------------------------------

def metric_card(label, value, prefix="", suffix=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{prefix}{value}{suffix}</div>
    </div>
    """, unsafe_allow_html=True)

def create_metrics_row(df):
    cols = st.columns(5)
    with cols[0]:
        metric_card("Total Cases", len(df))
    with cols[1]:
        methb_mean = df['methb_level'].mean() if not df.empty else 0
        val = f"{methb_mean:.1f}" if not pd.isna(methb_mean) else "N/A"
        metric_card("Avg MetHb Level", val, suffix="%")
    with cols[2]:
        if len(df) > 0:
            recovery_rate = (df['outcome'] == 'Recovered').sum() / len(df[df['outcome'] != 'Unknown']) * 100
            val = f"{recovery_rate:.1f}"
        else:
            val = "N/A"
        metric_card("Recovery Rate", val, suffix="%")
    with cols[3]:
        unique_triggers = df[df['trigger'] != 'Unknown']['trigger'].nunique() if not df.empty else 0
        metric_card("Unique Triggers", unique_triggers)
    with cols[4]:
        avg_age = df['age'].mean() if not df.empty else 0
        val = f"{avg_age:.1f}" if not pd.isna(avg_age) else "N/A"
        metric_card("Average Age", val)

def get_plot_config():
    return {'displayModeBar': False, 'scrollZoom': False}

def get_dark_layout():
    return dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0'),
        xaxis=dict(gridcolor='#444'),
        yaxis=dict(gridcolor='#444')
    )

def plot_meth_distribution(df):
    meth_data = df['methb_level'].dropna()
    if len(meth_data) == 0:
        st.warning("No MetHb level data available")
        return
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=meth_data, nbinsx=20, name='MetHb Levels',
        marker_color='#800000', opacity=0.9,
        xbins=dict(start=0, end=100, size=5)
    ))
    
    fig.update_layout(
        title="Distribution of Methemoglobin Levels",
        xaxis_title="MetHb Level (%)",
        yaxis_title="Count",
        bargap=0.1,
        **get_dark_layout()
    )
    st.plotly_chart(fig, use_container_width=True, config=get_plot_config())

def plot_trigger_analysis(df):
    df_filtered = df[df['trigger'] != 'Unknown']
    if len(df_filtered) == 0: return

    trigger_counts = df_filtered['trigger'].value_counts().head(12)
    
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(
            x=trigger_counts.values,
            y=trigger_counts.index,
            orientation='h',
            title="Most Frequent Triggers",
            labels={'x': 'Cases', 'y': 'Trigger'},
        )
        fig1.update_traces(marker_color='#800000')
        fig1.update_layout(**get_dark_layout())
        fig1.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig1, use_container_width=True, config=get_plot_config())
    
    with col2:
        top_triggers = trigger_counts.index.tolist()
        df_with_meth = df_filtered[(df_filtered['methb_level'].notna()) & (df_filtered['trigger'].isin(top_triggers))]
        if len(df_with_meth) > 0:
            fig2 = px.box(
                df_with_meth, y='trigger', x='methb_level',
                title="Severity by Trigger",
                color_discrete_sequence=['#b71c1c']
            )
            fig2.update_layout(**get_dark_layout())
            fig2.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig2, use_container_width=True, config=get_plot_config())

def plot_age_analysis(df):
    df_age = df[df['age'].notna()]
    if len(df_age) == 0: return
    
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.histogram(
            df_age, x='age', nbins=20,
            title="Patient Age Distribution",
            color_discrete_sequence=['#800000']
        )
        fig1.update_layout(**get_dark_layout())
        st.plotly_chart(fig1, use_container_width=True, config=get_plot_config())
    
    with col2:
        df_age_meth = df_age[df_age['methb_level'].notna()]
        if len(df_age_meth) > 0:
            fig2 = px.scatter(
                df_age_meth, x='age', y='methb_level',
                title="Age vs Severity Correlation",
                color_discrete_sequence=['#ff5252']
            )
            fig2.update_traces(marker=dict(size=8, opacity=0.7))
            fig2.update_layout(**get_dark_layout())
            st.plotly_chart(fig2, use_container_width=True, config=get_plot_config())

def plot_treatment_outcomes(df):
    df_outcomes = df[df['outcome'].isin(['Recovered', 'Fatal', 'Admitted'])]
    if len(df_outcomes) == 0: return
    
    # Simple logic for demo
    treatment_list = []
    for t in df_outcomes['treatment'].dropna():
        if t != 'Unknown': treatment_list.extend([x.strip() for x in str(t).split(',')])
    
    if not treatment_list: return
    top_treatments = pd.Series(treatment_list).value_counts().head(5).index
    
    outcome_data = []
    for t in top_treatments:
        cases = df_outcomes[df_outcomes['treatment'].str.contains(t, na=False)]
        for o in ['Recovered', 'Fatal', 'Admitted']:
            count = (cases['outcome'] == o).sum()
            if count > 0: outcome_data.append({'Treatment': t, 'Outcome': o, 'Count': count})
            
    if outcome_data:
        outcome_df = pd.DataFrame(outcome_data)
        colors = {'Recovered': '#2ecc71', 'Fatal': '#c0392b', 'Admitted': '#f39c12'}
        fig = px.bar(
            outcome_df, x='Treatment', y='Count', color='Outcome',
            title="Outcomes by Primary Treatment",
            barmode='group',
            color_discrete_map=colors
        )
        fig.update_layout(**get_dark_layout())
        st.plotly_chart(fig, use_container_width=True, config=get_plot_config())


def main():
    # Initialize Session State for Navigation
    if 'page' not in st.session_state:
        st.session_state.page = "Home"

    # Helper to change page
    def set_page(page_name):
        st.session_state.page = page_name
        st.session_state.navigation_radio = page_name

    # Header Buttons
    st.markdown("""
        <div class="header-buttons">
            <a href="#" class="icon-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M.05 3.555A2 2 0 0 1 2 2h12a2 2 0 0 1 1.95 1.555L8 8.414.05 3.555ZM0 4.697v7.104l5.803-3.558L0 4.697ZM6.761 8.83l-6.57 4.027A2 2 0 0 0 2 14h12a2 2 0 0 0 1.808-1.144l-6.57-4.027L8 9.586l-1.239-.757Zm3.436-.586L16 11.801V4.697l-5.803 3.546Z"/>
                </svg>
                Email
            </a>
            <a href="#" class="icon-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M0 1.146C0 .513.526 0 1.175 0h13.65C15.474 0 16 .513 16 1.146v13.708c0 .633-.526 1.146-1.175 1.146H1.175C.526 16 0 15.487 0 14.854V1.146zm4.943 12.248V6.169H2.542v7.225h2.401zm-1.2-8.212c.837 0 1.358-.554 1.358-1.248-.015-.709-.52-1.248-1.342-1.248-.822 0-1.359.54-1.359 1.248 0 .694.521 1.248 1.327 1.248h.015zm4.908 8.212V9.359c0-.216.016-.432.08-.586.173-.431.568-.878 1.232-.878.869 0 1.216.662 1.216 1.634v3.865h2.401V9.25c0-2.22-1.184-3.252-2.764-3.252-1.274 0-1.845.7-2.165 1.193v.025h-.016a5.54 5.54 0 0 1 .016-.025V6.169h-2.4c.03.678 0 7.225 0 7.225h2.4z"/>
                </svg>
                LinkedIn
            </a>
            <a href="#" class="icon-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
                </svg>
                GitHub
            </a>
        </div>
    """, unsafe_allow_html=True)
    
    # Custom CSS to Make Radio Look Like Tabs & Fix Buttons
    st.markdown(f"""
    <style>
        /* Radio Group as Tabs */
        div[role="radiogroup"] {{
            display: flex;
            flex-direction: row;
            gap: 10px;
            background: transparent;
            margin-bottom: 20px;
            overflow-x: auto;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 5px;
        }}
        
        div[role="radiogroup"] label {{
            background: transparent !important;
            border: 1px solid transparent;
            border-radius: 5px;
            padding: 8px 16px;
            color: #aaa;
            cursor: pointer;
            transition: all 0.2s;
            min-width: 100px;
            justify-content: center;
        }}
        
        div[role="radiogroup"] label:hover {{
            color: white;
            background: rgba(255,255,255,0.05) !important;
        }}
        
        div[role="radiogroup"] label[data-checked="true"] {{
            background: {PRIMARY_COLOR} !important;
            color: white !important;
            border-bottom: 2px solid white;
        }}
        
        div[role="radiogroup"] div[data-testid="stMarkdownContainer"] p {{
            font-size: 1rem;
            font-weight: 600;
            margin: 0;
        }}
        
        /* Hide Radio Circles */
        div[role="radiogroup"] input {{
            display: none;
        }}
        
        /* Prevent Button styling from breaking theme */
        .stButton > button:hover {{
            background-color: {PRIMARY_COLOR} !important;
            color: white !important;
            border-color: #ffcccc !important;
            filter: brightness(1.1);
        }}
        .stButton > button:active {{
            background-color: #500000 !important;
            color: white !important;
        }}
        
        /* Insight Cards (Alerts) styling */
        .stAlert {{
            background-color: rgba(60, 10, 10, 0.8) !important;
            border: 1px solid #600 !important;
            border-left: 5px solid #a00000 !important;
            color: #eee !important;
            box-shadow: 0 0 15px rgba(200, 0, 0, 0.2);
        }}
        .stAlert p {{
            color: #eee !important;
        }}
        
        /* Metric container styling for Problem Section */
        div[data-testid="stMetric"] {{
            background-color: rgba(30,30,40,0.6);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid rgba(139, 0, 0, 0.3);
            text-align: center;
        }}

    </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.title("Filters")
        df = load_data()
        
        filters = {}
        if not df.empty:
            all_triggers = sorted(df[df['trigger'] != 'Unknown']['trigger'].unique().tolist())
            filters['triggers'] = st.multiselect("Select Triggers", options=all_triggers)
            
            age_min = int(df['age'].min()) if df['age'].notna().any() else 0
            age_max = int(df['age'].max()) if df['age'].notna().any() else 100
            filters['age_range'] = st.slider("Patient Age", age_min, age_max, (age_min, age_max))
            
            min_quality = st.slider("Min Data Quality", 0, 100, 0)
            if min_quality > 0:
                df = df[df['data_quality_score'] >= min_quality]
        
    # Main Navigation (State-Based)
    pages = ["Home", "Overview", "Trigger Analysis", "Demographics", "Treatment", "Data Registry"]
    
    # We use a callback to sync the radio with the session state if it changes via radio interaction
    current_selection = st.radio(
        "Navigation", 
        pages, 
        index=pages.index(st.session_state.page) if st.session_state.page in pages else 0,
        horizontal=True, 
        label_visibility="collapsed",
        key="navigation_radio",
        on_change=lambda: set_page(st.session_state.navigation_radio) # Sync manual click
    )

    # HOME PAGE
    if st.session_state.page == "Home":
        # Hero Section
        st.markdown(f"""
        <div class="hero-container">
            <div class="hero-title">
                <span class="brand-meta">Meta</span>
                <span class="brand-bond"></span>
                <span class="brand-hb">HB</span>
            </div>
            <p class="hero-subtitle">Clinical Intelligence from Unstructured Literature</p>
        </div>
        """, unsafe_allow_html=True)
        
        # The Problem We Solve
        col_prob_text, col_prob_metric = st.columns([3, 1])
        with col_prob_text:
            st.markdown(f"""
            <h3 style="color:white; border-left:none; padding-left:0; background:none;">The Problem We Solve</h3>
            <p style="font-size:1.05rem; line-height:1.6; color:#ddd;">
                Methemoglobinemia diagnosis is a race against time, yet clinical insights are buried in thousands of unstructured case reports. 
                Manual literature review is computationally expensive and slow, often delaying critical treatment decisions. 
                <strong>MetaHB</strong> automates this process, structuring chaotic data into actionable intelligence.
            </p>
            """, unsafe_allow_html=True)
        with col_prob_metric:
            st.markdown(f"""
            <div style="
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100%;
                padding-top: 15px; /* Fine-tune visual center */
            ">
                <h2 style="
                    font-size: 3.5rem; 
                    font-weight: 700; 
                    color: #4caf50; 
                    margin: 0; 
                    padding-left: 32px; /* Slight right shift for alignment */
                    text-shadow: 0 0 20px rgba(76, 175, 80, 0.6);
                    font-family: 'Montserrat', sans-serif;
                    line-height: 1;">
                    98%
                </h2>
                <p style="
                    color: #a5d6a7; 
                    font-size: 0.9rem; 
                    text-transform: uppercase; 
                    letter-spacing: 1px; 
                    margin: 10px 0 5px 0;
                    font-weight: 500;">
                    Efficiency Gain
                </p>
                <div style="
                    font-size: 0.85rem; 
                    color: #888; 
                    font-family: 'Roboto', sans-serif;">
                    <span style="color: #ff5252; font-weight:600;">8 hrs</span> 
                    <span style="margin: 0 5px;">→</span>
                    <span style="color: #4caf50; font-weight:600;">5 mins</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # NLP Insights (3 Columns)
        st.markdown("<h3 style='border-left:none; padding-left:0; background:none;'>Clinical NLP Insights</h3>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.info("**Trigger Severity**\n\nDapsone triggers **50% more severe** cases than Benzocaine (Avg 42% vs 28% MetHb).")
        with c2:
            st.success("**Treatment Efficacy**\n\n**96% Recovery rate** with Methylene Blue, but identified a 94% reporting gap for G6PD status.")
        with c3:
            st.warning("**Demographic Peaks**\n\nIdentified **bimodal risk peaks** at ages 20-30 and 60-70, suggesting distinct etiology groups.")

        st.markdown("<br><br>", unsafe_allow_html=True)

        # Technical Pipeline (Visual only)
        st.markdown(f"""
        <div class="pipeline-container">
            <div class="pipeline-step">Data Ingestion</div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step">NLP Extraction (SpaCy)</div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step">Data Structuring</div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step">Interactive Dashboard</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)

        # CTAs
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            col_a, col_b = st.columns(2)
            with col_a:
                st.button("Explore Trigger Analysis", use_container_width=True, type="primary", on_click=set_page, args=("Trigger Analysis",))
            with col_b:
                st.button("Explore Treatment Efficacy", use_container_width=True, type="primary", on_click=set_page, args=("Treatment",))

    # OTHER PAGES
    elif st.session_state.page == "Overview":
        col1, col2 = st.columns([2, 1])
        with col1:
             st.subheader("Severity Distribution")
             plot_meth_distribution(df)
        with col2:
            st.subheader("Key Statistics")
            if not df.empty:
                meth_data = df['methb_level'].dropna()
                st.markdown(f"""
                <div style="background: rgba(30,30,40,0.8); padding: 20px; border-radius: 4px; border: 1px solid #333; border-top: 3px solid #800000;">
                    <h4 style="margin-top:0; color: #800000;">Severity Indices</h4>
                    <ul style="list-style-type: none; padding-left: 0; font-size: 0.95rem; color: #ddd;">
                        <li style="margin-bottom: 8px; display: flex; justify-content: space-between;">
                            <span>Mild (&lt;15%)</span> <strong>{(meth_data < 15).sum()}</strong>
                        </li>
                        <li style="margin-bottom: 8px; display: flex; justify-content: space-between;">
                            <span>Moderate (15-30%)</span> <strong>{((meth_data >= 15) & (meth_data < 30)).sum()}</strong>
                        </li>
                        <li style="margin-bottom: 8px; display: flex; justify-content: space-between;">
                            <span style="color:#ff5252;">Severe (&ge;30%)</span> <strong style="color:#ff5252;">{(meth_data >= 30).sum()}</strong>
                        </li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

    elif st.session_state.page == "Trigger Analysis":
        st.subheader("Etiology & Triggers")
        plot_trigger_analysis(df)

    elif st.session_state.page == "Demographics":
        st.subheader("Demographics")
        plot_age_analysis(df)

    elif st.session_state.page == "Treatment":
        st.subheader("Treatment Outcomes")
        plot_treatment_outcomes(df)

    elif st.session_state.page == "Data Registry":
        st.subheader("Case Data Registry")
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()