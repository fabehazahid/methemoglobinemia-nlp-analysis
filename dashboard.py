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

# Page configuration
st.set_page_config(
    page_title="MetHb Analysis Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the data"""
    try:
        df = pd.read_csv('data/processed/methb_structured_data.csv')
        return df
    except FileNotFoundError:
        st.error("❌ Data file not found! Make sure 'data/processed/methb_structured_data.csv' exists.")
        st.stop()

def create_metrics_row(df):
    """Create top-level metrics"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Cases", len(df))
    
    with col2:
        methb_mean = df['methb_level'].mean()
        st.metric("Avg MetHb Level", f"{methb_mean:.1f}%" if not pd.isna(methb_mean) else "N/A")
    
    with col3:
        recovery_rate = (df['outcome'] == 'Recovered').sum() / len(df[df['outcome'] != 'Unknown']) * 100
        st.metric("Recovery Rate", f"{recovery_rate:.1f}%")
    
    with col4:
        unique_triggers = df[df['trigger'] != 'Unknown']['trigger'].nunique()
        st.metric("Unique Triggers", unique_triggers)
    
    with col5:
        avg_age = df['age'].mean()
        st.metric("Avg Age", f"{avg_age:.1f}" if not pd.isna(avg_age) else "N/A")

def plot_meth_distribution(df):
    """Plot MetHb level distribution"""
    meth_data = df['methb_level'].dropna()
    
    if len(meth_data) == 0:
        st.warning("No MetHb level data available")
        return
    
    fig = go.Figure()
    
    # Histogram
    fig.add_trace(go.Histogram(
        x=meth_data,
        nbinsx=20,
        name='MetHb Levels',
        marker_color='steelblue',
        opacity=0.7
    ))
    
    # Add mean line
    fig.add_vline(
        x=meth_data.mean(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: {meth_data.mean():.1f}%",
        annotation_position="top"
    )
    
    # Add severity zones
    fig.add_vrect(x0=0, x1=15, fillcolor="green", opacity=0.1, annotation_text="Mild")
    fig.add_vrect(x0=15, x1=30, fillcolor="yellow", opacity=0.1, annotation_text="Moderate")
    fig.add_vrect(x0=30, x1=100, fillcolor="red", opacity=0.1, annotation_text="Severe")
    
    fig.update_layout(
        title="Distribution of Methemoglobin Levels",
        xaxis_title="MetHb Level (%)",
        yaxis_title="Number of Cases",
        showlegend=False,
        hovermode='x'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_trigger_analysis(df):
    """Plot trigger frequency and severity"""
    df_filtered = df[df['trigger'] != 'Unknown']
    
    if len(df_filtered) == 0:
        st.warning("No trigger data available")
        return
    
    # Frequency count
    trigger_counts = df_filtered['trigger'].value_counts()
    
    # Create subplot with two charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart of frequencies
        fig1 = px.bar(
            x=trigger_counts.values,
            y=trigger_counts.index,
            orientation='h',
            title="Trigger Frequency",
            labels={'x': 'Number of Cases', 'y': 'Trigger'},
            color=trigger_counts.values,
            color_continuous_scale='Blues'
        )
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Box plot of MetHb by trigger
        df_with_meth = df_filtered[df_filtered['methb_level'].notna()]
        
        if len(df_with_meth) > 0:
            fig2 = px.box(
                df_with_meth,
                y='trigger',
                x='methb_level',
                title="MetHb Levels by Trigger",
                labels={'methb_level': 'MetHb Level (%)', 'trigger': 'Trigger'},
                color='trigger'
            )
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

def plot_age_analysis(df):
    """Plot age distribution and patterns"""
    df_age = df[df['age'].notna()]
    
    if len(df_age) == 0:
        st.warning("No age data available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Age distribution histogram
        fig1 = px.histogram(
            df_age,
            x='age',
            nbins=15,
            title="Age Distribution",
            labels={'age': 'Age (years)', 'count': 'Number of Cases'},
            color_discrete_sequence=['lightblue']
        )
        fig1.add_vline(
            x=df_age['age'].mean(),
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {df_age['age'].mean():.1f}"
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Age vs MetHb scatter
        df_age_meth = df_age[df_age['methb_level'].notna()]
        
        if len(df_age_meth) > 0:
            fig2 = px.scatter(
                df_age_meth,
                x='age',
                y='methb_level',
                title="Age vs MetHb Severity",
                labels={'age': 'Age (years)', 'methb_level': 'MetHb Level (%)'},
                color='trigger',
                hover_data=['pmid', 'outcome']
            )
            st.plotly_chart(fig2, use_container_width=True)

def plot_treatment_outcomes(df):
    """Plot treatment effectiveness"""
    # Filter for cases with known outcomes
    df_outcomes = df[df['outcome'].isin(['Recovered', 'Fatal', 'Admitted'])]
    
    if len(df_outcomes) == 0:
        st.warning("No outcome data available")
        return
    
    # Get top treatments
    treatment_list = []
    for treatment in df_outcomes['treatment'].dropna():
        if treatment != 'Unknown':
            treatment_list.extend([t.strip() for t in str(treatment).split(',')])
    
    if len(treatment_list) == 0:
        return
    
    top_treatments = pd.Series(treatment_list).value_counts().head(5).index
    
    # Create outcome summary
    outcome_data = []
    for treatment in top_treatments:
        cases = df_outcomes[df_outcomes['treatment'].str.contains(treatment, na=False)]
        for outcome in ['Recovered', 'Fatal', 'Admitted']:
            count = (cases['outcome'] == outcome).sum()
            if count > 0:
                outcome_data.append({
                    'Treatment': treatment,
                    'Outcome': outcome,
                    'Count': count
                })
    
    if outcome_data:
        outcome_df = pd.DataFrame(outcome_data)
        
        fig = px.bar(
            outcome_df,
            x='Treatment',
            y='Count',
            color='Outcome',
            title="Treatment Outcomes",
            barmode='group',
            color_discrete_map={'Recovered': '#2ecc71', 'Fatal': '#e74c3c', 'Admitted': '#f39c12'}
        )
        st.plotly_chart(fig, use_container_width=True)

def show_data_table(df, filters):
    """Show filtered data table"""
    st.subheader("📋 Case Data Table")
    
    # Apply filters
    filtered_df = df.copy()
    
    if filters['triggers']:
        filtered_df = filtered_df[filtered_df['trigger'].isin(filters['triggers'])]
    
    if filters['age_range']:
        filtered_df = filtered_df[
            (filtered_df['age'] >= filters['age_range'][0]) & 
            (filtered_df['age'] <= filters['age_range'][1])
        ]
    
    if filters['methb_range']:
        filtered_df = filtered_df[
            (filtered_df['methb_level'] >= filters['methb_range'][0]) & 
            (filtered_df['methb_level'] <= filters['methb_range'][1])
        ]
    
    if filters['outcomes']:
        filtered_df = filtered_df[filtered_df['outcome'].isin(filters['outcomes'])]
    
    # Display summary
    st.write(f"Showing {len(filtered_df)} of {len(df)} cases")
    
    # Select columns to display
    display_cols = ['pmid', 'methb_level', 'trigger', 'treatment', 'age', 'gender', 
                   'symptoms', 'outcome', 'data_quality_score']
    display_cols = [col for col in display_cols if col in filtered_df.columns]
    
    # Format the dataframe
    display_df = filtered_df[display_cols].copy()
    
    # Round numeric columns
    if 'methb_level' in display_df.columns:
        display_df['methb_level'] = display_df['methb_level'].round(1)
    if 'age' in display_df.columns:
        display_df['age'] = display_df['age'].fillna('N/A')
    
    # Display
    st.dataframe(display_df, use_container_width=True, height=400)
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_meth_data.csv",
        mime="text/csv"
    )

def main():
    """Main dashboard app"""
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Methemoglobinemia Analysis Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Initialize filters
    filters = {}
    
    # Trigger filter
    all_triggers = df[df['trigger'] != 'Unknown']['trigger'].unique().tolist()
    if all_triggers:
        filters['triggers'] = st.sidebar.multiselect(
            "Select Triggers",
            options=all_triggers,
            default=[]
        )
    else:
        filters['triggers'] = []
    
    # Age range filter
    age_min = int(df['age'].min()) if df['age'].notna().any() else 0
    age_max = int(df['age'].max()) if df['age'].notna().any() else 100
    
    if age_min < age_max:
        filters['age_range'] = st.sidebar.slider(
            "Age Range",
            min_value=age_min,
            max_value=age_max,
            value=(age_min, age_max)
        )
    else:
        filters['age_range'] = None
    
    # MetHb range filter
    meth_min = float(df['methb_level'].min()) if df['methb_level'].notna().any() else 0.0
    meth_max = float(df['methb_level'].max()) if df['methb_level'].notna().any() else 100.0

    if meth_min < meth_max:
        filters['methb_range'] = st.sidebar.slider(
            "MetHb Level Range (%)",
            min_value=meth_min,
            max_value=meth_max,
            value=(meth_min, meth_max)
        )
    else:
        filters['methb_range'] = None
    
    # Outcome filter
    all_outcomes = df[df['outcome'] != 'Unknown']['outcome'].unique().tolist()
    if all_outcomes:
        filters['outcomes'] = st.sidebar.multiselect(
            "Select Outcomes",
            options=all_outcomes,
            default=all_outcomes
        )
    else:
        filters['outcomes'] = []
    
    # Data quality filter
    min_quality = st.sidebar.slider(
        "Minimum Data Quality Score",
        min_value=0,
        max_value=100,
        value=0
    )
    
    # Apply quality filter to main dataframe
    if min_quality > 0:
        df = df[df['data_quality_score'] >= min_quality]
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"📊 Total Cases: {len(df)}")
    
    # Main content
    
    # Top metrics
    create_metrics_row(df)
    
    st.markdown("---")
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "💊 Trigger Analysis", 
        "👥 Demographics", 
        "💉 Treatment", 
        "📋 Data Table"
    ])
    
    with tab1:
        st.header("Overview")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            plot_meth_distribution(df)
        
        with col2:
            st.subheader("Key Statistics")
            
            meth_data = df['methb_level'].dropna()
            if len(meth_data) > 0:
                st.metric("Cases with MetHb Data", len(meth_data))
                st.metric("Mean MetHb", f"{meth_data.mean():.1f}%")
                st.metric("Median MetHb", f"{meth_data.median():.1f}%")
                st.metric("Max MetHb", f"{meth_data.max():.1f}%")
                
                # Severity breakdown
                st.markdown("**Severity Breakdown:**")
                mild = (meth_data < 15).sum()
                moderate = ((meth_data >= 15) & (meth_data < 30)).sum()
                severe = (meth_data >= 30).sum()
                
                st.write(f"- Mild (<15%): {mild} cases")
                st.write(f"- Moderate (15-30%): {moderate} cases")
                st.write(f"- Severe (≥30%): {severe} cases")
    
    with tab2:
        st.header("Trigger Analysis")
        plot_trigger_analysis(df)
        
        # Additional stats
        st.subheader("Trigger Statistics")
        df_triggers = df[(df['trigger'] != 'Unknown') & (df['methb_level'].notna())]
        
        if len(df_triggers) > 0:
            trigger_stats = df_triggers.groupby('trigger')['methb_level'].agg([
                ('Count', 'count'),
                ('Mean', 'mean'),
                ('Median', 'median'),
                ('Max', 'max')
            ]).round(1).sort_values('Mean', ascending=False)
            
            st.dataframe(trigger_stats, use_container_width=True)
    
    with tab3:
        st.header("Demographics Analysis")
        plot_age_analysis(df)
        
        # Gender breakdown
        st.subheader("Gender Distribution")
        gender_counts = df['gender'].value_counts()
        
        if len(gender_counts) > 0:
            fig = px.pie(
                values=gender_counts.values,
                names=gender_counts.index,
                title="Gender Distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("Treatment Analysis")
        plot_treatment_outcomes(df)
        
        # Methylene Blue specific analysis
        st.subheader("Methylene Blue Analysis")
        mb_cases = df[df['treatment'].str.contains('Methylene Blue', na=False)]
        
        if len(mb_cases) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total MB Cases", len(mb_cases))
            
            with col2:
                mb_recovered = (mb_cases['outcome'] == 'Recovered').sum()
                mb_known_outcomes = len(mb_cases[mb_cases['outcome'] != 'Unknown'])
                if mb_known_outcomes > 0:
                    recovery_rate = mb_recovered / mb_known_outcomes * 100
                    st.metric("MB Recovery Rate", f"{recovery_rate:.1f}%")
            
            with col3:
                mb_with_methb = mb_cases[mb_cases['methb_level'].notna()]
                if len(mb_with_methb) > 0:
                    st.metric("Avg MetHb (MB cases)", f"{mb_with_methb['methb_level'].mean():.1f}%")

    with tab5:
        show_data_table(df, filters)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: gray;'>
            <p>Methemoglobinemia Clinical NLP Analysis Dashboard</p>
            <p>Data extracted from PubMed case reports using NLP</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()