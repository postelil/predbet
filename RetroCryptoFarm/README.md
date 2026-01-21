# Retro Crypto Farm Automation

This bot automates the MetaMask Rewards opt-in process for multiple accounts using Puppeteer and Proxies.

## Setup

1.  **Project Location**: The project is located at `C:\Users\user\.gemini\antigravity\scratch\RetroCryptoFarm`. You can move this folder to your Desktop if desired.
2.  **Install Dependencies**: (If not already done)
    ```powershell
    npm install
    ```
3.  **Download MetaMask Extension**:
    ```powershell
    node src/setup.js
    ```

## Configuration

1.  **Private Keys**: Open `input/private_keys.txt` and paste your private keys (one per line).
    ```text
    0x123abc...
    0x456def...
    ```
2.  **Proxies**: Open `input/proxies.txt` and paste your HTTP proxies.
    ```text
    ip:port:user:pass
    ```

## Running the Bot

Run the main script:
```powershell
npm start
```
Or directly:
```powershell
node src/bot.js
```

## What it does
1.  Launches a browser with the assigned proxy.
2.  Installs MetaMask and creates a temporary vault.
3.  Imports your Private Key.
4.  Navigates to `portfolio.metamask.io/rewards`.
5.  Attempts to connect and opt-in.
    *   **Note**: You may need to verify the first run visually to ensure the "Code Entry" flow works, as selectors change frequently.

## Troubleshooting
-   **Execution Policy Error**: Run `cmd /c npm install ...` or `Set-ExecutionPolicy RemoteSigned` in PowerShell as Admin.
-   **MetaMask not found**: Run `node src/setup.js` again.
