# Introduction
This script synchronizes two Google Shared Drives completely - all folders, all files, all everything.
It will copy files from one Shared Drive into another, skipping over files that already exist in the destination drive.
At the end, a full CSV list will be giving relating the old file locations (filename, path and ID) to the new ones.

This script does not delete, move or edit files in the source drive. It only copies the files into the destination drive. 
This script was not tested for other situations (e.g. copying a folder into another folder). Use at your own risk.

# Installation
Install the necessary libraries:

`pip install -r requirements.txt`

You will need to have JSON credentials for a GCP Service Account. If you don't, here's a quick version on how to do it:

```
1 - Create a new GCP project or select an existing one
2 - Configure your OAUTH consent screen. On request scopes, add the following path:
        https://www.googleapis.com/auth/drive
3 - Create a Service Account, and note down the Service Account's email address.
4 - Create a JSON key for this Service Account. Save it in this program's folder as "creds.json".
5 - Add the Service Account's email as an editor/commenter/viewer in the Shared Drives you want to copy from/into
6 - All done!
```

# Usage
```
usage: syncGDriveFolders [-h] [--src SRC] [--dst DST] [--creds CREDS]

optional arguments:
  -h, --help     show this help message and exit
  --src SRC      The source folder where files will be copied from
  --dst DST      The destination folder where files will be copied to
  --creds CREDS  The JSON file containing a Service Account's credentials
```

By default, credentials will be loaded from "./creds.json"

SRC and DST parameters must be given as drive id's. these can be found on your shared drive URL.
e.g.: if the link to your shared drive is `https://drive.google.com/drive/u/0/folders/B181BE91BE81B`, then your drive's ID is `B181BE91BE81B`