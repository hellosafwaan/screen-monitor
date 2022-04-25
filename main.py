import os, os.path,shutil
from datetime import date

from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload 
from httplib2 import Http
from httplib2.error import ServerNotFoundError
from oauth2client import file, client, tools
import pyscreenshot

# Obtaining application credentials & Authenticating
SCOPES = 'https://www.googleapis.com/auth/drive.readonly.metadata'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)

#  Creating Service 
DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))

def getFileDetails(fileName, mimeType, parentFileId = None):
    if parentFileId == None :
        fileList = DRIVE.files().list(q = "name = '{}' and mimeType = '{}'".format(fileName, mimeType)).execute().get('files')
    else:
        fileList = DRIVE.files().list(q = "parents = '{}' and name = '{}' and mimeType = '{}'".format(parentFileId, fileName, mimeType)).execute().get('files')
    if len(fileList) == 0 :
        print("No Files Found, fileDetails()")
    elif len(fileList) == 1:
        fileDetails = fileList[0]
        return fileDetails
    else:
        print("More Than One File Found, fileDetails()")