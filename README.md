#BUDGET4U by DARK SILICON FOR 2026 MSIH HACKATHON

Technical Acknowledgements & API Credits
Core Infrastructure & Frameworks

    Flask (Python): Used for the backend server architecture and routing.

    Firebase / Google Firestore: Utilized as the primary NoSQL database for real-time transaction storage.

    Jinja2: Used for dynamic HTML templating and frontend/backend integration.

AI & Data Processing

    Google Gemini API: Powering the Fintel AI Assistant for natural language financial queries and SMS data parsing logic.

Data Visualization & Frontend Libraries

    Chart.js: Used to generate the "Spent vs. Earned" bar charts and expense trend line graphs.

    Google Fonts: Utilizing Inter for UI readability and Fraunces for financial branding.

    SVGRepo: Source for all functional UI icons (Navigation, Add, Delete, and Sync).

# Transaction SMS Parser Dashboard

A Flask-based dashboard that fetches SMS data from Firebase Realtime Database, filters for real financial transactions, parses them using AI (Llama 3 / Gemini), and syncs the cleaned data to Google Cloud Firestore.

## 🛠 Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.9+**
* **Pip** (Python package manager)
* **A Firebase Project** (with Realtime Database and Firestore enabled)

---

## 🚀 Setup Instructions

### 1. Clone the Project

```bash
git clone <your-repo-url>
cd <project-folder-name>

```

### 2. Create a Virtual Environment

It is highly recommended to use a virtual environment to keep dependencies isolated.

```bash
# Create the environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate

```

### 3. Install Requirements

Install the necessary Python libraries:

```bash
pip install flask firebase-admin python-dotenv requests

```

> **Note:** Ensure your `aiparser.py` file is in the root directory as the Flask app depends on it.

### 4. Configuration & Environment Variables

Create a file named `.env` in the root directory and add your secret keys:

```ini
FLASK_SECRET_KEY="your_super_secret_key"
OPENROUTER_API_KEY="your_api_key_here"

```

### 5. Firebase Service Account

1. Go to the **Firebase Console** > Project Settings > Service Accounts.
2. Click **Generate New Private Key**.
3. Save the JSON file to your local machine.
4. **Update the path** in `app.py`:
```python
SERVICE_ACCOUNT_PATH = r"C:\Path\To\Your\serviceAccountKey.json"

```



### 6. Local Data Path

Ensure your transaction JSON files are located in the path defined in `app.py`:

```python
DATA_FOLDER = r"D:\Backup folder\Code\GitHub\trial"

```

---

## 🖥 Running the Application

Once everything is configured, start the Flask development server:

```bash
python app.py

```

* **Dashboard:** Open `http://127.0.0.1:5000/` to view the list of users.
* **Syncing:** Click on a User UID. The app will:
1. Scan the local `{UID}_messages.json` file.
2. Filter the last 25 real transactions.
3. Send them to the AI Parser.
4. Automatically upload/merge the results into **Firestore** under `Transactions/{UID}/history/`.



---

## 📂 Project Structure

```text
├── app.py              # Main Flask Application
├── aiparser.py         # AI Logic (Llama3/Gemini Integration)
├── .env                # API Keys (Do not share!)
├── templates/          # HTML files
│   ├── dashboard.html
│   └── user_view.html
└── requirements.txt    # List of dependencies

