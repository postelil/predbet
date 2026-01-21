const axios = require('axios');
const fs = require('fs-extra');
const AdmZip = require('adm-zip');
const path = require('path');

const METAMASK_RELEASE_URL = 'https://github.com/MetaMask/metamask-extension/releases/download/v11.16.2/metamask-chrome-11.16.2.zip'; // Using a recent stable version
const EXTENSION_DIR = path.join(__dirname, '../extensions/metamask');
const ZIP_PATH = path.join(__dirname, '../extensions/metamask.zip');

async function setup() {
    try {
        await fs.ensureDir(path.join(__dirname, '../extensions'));
        
        console.log('Downloading MetaMask extension...');
        const response = await axios({
            method: 'get',
            url: METAMASK_RELEASE_URL,
            responseType: 'arraybuffer'
        });
        
        await fs.writeFile(ZIP_PATH, response.data);
        console.log('Download complete.');
        
        console.log('Extracting MetaMask...');
        const zip = new AdmZip(ZIP_PATH);
        zip.extractAllTo(EXTENSION_DIR, true);
        
        console.log('Extension ready at:', EXTENSION_DIR);
        
        // Clean up zip
        await fs.remove(ZIP_PATH);
        
    } catch (error) {
        console.error('Setup failed:', error);
        process.exit(1);
    }
}

setup();
