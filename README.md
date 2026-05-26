# Resume Parser Pro 📄✨

A Resume Parser web application that parses unstructured PDF and DOCX resume documents into structured data dashboards using rule-based heuristics, light NLP, and persistent cloud storage.

> **Live Demo Link:** https://resume-parser-ovvm.onrender.com

---

## 🛠️ Tech Stack & Dependencies

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend UI** | Streamlit | Single-language native interactive dashboard & state management |
| **PDF Extraction** | `pdfminer.six` | Raw stream text extraction from PDF files |
| **DOCX Extraction** | `python-docx` | Structured text extraction from MS Word documents |
| **lightweight NLP** | `spaCy` (en_core_web_sm) | Name extraction via PERSON entity tag recognition |
| **Persistence** | MongoDB Atlas  | Permanent  cloud database for parsing history & comparisons |
| **Env Variables** | `python-dotenv` | Clean segregation of secrets locally and on host |
| **Testing Suite** | `pytest` | Test coverage for text mining, field parser, and scoring logic |


---

## 🌟 Features
* **Page 1: Upload & Parse**: Drag-and-drop PDF/DOCX parser displaying structured details, completeness & confidence bars, raw JSON downloads, and database saves.
* **Page 2: History**: Complete log of all parsed resumes retrieved from MongoDB. View full JSON outputs or delete past records.
* **Page 3: Compare**: Side-by-side comparative panel highlighting fields that differ and showing unique skills.
* **Page 4: About**:    System design patterns, and tech stack details.

---

## ⚙️ Local Setup Instructions

### 1. Clone & Setup Workspace
```bash
git clone https://github.com/FathimaShums/Resume_parser.git
cd Resume_parser
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory:
```env
MONGODB_URI=your_mongodb_atlas_connection_string
DB_NAME=resume_parser
```
*Note: Make sure `.env` is listed in your `.gitignore` to prevent credential exposure!*

### 4. Run the Application Locally
```bash
streamlit run streamlit_app.py
```


---


## 📈 Interpreting the Scores
* **Completeness Score (0-100)**: Evaluates the presence of the 7 core blocks (Name, Email, Phone, Location, Skills, Education, Work Experience). Each block counts for 1/7 (~14.3%) of the score.
* **Confidence Score (0-100)**: Measured by extraction type. Deterministic regex patterns (email, phone, urls) return 100% confidence, spaCy PERSON recognition returns 85%, and fallback heuristics return 40%-50% depending on header matching.
* **Null Values**: If a block is missing from the document, the parser returns `null` or empty lists `[]` rather than inventing false data.

---

## 🔮 Limitations & Future Roadmap
* **OCR Layer**: Add `pytesseract` or `easyocr` to support scanned image-based PDF parsing.
* **Bulk Uploads**: Support zip file bulk imports with parallel multi-core thread pool parsers.
* **LLM Hybrid Scoring**: Introduce a local lightweight LLM (Llama-3-8B-Instruct) to structure unstructured experience descriptions with strict JSON outputs.
* **ATS Compatibility Scoring**: Add a job-description matcher utilizing cosine similarity algorithms.
