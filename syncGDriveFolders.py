from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
import argparse
import csv
import time


#Return format - a list of lists (each object is a row)
#Format - File Type, Old path, Old Id, New Path, New ID
#Global Variable - YOLO!
csvResults = []


def getExistingFileID(file, dstFiles):
    for dstFile in dstFiles:
        if dstFile["name"] == file["name"]:
            return dstFile["id"]

def getFileID(service, name, drive, folder):
    try:
        fileID = service.files().list(
            supportsAllDrives=True,
            corpora="drive",
            includeItemsFromAllDrives=True,
            driveId=drive,
            q="'{}' in parents and trashed = false and name='{}'".format(folder,name)
        ).execute()["files"][0]["id"]
    except:
        #Recursive wait - sometimes, files won't appear via API right after being created
        #Yes, if this fails, this will infinitely loop. YOLO!
        time.sleep(0.1)
        return getFileID(service, name, drive, folder)
    return fileID

def fileExists(file, dstFiles):
    for destFile in dstFiles:
        if destFile["name"] == file["name"]:
            return True
    return False

def getFileList(drive, folder, service):
    files = []
    page_counter = 0

    fileSvc = service.files()
    request = fileSvc.list(
        supportsAllDrives=True,
        corpora="drive",
        includeItemsFromAllDrives=True,
        driveId=drive,
        q="'{}' in parents and trashed = false".format(folder)
    )


    while request is not None:
        file_page = request.execute()
        page_counter += 1

        # Add files to result
        files.extend(file_page["files"])

        # request the next page of files
        request = fileSvc.list_next(request, file_page)

    return files

def recursiveCopy(srcDrive, srcFolder, dstDrive, dstFolder, service, tabCount=0):

    # get the files in each foldefr
    srcFiles = getFileList(srcDrive, srcFolder, service)
    dstFiles = getFileList(dstDrive, dstFolder, service)

    #Execute until no new files are found
    for file in srcFiles:

        fileName = file["name"]
        fileType = ""
        fileID   = file["id"]

        copied = "ALREADY EXISTS"
        if (tabCount == 0):
            header = ""
        else:
            header = tabCount * "*" + " "

        # If not a folder, just copy the file
        if file['mimeType'] != 'application/vnd.google-apps.folder':
            fileType = "file"
            #Don't copy file if it already exists in destination
            if not fileExists(file, dstFiles):
                copied = "COPIED"
                requestBody = {"parents": [dstFolder], "name":file["name"]}
                service.files().copy(fileId=file["id"],body=requestBody,supportsAllDrives=True).execute()
                newID = getFileID(service, fileName, dstDrive, dstFolder)
            else:
                newID = getExistingFileID(file, dstFiles)
            print(header, fileName, " - ", copied, sep='')

        # If a folder, create a new folder on the destination and recall function
        else:
            fileType = "FOLDER"
            #If folder already exists, just recurse the function:
            #If it doesn't, then create folder and then recurse:
            if not fileExists(file, dstFiles):
                copied = "COPIED"
                requestBody = {"parents": [dstFolder], 'name':file["name"], 'mimeType': 'application/vnd.google-apps.folder'}
                service.files().create(body=requestBody,supportsAllDrives=True).execute()
               #Get created folder's ID
                newID = getFileID(service, fileName, dstDrive, dstFolder)
            else:
                newID = getExistingFileID(file, dstFiles)

            print(header, fileType, " - ", fileName, " - ", copied, sep='')
            #Recurse function
            recursiveCopy(srcDrive, file["id"], dstDrive, newID, service, tabCount+1)

            

        #CSV Format - File Type, File Name, Old path, Old Id, New Path, New ID
        if (fileType == "FOLDER"):
            oldPath = "https://drive.google.com/drive/u/0/folders/" + fileID
            newPath = "https://drive.google.com/drive/u/0/folders/" + newID
        else:
            oldPath = "https://drive.google.com/file/d/" + fileID
            newPath = "https://drive.google.com/file/d/" + newID
        
        csvResults.append([fileType, fileName, oldPath, fileID, newPath, newID])

####################################################################################################################

#Parse arguments
parser = argparse.ArgumentParser("syncGDriveFolders")
parser.add_argument("--src", help="The source folder where files will be copied from", type=str)
parser.add_argument("--dst", help="The destination folder where files will be copied to", type=str)
parser.add_argument("--creds", help="The JSON file containing a Service Account's credentials", type=str, default="./creds.json")
args = parser.parse_args()
srcFolder = args.src
dstFolder = args.dst
credentials = args.creds

#General variables
scopes = "https://www.googleapis.com/auth/drive"

#Authenticate to Drive API
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials, scopes=scopes)
service = build('drive', 'v3', credentials=credentials)

#Copy stuff
csvResults = []
csvResults.append(["File Type", "File Name", "Old path", "Old Id", "New Path", "New ID"])
recursiveCopy(srcFolder, srcFolder, dstFolder, dstFolder, service)

#Write to CSV
print("\n=== Writing to CSV... ===")
with open('results.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerows(csvResults)
    print("=== All Done! ===")