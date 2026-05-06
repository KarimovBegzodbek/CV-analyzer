# AI-Based CV Analysis System

## Overview

This project is a web-based application that analyses CVs using a combination of rule-based scoring and AI-generated feedback. It was developed as a final-year project for the BSc (Hons) Software Engineering / Computer Science programme.

The system is designed specifically to support graduates in Uzbekistan by providing **localised, explainable, and actionable CV feedback**, rather than simply filtering candidates like traditional ATS (Applicant Tracking Systems).

---

## Live Demo

https://cv-analyzer-xzez.onrender.com

> Note: The live demo may take a few seconds to load due to free hosting limitations.

---

## Features

* CV upload support (PDF and DOCX)
* Automated text extraction and analysis
* Rule-based scoring across four dimensions:

  * Structure & Flow
  * Skills Match
  * Formatting
  * Content & Clarity
* AI-generated feedback using Claude API:

  * General CV overview
  * Actionable improvement suggestions
* Bilingual support (English and Uzbek)
* User authentication and session management
* CV history tracking per user

---

## Technology Stack

### Backend

* Python
* Flask
* SQLAlchemy
* Flask-Login
* Flask-Bcrypt
* Flask-WTF (CSRF protection)

### AI & NLP

* Claude API (Anthropic)
* Natural Language Processing techniques

### File Processing

* pdfplumber (PDF parsing)
* python-docx (DOCX parsing)

### Frontend

* HTML, CSS, Jinja2 templates

### Internationalisation

* Flask-Babel (English / Uzbek)

---

## System Architecture

The application follows a modular design using Flask’s application factory pattern and MVC structure:

* **Routes** – handle user requests and workflow
* **Models** – database structure and data persistence
* **Templates** – UI rendering
* **Utils** – CV analysis pipeline and scoring logic

---

## How It Works

1. User uploads a CV (PDF or DOCX)
2. System validates file type and extracts text
3. Rule-based scoring evaluates:

   * structure
   * skills
   * formatting
   * content clarity
4. Extracted text + scores are sent to Claude API
5. AI generates:

   * overall CV evaluation
   * actionable suggestions
6. Results are stored and displayed to the user

---

## Installation (Run Locally)

1. Clone the repository:

```bash
git clone https://github.com/KarimovBegzodbek/CV-analyzer.git
cd CV-analyzer
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables (example):

```bash
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///database.db
CLAUDE_API_KEY=your_api_key
```

4. Run the application:

```bash
python app.py
```

5. Open in browser:

```
http://127.0.0.1:5000
```

---

## Limitations

* Scanned PDFs are not supported (no OCR integration)
* AI feedback depends on external Claude API availability
* Uzbek CV calibration is limited by available data
* Free hosting may cause slow initial loading

---

## Future Improvements

* OCR support for scanned CVs
* Improved Uzbek-language dataset and calibration
* Semantic analysis using embeddings
* Automated unit testing for scoring module
* Deployment optimisation for faster performance

---

## Author

Karimov Begzodbek
Wolverhampton University / Student

---

## Project Context

This project was developed as part of the **6CS007/ZB1 – Project and Professionalism** module.
It explores how AI systems can provide **explainable, localised feedback** rather than acting as opaque filtering tools.

---

## License

This project is for academic use.
