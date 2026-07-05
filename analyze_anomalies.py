import csv
from collections import Counter

def analyze_anomalies(file_path):
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            
    print(f"Total records read: {len(rows)}")
    
    # 1. Check for null or empty values
    fields = ['date', 'position', 'song', 'artist', 'popularity', 'duration_ms', 'album_type', 'total_tracks', 'is_explicit']
    nulls = {f: 0 for f in fields}
    for r in rows:
        for f in fields:
            if not r.get(f) or r[f].strip() == '':
                nulls[f] += 1
    print("\nNull/Empty counts:")
    for f, c in nulls.items():
        print(f"  {f}: {c}")
        
    # 2. Check for duplicate positions on the same date
    date_pos = Counter()
    for r in rows:
        date_pos[(r['date'], r['position'])] += 1
        
    dup_pos = {k: v for k, v in date_pos.items() if v > 1}
    print(f"\nDuplicate (date, position) pairs: {len(dup_pos)}")
    if dup_pos:
        print("Examples of duplicate (date, position) pairs:")
        for k, v in list(dup_pos.items())[:5]:
            print(f"  Date: {k[0]}, Position: {k[1]}, Count: {v}")
            # print the records
            matching = [r for r in rows if r['date'] == k[0] and r['position'] == k[1]]
            for m in matching:
                print(f"    - Song: {m['song']}, Artist: {m['artist']}, Popularity: {m['popularity']}")
                
    # 3. Check for same song appearing multiple times on same date (in different positions)
    date_song = Counter()
    for r in rows:
        # standardizing capitalization for this check
        song_key = (r['date'], r['song'].lower().strip(), r['artist'].lower().strip())
        date_song[song_key] += 1
        
    dup_songs = {k: v for k, v in date_song.items() if v > 1}
    print(f"\nDuplicate songs on the same date: {len(dup_songs)}")
    if dup_songs:
        print("Examples of songs appearing in multiple positions on the same date:")
        for k, v in list(dup_songs.items())[:5]:
            print(f"  Date: {k[0]}, Song: {k[1]}, Artist: {k[2]}, Count: {v}")
            matching = [r for r in rows if r['date'] == k[0] and r['song'].lower().strip() == k[1] and r['artist'].lower().strip() == k[2]]
            for m in matching:
                print(f"    - Position: {m['position']}, Popularity: {m['popularity']}")

if __name__ == "__main__":
    analyze_anomalies("spotify_south_korea_playlist.csv")
