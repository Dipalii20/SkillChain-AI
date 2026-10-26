# SkillChain AI — Django mini project

SkillChain AI is an educational prototype combining resume skill extraction, internship matching, and certificate fingerprint verification.

## Important scope note

The default application runs immediately in **local demo mode**. It computes SHA-256 fingerprints and records a demo reference in SQLite. This is **not a real blockchain**. The `contracts/CertificateRegistry.sol` file is a Solidity smart-contract starter for the optional Ethereum integration phase. Do not describe the default mode as decentralized or on-chain.

AI scope: the current MVP uses a transparent keyword-based skill extractor and skill-overlap ranking. This is a practical baseline, not a trained deep-learning system. You can later replace it with a trained NLP model.

## Requirements

- Python 3.10+
- Internet connection for Bootstrap CDN / Google Fonts (optional styling)
- Optional: Remix IDE, MetaMask and an Ethereum-compatible local/test network for real smart-contract deployment

## 1. Extract and open the project

Extract `SkillChain_AI_Project.zip`, then open the extracted `skillchain_ai` folder in VS Code.

## 2. Create a virtual environment

### Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt:
```bat
.venv\Scripts\activate.bat
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Create database tables and demo data

```bash
python manage.py migrate
python manage.py seed_internships
python manage.py createsuperuser
```

The superuser is for Django's admin site. You can also create a normal student account through the website.

## 4. Start the development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/

### Demo flow
1. Register a user.
2. Open **Profile** and add skills such as `Python, Django, SQL, HTML, CSS, Git`.
3. Open **Dashboard** to see matching internship cards.
4. Open **Analyze resume** and upload a PDF, DOCX, or TXT file (max 5 MB). Review detected skills.
5. Open **My certificates**, register a certificate. For a meaningful file comparison, upload a certificate file.
6. Click **Verify a file** and upload the exact same file: it should match. Change the file and it should mismatch.
7. Open **Verify credential** and search using the demo record ID.

## 5. Django admin

Go to http://127.0.0.1:8000/admin/ and sign in using the superuser created earlier. You can add/edit internship listings.

## 6. Optional MySQL setup

SQLite is enabled by default so the app is easier to run for a mini project. If you need MySQL:

1. Install and start MySQL; create a database, for example:
   ```sql
   CREATE DATABASE skillchain_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. Install the MySQL driver:
   ```bash
   pip install mysqlclient
   ```
3. Replace `DATABASES` in `skillchain_project/settings.py` with:
   ```python
   DATABASES = {
       "default": {
           "ENGINE": "django.db.backends.mysql",
           "NAME": "skillchain_ai",
           "USER": "your_mysql_user",
           "PASSWORD": "your_mysql_password",
           "HOST": "127.0.0.1",
           "PORT": "3306",
           "OPTIONS": {"charset": "utf8mb4"},
       }
   }
   ```
4. Do not commit credentials. Prefer environment variables for real deployments.
5. Run `python manage.py migrate` again.

## 7. Optional smart-contract deployment

The included contract is not wired into the default UI yet. This is an extension task, not enabled functionality in the MVP.

1. Open https://remix.ethereum.org/
2. Create `CertificateRegistry.sol`, paste the source from `contracts/CertificateRegistry.sol`, select compiler 0.8.20 or compatible, and compile.
3. Deploy to Remix VM first. The deployer is the initial owner and authorized issuer.
4. Test `registerCertificate`, `getRecord`, `verifyCertificate`, `setIssuer`, and `revokeCertificate`.
5. For a public testnet, configure MetaMask and use test ETH only. Never use a wallet with real funds for a class demo.
6. To connect Django, use `web3.py`: load the deployed contract ABI and address, hash a file's bytes into `bytes32`, call `registerCertificate`, wait for receipt, and store the transaction hash plus returned record ID in MySQL.
7. For a real integration, implement transaction signing securely and add tests for failed transactions, RPC errors, issuer permissions and revocation. Never hard-code private keys in source code or upload them to GitHub.

The contract's `documentHash` expects a `bytes32` hash. Convert a SHA-256 hex digest with `bytes.fromhex(digest)` before passing it to Web3.py.

## Security and accuracy notes

- Hash the exact bytes of a certificate file. A PDF re-saved with different metadata can legitimately produce a different hash.
- A hash match establishes byte-for-byte equality with the registered file, not that a credential is authentic. Verify the issuer's authority separately.
- The local demo record ID and transaction reference are placeholders, not blockchain transaction IDs.
- Do not store full resumes, personal details, passwords or certificate files on a public blockchain.
- The skill extractor only recognizes its configured vocabulary. Review results and do not use matching scores for high-stakes hiring decisions.
- Before deployment: set a strong secret key, set `DEBUG=False`, configure allowed hosts, use HTTPS, add upload scanning and authorization tests, and review privacy obligations.

## Troubleshooting

- `No module named django`: activate `.venv`, then run `pip install -r requirements.txt`.
- PDF parsing error: make sure the PDF is text-based; scanned PDFs need OCR, which is not included.
- `no such table`: run `python manage.py migrate`.
- No internships: run `python manage.py seed_internships`.
- Resume skills missing: add those skills manually to Profile; the extractor uses a limited vocabulary.
- File mismatch: upload the exact original file, not a screenshot or re-saved copy.
