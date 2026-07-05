import pandas as pd
import numpy as np

def calculate_runs_and_reentries(df):
    """
    Identifies continuous chart runs, exits, and re-entries for each song.
    Accounts for missing dates in the dataset.
    """
    # Ensure dataframe is sorted chronologically
    df = df.sort_values(by=['parsed_date', 'position']).reset_index(drop=True)
    
    # Get all unique dates in the dataset, sorted
    all_dates = sorted(df['parsed_date'].unique())
    date_to_idx = {date: idx for idx, date in enumerate(all_dates)}
    
    # Add a date index column to help find gaps
    df['date_idx'] = df['parsed_date'].map(date_to_idx)
    
    run_records = []
    
    # Group by song and artist to trace chart history
    grouped = df.groupby(['song', 'artist'])
    
    for (song, artist), group in grouped:
        # Sort group by date
        group = group.sort_values('parsed_date')
        
        # Identify gaps in the consecutive date indices
        # If the difference between consecutive date indices is > 1, there is a gap (exit and re-entry)
        group = group.copy()
        group['gap'] = group['date_idx'].diff() > 1
        group['run_id'] = group['gap'].cumsum()
        
        # Calculate metrics for each run of the song
        song_runs = group.groupby('run_id')
        num_runs = len(song_runs)
        
        for run_id, run_df in song_runs:
            run_df = run_df.sort_values('parsed_date')
            
            start_date = run_df['parsed_date'].min()
            end_date = run_df['parsed_date'].max()
            
            # Find the start rank and popularity
            start_row = run_df.iloc[0]
            start_rank = start_row['position']
            start_popularity = start_row['popularity']
            
            # Find the peak rank (minimum position value)
            peak_rank = run_df['position'].min()
            # Find first date the peak rank was achieved
            peak_rank_df = run_df[run_df['position'] == peak_rank]
            peak_rank_date = peak_rank_df['parsed_date'].min()
            
            # Find the peak popularity
            peak_popularity = run_df['popularity'].max()
            peak_popularity_df = run_df[run_df['popularity'] == peak_popularity]
            peak_popularity_date = peak_popularity_df['parsed_date'].min()
            
            # Compute time-to-peak metrics
            days_to_peak_rank = (peak_rank_date - start_date).days
            days_to_peak_pop = (peak_popularity_date - start_date).days
            
            # Duration and retention days
            retention_days = len(run_df)  # days actually present on the chart
            duration_days = (end_date - start_date).days + 1  # calendar days of the run
            
            # Calculate rank jump (Start Position - Peak Position)
            # Since rank 1 is higher than rank 50, a larger positive number is a bigger jump
            rank_jump = start_rank - peak_rank
            
            # Popularity change
            popularity_change = peak_popularity - start_popularity
            
            # Rank Recovery Speed
            # If peak was achieved on the first day, speed is rank_jump (or rank_jump / 1)
            rank_recovery_speed = rank_jump / max(1, days_to_peak_rank)
            
            # Popularity Spike Sharpness
            popularity_spike_sharpness = popularity_change / max(1, days_to_peak_pop)
            
            # Momentum Spike Score
            # Combines rank jump and popularity change during the first part of the run
            # Normalized to a reasonable range
            momentum_spike_score = max(0, (rank_jump / 49.0) * 50 + (popularity_change / 100.0) * 50)
            
            run_records.append({
                'song': song,
                'artist': artist,
                'album_type': start_row['album_type'],
                'total_tracks': start_row['total_tracks'],
                'is_explicit': start_row['is_explicit'],
                'album_cover_url': start_row['album_cover_url'],
                'run_id': run_id,  # 0 = first entry, 1 = first re-entry, etc.
                'is_reentry': run_id > 0,
                'start_date': start_date,
                'end_date': end_date,
                'start_rank': start_rank,
                'start_popularity': start_popularity,
                'peak_rank': peak_rank,
                'peak_popularity': peak_popularity,
                'days_to_peak_rank': days_to_peak_rank,
                'days_to_peak_pop': days_to_peak_pop,
                'retention_days': retention_days,
                'duration_days': duration_days,
                'rank_jump': max(0, rank_jump),
                'popularity_change': max(0, popularity_change),
                'rank_recovery_speed': max(0.0, rank_recovery_speed),
                'popularity_spike_sharpness': max(0.0, popularity_spike_sharpness),
                'momentum_spike_score': momentum_spike_score
            })
            
    runs_df = pd.DataFrame(run_records)
    return runs_df

def calculate_song_metrics(runs_df):
    """
    Aggregates run-level metrics to the song level.
    """
    song_metrics = []
    
    grouped = runs_df.groupby(['song', 'artist'])
    for (song, artist), group in grouped:
        num_runs = len(group)
        reentries = num_runs - 1
        
        # First entry metrics
        first_entry = group[group['run_id'] == 0].iloc[0]
        
        # Re-entry metrics (if any)
        reentries_df = group[group['run_id'] > 0]
        
        avg_reentry_spike_score = reentries_df['momentum_spike_score'].mean() if not reentries_df.empty else 0.0
        max_reentry_rank_jump = reentries_df['rank_jump'].max() if not reentries_df.empty else 0
        avg_reentry_retention = reentries_df['retention_days'].mean() if not reentries_df.empty else 0.0
        avg_reentry_recovery_speed = reentries_df['rank_recovery_speed'].mean() if not reentries_df.empty else 0.0
        
        # Overall song peak rank and popularity
        overall_peak_rank = group['peak_rank'].min()
        overall_peak_popularity = group['peak_popularity'].max()
        total_retention_days = group['retention_days'].sum()
        
        # Fandom Intensity Proxy Score
        # Compounds: re-entry frequency, recovery speed on comebacks, and spike intensity
        # Weighting: Reentry frequency (40%), Avg Spike Score (30%), Avg Recovery Speed (30%)
        # Let's scale each component relative to typical max values
        reentry_factor = min(100.0, reentries * 25.0)  # max score at 4+ re-entries
        spike_factor = min(100.0, avg_reentry_spike_score * 2.0)  # max score at spike score of 50
        speed_factor = min(100.0, avg_reentry_recovery_speed * 10.0)  # max score at speed of 10 positions/day
        
        # If no re-entries, fandom intensity is lower but not zero (based on first entry metrics)
        if reentries == 0:
            # For first entry, use first entry metrics as a baseline with lower weight
            first_spike = first_entry['momentum_spike_score']
            first_speed = first_entry['rank_recovery_speed']
            fandom_intensity_score = min(40.0, (first_spike * 0.5 + first_speed * 2.0))
        else:
            fandom_intensity_score = (reentry_factor * 0.4) + (spike_factor * 0.3) + (speed_factor * 0.3)
            
        song_metrics.append({
            'song': song,
            'artist': artist,
            'album_type': first_entry['album_type'],
            'total_tracks': first_entry['total_tracks'],
            'is_explicit': first_entry['is_explicit'],
            'album_cover_url': first_entry['album_cover_url'],
            'reentries_count': reentries,
            'first_entry_date': first_entry['start_date'],
            'overall_peak_rank': overall_peak_rank,
            'overall_peak_popularity': overall_peak_popularity,
            'total_retention_days': total_retention_days,
            'avg_reentry_spike_score': avg_reentry_spike_score,
            'max_reentry_rank_jump': max_reentry_rank_jump,
            'avg_reentry_retention': avg_reentry_retention,
            'avg_reentry_recovery_speed': avg_reentry_recovery_speed,
            'fandom_intensity_score': round(fandom_intensity_score, 2)
        })
        
    return pd.DataFrame(song_metrics)

def calculate_artist_metrics(song_metrics_df):
    """
    Aggregates song-level metrics to the artist level.
    """
    artist_metrics = []
    
    grouped = song_metrics_df.groupby('artist')
    for artist, group in grouped:
        total_songs = len(group)
        total_reentries = group['reentries_count'].sum()
        avg_reentries_per_song = group['reentries_count'].mean()
        best_peak_rank = group['overall_peak_rank'].min()
        max_popularity = group['overall_peak_popularity'].max()
        avg_fandom_score = group['fandom_intensity_score'].mean()
        max_fandom_score = group['fandom_intensity_score'].max()
        total_retention = group['total_retention_days'].sum()
        
        # Album Comeback Advantage Index components
        album_songs = group[group['album_type'] == 'album']
        single_songs = group[group['album_type'] == 'single']
        
        album_reentries = album_songs['reentries_count'].mean() if not album_songs.empty else 0.0
        single_reentries = single_songs['reentries_count'].mean() if not single_songs.empty else 0.0
        
        # Album advantage: ratio of album re-entries to single re-entries
        # > 1 means albums re-enter more, < 1 means singles re-enter more
        album_advantage_index = album_reentries / max(0.1, single_reentries) if single_reentries > 0 else (1.0 if not album_songs.empty else 0.0)
        
        artist_metrics.append({
            'artist': artist,
            'total_songs_charted': total_songs,
            'total_reentries': total_reentries,
            'avg_reentries_per_song': round(avg_reentries_per_song, 2),
            'best_peak_rank': best_peak_rank,
            'max_popularity': max_popularity,
            'avg_fandom_intensity_score': round(avg_fandom_score, 2),
            'max_fandom_intensity_score': round(max_fandom_score, 2),
            'total_retention_days': total_retention,
            'album_reentries_avg': round(album_reentries, 2),
            'single_reentries_avg': round(single_reentries, 2),
            'album_comeback_advantage_index': round(album_advantage_index, 2)
        })
        
    return pd.DataFrame(artist_metrics)

def analyze_time_gaps(runs_df):
    """
    Computes time gaps (days) between exits and re-entries.
    """
    gap_records = []
    
    grouped = runs_df.groupby(['song', 'artist'])
    for (song, artist), group in grouped:
        if len(group) < 2:
            continue
            
        group = group.sort_values('run_id')
        for i in range(len(group) - 1):
            prev_run = group.iloc[i]
            next_run = group.iloc[i+1]
            
            gap_days = (next_run['start_date'] - prev_run['end_date']).days
            
            gap_records.append({
                'song': song,
                'artist': artist,
                'from_run_id': prev_run['run_id'],
                'to_run_id': next_run['run_id'],
                'exit_date': prev_run['end_date'],
                'reentry_date': next_run['start_date'],
                'gap_days': gap_days,
                'reentry_position': next_run['start_rank'],
                'reentry_popularity': next_run['start_popularity'],
                'peak_reached_rank': next_run['peak_rank'],
                'momentum_spike_score': next_run['momentum_spike_score']
            })
            
    return pd.DataFrame(gap_records)
