import json
import os
import shutil

import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Path to the service account JSON file
SERVICE_ACCOUNT_FILE = './ohack.json'

# Scopes for accessing Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

# Authenticate using the service account credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Google Drive API service using the service account credentials
service = build('drive', 'v3', credentials=credentials)

Max_retries = 5

# def retrieve_file_by_name(file_name):
#     try:
#         query = f"name='{file_name}'"
#         response = service.files().list(q=query, fields="files(id, name, appProperties, mimeType, parents)").execute()
#         files = response.get('files', [])
#         if not files:
#             print(f"No file found with the name '{file_name}'")
#             return None
#         for file in files:
#             parent_folders = file.get('parents', ['Root'])
#             print(f"File ID: {file['id']}, File Name: {file['name']}, MIME Type: {file['mimeType']}, Parent Folder: {parent_folders}")
        
#         return files[0]  # Return the first matched file
    
#     except HttpError as error:
#         print(f"An error occurred: {error}")
#         return None

# def add_tags_to_file(file_id, tags):
#     try:
#         retries = 0
#         while retries < Max_retries:
#             try:
#                 # Convert tags list to a comma-separated string
#                 tags_string = ','.join(tags)
                
#                 # Update the file's appProperties with the new tags
#                 service.files().update(
#                     fileId=file_id,
#                     body={"appProperties": {"tags": tags_string}}
#                 ).execute()
                
#                 print(f"Tags '{tags_string}' added to file ID {file_id}.")
#                 break
#             except HttpError as error:
#                 retries += 1
#                 print(f"Retrying... ({retries}/{Max_retries}) - {error}")
                
#     except Exception as e:
#         print(f"An error occurred while adding tags: {e}")

# def view_metadata(file_id):
#     try:
#         print(f"Fetching metadata for file ID: {file_id}")
#         # Retrieve file metadata
#         file_metadata = service.files().get(fileId=file_id, fields="id, name, mimeType, size, appProperties").execute()
        
#         # Display metadata
#         print(f"File ID: {file_metadata['id']}")
#         print(f"File Name: {file_metadata['name']}")
#         print(f"MIME Type: {file_metadata['mimeType']}")
#         print(f"File Size: {file_metadata.get('size', 'Unknown')}")
#         print(f"Tags: {file_metadata.get('appProperties', {}).get('tags', 'No tags found')}")
        
#         return file_metadata

#     except HttpError as error:
#         print(f"An error occurred while retrieving metadata: {error}")
#         return None

def download_file_content(file_id, file_name, download_folder):
    try:
        # Download the file content using the alt=media query parameter
        download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
        response = requests.get(download_url, headers={"Authorization": f"Bearer {credentials.token}"})
        
        if response.status_code == 200:
            # Save the file to the specified local download folder
            file_path = os.path.join(download_folder, file_name)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"File '{file_name}' downloaded successfully to '{download_folder}'.")
        else:
            print(f"Failed to download file '{file_name}'. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while downloading the file: {e}")
def search_folder_by_name(folder_name):
    """Search for a folder by its name."""
    try:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        response = service.files().list(q=query, fields="files(id, name)").execute()
        folders = response.get('files', [])
        
        if not folders:
            print(f"No folder found with the name '{folder_name}'")
            return None
        
        # Return the folder ID for the ohack folder (assuming only one "ohack" folder)
        return folders[0]['id']
    
    except HttpError as error:
        print(f"An error occurred while searching for the folder: {error}")
        return None


def list_files_in_folder(folder_id):
    try:
        file_dict = {}
        query = f"'{folder_id}' in parents and trashed=false"
        response = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType,webViewLink)").execute()
        items = response.get('files', [])
        
        for item in items:
            # If it's a file, add its details to the dictionary
            if item['mimeType'] != 'application/vnd.google-apps.folder':
                print(f"Found file: {item['name']} (ID: {item['id']})")
                file_dict[item['id']] = {
                    "file_id": item['id'],
                    "file_name": item['name'],
                    "link": item.get('webViewLink', 'No link available'),
                    "file_type": item['mimeType']
                }
            else:
                print(f"Entering folder: {item['name']} (ID: {item['id']})")
                # Recursively list files in subfolder and update the main dictionary
                subfolder_files = list_files_in_folder(item['id'])
                file_dict.update(subfolder_files)
                
        return file_dict
    
    except HttpError as error:
        print(f"An error occurred while listing files in folder: {error}")
        return []

def delete_folder_if_exists(folder_path):
    if os.path.exists(folder_path):
        print(f"Deleting existing folder: {folder_path}")
        shutil.rmtree(folder_path)

def save_dict_to_json(file_dict, json_file_path):
    try:
        with open(json_file_path, 'w') as json_file:
            json.dump(file_dict, json_file, indent=4)
        print(f"File details saved to {json_file_path}")
    except Exception as e:
        print(f"An error occurred while saving to JSON: {e}")

def delete_file_if_exists(file_path):
    if os.path.exists(file_path):
        print(f"Deleting existing file: {file_path}")
        os.remove(file_path)


def main():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    download_folder = os.path.join(script_directory, 'fileDownload')  # Folder where files will be saved
    json_file_path = os.path.join(script_directory, 'file_details.json')
    # Step 2: Delete the 'fileDownload' folder if it exists
    delete_folder_if_exists(download_folder)
    delete_file_if_exists(json_file_path)

    # Step 3: Create the 'fileDownload' folder
    os.makedirs(download_folder)
    print(f"Created folder: {download_folder}")

    # Step 4: Search for the "ohack" folder by name
    folder_name = "ohack"  # Fixed folder name
    folder_id = search_folder_by_name(folder_name)
    
    if folder_id:
        # Step 5: List all file details in the "ohack" folder (and subfolders)
        print(f"Listing all files in the 'ohack' folder (ID: {folder_id})")
        file_dict = list_files_in_folder(folder_id)

        json_file_path = os.path.join(script_directory, 'file_details.json')
        save_dict_to_json(file_dict, json_file_path)

        # Print the dictionary of file details
        print("\nFile details dictionary:")
        for file_id, details in file_dict.items():
            print(f"{file_id}: {details}")
        
        # Step 6: Download each file by its ID
        for file_id, details in file_dict.items():
            download_file_content(details['file_id'], details['file_name'], download_folder)

if __name__ == "__main__":
    main()
