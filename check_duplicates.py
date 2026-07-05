import csv

def check_duplicates(file_path):
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            
    target_date = '01-03-2025'
    target_rows = [r for r in rows if r['date'] == target_date]
    print(f"Number of rows on {target_date}: {len(target_rows)}")
    
    # Check if they are exact duplicates
    serialized = [str(r) for r in target_rows]
    unique_serialized = set(serialized)
    print(f"Unique rows (as strings): {len(unique_serialized)}")
    
    # Let's print positions and songs for the first 10 and see if they repeat
    print("\nPositions and songs:")
    for r in target_rows[:15]:
        print(f"  Pos {r['position']}: {r['song']} - {r['artist']}")

if __name__ == "__main__":
    check_duplicates("spotify_south_korea_playlist.csv")
