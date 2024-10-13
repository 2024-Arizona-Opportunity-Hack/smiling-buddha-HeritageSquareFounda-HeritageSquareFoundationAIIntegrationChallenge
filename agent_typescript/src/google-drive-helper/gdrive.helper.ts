import * as fs from 'fs';
import * as path from 'path';
import * as axios from 'axios';
import * as googleapis from 'googleapis';
import * as util from 'util';
import * as rimraf from 'rimraf';

// Path to the service account JSON file
const SERVICE_ACCOUNT_FILE = 'credentials.json';


// const credential = JSON.parse(
//     Buffer.from(process.env.GOOGLE_CREDENTIALS!, "base64").toString()
//   );

// Scopes for accessing Google Drive
const SCOPES = ['https://www.googleapis.com/auth/drive'];

// Authenticate using the service account credentials
const auth = new googleapis.google.auth.GoogleAuth({
    keyFile: SERVICE_ACCOUNT_FILE,
    scopes: SCOPES
});

// Build the Google Drive API service using the service account credentials
const drive = googleapis.google.drive({ version: 'v3', auth });

const MAX_RETRIES = 5;


const scriptDirectory = __dirname;
const downloadFolder = path.join(scriptDirectory, 'fileDownload');

export async function downloadFileContent(fileId: string, fileName: string) {
    try {
        deleteFolderIfExists();
        fs.mkdirSync(downloadFolder);
        const downloadUrl = `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`;
        const headers = {
            Authorization: `Bearer ${await auth.getAccessToken()}`
        };
        const response = await axios.default.get(downloadUrl, { headers, responseType: 'arraybuffer' });
        
        if (response.status === 200) {
            const filePath = path.join(downloadFolder, fileName);
            fs.writeFileSync(filePath, response.data);
            //console.log(`File '${fileName}' downloaded successfully to '${downloadFolder}'.`);
        } else {
            //console.log(`Failed to download file '${fileName}'. Status code: ${response.status}`);
        }
    } catch (error) {
        console.log(`An error occurred while downloading the file: ${error}`);
    }
}

async function searchFolderByName(folderName: string): Promise<string | null> {
    try {
        const query = `name='${folderName}' and mimeType='application/vnd.google-apps.folder'`;
        const response = await drive.files.list({ q: query, fields: "files(id, name)" });
        const folders = response.data.files || [];
        
        if (folders.length === 0) {
            //console.log(`No folder found with the name '${folderName}'`);
            return null;
        }
        
        return folders[0].id!;
    } catch (error) {
        //console.log(`An error occurred while searching for the folder: ${error}`);
        return null;
    }
}

async function listFilesInFolder(folderId: string): Promise<{ [key: string]: any }> {
    try {
        let fileDict: { [key: string]: any } = {};
        const query = `'${folderId}' in parents and trashed=false`;
        const response = await drive.files.list({ q: query, fields: "nextPageToken, files(id, name, mimeType, webViewLink)" });
        const items = response.data.files || [];

        for (let item of items) {
            if (item.mimeType !== 'application/vnd.google-apps.folder') {
                //console.log(`Found file: ${item.name} (ID: ${item.id})`);
                fileDict[item.id!] = {
                    file_id: item.id,
                    file_name: item.name,
                    link: item.webViewLink || 'No link available',
                    file_type: item.mimeType
                };
            } else {
                //console.log(`Entering folder: ${item.name} (ID: ${item.id})`);
                const subfolderFiles = await listFilesInFolder(item.id!);
                Object.assign(fileDict, subfolderFiles);
            }
        }

        return fileDict;
    } catch (error) {
        //console.log(`An error occurred while listing files in folder: ${error}`);
        return {};
    }
}

function deleteFolderIfExists(folderPath: string = downloadFolder) {
    if (fs.existsSync(folderPath)) {
        //console.log(`Deleting existing folder: ${folderPath}`);
        rimraf.sync(folderPath);
    }
}

function saveDictToJson(fileDict: { [key: string]: any }, jsonFilePath: string) {
    try {
        fs.writeFileSync(jsonFilePath, JSON.stringify(fileDict, null, 4));
        //console.log(`File details saved to ${jsonFilePath}`);
    } catch (error) {
        //console.log(`An error occurred while saving to JSON: ${error}`);
    }
}

function deleteFileIfExists(filePath: string) {
    if (fs.existsSync(filePath)) {
        //console.log(`Deleting existing file: ${filePath}`);
        fs.unlinkSync(filePath);
    }
}

export async function getfiles() {
    const scriptDirectory = __dirname;
    const downloadFolder = path.join(scriptDirectory, 'fileDownload');
    const jsonFilePath = path.join(scriptDirectory, 'file_details.json');

    deleteFolderIfExists(downloadFolder);
    deleteFileIfExists(jsonFilePath);

    fs.mkdirSync(downloadFolder);
    //console.log(`Created folder: ${downloadFolder}`);

    const folderName = "ohack";
    const folderId = await searchFolderByName(folderName);
    let fileDict;
    if (folderId) {
        //console.log(`Listing all files in the 'ohack' folder (ID: ${folderId})`);
        fileDict = await listFilesInFolder(folderId);
        
        saveDictToJson(fileDict, jsonFilePath);

        // //console.log("\nFile details dictionary:");
        // for (const [fileId, details] of Object.entries(fileDict)) {
        //     //console.log(`${fileId}: ${JSON.stringify(details)}`);
        // }

        // for (const [fileId, details] of Object.entries(fileDict)) {
        //     await downloadFileContent(details.file_id, details.file_name, downloadFolder);
        // }
    }

    return fileDict
}

// getfiles().catch(console.error);