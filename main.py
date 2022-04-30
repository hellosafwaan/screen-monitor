import os, os.path
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

def get_file_details(file_name, mime_type, parent_file_id = None):
    if parent_file_id == None :
        file_list = DRIVE.files().list(q = "name = '{}' and mimeType = '{}'".format(file_name, mime_type)).execute().get('files')
    else:
        file_list = DRIVE.files().list(q = "parents = '{}' and name = '{}' and mimeType = '{}'".format(parent_file_id, file_name, mime_type)).execute().get('files')
    if len(file_list) == 0 :
        print("No Files Found, fileDetails()")
    elif len(file_list) == 1:
        file_details = file_list[0]
        return file_details
    else:
        print("More Than One File Found, fileDetails()")

def create_folder(new_folder_name, parent_folder_id = None, should_return_details = False):
    if parent_folder_id == None:
        folder_metadata = {
        'name' : new_folder_name,
        'mimeType' : 'application/vnd.google-apps.folder'
        }
    else:
        folder_metadata = {
            'name' : new_folder_name,
            'parents' : [parent_folder_id],
            'mimeType' : 'application/vnd.google-apps.folder'
            }
    DRIVE.files().create(body = folder_metadata).execute()
    if should_return_details:
        return get_file_details(new_folder_name,'application/vnd.google-apps.folder', parentFileId = parent_folder_id)

def check_folder_exits( sub_folder_name, parent_folder_id = None):
    if parent_folder_id == None:
        sub_folder = DRIVE.files().list(q = "name = '{}' and  mimeType = 'application/vnd.google-apps.folder'".format(sub_folder_name)).execute().get('files')
    else:
        sub_folder = DRIVE.files().list(q = "parents = '{}' and name = '{}' and  mimeType = 'application/vnd.google-apps.folder'".format(parent_folder_id, sub_folder_name)).execute().get('files')    
    if len(sub_folder) == 1:
        return True
    elif len(sub_folder) > 1:
        pass
    else:
        return False

def upload_file(to_folder_id, file_name, mime_type):
    file_metadata = {
        'name' : file_name,
        'parents' : [to_folder_id],
        'mimeType' : mime_type}
    media = MediaFileUpload(file_name)
    try:
        DRIVE.files().create(
            body = file_metadata,
            media_body = media
        ).execute()
        print(file_name)
    except TimeoutError:
        print("TimeOut Error")

def find_img_num(img_folder_id):
    files = DRIVE.files().list(q = "parents = '{}'".format(img_folder_id), pageSize = 1).execute().get('files')
    if len(files) == 0:
        return 0
    else:
        return int(files[0]['name'][5:][:-4])

def take_image(img_num):
    ss = pyscreenshot.grab()
    ss.save("photo{}.png".format(img_num))
    return "photo{}.png".format(img_num)

def client_test_and_details(application_folder_id):
    client_name = os.getlogin() 
    client_status = check_folder_exits(application_folder_id, client_name)
    if not client_status:
        return create_folder(application_folder_id, client_name, should_return_details = True)  
    else :
        return get_file_details(client_name, 'application/vnd.google-apps.folder',parent_file_id = application_folder_id)

def current_day_folder(client_folder_id, current_date = str(date.today())):
    if check_folder_exits(client_folder_id, current_date):
        return get_file_details(current_date, 'application/vnd.google-apps.folder',parent_file_id = client_folder_id)
    else:
        return create_folder(client_folder_id, current_date, should_return_details = True)

def check_trashed(file_id):
        return DRIVE.files().get(fileId = file_id, fields='parents,name,trashed').execute().get('trashed')
