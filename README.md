# AI Document Comparison Assistant

A Streamlit app for comparing two text-based PDF documents with Gemini. It extracts text using `pypdf`, summarizes each document, identifies supported similarities and differences, compares important details, and exports a DOCX report.

## Features

- Two PDF uploaders with filenames and extracted-text previews
- Validation for missing, empty, invalid, encrypted, unreadable, and scanned/image-only PDFs
- Separate summaries for Document A and Document B
- Similarities, differences, key details, conclusion, and limitations
- Downloadable DOCX report
- Gemini API error handling and one JSON repair attempt
- Reset and compare again

## Requirements

- Python 3.10 or newer (Python 3.11/3.12 recommended)
- Gemini API key
- Internet connection for Gemini API requests

## Setup (Linux / macOS)

```bash
cd ai-document-comparison-assistant
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and replace `your_gemini_api_key_here` with your Gemini API key. Keep `.env` private; never commit it to GitHub.

Run the app:

```bash
streamlit run app.py
```

Streamlit prints a local URL, usually `http://localhost:8501`.

## Setup (Windows PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env`, add your key, and run `streamlit run app.py`.

You can also paste the key into the password field in the app sidebar; it is used for that app session and is not written to `.env`.

## How to use

1. Upload a PDF into Document A and another into Document B.
2. Review filenames, extracted character/page counts, and text previews.
3. Enter a Gemini API key in the sidebar or configure `.env`.
4. Click **Compare Documents**.
5. Review each tab and download the DOCX report.

## Important limitations

- OCR is not included. Scanned/image-only PDFs are rejected if no text can be extracted.
- Very long inputs are rejected with a clear message; the app does not silently truncate documents.
- Gemini API usage may have quotas, rate limits, or costs depending on your account and current plan.
- LLM output can contain mistakes. Verify important findings against the source PDFs.
- This is an informational assistant, not legal advice or a legal/compliance decision-maker.
- Documents are sent to the configured Gemini API for analysis. Do not upload confidential material unless permitted by your organization and the provider's terms.

## Project structure

```text
ai-document-comparison-assistant/
├── app.py
├── document_reader.py
├── comparison.py
├── report_generator.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── sample_documents/
    ├── document_a.pdf
    └── document_b.pdf
```

## Git / GitHub

```bash
git init
git add .
git commit -m "Build AI Document Comparison Assistant"
```

Create an empty repository on GitHub, then follow GitHub's instructions to add the remote and push. Check that `.env` is ignored and never push your API key.

## Troubleshooting

- **API key error:** verify the key and that Gemini API access is enabled.
- **Quota / 429:** wait and retry or check your current quota.
- **Model not found:** change `GEMINI_MODEL` or the sidebar model field to a model available to your account.
- **No readable text:** try a selectable-text PDF; OCR is not included.
- **Install error:** ensure the virtual environment is activated and use `python -m pip install -r requirements.txt`.
