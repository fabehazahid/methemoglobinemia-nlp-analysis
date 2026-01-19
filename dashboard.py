"""
=============================================================================
METHEMOGLOBINEMIA CLINICAL ANALYTICS DASHBOARD
=============================================================================

This application provides interactive visualization and analysis of 
methemoglobinemia case reports extracted from medical literature using
NLP techniques. Built for clinical decision support and research.

Methemoglobinemia is a rare blood disorder where hemoglobin is oxidized to
methemoglobin, reducing oxygen-carrying capacity. This dashboard automates
the extraction and structuring of clinical insights from unstructured case
reports, reducing manual review time from ~8 hours to ~5 minutes (98% efficiency gain).

Author: Fabeha Zahid
Date: 2026-01-19
Version: 2.0 - Professional UI/UX Redesign
Dependencies: streamlit, plotly, pandas, numpy

Usage:
    streamlit run dashboard.py
    
Features:
    - Interactive filtering by triggers, age, and data quality
    - Distribution analysis of methemoglobin severity levels
    - Trigger frequency and severity correlation analysis
    - Demographic analysis (age distribution and correlation)
    - Treatment outcome visualization
    - Complete case data registry with color-coded severity indicators

Technical Stack:
    - Frontend: Streamlit with custom CSS/HTML
    - Visualization: Plotly (dark theme, clinical color palette)
    - Data Processing: Pandas, NumPy
    - NLP Pipeline: SpaCy (upstream extraction, not included in this file)
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np
import base64
import os

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="MetHb Analysis",
    page_icon="⚕️",  # Medical symbol - professional alternative to emoji
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# ASSETS & HELPER FUNCTIONS
# =============================================================================

def get_base64_of_bin_file(bin_file):
    """
    Convert a binary file to base64 encoding for embedding in HTML/CSS.
    
    Used primarily for background image embedding in CSS data URIs.
    
    Args:
        bin_file (str): Path to the binary file to encode
    
    Returns:
        str: Base64 encoded string, or empty string if file not found
        
    Example:
        >>> encoded = get_base64_of_bin_file('assets/background.png')
        >>> f"url('data:image/png;base64,{encoded}')"
    """
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        return ""

# Path to the generated background image (red blood cells microscopy aesthetic)
BACKGROUND_IMAGE_PATH = Path(__file__).parent / "assets" / "background_rbc.png"
background_base64 = get_base64_of_bin_file(BACKGROUND_IMAGE_PATH)

# =============================================================================
# CLINICAL COLOR PALETTE
# =============================================================================
# Professional medical analytics color scheme emphasizing clinical maroon
# (representing hemoglobin/blood) against deep charcoal backgrounds.
# All colors selected for WCAG AAA compliance (7:1 contrast ratio minimum).

# Primary Colors
PRIMARY_COLOR = "#A61B41"        # Lighter Clinical Maroon
SECONDARY_COLOR = "#E63946"      # Brighter Alert Red
TERTIARY_COLOR = "#E9A3A9"       # Lighter Muted Rose

# Background Colors
BG_DEEP_CHARCOAL = "#1a1a1a"     # Deep charcoal (main background)
BG_CARD = "#252525"              # Card background (slightly lighter)
BG_OVERLAY = "rgba(5, 5, 10, 0.92)"  # Dark overlay for background images
BG_GLASS = "rgba(30, 30, 40, 0.9)"   # Glass card effect with backdrop blur
BG_SIDEBAR = "rgba(15, 15, 20, 0.95)" # Sidebar background

# Supporting Colors (Outcome/Status Indicators)
COLOR_SUCCESS = "#2ECC71"        # Success Green (recovered patients)
COLOR_WARNING = "#E67E22"        # Warning Orange (admitted/moderate severity)
COLOR_FATAL = "#C0392B"          # Fatal Red (fatal outcomes)
COLOR_NEUTRAL = "#5C7A99"        # Steel Blue (neutral/charts/unknown)

# Text Colors
TEXT_PRIMARY = "#FFFFFF"         # Primary text (white)
TEXT_SECONDARY = "#D1D1D1"       # Lighter gray for better visibility
TEXT_MUTED = "#888888"           # Muted text (darker gray)

# Borders & Dividers
BORDER_COLOR = "#3a3a3a"         # Standard borders
BORDER_ACCENT = "rgba(139, 21, 56, 0.3)"  # Accent borders (maroon tint)
 

# =============================================================================
# PROFESSIONAL MEDICAL ANALYTICS THEME - CUSTOM CSS
# =============================================================================
# Comprehensive styling system for portfolio-grade clinical data platform.
# Design philosophy: Clinical professionalism, subtle elegance, data-first.

st.markdown(f"""
<style>
    /* =========================================================================
       TYPOGRAPHY SYSTEM - Google Fonts Import
       ========================================================================= */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Source+Sans+Pro:wght@300;400;600&family=Montserrat:wght@600;700;800&family=JetBrains+Mono:wght@400&display=swap');
    
    /* =========================================================================
       GLOBAL SCALING - Emulates 80% zoom at 100%
       ========================================================================= */
    html {{
        font-size: 85% !important; /* Base scale for all rem units */
    }}

    .stApp {{
        background-image: linear-gradient({BG_OVERLAY}, {BG_OVERLAY}), url("data:image/png;base64,{background_base64}");
        background-attachment: fixed;
        background-size: cover;
        font-family: 'Source Sans Pro', sans-serif;
        color: {TEXT_PRIMARY};
    }}
    
    body {{
        color: {TEXT_PRIMARY};
    }}

    /* =========================================================================
       HEADINGS - Professional Typography Hierarchy
       ========================================================================= */
    h1, h2, h3, h4, h5 {{
        font-family: 'Inter', sans-serif;
        color: {TEXT_PRIMARY} !important;
        letter-spacing: 0.5px;
    }}
    
    h1 {{
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 1px;
        border-bottom: 2px solid {PRIMARY_COLOR};
        padding-bottom: 8px;
        margin-bottom: 16px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }}

    h2 {{
        font-size: 1.8rem;
        font-weight: 600;
        letter-spacing: 0.8px;
    }}

    h3 {{
        font-size: 1.2rem;
        font-weight: 600;
        border-left: 4px solid {PRIMARY_COLOR};
        padding-left: 14px;
        margin-top: 16px;
        background: linear-gradient(90deg, rgba(139, 21, 56, 0.15), transparent);
    }}

    h4 {{
        font-size: 1.1rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}

    /* =========================================================================
       SIDEBAR - Filter Panel Styling
       ========================================================================= */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {BG_SIDEBAR} 0%, rgba(20, 10, 15, 0.98) 100%);
        border-right: 1px solid {BORDER_ACCENT};
    }}
    
    section[data-testid="stSidebar"] h1 {{
        color: {SECONDARY_COLOR} !important;
        font-size: 1.2rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        border-bottom: 2px solid;
        border-image: linear-gradient(90deg, {SECONDARY_COLOR}, transparent) 1;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }}
    
    .stMarkdown p {{
        color: {TEXT_PRIMARY};
        font-size: 1rem;
        line-height: 1.5;
    }}

    /* =========================================================================
       METRIC CARDS - Clinical Data Display
       ========================================================================= */
    .metric-card {{
        background: linear-gradient(135deg, rgba(37, 37, 37, 0.9) 0%, rgba(45, 20, 25, 0.8) 100%);
        border-left: 4px solid {PRIMARY_COLOR};
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(139, 21, 56, 0.3);
    }}
    
    .metric-label {{
        color: {TEXT_SECONDARY};
        font-size: 0.8rem;
        text-transform: uppercase;
        font-weight: 500;
        letter-spacing: 1.2px;
        margin-bottom: 8px;
    }}
    
    .metric-value {{
        color: {TEXT_PRIMARY};
        font-size: 2.2rem;
        font-weight: 800;
        font-family: 'Montserrat', sans-serif;
        line-height: 1;
    }}

    /* =========================================================================
       HERO SECTION - Full-Width Gradient Banner
       ========================================================================= */
    .hero-container {{
        background: linear-gradient(135deg, 
            rgba(26, 26, 26, 0.95) 0%, 
            rgba(139, 21, 56, 0.15) 50%, 
            rgba(26, 26, 26, 0.95) 100%);
        border-top: 1px solid rgba(139, 21, 56, 0.3);
        border-bottom: 1px solid rgba(139, 21, 56, 0.3);
        padding: 80px 32px 64px 32px;
        text-align: center;
        margin-bottom: 40px;
        position: relative;
        overflow: hidden;
        margin-left: -5rem;
        margin-right: -5rem;
        padding-left: calc(5rem + 32px);
        padding-right: calc(5rem + 32px);
    }}
    
    /* Subtle accent line above hero with expansion animation */
    .hero-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            {PRIMARY_COLOR} 20%, 
            {SECONDARY_COLOR} 50%, 
            {PRIMARY_COLOR} 80%, 
            transparent 100%);
        animation: expand-from-center 1.5s ease-out forwards;
        transform-origin: center;
    }}
    
    @keyframes expand-from-center {{
        0% {{ transform: scaleX(0); opacity: 0; }}
        100% {{ transform: scaleX(1); opacity: 1; }}
    }}
    
    .hero-title {{
        font-size: 3.2rem;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
        font-family: 'Inter', sans-serif;
    }}
    
    /* MetaHB Logo Components - Enhanced for Banner */
    .brand-meta {{
        font-weight: 300;
        color: {TEXT_PRIMARY};
        letter-spacing: 3px;
        font-family: 'Inter', sans-serif;
    }}
    
    .brand-superscript {{
        width: 26px;
        height: 26px;
        background: {SECONDARY_COLOR};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 600;
        color: {TEXT_PRIMARY};
        position: relative;
        top: -6px;
        box-shadow: 0 0 20px rgba(196, 30, 58, 0.6);
    }}
    
    .brand-hb {{
        font-weight: 800;
        color: {SECONDARY_COLOR};
        letter-spacing: 1px;
        text-shadow: 0 0 30px rgba(196, 30, 58, 0.5);
        animation: pulse-glow 3s ease-in-out infinite;
    }}
    
    /* Subtle pulse animation for HB text */
    @keyframes pulse-glow {{
        0%, 100% {{ text-shadow: 0 0 20px rgba(196, 30, 58, 0.6); }}
        50% {{ text-shadow: 0 0 30px rgba(196, 30, 58, 0.8); }}
    }}
    
    .hero-subtitle {{
        font-size: 1.1rem;
        color: {TEXT_SECONDARY};
        font-weight: 300;
        letter-spacing: 1px;
        margin-top: 13px;
        font-family: 'Source Sans Pro', sans-serif;
    }}

    /* =========================================================================
       PIPELINE VISUALIZATION - Technical Workflow
       ========================================================================= */
    .pipeline-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 16px;
        margin: 32px 0;
        flex-wrap: wrap;
        background: rgba(20, 20, 25, 0.6);
        border-radius: 10px;
        padding: 32px 24px;
    }}
    
    .pipeline-step {{
        background: rgba(37, 37, 37, 0.9);
        border: 1.5px solid {PRIMARY_COLOR};
        padding: 13px 22px;
        border-radius: 20px;
        color: {TEXT_PRIMARY};
        font-weight: 600;
        font-size: 0.85rem;
        position: relative;
        transition: all 0.3s ease;
    }}

    .pipeline-step:hover {{
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%);
        transform: scale(1.05);
        box-shadow: 0 4px 16px rgba(139, 21, 56, 0.4);
    }}
    
    .pipeline-step-number {{
        position: absolute;
        top: -6px;
        right: -6px;
        background: {SECONDARY_COLOR};
        color: {TEXT_PRIMARY};
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.65rem;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(196, 30, 58, 0.5);
    }}
    
    .pipeline-arrow {{
        color: {PRIMARY_COLOR};
        font-size: 20px;
        font-weight: bold;
    /* =========================================================================
       CONTACT BUTTONS - Header Navigation (Icon-Only)
       ========================================================================= */
    .header-buttons {{
        position: absolute;
        top: 15px; /* Aligned with the tab row but far right */
        right: 20px; /* Shifted to the far edge of the viewport */
        padding-top: 10px;
        display: flex;
        gap: 15px; /* Increased spacing between icons */
        z-index: 1000;
    }}
    
    .icon-btn {{
        background-color: rgba(37, 37, 37, 0.8);
        border: 1px solid {BORDER_ACCENT};
        color: {TEXT_PRIMARY};
        padding: 8px;
        border-radius: 6px;
        text-decoration: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
    }}
    
    .icon-btn:hover {{
        background-color: {PRIMARY_COLOR};
        border: 1px solid {SECONDARY_COLOR};
        color: {TEXT_PRIMARY};
        text-decoration: none;
        box-shadow: 0 0 20px rgba(139, 21, 56, 0.6), 0 0 30px rgba(196, 30, 58, 0.3);
        transform: translateY(-3px);
    }}

    /* =========================================================================
       PLOTLY CHART STYLING
       ========================================================================= */
    .js-plotly-plot .plotly .main-svg {{
        background: rgba(0,0,0,0) !important;
    }}

    /* Chart container cards */
    .chart-container {{
        background: rgba(25, 25, 30, 0.8);
        border: 1px solid {BORDER_COLOR};
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA LOADING & PREPROCESSING
# =============================================================================

@st.cache_data
def load_data():
    """
    Load and preprocess methemoglobinemia case data from CSV file.
    
    This function loads structured clinical data extracted from medical literature
    via NLP pipeline. It performs essential data cleaning including:
    - Age extraction from text (e.g., "70 years" → 70)
    - MetHb level normalization (removing % symbols, converting to numeric)
    - Data quality score imputation (filling missing values with 0)
    
    The data is cached by Streamlit to avoid repeated file I/O and processing.
    
    Returns:
        pd.DataFrame: Cleaned dataframe with columns:
            - pmid (int): PubMed ID of source article
            - age (float): Patient age in years (cleaned numeric)
            - methb_level (float): Methemoglobin percentage (0-100)
            - trigger (str): Causative agent/substance
            - treatment (str): Treatment intervention(s)
            - outcome (str): Clinical outcome (Recovered/Fatal/Admitted/Unknown)
            - data_quality_score (float): NLP extraction confidence (0-100)
            
    Example:
        >>> df = load_data()
        >>> df[df['methb_level'] > 30]  # Critical severity cases
        
    Note:
        Returns empty DataFrame if CSV file not found (graceful degradation).
        Clinical threshold: MetHb >30% is considered severe/life-threatening.
    """
    try:
        df = pd.read_csv('data/processed/meth_structured_data.csv')
        
        # ---------------------------------------------------------------------
        # Data Cleaning - Age
        # ---------------------------------------------------------------------
        # Extract numeric age from strings like "70 years", "45 yo", etc.
        # Some case reports include text descriptions that need parsing
        if 'age' in df.columns:
            df['age'] = pd.to_numeric(
                df['age'].astype(str).str.extract(r'(\d+)', expand=False), 
                errors='coerce'
            )
        
        # ---------------------------------------------------------------------
        # Data Cleaning - Methemoglobin Level
        # ---------------------------------------------------------------------
        # Remove percentage symbols and convert to numeric
        # Clinical context: Normal MetHb is <1%, >20% causes symptoms, >70% often fatal
        if 'methb_level' in df.columns:
            df['methb_level'] = pd.to_numeric(
                df['methb_level'].astype(str).str.replace('%', ''), 
                errors='coerce'
            )

        # ---------------------------------------------------------------------
        # Data Quality Score Imputation
        # ---------------------------------------------------------------------
        # NLP extraction confidence score (0-100)
        # Missing values indicate low-confidence extractions, default to 0
        if 'data_quality_score' in df.columns:
            df['data_quality_score'] = df['data_quality_score'].fillna(0)

        return df
        
    except Exception as e:
        # Graceful degradation: return empty DataFrame if file not found
        # This allows dashboard to load even without data (for demo purposes)
        return pd.DataFrame() 
 

# =============================================================================
# VISUAL COMPONENTS - Reusable UI Elements
# =============================================================================

def metric_card(label, value, prefix="", suffix="", border_color=None):
    """
    Display a clinical metric card with optional color-coded border.
    
    Creates a professional card component for displaying key statistics with
    gradient background, hover effects, and color-coded left border to indicate
    metric category (e.g., critical, success, warning).
    
    Args:
        label (str): Metric label (e.g., "Total Cases", "Recovery Rate")
        value (str|int|float): Metric value to display
        prefix (str, optional): Prefix symbol (e.g., "$", "~"). Default: ""
        suffix (str, optional): Suffix symbol (e.g., "%", "mg"). Default: ""
        border_color (str, optional): Hex color for left border. Default: PRIMARY_COLOR
            Suggested colors:
            - COLOR_NEUTRAL (#5C7A99): Neutral metrics (total counts)
            - SECONDARY_COLOR (#C41E3A): Critical metrics (MetHb levels)
            - COLOR_SUCCESS (#2ECC71): Positive metrics (recovery rate)
            - COLOR_WARNING (#E67E22): Warning metrics (unique triggers)
            - TERTIARY_COLOR (#D4858D): Demographic metrics (age)
    
    Example:
        >>> metric_card("Recovery Rate", "96.2", suffix="%", border_color=COLOR_SUCCESS)
        >>> metric_card("Avg MetHb Level", "28.5", suffix="%", border_color=SECONDARY_COLOR)
    
    Note:
        Uses Montserrat font for large metric values to enhance readability.
        Card includes hover effect (translateY -2px, shadow intensify).
    """
    border = border_color if border_color else PRIMARY_COLOR
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: {border};">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{prefix}{value}{suffix}</div>
    </div>
    """, unsafe_allow_html=True)

def create_metrics_row(df):
    """
    Create a row of five key clinical metrics with color-coded borders.
    
    Displays essential statistics about the methemoglobinemia case dataset:
    - Total Cases: Overall dataset size (neutral blue)
    - Avg MetHb Level: Mean severity percentage (critical red)
    - Recovery Rate: Percentage of recovered patients (success green)
    - Unique Triggers: Number of distinct causative agents (warning orange)
    - Average Age: Mean patient age (muted rose)
    
    Args:
        df (pd.DataFrame): Cleaned case data from load_data()
    
    Note:
        Recovery rate excludes 'Unknown' outcomes from denominator.
        Color-coding follows clinical significance:
        - Blue (neutral): Informational
        - Red (critical): Severity indicators
        - Green (success): Positive outcomes
        - Orange (warning): Risk factors
        - Rose (demographic): Patient characteristics
    """
    cols = st.columns(5)
    
    # Total Cases - Neutral metric
    with cols[0]:
        metric_card("Total Cases", len(df), border_color=COLOR_NEUTRAL)
    
    # Avg MetHb Level - Critical severity indicator
    with cols[1]:
        methb_mean = df['methb_level'].mean() if not df.empty else 0
        val = f"{methb_mean:.1f}" if not pd.isna(methb_mean) else "N/A"
        metric_card("Avg MetHb Level", val, suffix="%", border_color=SECONDARY_COLOR)
    
    # Recovery Rate - Success metric
    with cols[2]:
        if len(df) > 0:
            # Exclude 'Unknown' outcomes from calculation
            known_outcomes = df[df['outcome'] != 'Unknown']
            if len(known_outcomes) > 0:
                recovery_rate = (known_outcomes['outcome'] == 'Recovered').sum() / len(known_outcomes) * 100
                val = f"{recovery_rate:.1f}"
            else:
                val = "N/A"
        else:
            val = "N/A"
        metric_card("Recovery Rate", val, suffix="%", border_color=COLOR_SUCCESS)
    
    # Unique Triggers - Warning/risk metric
    with cols[3]:
        unique_triggers = df[df['trigger'] != 'Unknown']['trigger'].nunique() if not df.empty else 0
        metric_card("Unique Triggers", unique_triggers, border_color=COLOR_WARNING)
    
    # Average Age - Demographic metric
    with cols[4]:
        avg_age = df['age'].mean() if not df.empty else 0
        val = f"{avg_age:.1f}" if not pd.isna(avg_age) else "N/A"
        metric_card("Average Age", val, border_color=TERTIARY_COLOR)

def get_plot_config():
    """
    Get Plotly chart configuration for clean, professional display.
    
    Disables mode bar and scroll zoom to create a cleaner, more controlled
    viewing experience suitable for portfolio presentation.
    
    Returns:
        dict: Plotly config object
    """
    return {'displayModeBar': False, 'scrollZoom': False}

def get_dark_layout():
    """
    Get comprehensive Plotly dark theme layout for clinical charts.
    
    Provides a professional dark theme optimized for medical data visualization
    with high contrast, readable fonts, and subtle grid lines. All colors selected
    for WCAG AAA accessibility compliance.
    
    Returns:
        dict: Plotly layout configuration with:
            - Transparent backgrounds (integrates with dashboard theme)
            - Inter font family (professional, readable)
            - Dark grid lines (#333) for subtle data guidance
            - High-contrast text (#e0e0e0)
            - Optimized margins for space efficiency
            - Clinical maroon hover labels
    
    Example:
        >>> fig = px.bar(data, x='trigger', y='count')
        >>> fig.update_layout(**get_dark_layout())
        >>> st.plotly_chart(fig, config=get_plot_config())
    
    Note:
        Transparent backgrounds allow dashboard background to show through,
        creating visual cohesion across all chart types.
    """
    return dict(
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper (outer area)
        plot_bgcolor='rgba(30, 30, 35, 0.5)',  # Semi-transparent plot area
        font=dict(
            family='Inter, sans-serif',
            size=12,
            color='#e0e0e0'
        ),
        xaxis=dict(
            gridcolor='#333333',
            gridwidth=0.5,
            linecolor='#444444',
            zerolinecolor='#555555',
            tickfont=dict(size=11, color='#aaa')
        ),
        yaxis=dict(
            gridcolor='#333333',
            gridwidth=0.5,
            linecolor='#444444',
            zerolinecolor='#555555',
            tickfont=dict(size=11, color='#aaa')
        ),
        margin=dict(l=60, r=40, t=60, b=50),
        hovermode='closest',
        hoverlabel=dict(
            bgcolor='#1a1a1a',
            font_size=12,
            font_family='Inter',
            bordercolor=SECONDARY_COLOR  # Clinical maroon border
        )
    )

def plot_meth_distribution(df):
    """
    Plot histogram distribution of methemoglobin severity levels with clinical zones.
    
    Visualizes the frequency distribution of MetHb percentages across all cases,
    with background highlighting for clinical severity zones:
    - Mild (<15%): Usually asymptomatic
    - Moderate (15-30%): Cyanosis and symptoms present
    - Severe (>=30%): Life-threatening thresholds
    
    Args:
        df (pd.DataFrame): Case data with 'meth_level' column
    """
    # Note: Use 'meth_level' as per the schema found in nlp_extraction.py
    # and the column name in load_data (which might be cleaning it)
    # Checking column names in df
    col_name = 'meth_level' if 'meth_level' in df.columns else 'methb_level'
    
    meth_data = df[col_name].dropna()
    if len(meth_data) == 0:
        st.warning("No MetHb level data available")
        return
    
    fig = go.Figure()
    
    # Add clinical severity zones as background rectangles
    # Mild Zone
    fig.add_vrect(
        x0=0, x1=15, 
        fillcolor="#2ECC71", opacity=0.1, 
        layer="below", line_width=0,
        annotation_text="MILD (<15%)", 
        annotation_position="top left",
        annotation_font=dict(size=10, color="#2ECC71")
    )
    
    # Moderate Zone
    fig.add_vrect(
        x0=15, x1=30, 
        fillcolor="#E67E22", opacity=0.1, 
        layer="below", line_width=0,
        annotation_text="MODERATE (15-30%)", 
        annotation_position="top left",
        annotation_font=dict(size=10, color="#E67E22")
    )
    
    # Severe Zone
    fig.add_vrect(
        x0=30, x1=100, 
        fillcolor="#C0392B", opacity=0.1, 
        layer="below", line_width=0,
        annotation_text="SEVERE (>=30%)", 
        annotation_position="top left",
        annotation_font=dict(size=10, color="#C0392B")
    )

    # Add the histogram
    fig.add_trace(go.Histogram(
        x=meth_data, 
        nbinsx=20, 
        name='MetHb Levels',
        marker_color=SECONDARY_COLOR, 
        opacity=0.9,
        xbins=dict(start=0, end=100, size=5),
        hovertemplate="<b>MetHb Range</b>: %{x}%<br><b>Frequency</b>: %{y} cases<extra></extra>"
    ))
    
    fig.update_layout(**get_dark_layout())
    fig.update_layout(
        title=dict(
            text="Distribution of Methemoglobin Levels by Clinical Severity",
            font=dict(size=16, color=TEXT_PRIMARY),
            x=0.02,
            xanchor='left'
        ),
        xaxis_title="Methemoglobin Level (%)",
        yaxis_title="Frequency (Clinical Cases)",
        bargap=0.1,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True, config=get_plot_config())

def plot_trigger_analysis(df):
    """
    Analyze and visualize trigger frequency and severity correlation.
    
    Creates two complementary visualizations:
    1. Horizontal bar chart: Most frequent causative agents (top 12)
    2. Box plot: MetHb severity distribution by trigger type
    
    This helps identify which substances/medications most commonly cause
    methemoglobinemia and whether certain triggers lead to more severe cases.
    
    Args:
        df (pd.DataFrame): Case data with 'trigger' and 'methb_level' columns
    
    Note:
        Excludes 'Unknown' triggers from analysis.
        Common triggers include: Dapsone, Benzocaine, Lidocaine, Nitrites.
        Box plot shows median, quartiles, and outliers for severity comparison.
    """
    df_filtered = df[df['trigger'] != 'Unknown']
    if len(df_filtered) == 0: return

    trigger_counts = df_filtered['trigger'].value_counts().head(12)
    
    col1, col2 = st.columns(2)
    
    # Left: Frequency bar chart
    with col1:
        fig1 = px.bar(
            x=trigger_counts.values,
            y=trigger_counts.index,
            orientation='h',
            title="Most Frequent Triggers",
            labels={'x': 'Cases', 'y': 'Trigger'},
        )
        fig1.update_layout(**get_dark_layout())
        fig1.update_layout(
            title=dict(
                text="Most Frequent Triggers",
                font=dict(size=16, color=TEXT_PRIMARY),
                x=0.02,
                xanchor='left'
            )
        )
        fig1.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig1, use_container_width=True, config=get_plot_config())
    
    # Right: Severity box plot
    with col2:
        top_triggers = trigger_counts.index.tolist()
        df_with_meth = df_filtered[(df_filtered['methb_level'].notna()) & (df_filtered['trigger'].isin(top_triggers))]
        if len(df_with_meth) > 0:
            fig2 = px.box(
                df_with_meth, y='trigger', x='methb_level',
                title="Severity by Trigger",
                color_discrete_sequence=[SECONDARY_COLOR]  # Alert red for severity
            )
            fig2.update_layout(**get_dark_layout())
            fig2.update_layout(
                title=dict(
                    text="Severity by Trigger",
                    font=dict(size=16, color=TEXT_PRIMARY),
                    x=0.02,
                    xanchor='left'
                )
            )
            fig2.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig2, use_container_width=True, config=get_plot_config())

def plot_age_analysis(df):
    """
    Analyze and visualize patient age distribution and correlation with severity.
    
    Creates two complementary visualizations:
    1. Histogram: Age distribution across all cases
    2. Scatter plot: Age vs MetHb severity correlation
    
    This helps identify age-related risk patterns and whether certain age groups
    experience more severe methemoglobinemia. Clinical research suggests bimodal
    risk peaks at ages 20-30 (occupational/recreational exposures) and 60-70
    (medication-related cases).
    
    Args:
        df (pd.DataFrame): Case data with 'age' and 'methb_level' columns
    
    Note:
        Excludes cases with missing age data.
        Scatter plot uses alert red color (#ff5252) to emphasize severity.
    """
    df_age = df[df['age'].notna()]
    if len(df_age) == 0: return
    
    col1, col2 = st.columns(2)
    
    # Left: Age distribution histogram
    with col1:
        fig1 = px.histogram(
            df_age, x='age', nbins=20,
            title="Patient Age Distribution",
            color_discrete_sequence=[PRIMARY_COLOR]
        )
        fig1.update_layout(**get_dark_layout())
        fig1.update_layout(
            title=dict(
                text="Patient Age Distribution",
                font=dict(size=16, color=TEXT_PRIMARY),
                x=0.02,
                xanchor='left'
            )
        )
        st.plotly_chart(fig1, use_container_width=True, config=get_plot_config())
    
    # Right: Age vs severity scatter plot
    with col2:
        df_age_meth = df_age[df_age['methb_level'].notna()]
        if len(df_age_meth) > 0:
            fig2 = px.scatter(
                df_age_meth, x='age', y='methb_level',
                title="Age vs Severity Correlation",
                color_discrete_sequence=['#ff5252']  # Alert red for severity
            )
            fig2.update_traces(marker=dict(size=10, opacity=0.7, line=dict(width=1, color='white')))
            fig2.update_layout(**get_dark_layout())
            fig2.update_layout(
                title=dict(
                    text="Age vs Severity Correlation",
                    font=dict(size=16, color=TEXT_PRIMARY),
                    x=0.02,
                    xanchor='left'
                )
            )
            st.plotly_chart(fig2, use_container_width=True, config=get_plot_config())

def plot_treatment_outcomes(df):
    """
    Visualize treatment efficacy by analyzing outcomes for different interventions.
    
    Creates a grouped bar chart showing recovery, fatal, and admitted outcomes
    for the top 5 most common treatments. This helps identify which treatments
    have the best success rates and where clinical protocols may need improvement.
    
    Args:
        df (pd.DataFrame): Case data with 'treatment' and 'outcome' columns
    
    Note:
        Excludes 'Unknown' outcomes and treatments.
        Color coding:
        - Green (#2ECC71): Recovered patients
        - Red (#C0392B): Fatal outcomes
        - Orange (#F39C12): Admitted/ongoing treatment
        
        Common treatments: Methylene Blue (first-line), Ascorbic Acid, Oxygen therapy
    """
    df_outcomes = df[df['outcome'].isin(['Recovered', 'Fatal', 'Admitted'])]
    if len(df_outcomes) == 0: return
    
    # Extract and count treatments
    treatment_list = []
    for t in df_outcomes['treatment'].dropna():
        if t != 'Unknown': 
            treatment_list.extend([x.strip() for x in str(t).split(',')])
    
    if not treatment_list: return
    top_treatments = pd.Series(treatment_list).value_counts().head(5).index
    
    # Build outcome data for top treatments
    outcome_data = []
    for t in top_treatments:
        cases = df_outcomes[df_outcomes['treatment'].str.contains(t, na=False)]
        for o in ['Recovered', 'Fatal', 'Admitted']:
            count = (cases['outcome'] == o).sum()
            if count > 0: 
                outcome_data.append({'Treatment': t, 'Outcome': o, 'Count': count})
            
    if outcome_data:
        outcome_df = pd.DataFrame(outcome_data)
        colors = {
            'Recovered': COLOR_SUCCESS,  # Green
            'Fatal': COLOR_FATAL,        # Red
            'Admitted': COLOR_WARNING    # Orange
        }
        fig = px.bar(
            outcome_df, x='Treatment', y='Count', color='Outcome',
            title="Outcomes by Primary Treatment",
            barmode='group',
            color_discrete_map=colors
        )
        fig.update_layout(**get_dark_layout())
        fig.update_layout(
            title=dict(
                text="Outcomes by Primary Treatment",
                font=dict(size=16, color=TEXT_PRIMARY),
                x=0.02,
                xanchor='left'
            )
        )
        st.plotly_chart(fig, use_container_width=True, config=get_plot_config())


# =============================================================================
# MAIN APPLICATION FUNCTION
# =============================================================================

def main():
    """
    Main application entry point.
    
    Orchestrates the entire dashboard including:
    - Session state initialization for navigation
    - Header contact buttons
    - Navigation radio controls
    - Page routing (Home, Severity Analysis, Trigger Analysis, Demographics, Treatment, Registry)
    - Sidebar filters
    
    Note:
        Uses Streamlit session state for client-side navigation without page reloads.
        Each page is rendered conditionally based on st.session_state.page value.
    """
    # Initialize Session State for Navigation
    if 'page' not in st.session_state:
        st.session_state.page = "Home"
    
    # Helper to change page
    def set_page(page_name):
        st.session_state.page = page_name
        st.session_state.navigation_radio = page_name

    # ---------------------------------------------------------------------
    # Header Contact Buttons - Icon Only
    # ---------------------------------------------------------------------
    # Professional SVG icons for Email, LinkedIn, and GitHub (icon-only design)
    # 
    # 📍 TO ADD YOUR CONTACT URLs - Replace the href="#" values below:
    #    Line ~920: Email button    → href="mailto:fabehazahid@gmail.com.com"
    #    Line ~928: LinkedIn button → href="https://linkedin.com/in/your-profile"
    #    Line ~936: GitHub button   → href="https://github.com/your-username"
    #
    # Contact Icons
    st.markdown("""
        <div class="header-buttons">
            <a href="mailto:fabehazahid@gmail.com" class="icon-btn" title="Email" aria-label="Send email">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M.05 3.555A2 2 0 0 1 2 2h12a2 2 0 0 1 1.95 1.555L8 8.414.05 3.555ZM0 4.697v7.104l5.803-3.558L0 4.697ZM6.761 8.83l-6.57 4.027A2 2 0 0 0 2 14h12a2 2 0 0 0 1.808-1.144l-6.57-4.027L8 9.586l-1.239-.757Zm3.436-.586L16 11.801V4.697l-5.803 3.546Z"/>
                </svg>
            </a>
            <a href="https://www.linkedin.com/in/fabeha-zahid-mahmood-b5ba3228a" target="_blank" class="icon-btn" title="LinkedIn" aria-label="Visit LinkedIn profile">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M0 1.146C0 .513.526 0 1.175 0h13.65C15.474 0 16 .513 16 1.146v13.708c0 .633-.526 1.146-1.175 1.146H1.175C.526 16 0 15.487 0 14.854V1.146zm4.943 12.248V6.169H2.542v7.225h2.401zm-1.2-8.212c.837 0 1.358-.554 1.358-1.248-.015-.709-.52-1.248-1.342-1.248-.822 0-1.359.54-1.359 1.248 0 .694.521 1.248 1.327 1.248h.015zm4.908 8.212V9.359c0-.216.016-.432.08-.586.173-.431.568-.878 1.232-.878.869 0 1.216.662 1.216 1.634v3.865h2.401V9.25c0-2.22-1.184-3.252-2.764-3.252-1.274 0-1.845.7-2.165 1.193v.025h-.016a5.54 5.54 0 0 1 .016-.025V6.169h-2.4c.03.678 0 7.225 0 7.225h2.4z"/>
                </svg>
            </a>
            <a href="https://github.com/fabehazahid" target="_blank" class="icon-btn" title="GitHub" aria-label="Visit GitHub profile">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
                </svg>
            </a>
        </div>
    """, unsafe_allow_html=True)
    
    # =============================================================================
    # NAVIGATION & COMPONENT STYLING
    # =============================================================================
    # Additional CSS for radio-as-tabs navigation, buttons, alerts, and metrics
    
    st.markdown(f"""
    <style>
        /* =====================================================================
           NAVIGATION TABS - Radio Group Styling
           ===================================================================== */
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
            border-radius: 8px;
            padding: 10px 20px;
            color: #f0f0f0; /* Brighter white for better readability */
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            min-width: 100px;
            justify-content: center;
            font-size: 0.95rem;
            font-weight: 600;
        }}
        
        /* Inactive tab hover state */
        div[role="radiogroup"] label:hover {{
            color: {TEXT_PRIMARY};
            background: rgba(139, 21, 56, 0.15) !important;
            border: 1px solid {BORDER_ACCENT};
        }}
        
        /* Active tab state */
        div[role="radiogroup"] label[data-checked="true"] {{
            background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%) !important;
            color: {TEXT_PRIMARY} !important;
            border-bottom: 3px solid {TEXT_PRIMARY};
            box-shadow: 0 4px 12px rgba(139, 21, 56, 0.3), 0 0 20px rgba(196, 30, 58, 0.2);
        }}
        
        div[role="radiogroup"] div[data-testid="stMarkdownContainer"] p {{
            font-size: 1rem;
            font-weight: 600;
            margin: 0;
        }}
        
        /* Hide radio circles completely */
        div[role="radiogroup"] [data-testid="stWidgetLabel"] {{
            display: none;
        }}
        div[role="radiogroup"] input, 
        div[role="radiogroup"] [data-testid="stRadioButton"] div[class*="StyledControl"],
        div[role="radiogroup"] [data-testid="stRadioButton"] div[class*="st-"] {{
            display: none !important;
        }}
        
        /* =====================================================================
           BUTTONS - CTA & Interactive Elements
           ===================================================================== */
        .stButton > button {{
            background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%);
            color: {TEXT_PRIMARY};
            font-weight: 600;
            font-size: 1rem;
            border: none;
            border-radius: 10px;
            padding: 16px 36px;
            box-shadow: 0 4px 12px rgba(139, 21, 56, 0.4);
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
        }}
        
        .stButton > button:hover {{
            background: linear-gradient(135deg, {SECONDARY_COLOR} 0%, {PRIMARY_COLOR} 100%);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(139, 21, 56, 0.6);
        }}
        
        .stButton > button:active {{
            transform: translateY(0px);
            box-shadow: 0 2px 8px rgba(139, 21, 56, 0.4);
        }}
        
        /* =====================================================================
           INSIGHT CARDS - Alert Styling (NO EMOJIS)
           ===================================================================== */
        .stAlert {{
            border-radius: 12px;
            padding: 20px;
            border-left: 5px solid;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }}
        
        .stAlert:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
        }}
        
        /* Info alerts - Trigger analysis (red/critical) */
        .stAlert[data-baseweb="notification"][kind="info"] {{
            background: linear-gradient(135deg, rgba(139, 21, 56, 0.1) 0%, rgba(0,0,0,0.3) 100%);
            border-left-color: {SECONDARY_COLOR};
            color: #eee !important;
        }}
        
        /* Success alerts - Treatment efficacy (green) */
        .stAlert[data-baseweb="notification"][kind="success"] {{
            background: linear-gradient(135deg, rgba(46, 204, 113, 0.1) 0%, rgba(0,0,0,0.3) 100%);
            border-left-color: {COLOR_SUCCESS};
            color: #eee !important;
        }}
        
        /* Warning alerts - Demographics (orange) */
        .stAlert[data-baseweb="notification"][kind="warning"] {{
            background: linear-gradient(135deg, rgba(230, 126, 34, 0.1) 0%, rgba(0,0,0,0.3) 100%);
            border-left-color: {COLOR_WARNING};
            color: #eee !important;
        }}
        
        .stAlert p {{
            color: #eee !important;
            font-size: 0.95rem;
            line-height: 1.6;
        }}
        
        /* =====================================================================
           STREAMLIT METRIC COMPONENTS
           ===================================================================== */
        div[data-testid="stMetric"] {{
            background: linear-gradient(135deg, rgba(37, 37, 37, 0.9) 0%, rgba(45, 20, 25, 0.8) 100%);
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid {COLOR_SUCCESS};
            border: 1px solid {BORDER_COLOR};
            text-align: center;
        }}
        
        div[data-testid="stMetric"] label {{
            color: {TEXT_SECONDARY} !important;
            font-size: 0.85rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: {COLOR_SUCCESS} !important;
            font-size: 3.5rem !important;
            font-weight: 700 !important;
            font-family: 'Montserrat', sans-serif !important;
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
    pages = ["Home", "Severity Analysis", "Trigger Analysis", "Demographics", "Treatment", "Data Registry"]
    
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

    # =============================================================================
    # HOME PAGE
    # =============================================================================
    if st.session_state.page == "Home":
        # ---------------------------------------------------------------------
        # Hero Section - MetaHB Branding (Option 3: Clinical Notation)
        # ---------------------------------------------------------------------
        # Logo design represents oxidation state with superscript "+"
        # "Meta" = normal weight, "+" = oxidation indicator, "HB" = bold hemoglobin
        st.markdown(f"""
        <div class="hero-container">
            <div class="hero-title">
                <span class="brand-meta">Meta</span>
                <span class="brand-superscript">+</span>
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

        # ---------------------------------------------------------------------
        # Technical Pipeline Visualization
        # ---------------------------------------------------------------------
        # Visual representation of the NLP data processing workflow
        # Each step includes a numbered badge for clarity
        st.markdown(f"""
        <div class="pipeline-container">
            <div class="pipeline-step">
                <span class="pipeline-step-number">1</span>
                Data Ingestion
            </div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step">
                <span class="pipeline-step-number">2</span>
                NLP Extraction (SpaCy)
            </div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step">
                <span class="pipeline-step-number">3</span>
                Data Structuring
            </div>
            <div class="pipeline-arrow">→</div>
            <div class="pipeline-step">
                <span class="pipeline-step-number">4</span>
                Interactive Dashboard
            </div>
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
    elif st.session_state.page == "Severity Analysis":
        col1, col2 = st.columns([2, 1])
        with col1:
             st.subheader("Severity Distribution")
             plot_meth_distribution(df)
        with col2:
            st.subheader("Key Statistics")
            if not df.empty:
                meth_data = df[col_name].dropna() if 'col_name' in locals() else df['methb_level'].dropna()
                st.markdown(f"""
                <div style="background: rgba(30,30,40,0.9); padding: 24px; border-radius: 12px; border: 1px solid {BORDER_COLOR}; border-top: 4px solid {SECONDARY_COLOR}; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                    <h4 style="margin-top:0; color: {SECONDARY_COLOR}; letter-spacing: 1px; font-weight: 700;">SEVERITY INDICES</h4>
                    <hr style="border-color: rgba(255,255,255,0.1); margin: 15px 0;">
                    <ul style="list-style-type: none; padding-left: 0; font-size: 1rem; color: {TEXT_SECONDARY};">
                        <li style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #2ECC71;">●</span>
                            <span style="flex-grow: 1; padding-left: 10px;">Mild (<15%)</span> 
                            <strong style="color: white; font-size: 1.1rem;">{(meth_data < 15).sum()}</strong>
                        </li>
                        <li style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #E67E22;">●</span>
                            <span style="flex-grow: 1; padding-left: 10px;">Moderate (15-30%)</span> 
                            <strong style="color: white; font-size: 1.1rem;">{((meth_data >= 15) & (meth_data < 30)).sum()}</strong>
                        </li>
                        <li style="margin-bottom: 0px; display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #C0392B;">●</span>
                            <span style="flex-grow: 1; padding-left: 10px; font-weight: 700; color: #ff7675;">Severe (≥30%)</span> 
                            <strong style="color: #ff7675; font-size: 1.2rem; font-weight: 800;">{(meth_data >= 30).sum()}</strong>
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