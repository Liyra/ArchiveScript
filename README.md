# ArchiveScript
Script to download complete records from archives website that use Mnesys.

# Requirements
Python 3, with joblib and Pillow.

# Usage
python script.py -u <url> -n <name> -p <number_of_pages>

The url of the upperleft image is being passed as url (matching (http:\/\/.+)_(\d\d\d\d)_jpg_\/(\d)_(\d).jpg).

See --help for all the arguments.
