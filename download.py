import requests, os, time, argparse

# Function to download a file from a URL
def download_file(url, save_path):
    print(f"Downloading {url}...")
    delay = 15

    for _ in range(10): 
        try:
            # Send a GET request to the URL
            response = session.get(url, stream=True)

            # Cancel and log if we get a 5xx status code (server error)
            if response.status_code in [500, 502, 503, 504]:
                print(f"Got status code {response.status_code} - Skipping and logging error...")
                with open('failed.txt', 'a') as file:
                    file.write(f"Got {response.status_code}: {url}\n")
                return False
            else:
                # Save the file to disk
                with open(save_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                return True

        # Retry if we get a connection error (utilising exponential backoff)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url} - Will retry in {delay} seconds...")
            time.sleep(delay)
            delay *= 2
    
    # Log the error if we fail to download the file
    print(f"Maximum recursion reached - Skipping and logging error...")
    with open('failed.txt', 'a') as file:
        file.write(f"Maximum recursion reached: {url}\n")
    return False

# Create the argument parser
parser = argparse.ArgumentParser(description='download files from web.archive.org. example use: python download.py https://example.com txt html')

# Add the positional argument for the URL
parser.add_argument('url', metavar='url', type=str, help='the URL to download files from')

# Add the positional argument for file extensions
parser.add_argument('ext', metavar='ext', type=str, nargs='*', default=[], help='[optional] file extensions to filter by (all files if left empty)')

# Parse the command-line arguments
args = parser.parse_args()

print("\n==========================================\nWelcome to the Wayback Machine Downloader!\n==========================================\n")

# Get user input for the URL to download, as well as file extentions to filter by

api_url = f'http://web.archive.org/cdx/search/cdx?url={args.url}*&output=json'

if args.ext:
    print(f"You are about to download files from '{args.url}' with the following extentions: {', '.join(args.ext)}\n")
else:
    args.ext = ['ALL_OF_THE_FILES_GET_EM_ALL']
    print(f"Downloading all files from '{args.url}'.\n")

try:
    input("Press Enter to begin downloading, or press Ctrl+C to cancel. ")
except KeyboardInterrupt:
    print("\nDownload cancelled. Exiting...\n")
    exit()

print("\nSetting up...")

download_dir = 'files'
logfile = 'wayback-downloader.log'
try:
    # Create a directory to save the downloaded files
    os.makedirs(download_dir, exist_ok=True)
except:
    print(f"Error creating the '{download_dir}' directory. Please ensure you have the correct permissions and try again.")
    exit()

print("Fetching data from the Wayback Machine API...")

try:
    # Fetch the JSON data from the Wayback Machine API
    response = requests.get(api_url)
    data = response.json()
except:
    print("Error fetching data from the Wayback Machine API. Please check the URL and try again.")
    exit()

print(f"Data fetched successfully! (found {len(data)} files)\n")

downloaded_files = []

try:
    # Ignore files that have already been downloaded
    for filename in os.listdir(download_dir):
            downloaded_files.append(filename)
    if len(downloaded_files) > 0:
        print(f"Found {len(downloaded_files)} file(s) already downloaded, marking as complete...")
except:
    print(f"Error reading the '{download_dir}' directory. Please ensure you have the correct permissions and try again.")
    exit()

# Create a session to reuse the connection
print("Starting session...")
try:
    session = requests.Session()
except:
    print("Error starting session. Please check your internet connection and try again.")
    exit()

print("Beginning download...\n")

files_processed = 0
files_downloaded = 0
files_failed = 0

# Parse the JSON data and download each file
for entry in data[1:]:  # Skip the first entry as it contains column headers

    files_processed += 1

    try:

        timestamp = entry[1]
        original_url = entry[2]
        status = entry[4]

        # Extract the filename from the original URL
        filename = os.path.basename(original_url)
            
        # Download the file
        if (filename.endswith(tuple(args.ext)) or args.ext[0] == 'ALL_OF_THE_FILES_GET_EM_ALL') and (status == '200' or status == '-') and filename not in downloaded_files:

            # Construct the Wayback Machine URL
            archive_url = f"https://web.archive.org/web/{timestamp}/{original_url}"

            # Create the full path for saving the file
            save_path = os.path.join(download_dir, filename)

            # Run the downloading function
            if download_file(archive_url, save_path):
                files_downloaded += 1
            else:
                files_failed += 1

            # Add the filename to the list of downloaded files
            downloaded_files.append(original_url.split('/')[-1])

    except Exception as e:
        print(f"Could not download {original_url}. Skipping and logging error...")
        files_failed += 1
        with open('errors.log', 'a') as file:
            file.write(f"Error downloading {original_url}: {e}\n")

if (files_downloaded + files_failed) > 0:
    print(f"\nDownload complete! ({files_processed} processed, {files_downloaded} downloaded, {files_failed} failed - {round(files_downloaded / (files_downloaded + files_failed) * 100)}% success rate)\n")
else:
    print("Complete - No files were found to download. Either you already have them all, or all of the files processed were duplicates/redirects.\n")

