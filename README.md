# Apex Telemetry — Initial Scaffold

This is an initial scaffold for the Apex Telemetry project. It includes a minimal Flask app with user registration/login and a placeholder dashboard that uses Chart.js for visuals.

Quick start (Windows PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

Next steps I can implement for you:
- Integrate the F1 API to fetch historical telemetry
- Add CRUD for saved sessions
- Implement email notifications
