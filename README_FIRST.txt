# HealthDecode — Streamlit starter project

## Files
- `app.py`: the website
- `requirements.txt`: Python dependencies
- `packages.txt`: system package for OCR (Tesseract)

## Run on your laptop
1. Install Python 3.10 or newer from https://www.python.org/downloads/
2. Open a terminal/Command Prompt in this folder.
3. Create an environment (optional but recommended):
   - Windows: `py -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Install the Tesseract OCR engine on your computer:
   - Windows: install the Tesseract OCR application and add its install folder to PATH.
   - macOS: `brew install tesseract`
   - Ubuntu/Debian: `sudo apt install tesseract-ocr`
6. Run: `streamlit run app.py`
7. Your browser should open the app (usually http://localhost:8501).

## Deploy
1. Upload these files to a GitHub repository.
2. Open https://share.streamlit.io and connect GitHub.
3. Choose the repository, branch `main`, and entry file `app.py`, then deploy.
4. `packages.txt` requests Tesseract on supported Streamlit Community Cloud deployments. Check deployment logs if OCR fails.

## Important limitations
This is an EDUCATIONAL prototype. PDF text extraction works only when the PDF contains selectable text. The current parser is basic and may miss or misread results in different report layouts. The user must verify every extracted value, unit, and range. Scanned PDFs are not OCR'd automatically in this first version; upload a clear image page instead. It does not diagnose or recommend treatment. Do not upload identifiable real patient records.
