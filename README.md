# wayback-downloader
bulk download files from the Wayback Machine.

_useful for images and music files._

### To run:
- download `downloader.py` from this repository
- make sure you have a modern version of python installed
- download the required libraries: `python -m pip install requests argparse`
- run the thing: `python downloader.py`

### Usage:

`python downloader.py [website] [optional: ext]` <br><br>

[website]: _the website you want to download the content from. can be a root or sub directory._

examples: `python downloader.py https/example.com` _or_ `python downloader.py https/example.com/assets/images/`  <br><br>

[ext]: _file extensions to filter by, seperated by spaces. if left blank, the script will simply download every file it sees._

example: `python downloader.py https/example.com/assets/images/ jpeg jpg png`
