const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs-extra');
const path = require('path');
const chalk = require('chalk');

puppeteer.use(StealthPlugin());

const EXTENSION_PATH = path.join(__dirname, '../extensions/metamask');
const PRIVATE_KEYS_PATH = path.join(__dirname, '../input/private_keys.txt');
const PROXIES_PATH = path.join(__dirname, '../input/proxies.txt');
const PASSWORD = 'Password123!'; // Dummy password for the vault

const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const randomSleep = (min, max) => sleep(Math.floor(Math.random() * (max - min + 1) + min));

async function getProxies() {
    if (!fs.existsSync(PROXIES_PATH)) return [];
    const content = await fs.readFile(PROXIES_PATH, 'utf8');
    return content.split('\n').filter(l => l.trim() && !l.startsWith('#')).map(l => l.trim());
}

async function getKeys() {
    if (!fs.existsSync(PRIVATE_KEYS_PATH)) return [];
    const content = await fs.readFile(PRIVATE_KEYS_PATH, 'utf8');
    return content.split('\n').filter(l => l.trim() && !l.startsWith('#')).map(l => l.trim());
}

async function runProfile(privateKey, proxyStr, index) {
    console.log(chalk.blue(`[Account ${index}] Starting...`));

    // Validate key
    if (!privateKey.startsWith('0x')) {
        console.log(chalk.yellow(`[Account ${index}] Adding 0x prefix to key`));
        privateKey = '0x' + privateKey;
    }

    const args = [
        `--disable-extensions-except=${EXTENSION_PATH}`,
        `--load-extension=${EXTENSION_PATH}`,
        '--no-sandbox',
        '--disable-setuid-sandbox'
    ];

    if (proxyStr) {
        const parts = proxyStr.split(':');
        // Basic check for ip:port
        if (parts.length >= 2) {
            args.push(`--proxy-server=${parts[0]}:${parts[1]}`);
        }
    }

    const browser = await puppeteer.launch({
        headless: false,
        args: args,
        defaultViewport: null
    });

    try {
        const page = await browser.newPage();

        // Proxy Auth
        if (proxyStr) {
            const parts = proxyStr.split(':');
            if (parts.length === 4) {
                await page.authenticate({ username: parts[2], password: parts[3] });
            }
        }

        // 1. Initial Setup to create Vault
        await setupMetaMaskVault(browser);

        // 2. Import the actual Private Key
        await importPrivateKey(browser, privateKey);

        // 3. Connect to Portfolio & Enter Codes
        await performRewardsActions(page, index);

    } catch (e) {
        console.error(chalk.red(`[Account ${index}] Error: ${e.message}`));
        await page.screenshot({ path: `error_${index}.png` });
    } finally {
        await browser.close();
    }
}

async function getMetaMaskPage(browser) {
    const targets = await browser.targets();
    const extensionTarget = targets.find(t => t.type() === 'page' && t.url().includes('home.html'));
    if (extensionTarget) return await extensionTarget.page();

    // Fallback
    const pages = await browser.pages();
    for (const p of pages) {
        if (p.url().includes('home.html')) return p;
    }
    return null;
}

async function setupMetaMaskVault(browser) {
    console.log('Setting up MetaMask Vault...');
    await sleep(3000); // Wait for extension to load

    let extPage = await getMetaMaskPage(browser);
    if (!extPage) {
        // Manually open if not popped up
        // Need extension ID. It varies for unpacked??
        // Usually with --load-extension it's consistent if path is hash. 
        // But for now let's hope it opened or we find it.
        // Try getting it from targets again after delay
        await sleep(2000);
        extPage = await getMetaMaskPage(browser);
        if (!extPage) throw new Error("MetaMask page not found");
    }

    await extPage.bringToFront();
    await extPage.reload(); // Refresh to ensure clean state
    await sleep(2000);

    // Click Checkbox
    const checkbox = await extPage.waitForSelector('input[type="checkbox"]', { timeout: 10000 });
    if (checkbox) await checkbox.click();

    // Click "Create a new wallet"
    // Using evaluate to find text is safer than fixed selectors
    await clickButtonByText(extPage, 'Create a new wallet');

    // "I agree" (Metrics)
    await sleep(1000);
    await clickButtonByText(extPage, 'I agree');

    // Password
    await extPage.waitForSelector('input[type="password"]');
    const passwords = await extPage.$$('input[type="password"]');
    for (const p of passwords) await p.type(PASSWORD);

    const terms = await extPage.$$('input[type="checkbox"]');
    if (terms.length > 0) await terms[0].click(); // "I understand..."

    await clickButtonByText(extPage, 'Create a new wallet');

    // Secure wallet? -> "Remind me later"
    await sleep(2000);
    await clickButtonByText(extPage, 'Remind me later');

    // Checkbox "I understand"
    const skipCheckbox = await extPage.$('input[type="checkbox"]');
    if (skipCheckbox) await skipCheckbox.click();

    await clickButtonByText(extPage, 'Skip');

    // "Great job" -> "Got it"
    await clickButtonByText(extPage, 'Got it');
    await clickButtonByText(extPage, 'Next');
    await clickButtonByText(extPage, 'Done');

    // Close "What's new"
    const closeBtn = await extPage.$('button[data-testid="popover-close"]');
    if (closeBtn) await closeBtn.click();

    console.log('Vault created.');
}

async function importPrivateKey(browser, privateKey) {
    console.log('Importing Private Key...');
    const extPage = await getMetaMaskPage(browser);
    if (!extPage) throw new Error("Lost MetaMask page");

    // Open Account Menu
    const accountMenu = await extPage.waitForSelector('button[data-testid="account-menu-icon"]');
    await accountMenu.click();

    // Click "Add account or hardware wallet"
    await clickButtonByText(extPage, 'Add account or hardware wallet');

    // Click "Import account"
    await clickButtonByText(extPage, 'Import account');

    // Enter key
    const input = await extPage.waitForSelector('input#private-key-box');
    await input.type(privateKey);

    // Click Import
    await clickButtonByText(extPage, 'Import');
    await sleep(1000);
    console.log('Account imported.');
}

async function performRewardsActions(page, index) {
    console.log(chalk.yellow(`[Account ${index}] Go to Rewards...`));

    // Direct link to activate referral
    await page.goto('https://portfolio.metamask.io/explore', { waitUntil: 'domcontentloaded' });
    await sleep(5000);

    // Connect Wallet Button
    // This part is tricky. It triggers a popup.
    // Puppeteer handles popups if we listen for 'targetcreated'.

    try {
        const connectBtn = await page.$x("//button[contains(., 'Connect')]");
        if (connectBtn.length > 0) {
            connectBtn[0].click();
            console.log('Clicked Connect...');
            // Handle popup...
        }
    } catch (e) {
        console.log('Already connected or no button?');
    }

    // Checking for "Rewards" tab
    await page.goto('https://portfolio.metamask.io/rewards', { waitUntil: 'networkidle2' });
    await sleep(3000);

    // Attempt to find Opt In / Input
    console.log('Looking for inputs...');

    // Placeholder for User: MANUAL INTERVENTION or ROBUST SELECTORS needed here.
    // Because I cannot see the page, I cannot write reliable selectors for the Code Entry.
    // I will log instructions.

    console.log(chalk.magenta('!!! PLEASE MANUALLY CHECK IF CODE ENTRY IS NEEDED OR IF URL AUTOMATICALLY APPLIED IT !!!'));
    console.log('Taking screenshot of Rewards page...');
    await page.screenshot({ path: `rewards_${index}.png` });
}

async function clickButtonByText(page, text) {
    const buttons = await page.$$('button');
    for (const btn of buttons) {
        const t = await page.evaluate(el => el.textContent, btn);
        if (t && t.toLowerCase().includes(text.toLowerCase())) {
            await btn.click();
            return true;
        }
    }
    return false;
}

(async () => {
    const keys = await getKeys();
    const proxies = await getProxies();

    if (keys.length === 0) {
        console.log(chalk.red('No keys found in input/private_keys.txt. Please add them!'));
        process.exit(0);
    }

    console.log(chalk.green(`Found ${keys.length} accounts. Starting farm...`));

    for (let i = 0; i < keys.length; i++) {
        await runProfile(keys[i], proxies[i % proxies.length], i);
        // Random delay
        const delay = Math.floor(Math.random() * (15000 - 5000 + 1) + 5000);
        console.log(`Waiting ${delay}ms...`);
        await sleep(delay);
    }
})();
