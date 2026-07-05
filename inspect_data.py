import csv
from datetime import datetime

def inspect_csv(file_path):
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            
    print(f"Total rows: {len(rows)}")
    if len(rows) == 0:
        return
        
    print("\nSample row:")
    for k, v in rows[0].items():
        print(f"  {k}: {v}")
        
    # Analyze dates
    dates = []
    positions = []
    artists = set()
    songs = set()
    album_types = set()
    is_explicit_vals = set()
    
    for r in rows:
        dates.append(r['date'])
        positions.append(int(r['position']))
        artists.add(r['artist'])
        songs.add((r['song'], r['artist']))
        album_types.add(r['album_type'])
        is_explicit_vals.add(r['is_explicit'])
        
    unique_dates = sorted(list(set(dates)), key=lambda d: datetime.strptime(d, '%d-%m-%Y') if '-' in d else d)
    print(f"\nUnique dates: {len(unique_dates)}")
    print(f"Date range: {unique_dates[0]} to {unique_dates[-1]}")
    print(f"Unique artists: {len(artists)}")
    print(f"Unique songs (song, artist pairs): {len(songs)}")
    print(f"Album types: {album_types}")
    print(f"Is explicit values: {is_explicit_vals}")
    print(f"Position range: {min(positions)} to {max(positions)}")
    
    # Check if there are exactly 50 entries per day
    date_counts = {}
    for d in dates:
        date_counts[d] = date_counts.get(d, 0) + 1
        
    not_50 = {d: c for d, c in date_counts.items() if c != 50}
    if not_50:
        print(f"\nWarning: {len(not_50)} dates do not have exactly 50 entries. Examples: {list(not_50.items())[:5]}")
    else:
        print("\nAll dates have exactly 50 entries.")

if __name__ == "__main__":
    inspect_csv("spotify_south_korea_playlist.csv")
