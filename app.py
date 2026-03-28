import streamlit as st
import json
import time
from datetime import datetime
from pathlib import Path

# Page config
st.set_page_config(
    page_title="KB Intelligence Hub",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

    :root {
        --bg-primary: #0a0e1a;
        --bg-secondary: #0f1629;
        --bg-card: #131c35;
        --accent-cyan: #00e5ff;
        --accent-purple: #7c3aed;
        --accent-green: #00ff88;
        --accent-amber: #ffb800;
        --accent-red: #ff4757;
        --text-primary: #e8eaf6;
        --text-muted: #7986cb;
        --border: #1e2d5a;
    }

    html, body, .stApp {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: 'Syne', sans-serif;
    }

    /* Hide streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }

    /* Custom header */
    .kb-header {
        background: linear-gradient(135deg, #0f1629 0%, #131c35 50%, #0a0e1a 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .kb-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(ellipse at center, rgba(0,229,255,0.04) 0%, transparent 60%);
    }
    .kb-header h1 {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        font-size: 2.2rem;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding: 0;
    }
    .kb-header p {
        color: var(--text-muted);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }

    /* Status badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
    }
    .status-online { background: rgba(0,255,136,0.1); color: var(--accent-green); border: 1px solid rgba(0,255,136,0.3); }
    .status-offline { background: rgba(255,71,87,0.1); color: var(--accent-red); border: 1px solid rgba(255,71,87,0.3); }
    .status-loading { background: rgba(255,184,0,0.1); color: var(--accent-amber); border: 1px solid rgba(255,184,0,0.3); }

    /* Cards */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .metric-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        font-size: 2rem;
        color: var(--accent-cyan);
    }
    .metric-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-secondary);
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
        border: 1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-muted);
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-purple), rgba(0,229,255,0.3)) !important;
        color: white !important;
    }

    /* Inputs */
    .stTextArea textarea, .stTextInput input, .stSelectbox select {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 0 1px var(--accent-cyan) !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan)) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.5rem !important;
        letter-spacing: 0.5px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(124,58,237,0.4) !important;
    }

    /* Output cards */
    .output-section {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    .output-section h3 {
        font-family: 'Syne', sans-serif;
        color: var(--accent-cyan);
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Priority badges */
    .priority-critical { background: rgba(255,71,87,0.15); color: #ff4757; border: 1px solid rgba(255,71,87,0.4); padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; }
    .priority-high { background: rgba(255,184,0,0.15); color: #ffb800; border: 1px solid rgba(255,184,0,0.4); padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; }
    .priority-medium { background: rgba(0,229,255,0.15); color: #00e5ff; border: 1px solid rgba(0,229,255,0.4); padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; }
    .priority-low { background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid rgba(0,255,136,0.4); padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; }

    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    .streamlit-expanderContent {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }

    /* Success/Warning/Error */
    .stSuccess { background: rgba(0,255,136,0.1) !important; border: 1px solid rgba(0,255,136,0.3) !important; }
    .stWarning { background: rgba(255,184,0,0.1) !important; border: 1px solid rgba(255,184,0,0.3) !important; }
    .stError { background: rgba(255,71,87,0.1) !important; border: 1px solid rgba(255,71,87,0.3) !important; }

    /* Markdown content area */
    .generated-content {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1.2rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        line-height: 1.7;
        color: var(--text-primary);
        white-space: pre-wrap;
        max-height: 500px;
        overflow-y: auto;
    }

    .sidebar-section {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .sidebar-section h4 {
        font-family: 'Syne', sans-serif;
        color: var(--accent-cyan);
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .model-chip {
        background: rgba(124,58,237,0.2);
        border: 1px solid rgba(124,58,237,0.4);
        color: #a78bfa;
        padding: 2px 8px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
    }

    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3 {
        font-family: 'Syne', sans-serif;
        color: var(--accent-cyan);
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# Import backend
from kb_engine import KBEngine, check_ollama_status

# ─── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-section">
        <h4>⚙️ Model Config</h4>
    </div>
    """, unsafe_allow_html=True)

    ollama_url = st.text_input("Ollama URL", value="http://localhost:11434", label_visibility="collapsed")
    
    model_options = ["llama3.2", "llama3.1", "llama3", "llama2", "mistral", "mixtral", "codellama", "phi3", "gemma2"]
    selected_model = st.selectbox("LLM Model", model_options)

    # Status check
    if st.button("🔍 Check Connection"):
        status = check_ollama_status(ollama_url)
        if status["online"]:
            st.success(f"✅ Connected — {len(status.get('models', []))} model(s) available")
        else:
            st.error(f"❌ {status['message']}")

    st.markdown("---")

    st.markdown("""
    <div class="sidebar-section">
        <h4>📂 Document KB</h4>
    </div>
    """, unsafe_allow_html=True)

    uploaded_kb = st.file_uploader(
        "Upload existing KB / SOPs",
        type=["txt", "md", "pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown("""
    <div class="sidebar-section">
        <h4>🎛️ Generation Settings</h4>
    </div>
    """, unsafe_allow_html=True)

    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.05)
    max_tokens = st.slider("Max Tokens", 512, 4096, 2048, 128)
    
    st.markdown("---")

    st.markdown("""
    <div class="sidebar-section">
        <h4>📋 Session Stats</h4>
    </div>
    """, unsafe_allow_html=True)

    if "session_stats" not in st.session_state:
        st.session_state.session_stats = {"kb_generated": 0, "sop_generated": 0, "incidents_analyzed": 0, "guides_created": 0}

    cols = st.columns(2)
    with cols[0]:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state.session_stats["kb_generated"]}</div><div class="metric-label">KB Articles</div></div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state.session_stats["sop_generated"]}</div><div class="metric-label">SOPs</div></div>', unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────
st.markdown("""
<div class="kb-header">
    <h1>🧠 KB Intelligence Hub</h1>
    <p>// AI-powered incident resolution · KB prediction · SOP generation · Troubleshooting guides</p>
</div>
""", unsafe_allow_html=True)

# Initialize engine
engine = KBEngine(ollama_url=ollama_url, model=selected_model, temperature=temperature, max_tokens=max_tokens)

# ─── Main Tabs ───────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚨 Incident Analyzer",
    "📚 KB Article Generator",
    "📋 SOP Builder",
    "🔧 Troubleshooting Guide",
    "🔮 KB Predictor"
])

# ─── Tab 1: Incident Analyzer ────────────────────────────────
with tab1:
    st.markdown("### 🚨 Incident Analysis & Resolution")
    st.caption("Paste an incident description to get AI-powered resolution recommendations, owner assignment, and auto-generated KB article.")

    col1, col2 = st.columns([3, 1])
    with col1:
        incident_title = st.text_input("Incident Title", placeholder="e.g., Database connection timeout causing API failures")
    with col2:
        severity = st.selectbox("Severity", ["P1 - Critical", "P2 - High", "P3 - Medium", "P4 - Low"])

    incident_desc = st.text_area(
        "Incident Description",
        height=150,
        placeholder="Describe the incident in detail: what happened, when, impact, affected systems, error messages, steps already tried..."
    )

    col_env, col_sys = st.columns(2)
    with col_env:
        environment = st.selectbox("Environment", ["Production", "Staging", "Development", "DR"])
    with col_sys:
        affected_system = st.text_input("Affected System", placeholder="e.g., Payment Gateway, Auth Service")

    if st.button("🔍 Analyze Incident", use_container_width=True):
        if incident_desc:
            with st.spinner("🤖 AI analyzing incident..."):
                result = engine.analyze_incident(
                    title=incident_title,
                    description=incident_desc,
                    severity=severity,
                    environment=environment,
                    affected_system=affected_system
                )

            st.session_state.session_stats["incidents_analyzed"] += 1

            # Display results
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value" style="font-size:1.2rem">🧑‍💻</div>
                    <div class="metric-label">Suggested Owner</div>
                    <div style="color:#00e5ff;font-weight:700;margin-top:4px">{result.get('suggested_owner','N/A')}</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value" style="font-size:1.2rem">⏱️</div>
                    <div class="metric-label">Est. Resolution Time</div>
                    <div style="color:#ffb800;font-weight:700;margin-top:4px">{result.get('est_resolution','N/A')}</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value" style="font-size:1.2rem">🎯</div>
                    <div class="metric-label">Confidence</div>
                    <div style="color:#00ff88;font-weight:700;margin-top:4px">{result.get('confidence','N/A')}</div>
                </div>""", unsafe_allow_html=True)

            with st.expander("📊 Full Analysis", expanded=True):
                st.markdown(result.get("analysis", ""))

            with st.expander("🛠️ Recommended Resolution Steps"):
                st.markdown(result.get("resolution_steps", ""))

            with st.expander("📚 Auto-Generated KB Draft"):
                kb_draft = result.get("kb_draft", "")
                st.text_area("KB Article (editable)", value=kb_draft, height=300, key="kb_draft_incident")
                if st.button("💾 Save KB Article"):
                    st.success("KB Article saved to session knowledge base!")
                    st.session_state.session_stats["kb_generated"] += 1
        else:
            st.warning("Please enter an incident description.")

# ─── Tab 2: KB Article Generator ─────────────────────────────
with tab2:
    st.markdown("### 📚 Knowledge Base Article Generator")
    st.caption("Generate professional KB articles from problem descriptions or existing incident data.")

    col_a, col_b = st.columns(2)
    with col_a:
        kb_topic = st.text_input("Topic / Problem Statement", placeholder="e.g., How to resolve SSL certificate expiry errors")
    with col_b:
        kb_category = st.selectbox("Category", [
            "Infrastructure", "Application", "Security", "Network",
            "Database", "Cloud Services", "DevOps", "End-user Support", "API/Integration"
        ])

    kb_context = st.text_area(
        "Additional Context (optional)",
        height=120,
        placeholder="Include any specific details, constraints, environment specifics, or related incidents..."
    )

    col_au, col_ta = st.columns(2)
    with col_au:
        audience = st.selectbox("Target Audience", ["L1 Support", "L2 Support", "L3 Engineering", "End Users", "DevOps/SRE"])
    with col_ta:
        kb_style = st.selectbox("Article Style", ["Step-by-step", "Conceptual Overview", "FAQ Format", "Decision Tree", "Quick Reference"])

    if st.button("📝 Generate KB Article", use_container_width=True):
        if kb_topic:
            with st.spinner("✍️ Generating KB article..."):
                result = engine.generate_kb_article(
                    topic=kb_topic,
                    category=kb_category,
                    context=kb_context,
                    audience=audience,
                    style=kb_style
                )
            st.session_state.session_stats["kb_generated"] += 1

            st.markdown(f"""<div class="output-section">
                <h3>📄 Generated KB Article</h3>
            </div>""", unsafe_allow_html=True)

            st.text_area("Article Content (editable & copyable)", value=result, height=400, key="kb_output")

            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button("⬇️ Download as .md", data=result,
                    file_name=f"KB_{kb_topic[:30].replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown", use_container_width=True)
            with col_dl2:
                st.download_button("⬇️ Download as .txt", data=result,
                    file_name=f"KB_{kb_topic[:30].replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain", use_container_width=True)
        else:
            st.warning("Please enter a topic.")

# ─── Tab 3: SOP Builder ──────────────────────────────────────
with tab3:
    st.markdown("### 📋 Standard Operating Procedure Builder")
    st.caption("Create detailed, structured SOPs for any operational process.")

    sop_process = st.text_input("Process Name", placeholder="e.g., Database Failover Procedure, Incident Escalation Process")

    col_dept, col_freq = st.columns(2)
    with col_dept:
        department = st.selectbox("Department / Team", [
            "IT Operations", "SRE/DevOps", "Security", "Network Engineering",
            "Database Administration", "Application Support", "Service Desk", "Cloud Infrastructure"
        ])
    with col_freq:
        frequency = st.selectbox("Process Frequency", ["Ad-hoc / Emergency", "Daily", "Weekly", "Monthly", "Quarterly", "Annual"])

    sop_objective = st.text_area(
        "Process Objective & Scope",
        height=100,
        placeholder="What does this SOP achieve? What systems, teams, or scenarios does it cover?"
    )

    pre_conditions = st.text_area(
        "Pre-conditions / Prerequisites",
        height=80,
        placeholder="What must be true or done before this procedure begins?"
    )

    risk_level = st.select_slider("Risk Level", options=["Low", "Medium", "High", "Critical"])

    if st.button("📋 Build SOP", use_container_width=True):
        if sop_process:
            with st.spinner("🏗️ Building SOP document..."):
                result = engine.generate_sop(
                    process=sop_process,
                    department=department,
                    frequency=frequency,
                    objective=sop_objective,
                    pre_conditions=pre_conditions,
                    risk_level=risk_level
                )
            st.session_state.session_stats["sop_generated"] += 1

            st.text_area("SOP Document", value=result, height=450, key="sop_output")

            st.download_button(
                "⬇️ Download SOP",
                data=result,
                file_name=f"SOP_{sop_process[:30].replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        else:
            st.warning("Please enter a process name.")

# ─── Tab 4: Troubleshooting Guide ────────────────────────────
with tab4:
    st.markdown("### 🔧 Troubleshooting Guide Generator")
    st.caption("Generate comprehensive troubleshooting guides with decision trees, common causes, and diagnostic steps.")

    issue_title = st.text_input("Issue Title", placeholder="e.g., Application pods crashing in Kubernetes")

    col_tech, col_env2 = st.columns(2)
    with col_tech:
        technology = st.selectbox("Technology Stack", [
            "Kubernetes / Docker", "AWS Cloud", "Azure Cloud", "GCP Cloud",
            "Linux/Unix Systems", "Windows Server", "Databases (SQL/NoSQL)",
            "Network / Firewall", "Web Applications", "Microservices", "CI/CD Pipeline", "Other"
        ])
    with col_env2:
        guide_env = st.selectbox("Environment", ["Production", "Staging", "All Environments"])

    symptoms = st.text_area(
        "Symptoms / Error Messages",
        height=100,
        placeholder="Describe what users/systems are experiencing. Include any error codes, logs, or alerts..."
    )

    already_tried = st.text_area(
        "What Has Already Been Tried?",
        height=80,
        placeholder="List any steps already attempted to resolve the issue..."
    )

    include_decision_tree = st.checkbox("Include Decision Tree / Flowchart (text-based)", value=True)

    if st.button("🔧 Generate Troubleshooting Guide", use_container_width=True):
        if symptoms or issue_title:
            with st.spinner("🔍 Generating troubleshooting guide..."):
                result = engine.generate_troubleshooting_guide(
                    issue_title=issue_title,
                    technology=technology,
                    environment=guide_env,
                    symptoms=symptoms,
                    already_tried=already_tried,
                    include_decision_tree=include_decision_tree
                )
            st.session_state.session_stats["guides_created"] += 1

            st.text_area("Troubleshooting Guide", value=result, height=450, key="tsg_output")
            st.download_button(
                "⬇️ Download Guide",
                data=result,
                file_name=f"TSG_{issue_title[:30].replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        else:
            st.warning("Please describe the symptoms or provide an issue title.")

# ─── Tab 5: KB Predictor ──────────────────────────────────────
with tab5:
    st.markdown("### 🔮 KB Article Predictor")
    st.caption("Based on incident patterns and trends, predict which KB articles should be created proactively.")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        incident_volume = st.number_input("Weekly Incident Volume", min_value=1, max_value=10000, value=50)
        top_categories = st.multiselect(
            "Top Incident Categories",
            ["Network", "Application", "Database", "Security", "Cloud", "Authentication", "Performance", "Storage"],
            default=["Application", "Network"]
        )
    with col_p2:
        team_size = st.number_input("Support Team Size", min_value=1, max_value=500, value=10)
        current_kb_count = st.number_input("Current KB Articles", min_value=0, value=25)

    recurring_issues = st.text_area(
        "Describe Recurring / Common Issues",
        height=120,
        placeholder="What issues keep coming back? What are your team's pain points? What questions does L1 escalate most?"
    )

    predict_horizon = st.selectbox("Prediction Horizon", ["Next 2 Weeks", "Next Month", "Next Quarter"])

    if st.button("🔮 Predict KB Gaps & Generate Articles", use_container_width=True):
        if recurring_issues or top_categories:
            with st.spinner("🧠 Analyzing patterns and predicting knowledge gaps..."):
                result = engine.predict_kb_gaps(
                    incident_volume=incident_volume,
                    top_categories=top_categories,
                    team_size=team_size,
                    current_kb_count=current_kb_count,
                    recurring_issues=recurring_issues,
                    horizon=predict_horizon
                )

            st.markdown("#### 📊 Prediction Results")

            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value">{result.get('predicted_gaps', '?')}</div>
                    <div class="metric-label">KB Gaps Identified</div>
                </div>""", unsafe_allow_html=True)
            with col_r2:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value">{result.get('priority_articles', '?')}</div>
                    <div class="metric-label">Priority Articles</div>
                </div>""", unsafe_allow_html=True)
            with col_r3:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value">{result.get('impact_score', 'N/A')}</div>
                    <div class="metric-label">Expected Impact</div>
                </div>""", unsafe_allow_html=True)

            with st.expander("📋 Predicted KB Gaps & Recommendations", expanded=True):
                st.markdown(result.get("analysis", ""))

            with st.expander("📝 Sample Article Stubs (Auto-Generated)"):
                st.markdown(result.get("article_stubs", ""))
        else:
            st.warning("Please provide recurring issues or select categories.")
