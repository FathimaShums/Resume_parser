# Resume Parser Pro 📄✨

An enterprise-ready, portfolio-quality, $0-cost Resume Parser web application that parses unstructured PDF and DOCX resume documents into beautiful structured data dashboards using rule-based heuristics, light NLP, and persistent cloud storage.

> **Live Demo Link:** [https://resume-parser-pro.onrender.com](https://resume-parser-pro.onrender.com) *(Configure your own DB to test or view mock local parsers)*

---

## 🛠️ Tech Stack & Dependencies

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend UI** | Streamlit | Single-language native interactive dashboard & state management |
| **PDF Extraction** | `pdfminer.six` | Raw stream text extraction from PDF files |
| **DOCX Extraction** | `python-docx` | Structured text extraction from MS Word documents |
| **lightweight NLP** | `spaCy` (en_core_web_sm) | Name extraction via PERSON entity tag recognition |
| **Persistence** | MongoDB Atlas (M0 Free Tier) | Permanent $0 cloud database for parsing history & comparisons |
| **Env Variables** | `python-dotenv` | Clean segregation of secrets locally and on host |
| **Testing Suite** | `pytest` | Test coverage for text mining, field parser, and scoring logic |

---

## 🧠 Architectural Decisions (Interview Talking Points)

### 1. Why Streamlit over React/Next.js?
* **Zero API Complexity**: Building a single-language (Python) stack avoids setting up backend REST interfaces, handling CORS, or writing redundant TypeScript interfaces.
* **Server-Side Security**: All environment credentials (like `MONGODB_URI`) remain protected in the backend container context and are never exposed to the client browser, mitigating standard single-page app (SPA) security risks.
* **Prototyping Speed**: We can build robust, dynamic dashboards complete with interactive sidebars and comparisons in hours instead of days.

### 2. Why Heuristic & Rule-Based Parsing over LLMs?
* **Zero Runtime Cost**: Standard LLM APIs (OpenAI, Anthropic) incur pay-per-call costs and lack a permanent free tier. Our custom regex and distance heuristics run completely local and cost $0 to run forever.
* **Ultra-Low Latency**: Heuristic string extraction executes in under **50 milliseconds**, whereas LLM api calls take several seconds, heavily degrading real-time user experiences.
* **Privacy & GDPR Compliance**: PII data (emails, phone numbers, addresses) remains offline. Resumes are analyzed locally in memory and never transmitted to third-party commercial APIs.

### 3. Why MongoDB Atlas M0 Cluster over Relational SQL?
* **Variable Document Schema**: Resume datasets vary wildly. Some candidates have multiple work experience records and languages, while others have none. MongoDB's document model represents this semi-structured data organically without massive relational tables or complex join queries.
* **Permanent Free Tier**: Atlas provides 512MB of cloud MongoDB clusters completely free forever, ideal for hosting independent portfolio projects.

### 4. Why PDF and DOCX Only in v1?
* **Industry Standards**: Over 99% of resumes are submitted in PDF or MS Word format.
* **No OCR Overhead**: Scanned images require heavy libraries (like Tesseract) which increase container size, delay boot times, and trigger memory usage crashes on free hosting platforms. v1.0 targets standard text-based exports.

### 5. Why Avoid AWS?
* **Zero Cost Constraints**: AWS free tiers expire after 12 months, which risks sudden billing surprises. By choosing MongoDB Atlas and Render, we guarantee the project costs exactly $0 to run in perpetuity.

---

## 🌟 Features
* **Page 1: Upload & Parse**: Drag-and-drop PDF/DOCX parser displaying structured details, completeness & confidence bars, raw JSON downloads, and database saves.
* **Page 2: History**: Complete log of all parsed resumes retrieved from MongoDB. View full JSON outputs or delete past records.
* **Page 3: Compare**: Side-by-side comparative panel highlighting fields that differ and showing unique skills.
* **Page 4: About**: Dedicated interview talking points, system design patterns, and tech stack details.

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

## 🍃 MongoDB Atlas Setup Instructions (Step-by-Step)
1. Go to [mongodb.com/atlas](https://mongodb.com/atlas) and register a free account.
2. Create a new project.
3. Build a free **M0 cluster** (select the free tier option explicitly).
4. Under **Database Access**, create a database user with read/write permissions.
5. Under **Network Access**, add IP `0.0.0.0/0` (required to authorize Render's dynamic application servers).
6. Click **Connect** → **Drivers** → copy the connection string.
7. Replace `<password>` in the connection string with your database user password.
8. Add this string as `MONGODB_URI` in your `.env` file.

---

## ☁️ Deployment to Render (Free Tier)
1. Commit and push all your code changes to GitHub.
2. Sign in to your [Render.com](https://render.com) dashboard.
3. Click **New** → **Web Service** → Connect your GitHub repository.
4. Set the following settings:
   - **Environment:** `Python 3`
   - **Start Command:** `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
5. Go to the **Environment** tab in Render and add the environment variables:
   - `MONGODB_URI` = *[Your Atlas connection string]*
   - `DB_NAME` = `resume_parser`
6. Click **Deploy**. The platform will compile and host your web service live!

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
