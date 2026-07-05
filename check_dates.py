import csv
from datetime import datetime, timedelta

def check_dates(file_path):
    dates = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dates.add(row['date'])
            
    # Parse dates
    parsed_dates = []
    for d in dates:
        try:
            parsed_dates.append(datetime.strptime(d, '%d-%m-%Y'))
        except Exception as e:
            print(f"Error parsing date {d}: {e}")
            
    parsed_dates.sort()
    print(f"Total unique dates: {len(parsed_dates)}")
    print(f"Start date: {parsed_dates[0].strftime('%Y-%m-%d')}")
    print(f"End date: {parsed_dates[-1].strftime('%Y-%m-%d')}")
    
    # Check for missing days
    missing_days = []
    curr = parsed_dates[0]
    while curr <= parsed_dates[-1]:
        if curr not in parsed_dates:
            missing_days.append(curr)
        curr += timedelta(days=1)
        
    print(f"Missing days: {len(missing_days)}")
    if missing_days:
        print("First 10 missing days:")
        for m in missing_days[:10]:
            print(f"  {m.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    check_dates("spotify_south_korea_playlist.csv")
