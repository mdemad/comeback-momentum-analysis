import urllib.request
import re
import sys

def download_file_from_google_drive(file_id, destination):
    URL = "https://docs.google.com/uc?export=download"
    
    # Request the download page
    req = urllib.request.Request(f"{URL}&id={file_id}", headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read()
            
            # Check if there is a confirmation token
            # Typically looks like: confirm=XXXX or download_warning_...
            # Let's inspect the html response for confirm token
            html = content.decode('utf-8', errors='ignore')
            confirm_token = None
            
            # Search for confirm query param in the html
            # E.g. href="/uc?export=download&amp;confirm=t_g8&amp;id=..."
            match = re.search(r'confirm=([a-zA-Z0-9_]+)', html)
            if match:
                confirm_token = match.group(1)
                print(f"Found confirmation token: {confirm_token}")
                # Request again with the token
                confirm_url = f"{URL}&confirm={confirm_token}&id={file_id}"
                confirm_req = urllib.request.Request(confirm_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(confirm_req) as confirm_response:
                    content = confirm_response.read()
            
            with open(destination, 'wb') as f:
                f.write(content)
            print(f"File downloaded to {destination}. Size: {len(content)} bytes")
            
            # Let's print the first few lines of the file to verify
            try:
                print("First line preview:")
                preview = content[:200].decode('utf-8', errors='ignore')
                print(preview)
            except Exception as e:
                print("Could not decode preview:", e)
                
    except Exception as e:
        print(f"Error downloading file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    file_id = "1OMVl8OHgM09zLo-IO3A0R__ZSTJuglUS"
    destination = "spotify_south_korea_playlist.csv"
    download_file_from_google_drive(file_id, destination)
