import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_clean_data
from src.analytics import calculate_runs_and_reentries, calculate_song_metrics

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_path = os.path.join(project_root, "data", "spotify_south_korea_playlist.csv")
    
    df = load_clean_data(data_path)
    runs_df = calculate_runs_and_reentries(df)
    song_metrics = calculate_song_metrics(runs_df)
    
    print("=== Album Type Stats ===")
    album_stats = song_metrics.groupby('album_type').agg(
        avg_reentries=('reentries_count', 'mean'),
        avg_fandom_score=('fandom_intensity_score', 'mean'),
        avg_retention=('total_retention_days', 'mean'),
        song_count=('song', 'count')
    ).reset_index()
    print(album_stats.to_string(index=False))
    
    print("\n=== Explicit Rating Stats ===")
    explicit_stats = song_metrics.groupby('is_explicit').agg(
        avg_reentries=('reentries_count', 'mean'),
        avg_fandom_score=('fandom_intensity_score', 'mean'),
        avg_retention=('total_retention_days', 'mean'),
        song_count=('song', 'count')
    ).reset_index()
    print(explicit_stats.to_string(index=False))
    
    print("\n=== Top Artists by Total Re-entries ===")
    artist_reentries = song_metrics.groupby('artist')['reentries_count'].sum().reset_index()
    print(artist_reentries.sort_values(by='reentries_count', ascending=False).head(5).to_string(index=False))

if __name__ == "__main__":
    main()
