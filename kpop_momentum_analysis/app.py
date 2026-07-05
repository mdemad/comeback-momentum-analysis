import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

from src.data_loader import load_clean_data, validate_data
from src.analytics import (
    calculate_runs_and_reentries, 
    calculate_song_metrics, 
    calculate_artist_metrics, 
    analyze_time_gaps
)

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="K-Pop Comeback & Fandom Intensity Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Injection
st.markdown("""
<style>
    /* Dark Mode Glassmorphism Style */
    .stApp {
        background: linear-gradient(135deg, #09090e 0%, #11111d 50%, #070709 100%);
        color: #e2e8f0;
        font-family: 'Inter', 'Outfit', sans-serif;
    }
    
    /* Custom headers */
    h1, h2, h3 {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #ff007f 0%, #7928ca 50%, #00dfd8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px !important;
    }
    
    /* Metrics glassmorphism cards */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #00dfd8 !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #94a3b8 !important;
    }
    
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        border-color: rgba(255, 0, 127, 0.4);
    }
    
    /* Glassmorphism sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(9, 9, 14, 0.7) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
    }
    
    /* Styled tabs */
    button[data-baseweb="tab"] {
        font-size: 1.05rem;
        font-weight: 600;
        color: #94a3b8;
        background-color: transparent !important;
        border: none !important;
        padding: 12px 24px !important;
        transition: color 0.3s ease, border-bottom 0.3s ease;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ff007f !important;
        border-bottom: 2px solid #ff007f !important;
    }
    
    /* Custom buttons */
    .stButton>button {
        background: linear-gradient(90deg, #ff007f 0%, #7928ca 100%);
        border: none;
        color: white;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: opacity 0.2s ease, transform 0.2s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        opacity: 0.95;
    }
    
    /* Decorative banner */
    .hero-banner {
        background: linear-gradient(90deg, rgba(255,0,127,0.15) 0%, rgba(121,40,202,0.15) 50%, rgba(0,223,216,0.15) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 30px;
        border-radius: 16px;
        margin-bottom: 30px;
        text-align: left;
        backdrop-filter: blur(10px);
    }
    
    .hero-banner h1 {
        margin: 0 !important;
        font-size: 2.5rem;
        background: linear-gradient(90deg, #fff 0%, #e2e8f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-banner p {
        color: #cbd5e1;
        font-size: 1.1rem;
        margin-top: 10px;
        margin-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)

# Cache loaded and processed data
@st.cache_data
def get_processed_data(file_path):
    df = load_clean_data(file_path)
    runs_df = calculate_runs_and_reentries(df)
    song_metrics = calculate_song_metrics(runs_df)
    artist_metrics = calculate_artist_metrics(song_metrics)
    gaps_df = analyze_time_gaps(runs_df)
    return df, runs_df, song_metrics, artist_metrics, gaps_df

# Resolve absolute path to data file
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "data", "spotify_south_korea_playlist.csv")

try:
    df, runs_df, song_metrics, artist_metrics, gaps_df = get_processed_data(data_path)
except Exception as e:
    st.error(f"Failed to load data from {data_path}. Error: {e}")
    st.info("Please make sure the dataset is placed inside the 'data/' directory.")
    st.stop()

# ----------------- SIDEBAR FILTERS -----------------
st.sidebar.markdown("## 🎛️ Analysis Controls")

# Date range selector
min_date = df['parsed_date'].min().to_pydatetime()
max_date = df['parsed_date'].max().to_pydatetime()

start_date, end_date = st.sidebar.slider(
    "Date Range Selection",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="DD-MM-YYYY"
)

# Album type filter
album_types = st.sidebar.multiselect(
    "Album Release Type",
    options=["single", "album", "compilation"],
    default=["single", "album", "compilation"]
)

# Explicit filter
explicit_option = st.sidebar.radio(
    "Content Explicit Type",
    options=["All Content", "Clean Only", "Explicit Only"],
    index=0
)

# Re-entries count threshold filter
max_reentries_in_dataset = int(song_metrics['reentries_count'].max())
reentry_threshold = st.sidebar.slider(
    "Minimum Re-entry Count",
    min_value=0,
    max_value=max_reentries_in_dataset,
    value=0
)

# Search Filters (Artist & Song)
st.sidebar.markdown("## 🔍 Quick Search")
search_artist = st.sidebar.text_input("Search Artist")
search_song = st.sidebar.text_input("Search Song Title")

# ----------------- APPLY FILTER LOGIC -----------------
filtered_df = df[
    (df['parsed_date'] >= pd.Timestamp(start_date)) & 
    (df['parsed_date'] <= pd.Timestamp(end_date))
]

# Apply explicit filtering to base df
if explicit_option == "Clean Only":
    filtered_df = filtered_df[filtered_df['is_explicit'] == False]
elif explicit_option == "Explicit Only":
    filtered_df = filtered_df[filtered_df['is_explicit'] == True]

# Filter runs and metrics tables based on selection
selected_songs = song_metrics[
    (song_metrics['album_type'].isin(album_types)) &
    (song_metrics['reentries_count'] >= reentry_threshold)
]

if explicit_option == "Clean Only":
    selected_songs = selected_songs[selected_songs['is_explicit'] == False]
elif explicit_option == "Explicit Only":
    selected_songs = selected_songs[selected_songs['is_explicit'] == True]

if search_artist:
    selected_songs = selected_songs[selected_songs['artist'].str.contains(search_artist, case=False)]
    filtered_df = filtered_df[filtered_df['artist'].str.contains(search_artist, case=False)]
    
if search_song:
    selected_songs = selected_songs[selected_songs['song'].str.contains(search_song, case=False)]
    filtered_df = filtered_df[filtered_df['song'].str.contains(search_song, case=False)]

# Sync filters to runs and gaps
runs_filtered = runs_df[
    runs_df['song'].isin(selected_songs['song']) & 
    runs_df['artist'].isin(selected_songs['artist'])
]
runs_filtered = runs_filtered[
    (runs_filtered['start_date'] >= pd.Timestamp(start_date)) &
    (runs_filtered['start_date'] <= pd.Timestamp(end_date))
]

gaps_filtered = gaps_df[
    gaps_df['song'].isin(selected_songs['song']) &
    gaps_df['artist'].isin(selected_songs['artist'])
]
gaps_filtered = gaps_filtered[
    (gaps_filtered['reentry_date'] >= pd.Timestamp(start_date)) &
    (gaps_filtered['reentry_date'] <= pd.Timestamp(end_date))
]

# ----------------- HERO HEADER -----------------
st.markdown(f"""
<div class="hero-banner">
    <h1>Comeback Momentum & Fandom Intensity</h1>
    <p>South Korea Spotify Top 50 Playlist Analytics | Atlantic Recording Corporation Strategy Portal</p>
</div>
""", unsafe_allow_html=True)

# ----------------- TABS CREATION -----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Dashboard", 
    "📈 Re-entry & Chart Timelines", 
    "⚡ Momentum Spike Detection", 
    "🏆 Fandom Intensity Leaderboard", 
    "🎨 Content & Duration Metrics"
])

# ================= TAB 1: EXECUTIVE DASHBOARD =================
with tab1:
    st.subheader("Key Performance Indicators (KPIs)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate values
    total_active_songs = len(selected_songs)
    total_reentries = int(selected_songs['reentries_count'].sum())
    avg_reentries_per_song = selected_songs['reentries_count'].mean() if len(selected_songs) > 0 else 0
    
    # Highest momentum spike score
    max_spike_row = runs_filtered.sort_values(by='momentum_spike_score', ascending=False)
    max_spike_val = max_spike_row['momentum_spike_score'].max() if not max_spike_row.empty else 0.0
    max_spike_song = f"{max_spike_row.iloc[0]['song']} ({max_spike_row.iloc[0]['artist']})" if not max_spike_row.empty else "N/A"
    
    # Average retention days post comeback
    avg_comeback_retention = runs_filtered[runs_filtered['is_reentry'] == True]['retention_days'].mean() if not runs_filtered[runs_filtered['is_reentry'] == True].empty else 0.0
    
    with col1:
        st.metric(
            label="Total Active Songs", 
            value=f"{total_active_songs}",
            help="Total unique song-artist combinations matching your filters"
        )
    with col2:
        st.metric(
            label="Total Chart Re-Entries", 
            value=f"{total_reentries}", 
            delta=f"{avg_reentries_per_song:.2f} avg per song",
            delta_color="normal",
            help="Sum of all re-entries across selected songs (fandom reactivation indicator)"
        )
    with col3:
        st.metric(
            label="Peak Comeback Momentum", 
            value=f"{max_spike_val:.1f}",
            delta=max_spike_song[:25] + ("..." if len(max_spike_song) > 25 else ""),
            delta_color="off",
            help="Highest individual run comeback momentum spike score"
        )
    with col4:
        st.metric(
            label="Avg Comeback Retention", 
            value=f"{avg_comeback_retention:.1f} Days",
            help="Average days a song retains its position on the playlist during a comeback run"
        )
        
    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("💡 Strategic Insights Summary")
        st.markdown(f"""
        - **Market Behavior**: Fandoms in South Korea utilize streaming strategies that lead to multiple chart entry peaks. In this dataset, we track **{len(runs_df[runs_df['is_reentry'] == True])} total re-entries** over **{df['parsed_date'].nunique()} days**.
        - **Comeback Lifespan**: Re-entering songs stay on the chart for an average of **{runs_df[runs_df['is_reentry'] == True]['retention_days'].mean():.1f} days** per comeback run, indicating that comebacks generate brief but intense momentum bursts.
        - **Singles vs. Albums**: Singles benefit from highly targeted initial promotion, but album tracks show higher re-entry rates during special events (anniversaries, awards) due to deep-catalog fandom streaming.
        - **Data Quality Check**: Deduplication removed redundant logs (e.g. duplicate positions on 01-03-2025). The dataset is clean with exactly 50 positions per day.
        """)
        
        # Add visual overview chart: Cumulative re-entries over time
        reentry_dates = runs_df[runs_df['is_reentry'] == True].groupby('start_date').size().reset_index(name='reentries_count')
        reentry_dates['cumulative_reentries'] = reentry_dates['reentries_count'].cumsum()
        
        fig = px.area(
            reentry_dates, 
            x='start_date', 
            y='cumulative_reentries',
            title="Cumulative Comeback Re-entries Over Time",
            labels={'start_date': 'Date', 'cumulative_reentries': 'Cumulative Count'},
            color_discrete_sequence=['#ff007f']
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="rgba(255,255,255,0.08)")
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col_right:
        st.subheader("🏁 Fandom Intensity Proxy")
        st.markdown("Compound score: **40% Re-entry freq**, **30% Peak rank acceleration**, **30% Recovery speed**.")
        
        leaderboard_mini = selected_songs.sort_values(by='fandom_intensity_score', ascending=False).head(5)
        
        for idx, row in leaderboard_mini.reset_index(drop=True).iterrows():
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px; margin-bottom: 10px; border-left: 4px solid #7928ca;">
                <div style="font-weight: bold; color: #fff;">#{idx+1} {row['song']}</div>
                <div style="font-size: 0.85rem; color: #94a3b8;">{row['artist']} | Score: <span style="color:#00dfd8; font-weight:bold;">{row['fandom_intensity_score']}</span></div>
                <div style="font-size: 0.75rem; color: #cbd5e1;">Re-entries: {row['reentries_count']} | Peak Rank: #{row['overall_peak_rank']}</div>
            </div>
            """, unsafe_allow_html=True)

# ================= TAB 2: RE-ENTRY TIMELINE & CHART TIMELINES =================
with tab2:
    st.subheader("📈 Song Position Trajectory & Re-Entry Timelines")
    st.markdown("Select a specific song to trace its entry, exit, and re-entry history over time.")
    
    # Dropdowns for song selection
    available_artists = sorted(selected_songs['artist'].unique())
    selected_artist = st.selectbox("Select Artist for Timeline", options=available_artists)
    
    songs_by_artist = sorted(selected_songs[selected_songs['artist'] == selected_artist]['song'].unique())
    selected_song = st.selectbox("Select Song", options=songs_by_artist)
    
    # Extract chart path for selected song
    song_chart_history = filtered_df[
        (filtered_df['song'] == selected_song) & 
        (filtered_df['artist'] == selected_artist)
    ].sort_values('parsed_date')
    
    if song_chart_history.empty:
        st.warning("No chart history found for the selected song in this date range.")
    else:
        # Show runs for this song
        song_runs = runs_df[
            (runs_df['song'] == selected_song) & 
            (runs_df['artist'] == selected_artist)
        ].sort_values('run_id')
        
        col_meta1, col_meta2, col_meta3 = st.columns(3)
        with col_meta1:
            st.markdown(f"**Total Runs (Entries):** {len(song_runs)}")
        with col_meta2:
            st.markdown(f"**Re-entries:** {len(song_runs)-1}")
        with col_meta3:
            st.markdown(f"**Overall Peak Rank:** #{song_chart_history['position'].min()}")
            
        # Draw chart position history (inverted Y axis, because position 1 is highest)
        fig_timeline = go.Figure()
        
        # Plot continuous path (we will connect consecutive days and break on gaps)
        # To show gaps clearly, we will add markers for each run
        for idx, run in song_runs.iterrows():
            run_data = song_chart_history[
                (song_chart_history['parsed_date'] >= run['start_date']) & 
                (song_chart_history['parsed_date'] <= run['end_date'])
            ]
            run_label = f"Initial Entry" if run['run_id'] == 0 else f"Re-Entry #{run['run_id']}"
            
            fig_timeline.add_trace(go.Scatter(
                x=run_data['parsed_date'],
                y=run_data['position'],
                mode='lines+markers',
                name=run_label,
                hovertemplate="<b>Date:</b> %{x}<br><b>Position:</b> #%{y}<br><b>Popularity:</b> %{customdata}<extra></extra>",
                customdata=run_data['popularity']
            ))
            
        fig_timeline.update_layout(
            title=f"Chart Position History: '{selected_song}' by {selected_artist}",
            xaxis_title="Date",
            yaxis_title="Playlist Position (Rank)",
            yaxis=dict(autorange="reversed", range=[50.5, 0.5], gridcolor="rgba(255,255,255,0.08)"),
            xaxis=dict(showgrid=False),
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Display the runs log
        st.markdown("### 📋 Chart Runs History Log")
        display_runs = song_runs[[
            'run_id', 'start_date', 'end_date', 'start_rank', 'peak_rank', 
            'days_to_peak_rank', 'retention_days', 'rank_jump', 'momentum_spike_score'
        ]].copy()
        
        display_runs['start_date'] = display_runs['start_date'].dt.strftime('%d-%m-%Y')
        display_runs['end_date'] = display_runs['end_date'].dt.strftime('%d-%m-%Y')
        display_runs.columns = [
            'Run ID', 'Start Date', 'End Date', 'Start Rank', 'Peak Rank', 
            'Days to Peak', 'Days on Chart', 'Rank Jump Magnitude', 'Momentum Score'
        ]
        
        st.dataframe(display_runs.reset_index(drop=True), use_container_width=True)

# ================= TAB 3: MOMENTUM & SPIKE DETECTION =================
with tab3:
    st.subheader("⚡ Comeback Momentum Spike Detection")
    st.markdown("Analysis of rank jumps and popularity surges immediately after re-entries.")
    
    # Filter to only re-entries
    reentries_only = runs_filtered[runs_filtered['is_reentry'] == True]
    
    if reentries_only.empty:
        st.info("No re-entries match your filters. Adjust the filters in the sidebar (e.g. set Re-entry Count threshold to 0 or check date range) to view momentum graphs.")
    else:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("#### Rank Jump Magnitude vs. Popularity Change")
            st.markdown("Larger bubbles represent higher Fandom Intensity Scores. High comeback momentum sits in the top-right corner.")
            
            # Map fandom scores back to runs for coloring/sizing
            reentries_with_scores = reentries_only.merge(
                selected_songs[['song', 'artist', 'fandom_intensity_score']], 
                on=['song', 'artist'], 
                how='left'
            )
            
            fig_scatter = px.scatter(
                reentries_with_scores,
                x='rank_jump',
                y='popularity_change',
                size='fandom_intensity_score',
                color='album_type',
                hover_name='song',
                hover_data=['artist', 'start_rank', 'peak_rank', 'momentum_spike_score'],
                labels={
                    'rank_jump': 'Rank Jump Magnitude (Start vs Peak)',
                    'popularity_change': 'Popularity Score Surge',
                    'album_type': 'Album Type'
                },
                color_discrete_map={'single': '#ff007f', 'album': '#7928ca', 'compilation': '#00dfd8'}
            )
            fig_scatter.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.08)")
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with col_chart2:
            st.markdown("#### Rank Recovery Speed Distribution")
            st.markdown("Calculates positions climbed per day. Fandom-driven comebacks often feature a near-vertical climb.")
            
            fig_hist = px.histogram(
                reentries_only,
                x='rank_recovery_speed',
                color='album_type',
                nbins=20,
                labels={'rank_recovery_speed': 'Rank Recovery Speed (Ranks/Day)'},
                color_discrete_map={'single': '#ff007f', 'album': '#7928ca', 'compilation': '#00dfd8'},
                barmode='overlay'
            )
            fig_hist.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.08)")
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
        st.markdown("---")
        st.markdown("### 🏆 Top 10 Most Intense Comeback Spikes")
        
        top_spikes = reentries_only.sort_values(by='momentum_spike_score', ascending=False).head(10)
        
        display_spikes = top_spikes[[
            'song', 'artist', 'start_date', 'start_rank', 'peak_rank', 
            'rank_jump', 'popularity_change', 'rank_recovery_speed', 'momentum_spike_score'
        ]].copy()
        
        display_spikes['start_date'] = display_spikes['start_date'].dt.strftime('%d-%m-%Y')
        display_spikes.columns = [
            'Song', 'Artist', 'Comeback Date', 'Re-entry Rank', 'Peak Rank', 
            'Rank Jump', 'Popularity Change', 'Recovery Speed (Ranks/Day)', 'Spike Score'
        ]
        
        st.dataframe(display_spikes.reset_index(drop=True), use_container_width=True)

# ================= TAB 4: FANDOM INTENSITY LEADERBOARD =================
with tab4:
    st.subheader("🏆 Fandom Intensity Leaderboard")
    st.markdown("Identifying songs and artists whose success is heavily characterized by recurring peaks and intense fandom reactivation.")
    
    col_lead1, col_lead2 = st.columns(2)
    
    with col_lead1:
        st.markdown("#### Top Songs by Fandom Intensity Score")
        top_songs = selected_songs.sort_values(by='fandom_intensity_score', ascending=False).head(10)
        
        fig_songs = px.bar(
            top_songs,
            x='fandom_intensity_score',
            y='song',
            color='reentries_count',
            hover_data=['artist', 'overall_peak_rank', 'total_retention_days'],
            orientation='h',
            labels={
                'fandom_intensity_score': 'Fandom Intensity Score',
                'song': 'Song Title',
                'reentries_count': 'Re-entries Count'
            },
            color_continuous_scale=px.colors.sequential.Sunsetdark
        )
        fig_songs.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(autorange="reversed", showgrid=False),
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)")
        )
        st.plotly_chart(fig_songs, use_container_width=True)
        
    with col_lead2:
        st.markdown("#### Top Artists by Average Fandom Intensity")
        
        # Calculate artist metrics from filtered list
        filtered_artist_metrics = calculate_artist_metrics(selected_songs)
        top_artists = filtered_artist_metrics.sort_values(by='avg_fandom_intensity_score', ascending=False).head(10)
        
        fig_artists = px.bar(
            top_artists,
            x='avg_fandom_intensity_score',
            y='artist',
            color='total_reentries',
            hover_data=['total_songs_charted', 'avg_reentries_per_song'],
            orientation='h',
            labels={
                'avg_fandom_intensity_score': 'Avg Fandom Score',
                'artist': 'Artist',
                'total_reentries': 'Total Re-entries'
            },
            color_continuous_scale=px.colors.sequential.Agsunset
        )
        fig_artists.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(autorange="reversed", showgrid=False),
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)")
        )
        st.plotly_chart(fig_artists, use_container_width=True)
        
    st.markdown("---")
    
    # Leaderboard Table with full attributes
    st.markdown("### 📊 Comprehensive Fandom Metrics Table")
    
    display_lead = selected_songs.sort_values(by='fandom_intensity_score', ascending=False)[[
        'song', 'artist', 'album_type', 'reentries_count', 
        'overall_peak_rank', 'total_retention_days', 'fandom_intensity_score'
    ]].copy()
    
    display_lead.columns = [
        'Song', 'Artist', 'Release Type', 'Re-entries', 'Peak Position', 'Total Days Charted', 'Fandom Intensity Score'
    ]
    
    st.dataframe(display_lead.reset_index(drop=True), use_container_width=True)

# ================= TAB 5: CONTENT & DURATION METRICS =================
with tab5:
    st.subheader("🎨 Content Attributes vs. Comeback Momentum")
    st.markdown("Investigating how release format, song duration, and explicit flags correlate with comeback velocity and sustainability.")
    
    col_attr1, col_attr2 = st.columns(2)
    
    with col_attr1:
        st.markdown("#### Album Type Advantage Index")
        st.markdown("Does releasing a song as a single vs. part of a full album result in different chart comeback momentum?")
        
        # Compare reentries and spikes across album_type
        if not runs_filtered.empty:
            album_type_comp = runs_filtered.groupby('album_type').agg(
                avg_reentries=('is_reentry', 'sum'),
                avg_spike_score=('momentum_spike_score', 'mean'),
                avg_retention=('retention_days', 'mean'),
                count=('song', 'nunique')
            ).reset_index()
            
            # Normalize reentries count by number of songs in category
            album_type_comp['avg_reentries_per_song'] = album_type_comp['avg_reentries'] / album_type_comp['count']
            
            fig_bar_comp = px.bar(
                album_type_comp,
                x='album_type',
                y='avg_reentries_per_song',
                color='album_type',
                hover_data=['avg_spike_score', 'avg_retention'],
                labels={
                    'album_type': 'Album Release Type',
                    'avg_reentries_per_song': 'Avg Re-entries per Song'
                },
                color_discrete_map={'single': '#ff007f', 'album': '#7928ca', 'compilation': '#00dfd8'}
            )
            fig_bar_comp.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="rgba(255,255,255,0.08)")
            )
            st.plotly_chart(fig_bar_comp, use_container_width=True)
        else:
            st.write("No data available.")
            
    with col_attr2:
        st.markdown("#### Explicit vs Clean Content Momentum")
        st.markdown("Comparing the distribution of Fandom Intensity Scores for Clean vs. Explicit songs.")
        
        if not selected_songs.empty:
            # We map explicit boolean to label
            selected_songs_viz = selected_songs.copy()
            selected_songs_viz['Content Rating'] = selected_songs_viz['is_explicit'].map({True: 'Explicit 🔞', False: 'Clean 🟢'})
            
            fig_box = px.box(
                selected_songs_viz,
                x='Content Rating',
                y='fandom_intensity_score',
                color='Content Rating',
                labels={'fandom_intensity_score': 'Fandom Intensity Score'},
                color_discrete_map={'Explicit 🔞': '#ff007f', 'Clean 🟢': '#00dfd8'}
            )
            fig_box.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="rgba(255,255,255,0.08)")
            )
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.write("No data available.")
            
    st.markdown("---")
    
    col_attr3, col_attr4 = st.columns(2)
    
    with col_attr3:
        st.markdown("#### Song Duration vs. Comeback Magnitude")
        st.markdown("Is there a sweet spot in song length (minutes) that optimizes re-entry momentum? Fandom streaming behaviors can favor shorter tracks.")
        
        # Link song duration from df to selected_songs
        song_duration_df = df.groupby(['song', 'artist'])['duration_min'].first().reset_index()
        selected_songs_dur = selected_songs.merge(song_duration_df, on=['song', 'artist'], how='left')
        
        fig_dur_scatter = px.scatter(
            selected_songs_dur,
            x='duration_min',
            y='fandom_intensity_score',
            color='album_type',
            hover_name='song',
            hover_data=['artist', 'reentries_count'],
            labels={
                'duration_min': 'Song Duration (Minutes)',
                'fandom_intensity_score': 'Fandom Intensity Score',
                'album_type': 'Album Type'
            },
            color_discrete_map={'single': '#ff007f', 'album': '#7928ca', 'compilation': '#00dfd8'}
        )
        fig_dur_scatter.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.08)")
        )
        st.plotly_chart(fig_dur_scatter, use_container_width=True)
        
    with col_attr4:
        st.markdown("#### Album Size vs. Fandom Intensity")
        st.markdown("Does releasing larger albums dilute fandom streaming focus, or does it boost collective catalog re-entries?")
        
        # Album size is 'total_tracks'
        fig_size_scatter = px.scatter(
            selected_songs,
            x='total_tracks',
            y='fandom_intensity_score',
            color='album_type',
            hover_name='song',
            hover_data=['artist', 'reentries_count'],
            labels={
                'total_tracks': 'Total Tracks in Album',
                'fandom_intensity_score': 'Fandom Intensity Score',
                'album_type': 'Album Type'
            },
            color_discrete_map={'single': '#ff007f', 'album': '#7928ca', 'compilation': '#00dfd8'}
        )
        fig_size_scatter.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.08)")
        )
        st.plotly_chart(fig_size_scatter, use_container_width=True)
