import os
import sys

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_clean_data, validate_data
from src.analytics import calculate_runs_and_reentries, calculate_song_metrics, calculate_artist_metrics, analyze_time_gaps

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_path = os.path.join(project_root, "data", "spotify_south_korea_playlist.csv")
    
    print("=== Step 1: Loading and Cleaning Data ===")
    df = load_clean_data(data_path)
    validation = validate_data(df)
    
    print(f"Total Rows after cleaning: {validation['total_records']}")
    print(f"Start Date: {validation['start_date']}")
    print(f"End Date: {validation['end_date']}")
    print(f"Days without 50 entries: {validation['days_without_50_entries']}")
    print(f"Min Position: {validation['min_position']}, Max Position: {validation['max_position']}")
    
    print("\n=== Step 2: Running Analytics (Runs & Re-Entries) ===")
    runs_df = calculate_runs_and_reentries(df)
    print(f"Total Runs detected across all songs: {len(runs_df)}")
    print(f"Total Re-entries detected: {runs_df['is_reentry'].sum()}")
    
    print("\n=== Step 3: Aggregating Song Metrics ===")
    song_metrics = calculate_song_metrics(runs_df)
    print(f"Total Unique Songs: {len(song_metrics)}")
    
    print("\nTop 5 Songs by Fandom Intensity Score:")
    top_fandom_songs = song_metrics.sort_values(by='fandom_intensity_score', ascending=False).head(5)
    for idx, r in top_fandom_songs.iterrows():
        print(f"  {r['song']} by {r['artist']} | Re-entries: {r['reentries_count']} | Fandom Score: {r['fandom_intensity_score']} | Peak Rank: {r['overall_peak_rank']}")
        
    print("\nTop 5 Songs by Re-entries Count:")
    top_reentry_songs = song_metrics.sort_values(by='reentries_count', ascending=False).head(5)
    for idx, r in top_reentry_songs.iterrows():
        print(f"  {r['song']} by {r['artist']} | Re-entries: {r['reentries_count']} | Avg Re-entry Spike: {r['avg_reentry_spike_score']:.2f}")
        
    print("\n=== Step 4: Aggregating Artist Metrics ===")
    artist_metrics = calculate_artist_metrics(song_metrics)
    print(f"Total Unique Artists: {len(artist_metrics)}")
    
    print("\nTop 5 Artists by Average Fandom Intensity Score:")
    top_fandom_artists = artist_metrics.sort_values(by='avg_fandom_intensity_score', ascending=False).head(5)
    for idx, r in top_fandom_artists.iterrows():
        print(f"  {r['artist']} | Avg Fandom Score: {r['avg_fandom_intensity_score']} | Total Re-entries: {r['total_reentries']}")

    print("\n=== Step 5: Analyzing Time Gaps ===")
    gaps_df = analyze_time_gaps(runs_df)
    print(f"Total Gaps (exits followed by re-entries): {len(gaps_df)}")
    print(f"Average Gap Duration: {gaps_df['gap_days'].mean():.2f} days")
    print(f"Median Gap Duration: {gaps_df['gap_days'].median():.2f} days")
    
if __name__ == "__main__":
    main()
