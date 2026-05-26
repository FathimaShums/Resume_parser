import streamlit as st
import json
import io
import copy
from typing import Dict, Any, List
from app.parser.extractor import extract_text
from app.parser.fields import parse_fields
from app.parser.scorer import score_resume
from app.database.mongo import db_client
from app.utils.helpers import format_date, get_score_color, DateTimeEncoder

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Resume Parser Pro - AI Portfolio App",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Harmonious Theme Injection (Glassmorphism, Dark UI, Gradient headers)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #161a24 100%);
        color: #f0f2f6;
    }
    
    /* Premium Headers */
    .main-title {
        background: linear-gradient(90deg, #a78bfa 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        color: #9ca3af;
        font-size: 1.15rem;
        margin-bottom: 2rem;
    }
    
    /* Custom Card Style (Glassmorphism) */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    }
    
    /* Badges */
    .badge {
        padding: 0.25rem 0.6rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
    }
    
    .badge-green { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-blue { background-color: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4); }
    .badge-orange { background-color: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0c0e14 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.image("https://img.icons8.com/gradient/100/resume.png", width=70)
st.sidebar.markdown("<h2 style='font-weight:700; color:#f0f2f6; margin-bottom:1.5rem;'>Resume Parser Pro</h2>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "NAVIGATION",
    ["UPLOAD & PARSE", "HISTORY", "COMPARE", "ABOUT"],
    index=0
)

# MongoDB Connection Check & Info Banner
db_online = db_client.is_connected()
st.sidebar.markdown("---")
if db_online:
    st.sidebar.markdown('<p style="color:#34d399; font-weight:600;"><span class="badge badge-green">●</span> MongoDB Atlas Connected</p>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<p style="color:#f87171; font-weight:600;"><span class="badge badge-orange">▲</span> MongoDB Offline (Local Mode)</p>', unsafe_allow_html=True)

# ==========================================
# PAGE 1: UPLOAD & PARSE
# ==========================================
if page == "UPLOAD & PARSE":
    st.markdown('<h1 class="main-title">Upload & Parse Resume</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Extract contacts, skills, education, and experiences using lightning-fast deterministic heuristics.</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Drag & Drop or Browse (PDF / DOCX only)",
        type=["pdf", "docx"],
        help="Upload standard PDF or Word document resume formats."
    )
    
    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_bytes = uploaded_file.read()
        file_ext = "." + file_name.split(".")[-1]
        
        col1, col2 = st.columns([1, 4])
        with col1:
            parse_btn = st.button("🚀 Parse Resume", use_container_width=True, type="primary")
            
        if parse_btn:
            with st.spinner("Extracting and analyzing text..."):
                try:
                    # 1. Text Extraction
                    raw_text = extract_text(io.BytesIO(file_bytes), file_ext)
                    
                    if not raw_text or len(raw_text.strip()) < 50:
                        st.warning("⚠️ This file appears to contain empty or scanned/image-based text. OCR is not supported in v1.0.")
                        
                    # 2. Heuristic Field Parsing
                    parsed_result = parse_fields(raw_text)
                    
                    # 3. Scoring Engine
                    final_result = score_resume(parsed_result)
                    
                    # Cache result in session state for downloading/saving
                    st.session_state["last_parsed"] = {
                        "filename": file_name,
                        "raw_text": raw_text,
                        "result": final_result
                    }
                    
                    st.success("🎉 Parsing Complete!")
                except Exception as e:
                    st.error(f"Failed to parse resume: {str(e)}")
                    
        # If we have a cached parsed result, display it
        if "last_parsed" in st.session_state and st.session_state["last_parsed"]["filename"] == file_name:
            cached = st.session_state["last_parsed"]
            res = cached["result"]
            data = res["parsed_data"]
            meta = res["metadata"]
            
            # Scores & Visual Indicators
            c_score = res.get("completeness_score", 0.0)
            conf_score = res.get("confidence_score", 0.0)
            
            st.markdown("---")
            score_col1, score_col2 = st.columns(2)
            with score_col1:
                st.markdown("### 📊 Completeness Score")
                st.progress(int(c_score))
                st.markdown(f"**Score: {c_score}%** (Ratio of populated core fields)")
                
            with score_col2:
                st.markdown("### 🎯 Extraction Confidence")
                st.progress(int(conf_score))
                st.markdown(f"**Score: {conf_score}%** (Certainty of heuristic/regex patterns)")
                
            # Expandable Detailed Layout
            st.markdown("### 📁 Extracted Information")
            
            with st.expander("👤 Contact Details", expanded=True):
                col_det1, col_det2 = st.columns(2)
                with col_det1:
                    st.text_input("Full Name", value=data.get("full_name") or "", disabled=True)
                    st.text_input("Email Address", value=data.get("email") or "", disabled=True)
                    st.text_input("Phone Number", value=data.get("phone") or "", disabled=True)
                with col_det2:
                    st.text_input("Location", value=data.get("location") or "", disabled=True)
                    st.text_input("LinkedIn Profile", value=data.get("linkedin_url") or "", disabled=True)
                    st.text_input("GitHub Profile", value=data.get("github_url") or "", disabled=True)
                    
            with st.expander("🛠️ Technical Skills", expanded=True):
                skills = data.get("skills", [])
                if skills:
                    st.markdown(" ".join([f'<span class="badge badge-blue">{s}</span>' for s in skills]), unsafe_allow_html=True)
                else:
                    st.info("No skills detected.")
                    
            with st.expander("💼 Professional Work Experience", expanded=True):
                experience = data.get("work_experience", [])
                if experience:
                    for exp in experience:
                        st.markdown(
                            f"""
                            <div class="glass-card">
                                <h4 style="margin:0; color:#a78bfa;">{exp.get('title') or 'Job Title'}</h4>
                                <p style="margin:0.25rem 0; font-size:0.9rem; color:#9ca3af;">
                                    <strong>{exp.get('company') or 'Company'}</strong> | 📅 {exp.get('dates') or 'Dates'}
                                </p>
                                <p style="white-space: pre-wrap; font-size:0.95rem; margin-top:0.5rem; line-height:1.4;">{exp.get('description') or ''}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No work experience detected.")
                    
            with st.expander("🎓 Education History", expanded=True):
                education = data.get("education", [])
                if education:
                    for edu in education:
                        st.markdown(
                            f"""
                            <div class="glass-card">
                                <h4 style="margin:0; color:#ec4899;">{edu.get('degree') or 'Degree'} in {edu.get('field') or 'Field'}</h4>
                                <p style="margin:0.25rem 0; font-size:0.9rem; color:#9ca3af;">
                                    <strong>{edu.get('institution') or 'Institution'}</strong> | 📅 {edu.get('dates') or 'Dates'}
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No education records detected.")
                    
            with st.expander("🎖️ Certifications & Languages", expanded=False):
                col_cert, col_lang = st.columns(2)
                with col_cert:
                    st.markdown("#### Certifications")
                    certs = data.get("certifications", [])
                    if certs:
                        for cert in certs:
                            st.markdown(f"- {cert}")
                    else:
                        st.info("No certifications found.")
                with col_lang:
                    st.markdown("#### Languages")
                    langs = data.get("languages", [])
                    if langs:
                        st.markdown(", ".join(langs))
                    else:
                        st.info("No languages found.")
                        
            # Download & Database Save Buttons
            st.markdown("### ⚙️ Actions")
            act_col1, act_col2 = st.columns(2)
            
            with act_col1:
                # Custom JSON encoder to serialize datetime
                json_str = json.dumps(data, indent=2, cls=DateTimeEncoder)
                st.download_button(
                    label="💾 Download Parsed Result as JSON",
                    data=json_str,
                    file_name=f"parsed_{file_name.replace('.pdf', '').replace('.docx', '')}.json",
                    mime="application/json",
                    use_container_width=True
                )
                
            with act_col2:
                if db_online:
                    save_btn = st.button("☁️ Save Parsed Resume to MongoDB Atlas", use_container_width=True)
                    if save_btn:
                        res_id = db_client.save_resume(file_name, res, cached["raw_text"])
                        if res_id:
                            st.success(f"Successfully saved to database! Record ID: {res_id}")
                        else:
                            st.error("Failed to save to database.")
                else:
                    st.button("☁️ Save Parsed Resume to MongoDB Atlas", disabled=True, use_container_width=True, help="MongoDB is offline. Please configure your credentials.")

# ==========================================
# PAGE 2: HISTORY
# ==========================================
elif page == "HISTORY":
    st.markdown('<h1 class="main-title">Parsing History</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Access and manage all previously analyzed resumes stored in MongoDB.</p>', unsafe_allow_html=True)
    
    if not db_online:
        st.warning("⚠️ MongoDB is offline. You need an active database connection to view or search history.")
    else:
        resumes = db_client.fetch_all_resumes()
        
        if not resumes:
            st.info("No parsed resumes found in MongoDB Atlas. Parse and save some resumes first!")
        else:
            # Display stats header cards
            stat1, stat2, stat3 = st.columns(3)
            with stat1:
                st.markdown(f'<div class="glass-card" style="text-align:center;"><h3 style="margin:0; color:#a78bfa;">{len(resumes)}</h3><p style="margin:0; font-size:0.9rem; color:#9ca3af;">Total Resumes</p></div>', unsafe_allow_html=True)
            with stat2:
                avg_comp = round(sum(r.get("completeness_score", 0.0) for r in resumes) / len(resumes), 1)
                st.markdown(f'<div class="glass-card" style="text-align:center;"><h3 style="margin:0; color:#34d399;">{avg_comp}%</h3><p style="margin:0; font-size:0.9rem; color:#9ca3af;">Avg Completeness</p></div>', unsafe_allow_html=True)
            with stat3:
                avg_conf = round(sum(r.get("confidence_score", 0.0) for r in resumes) / len(resumes), 1)
                st.markdown(f'<div class="glass-card" style="text-align:center;"><h3 style="margin:0; color:#60a5fa;">{avg_conf}%</h3><p style="margin:0; font-size:0.9rem; color:#9ca3af;">Avg Confidence</p></div>', unsafe_allow_html=True)
                
            st.markdown("### 📋 Stored Resumes")
            
            # Simple Interactive Row List
            for idx, r in enumerate(resumes):
                cols = st.columns([4, 2, 2, 2, 2])
                with cols[0]:
                    st.markdown(f"**{r.get('filename')}**")
                    st.caption(f"Uploaded: {format_date(r.get('uploaded_at'))}")
                with cols[1]:
                    st.markdown(f"Completeness: **{r.get('completeness_score')}%**")
                with cols[2]:
                    st.markdown(f"Confidence: **{r.get('confidence_score')}%**")
                with cols[3]:
                    view_btn = st.button("👁️ View Details", key=f"view_{r.get('_id')}", use_container_width=True)
                with cols[4]:
                    del_btn = st.button("🗑️ Delete", key=f"del_{r.get('_id')}", use_container_width=True, type="secondary")
                    
                if view_btn:
                    st.session_state["view_id"] = r.get('_id')
                if del_btn:
                    if db_client.delete_resume(r.get('_id')):
                        st.success(f"Deleted {r.get('filename')}")
                        st.rerun()
                        
                st.markdown("<hr style='margin:0.5rem 0; opacity:0.15;'>", unsafe_allow_html=True)
                
            # Expand Details drawer if one is selected
            if "view_id" in st.session_state:
                view_doc = db_client.fetch_resume_by_id(st.session_state["view_id"])
                if view_doc:
                    st.markdown("---")
                    st.markdown(f"### 📄 Detailed View: {view_doc.get('filename')}")
                    
                    data = view_doc.get("parsed_data", {})
                    
                    col_back, _ = st.columns([1, 8])
                    with col_back:
                        if st.button("❌ Close Panel", key="close_view"):
                            del st.session_state["view_id"]
                            st.rerun()
                            
                    st.json(data)

# ==========================================
# PAGE 3: COMPARE
# ==========================================
elif page == "COMPARE":
    st.markdown('<h1 class="main-title">Compare Resumes</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Perform detailed, side-by-side comparison of any two parsed profiles from database history.</p>', unsafe_allow_html=True)
    
    if not db_online:
        st.warning("⚠️ MongoDB is offline. You need an active database connection to compare resumes.")
    else:
        resumes = db_client.fetch_all_resumes()
        if len(resumes) < 2:
            st.info("You need at least 2 saved resumes in the database to compare. Please parse and save more resumes!")
        else:
            resume_options = {f"{r.get('filename')} (Saved: {format_date(r.get('uploaded_at'))})": r.get('_id') for r in resumes}
            
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                r1_sel = st.selectbox("Select First Resume", list(resume_options.keys()), index=0)
            with c_col2:
                r2_sel = st.selectbox("Select Second Resume", list(resume_options.keys()), index=min(1, len(resume_options)-1))
                
            id1 = resume_options[r1_sel]
            id2 = resume_options[r2_sel]
            
            doc1 = db_client.fetch_resume_by_id(id1)
            doc2 = db_client.fetch_resume_by_id(id2)
            
            if doc1 and doc2:
                data1 = doc1["parsed_data"]
                data2 = doc2["parsed_data"]
                
                st.markdown("### ⚖️ Side-by-Side Comparison")
                
                comp_col1, comp_col2 = st.columns(2)
                
                with comp_col1:
                    st.markdown(
                        f"""
                        <div class="glass-card" style="border-top: 4px solid #a78bfa;">
                            <h3 style="margin:0;">{data1.get('full_name') or 'Candidate A'}</h3>
                            <p style="color:#9ca3af; font-size:0.9rem;">Completeness: <strong>{doc1.get('completeness_score')}%</strong> | Confidence: <strong>{doc1.get('confidence_score')}%</strong></p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with comp_col2:
                    st.markdown(
                        f"""
                        <div class="glass-card" style="border-top: 4px solid #ec4899;">
                            <h3 style="margin:0;">{data2.get('full_name') or 'Candidate B'}</h3>
                            <p style="color:#9ca3af; font-size:0.9rem;">Completeness: <strong>{doc2.get('completeness_score')}%</strong> | Confidence: <strong>{doc2.get('confidence_score')}%</strong></p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                # Fields mapping to compare
                compare_fields = [
                    ("Email", "email"),
                    ("Phone", "phone"),
                    ("Location", "location"),
                    ("LinkedIn", "linkedin_url"),
                    ("GitHub", "github_url")
                ]
                
                for label, key in compare_fields:
                    val1 = data1.get(key)
                    val2 = data2.get(key)
                    
                    diff_style = "border: 1px solid rgba(245, 158, 11, 0.3); background-color: rgba(245, 158, 11, 0.02);" if val1 != val2 else ""
                    
                    col_diff1, col_diff2 = st.columns(2)
                    with col_diff1:
                        st.markdown(
                            f"""
                            <div class="glass-card" style="padding:1rem; margin-bottom:0.75rem; {diff_style}">
                                <span style="font-size:0.8rem; color:#9ca3af; text-transform:uppercase;">{label}</span>
                                <p style="margin:0.25rem 0 0 0; font-weight:600;">{val1 or '—'}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    with col_diff2:
                        st.markdown(
                            f"""
                            <div class="glass-card" style="padding:1rem; margin-bottom:0.75rem; {diff_style}">
                                <span style="font-size:0.8rem; color:#9ca3af; text-transform:uppercase;">{label}</span>
                                <p style="margin:0.25rem 0 0 0; font-weight:600;">{val2 or '—'}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                # Compare Skills
                skills1 = set(data1.get("skills", []))
                skills2 = set(data2.get("skills", []))
                
                col_sk1, col_sk2 = st.columns(2)
                with col_sk1:
                    st.markdown("#### Unique Skills")
                    uniq1 = skills1 - skills2
                    if uniq1:
                        st.markdown(" ".join([f'<span class="badge badge-blue">{s}</span>' for s in uniq1]), unsafe_allow_html=True)
                    else:
                        st.caption("No unique skills compared to Candidate B.")
                with col_sk2:
                    st.markdown("#### Unique Skills")
                    uniq2 = skills2 - skills1
                    if uniq2:
                        st.markdown(" ".join([f'<span class="badge badge-orange">{s}</span>' for s in uniq2]), unsafe_allow_html=True)
                    else:
                        st.caption("No unique skills compared to Candidate A.")

# ==========================================
# PAGE 4: ABOUT & SYSTEM ARCHITECTURE
# ==========================================
elif page == "ABOUT":
    st.markdown('<h1 class="main-title">About This Project</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Technical architecture, design decisions, and system stack details.</p>', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="glass-card">
            <h3>📖 Overview</h3>
            <p>
                This <strong>Resume Parser Pro</strong> application is built as a portfolio-grade showcasing project demonstrating 
                how rule-based AI heuristics and deterministic text mining can solve complex unstructured text parsing problems 
                without incurring large model API fees.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("### 🧠 Technical Architecture & Interview Talking Points")
    
    # 4 beautiful key point grids
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown(
            """
            <div class="glass-card" style="height: 250px;">
                <h4 style="color:#a78bfa; margin-top:0;">⚡ Rule-Based Parser over LLMs</h4>
                <p style="font-size:0.95rem; line-height:1.4;">
                    <strong>Decision:</strong> Using regular expressions, token distance, and structural HTML section heuristics instead of OpenAI/Anthropic APIs.
                    <br><strong>Justification:</strong> Extreme cost-efficiency ($0 runtime), total execution privacy (GDPR compliance), and sub-millisecond low-latency processing speeds.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <div class="glass-card" style="height: 250px;">
                <h4 style="color:#34d399; margin-top:0;">📂 MongoDB Document Storage</h4>
                <p style="font-size:0.95rem; line-height:1.4;">
                    <strong>Decision:</strong> Storing data in MongoDB Atlas's M0 free cluster.
                    <br><strong>Justification:</strong> Resumes are naturally semi-structured and highly variable (varying work items, skill lists, language lists). Document storage provides dynamic schemas without strict relational SQL foreign key mappings.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t_col2:
        st.markdown(
            """
            <div class="glass-card" style="height: 250px;">
                <h4 style="color:#60a5fa; margin-top:0;">🌐 Python-Native Streamlit Stack</h4>
                <p style="font-size:0.95rem; line-height:1.4;">
                    <strong>Decision:</strong> Building the entire UI layer inside Streamlit rather than React or Next.js.
                    <br><strong>Justification:</strong> Rapid prototype engineering, zero-API backend abstraction, clean state encapsulation, and native Python security where credentials are never exposed to the client.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <div class="glass-card" style="height: 250px;">
                <h4 style="color:#ec4899; margin-top:0;">🛠️ Offline spaCy Name Processing</h4>
                <p style="font-size:0.95rem; line-height:1.4;">
                    <strong>Decision:</strong> Integrating the lightweight <code>en_core_web_sm</code> spaCy NER model for name extraction only.
                    <br><strong>Justification:</strong> High reliability for PERSON tagging in early document sections without incurring complex deep learning dependencies or cloud API overheads.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown(
        """
        <div class="glass-card">
            <h3>⚙️ Software Tech Stack</h3>
            <ul>
                <li><strong>UI Dashboard:</strong> Streamlit</li>
                <li><strong>Text Extractions:</strong> pdfminer.six, python-docx</li>
                <li><strong>Named Entity Recognition:</strong> spaCy en_core_web_sm</li>
                <li><strong>Database Integration:</strong> pymongo (MongoDB Atlas Free M0)</li>
                <li><strong>Unit Testing:</strong> pytest</li>
                <li><strong>Deployment Config:</strong> Render / Railway configuration</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
