# Cybersecurity Incident Report Generator

A Flask web app that turns structured cybersecurity incident data into a
professional natural-language incident report using **FLAN-T5** (Hugging
Face Transformers) — a pretrained data-to-text generation model. Reports
can be saved to a local SQLite database, browsed in a history page, and
exported to PDF.

---

## 1. Project Structure

```
CyberIncidentReportGenerator/
├── app.py                 # Flask routes (the web app entry point)
├── config.py               # Paths, model name, Flask settings
├── database.py              # SQLite: create table, insert, list, delete
├── model.py                  # Loads FLAN-T5, exposes generate_text()
├── report_generator.py        # Builds prompts, assembles report sections
├── pdf_export.py               # ReportLab PDF generation
├── generate_dataset.py          # One-time script that built the sample CSV
├── requirements.txt
├── dataset/incidents.csv         # 120 sample incidents for testing/demo
├── database/incidents.db          # created automatically on first run
├── reports/                        # generated PDFs land here
├── templates/                       # Jinja2 HTML (layout, form, report, history)
└── static/
    ├── css/style.css                 # dark-mode cybersecurity dashboard theme
    ├── js/script.js                   # client-side validation + UX polish
    └── images/
```

## 2. Setup

Requires **Python 3.10+** (tested with 3.14). `requirements.txt` uses
minimum-version pins (`>=`) rather than exact pins, because `torch` and
`sentencepiece` only shipped Python 3.14-compatible wheels in their more
recent releases (torch 2.9+, sentencepiece 0.2.1+) — older exact pins
will fail to install on 3.14.

```bash
cd CyberIncidentReportGenerator
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> `transformers` + `torch` are ~1-2 GB combined and FLAN-T5-base itself is
> ~1 GB — the first `pip install` and the first report generation will
> both take a few minutes and need an internet connection to reach
> `huggingface.co`. After the first run, the model is cached locally
> (`~/.cache/huggingface`) and loads fast.

## 3. Run

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## 4. Using the App

1. **Home** → click *Generate Report*.
2. **New Incident** form → fill in all 12 fields (or copy a row from
   `dataset/incidents.csv` to try it quickly) → *Generate Report*.
   First generation is slower (~10-30s on CPU) because the model loads
   into memory; later generations are faster.
3. **Report page** → review the 5 sections (Executive Summary, Technical
   Details, Incident Impact, Response Taken, Recommendations) → *Save
   Report* and/or *Download PDF*.
4. **History** → browse, open, re-download, or delete saved reports.

## 5. Regenerating the Sample Dataset

```bash
python generate_dataset.py
```

This overwrites `dataset/incidents.csv` with 120 freshly randomized
incidents across all 14 attack types and 4 severity levels. It's a
standalone script, not used by the running app — it's just there so you
have realistic data to test the form with.

## 6. Testing Without Downloading the Model

If you want to test the Flask app (routes, validation, database, PDF
export) without waiting on the ~1 GB FLAN-T5 download, you can stub
`report_generator.generate_text` in a quick script:

```python
import report_generator
report_generator.generate_text = lambda prompt, max_new_tokens=512: "Stub sentence."
```

Then run your normal Flask test client / route calls. This is exactly
how the app was verified while building it.

## 7. Common Errors & Fixes

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'transformers'` | Dependencies not installed | `pip install -r requirements.txt` |
| First report takes a long time / seems frozen | FLAN-T5 downloading + loading into memory | Wait — check console for `[model.py] Loading google/flan-t5-base ...`. Only happens once per process. |
| `sqlite3.OperationalError: unable to open database file` | `database/` folder missing | It's created automatically by `config.py`; make sure you're running `app.py` from inside the project folder. |
| Form shows "Source IP is not a valid IP address" | Typo in IP, e.g. missing octet | Enter a valid IPv4 (`192.168.1.25`) or IPv6 address. |
| PDF download gives 404 / report not found | Report id doesn't exist (deleted already) | Go back to History and pick an existing report. |
| Port 5000 already in use | Another process (often macOS AirPlay Receiver) is using port 5000 | Either stop that process, or run `app.run(port=5001)` in `app.py`. |

## 8. Notes on the NLP Approach

`report_generator.py` does **not** ask FLAN-T5 to write one giant report
in a single generation call. FLAN-T5-base is a relatively small model, so
one prompt per section (Executive Summary, Technical Details, Incident
Impact, Response Taken, Recommendations) produces much more reliable,
on-topic output than a single long prompt, which tends to ramble or drop
sections. This is a standard data-to-text pattern: **structured data →
per-field prompt → natural language → template assembly**.

No model is trained from scratch — `google/flan-t5-base` is loaded
pretrained and only prompted (zero-shot instruction following).
