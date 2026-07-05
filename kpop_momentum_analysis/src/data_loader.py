import pandas as pd
import numpy as np
import os

def load_clean_data(csv_path):
    """
    Loads, cleans, and validates the Spotify South Korea Top 50 Playlist dataset.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset file not found at: {csv_path}")
        
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # 1. Clean column strings and strip spaces
    df['song'] = df['song'].astype(str).str.strip()
    df['artist'] = df['artist'].astype(str).str.strip()
    df['album_type'] = df['album_type'].astype(str).str.lower().str.strip()
    
    # Normalize boolean explicit flag
    if df['is_explicit'].dtype == object:
        df['is_explicit'] = df['is_explicit'].astype(str).str.upper().str.strip() == 'TRUE'
    else:
        df['is_explicit'] = df['is_explicit'].astype(bool)
        
    # 2. Parse dates
    df['parsed_date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
    
    # Drop rows with invalid dates
    invalid_dates = df['parsed_date'].isna().sum()
    if invalid_dates > 0:
        df = df.dropna(subset=['parsed_date'])
        
    # 3. Handle duplicates
    # We want exactly 50 entries per day. If a date has duplicates, we group by (date, position)
    # and keep the one with the highest popularity score.
    df = df.sort_values(by=['parsed_date', 'position', 'popularity'], ascending=[True, True, False])
    df = df.drop_duplicates(subset=['parsed_date', 'position'], keep='first')
    
    # 4. Convert duration to minutes
    df['duration_min'] = df['duration_ms'] / 60000.0
    
    # 5. Clean metadata (fill missing, enforce types)
    df['position'] = df['position'].astype(int)
    df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce').fillna(0).astype(int)
    df['total_tracks'] = pd.to_numeric(df['total_tracks'], errors='coerce').fillna(1).astype(int)
    
    # Sort final dataframe chronologically and by chart rank
    df = df.sort_values(by=['parsed_date', 'position']).reset_index(drop=True)
    
    return df

def validate_data(df):
    """
    Validates that the processed DataFrame meets critical project requirements.
    """
    validation_results = {}
    
    # Check 1: 50 entries per day
    entries_per_day = df.groupby('parsed_date').size()
    days_not_50 = entries_per_day[entries_per_day != 50]
    validation_results['days_without_50_entries'] = len(days_not_50)
    validation_results['days_without_50_details'] = days_not_50.to_dict()
    
    # Check 2: Position range is 1-50
    validation_results['min_position'] = int(df['position'].min())
    validation_results['max_position'] = int(df['position'].max())
    
    # Check 3: Check for nulls in critical columns
    validation_results['null_songs'] = int(df['song'].isna().sum())
    validation_results['null_artists'] = int(df['artist'].isna().sum())
    
    # Check 4: Date range
    validation_results['start_date'] = df['parsed_date'].min().strftime('%Y-%m-%d')
    validation_results['end_date'] = df['parsed_date'].max().strftime('%Y-%m-%d')
    validation_results['total_records'] = len(df)
    
    return validation_results

if __name__ == "__main__":
    # Test script execution
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_path = os.path.join(project_root, "data", "spotify_south_korea_playlist.csv")
    
    print(f"Testing loader with data from {data_path}...")
    try:
        cleaned_df = load_clean_data(data_path)
        metrics = validate_data(cleaned_df)
        print("\nValidation Metrics:")
        for k, v in metrics.items():
            if k == 'days_without_50_details':
                continue
            print(f"  {k}: {v}")
        if metrics['days_without_50_entries'] > 0:
            print("Days without 50 entries details:", metrics['days_without_50_details'])
    except Exception as e:
        print(f"Error in data processing: {e}")
