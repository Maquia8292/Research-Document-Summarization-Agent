"""
Research & Document Summarization Agent - Streamlit Application.
Main entry point for document parsing, Gemini API summarization, key points extraction, Q&A, and insights.
"""

import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Local module imports
from document_parser import parse_uploaded_document, chunk_text
from summarizer import GeminiSummarizer, NEW_SDK_AVAILABLE, LEGACY_SDK_AVAILABLE

# Load environment variables from .env file
load_dotenv(override=True)

# --- STREAMLIT PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Research & Document Summarizer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM GLASSMORPHIC STYLING ---
CUSTOM_CSS = """
<style>
    /* Google Font import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Gradient Banner */
    .header-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 70%, #6366f1 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 18px;
        color: #ffffff;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.3);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0 0 0.4rem 0;
        letter-spacing: -0.02em;
    }

    .header-subtitle {
        font-size: 1.05rem;
        opacity: 0.9;
        margin: 0;
        font-weight: 400;
    }

    .badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 50px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.5rem;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(229, 231, 235, 0.2);
        border-radius: 14px;
        padding: 1.2rem 1rem;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
    }

    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #4f46e5;
        margin-bottom: 0.2rem;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #6b7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        margin-bottom: 1.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 10px;
        padding: 0 20px;
        font-weight: 600;
        background-color: rgba(243, 244, 246, 0.6);
        border: 1px solid transparent;
    }

    .stTabs [aria-selected="true"] {
        background-color: #4f46e5 !important;
        color: white !important;
    }

    /* Chat bubble enhancements */
    .chat-user {
        background-color: #e0e7ff;
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        color: #1e1b4b;
        margin-bottom: 0.5rem;
    }
    
    .chat-assistant {
        background-color: #f3f4f6;
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        color: #111827;
        margin-bottom: 0.5rem;
        border-left: 4px solid #4f46e5;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "parsed_doc" not in st.session_state:
    st.session_state["parsed_doc"] = None
if "summary_output" not in st.session_state:
    st.session_state["summary_output"] = None
if "key_points_output" not in st.session_state:
    st.session_state["key_points_output"] = None
if "analytics_output" not in st.session_state:
    st.session_state["analytics_output"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Fetch GEMINI_API_KEY from environment / .env file
api_key_from_env = os.getenv("GEMINI_API_KEY", "").strip()

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.markdown("---")

    # Display API Key status loaded from .env
    st.subheader("🔑 API Key Status")
    if api_key_from_env:
        st.success("Loaded from `.env` file ✅", icon="✅")
    else:
        st.error("Missing in `.env` file ⚠️\nPlease set `GEMINI_API_KEY=your_key` in `.env`", icon="⚠️")

    st.markdown("---")
    st.subheader("🤖 Model & Parameters")

    # Model Selection
    selected_model = st.selectbox(
        "Select Gemini Model",
        options=GeminiSummarizer.SUPPORTED_MODELS,
        index=0,
        help="gemini-2.5-flash is recommended for fast & high quality summaries."
    )

    # Summary Settings
    summary_style = st.selectbox(
        "Summary Mode",
        options=[
            "Executive Summary",
            "Detailed Technical Summary",
            "Actionable Bullet Points",
            "TL;DR Quick Overview"
        ],
        index=0
    )

    custom_prompt = st.text_area(
        "Custom Instructions (Optional)",
        placeholder="e.g. Focus on financial metrics, or emphasize research methodology...",
        height=90
    )

    st.markdown("---")

    # Quick Reset Button
    if st.button("🔄 Reset Session State", use_container_width=True):
        st.session_state["parsed_doc"] = None
        st.session_state["summary_output"] = None
        st.session_state["key_points_output"] = None
        st.session_state["analytics_output"] = None
        st.session_state["chat_history"] = []
        st.rerun()

    st.caption("Powered by Google Gemini & Streamlit")

# --- MAIN APP LAYOUT ---

# Header Banner
st.markdown("""
<div class="header-banner">
    <div>
        <span class="badge">🤖 Gemini AI Powered</span>
        <span class="badge">📄 PDF & TXT Parser</span>
        <span class="badge">⚡ Fast Intelligence</span>
    </div>
    <h1 class="header-title">Research & Document Summarization Agent</h1>
    <p class="header-subtitle">Extract key insights, generate executive summaries, and interact with your documents effortlessly.</p>
</div>
""", unsafe_allow_html=True)

# File Upload Widget
uploaded_file = st.file_uploader(
    "📤 Upload Document (PDF, TXT, or MD)",
    type=["pdf", "txt", "md"],
    help="Upload your research paper, report, article, or text file (max 20MB)."
)

# Process Uploaded File
if uploaded_file is not None:
    # Check if a new file was uploaded or changed
    if (st.session_state["parsed_doc"] is None or 
        st.session_state["parsed_doc"].get("file_name") != uploaded_file.name):
        with st.spinner(f"Parsing document '{uploaded_file.name}'..."):
            try:
                file_bytes = uploaded_file.read()
                parsed_data = parse_uploaded_document(uploaded_file.name, file_bytes)
                st.session_state["parsed_doc"] = parsed_data
                # Clear previous outputs for new document
                st.session_state["summary_output"] = None
                st.session_state["key_points_output"] = None
                st.session_state["analytics_output"] = None
                st.session_state["chat_history"] = []
                st.toast(f"Successfully loaded '{uploaded_file.name}'!", icon="🎉")
            except Exception as e:
                st.error(f"Error parsing document: {str(e)}")

# Display Tabs if Document Loaded
if st.session_state["parsed_doc"]:
    doc_data = st.session_state["parsed_doc"]
    stats = doc_data["stats"]
    text = doc_data["text"]
    clean_text = doc_data.get("clean_text", text)
    target_ai_text = clean_text if clean_text.strip() else text


    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Document Overview",
        "⚡ AI Summary & Key Points",
        "💬 Interactive Q&A",
        "📊 Analytical Insights"
    ])

    # --- TAB 1: OVERVIEW & STATS ---
    with tab1:
        st.subheader("📌 Document Metadata & Analytics")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stats['page_count']}</div>
                <div class="metric-label">Total Pages</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stats['word_count']:,}</div>
                <div class="metric-label">Word Count</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stats['char_count']:,}</div>
                <div class="metric-label">Characters</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">~{stats['read_time_minutes']} min</div>
                <div class="metric-label">Reading Time</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🔍 Extracted Text Preview")
        
        with st.expander("View Full Document Content", expanded=False):
            st.text_area("Full Document Text", value=text, height=350, disabled=True)

    # --- TAB 2: AI SUMMARY & KEY POINTS ---
    with tab2:
        st.subheader("✨ AI Intelligence Hub")

        if not api_key_from_env:
            st.warning("⚠️ `GEMINI_API_KEY` is not set in `.env`. Please add `GEMINI_API_KEY=your_key` to your `.env` file.")
        else:
            col_sum, col_pts = st.columns(2)

            with col_sum:
                st.markdown("### 📝 Executive Summary")
                if st.button("🚀 Generate Summary", type="primary", use_container_width=True):
                    with st.spinner(f"Generating '{summary_style}' using {selected_model}..."):
                        try:
                            summarizer = GeminiSummarizer(api_key=api_key_from_env, model_name=selected_model)
                            summary_res = summarizer.generate_summary(
                                target_ai_text,
                                summary_style=summary_style,
                                custom_instructions=custom_prompt
                            )
                            st.session_state["summary_output"] = summary_res
                        except Exception as e:
                            st.error(f"Failed to generate summary: {str(e)}")

                if st.session_state["summary_output"]:
                    st.markdown("---")
                    st.markdown(st.session_state["summary_output"])
                    st.download_button(
                        "📥 Download Summary (.md)",
                        data=st.session_state["summary_output"],
                        file_name=f"Summary_{doc_data['file_name']}.md",
                        mime="text/markdown"
                    )

            with col_pts:
                st.markdown("### 🔑 Key Takeaways & Highlights")
                if st.button("🌟 Extract Key Points", use_container_width=True):
                    with st.spinner("Extracting critical insights & key concepts..."):
                        try:
                            summarizer = GeminiSummarizer(api_key=api_key_from_env, model_name=selected_model)
                            key_pts_res = summarizer.extract_key_points(target_ai_text)
                            st.session_state["key_points_output"] = key_pts_res
                        except Exception as e:
                            st.error(f"Failed to extract key points: {str(e)}")

                if st.session_state["key_points_output"]:
                    st.markdown("---")
                    st.markdown(st.session_state["key_points_output"])
                    st.download_button(
                        "📥 Download Key Points (.md)",
                        data=st.session_state["key_points_output"],
                        file_name=f"Key_Points_{doc_data['file_name']}.md",
                        mime="text/markdown"
                    )

    # --- TAB 3: INTERACTIVE Q&A ---
    with tab3:
        st.subheader("💬 Ask Anything About Your Document")
        st.caption("Answers are strictly grounded in the content of your uploaded document.")

        if not api_key_from_env:
            st.warning("⚠️ `GEMINI_API_KEY` is not set in `.env`. Please add `GEMINI_API_KEY=your_key` to your `.env` file.")
        else:
            # Suggested Question Chips
            st.markdown("**Suggested Questions:**")
            sug_col1, sug_col2, sug_col3 = st.columns(3)
            suggested_q = None
            with sug_col1:
                if st.button("💡 What is the main conclusion?", use_container_width=True):
                    suggested_q = "What is the main conclusion of this document?"
            with sug_col2:
                if st.button("🎯 What methodology was used?", use_container_width=True):
                    suggested_q = "What methodology or key approach was used or discussed?"
            with sug_col3:
                if st.button("📌 Key recommendations?", use_container_width=True):
                    suggested_q = "What are the primary recommendations or action items?"

            # Display Chat History
            for message in st.session_state["chat_history"]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Process User Query
            user_query = st.chat_input("Ask a question about this document...")
            query_to_run = user_query or suggested_q

            if query_to_run:
                # Append user question
                st.session_state["chat_history"].append({"role": "user", "content": query_to_run})
                with st.chat_message("user"):
                    st.markdown(query_to_run)

                # Generate Answer
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing document context..."):
                        try:
                            summarizer = GeminiSummarizer(api_key=api_key_from_env, model_name=selected_model)
                            answer = summarizer.answer_question(
                                target_ai_text,
                                question=query_to_run,
                                chat_history=st.session_state["chat_history"][:-1]
                            )
                            st.markdown(answer)
                            st.session_state["chat_history"].append({"role": "assistant", "content": answer})
                        except Exception as e:
                            st.error(f"Error generating answer: {str(e)}")

            if st.session_state["chat_history"]:
                if st.button("🗑️ Clear Chat History"):
                    st.session_state["chat_history"] = []
                    st.rerun()

    # --- TAB 4: ANALYTICAL INSIGHTS ---
    with tab4:
        st.subheader("📊 Tone, Target Audience & Domain Breakdown")

        if not api_key_from_env:
            st.warning("⚠️ `GEMINI_API_KEY` is not set in `.env`. Please add `GEMINI_API_KEY=your_key` to your `.env` file.")
        else:
            if st.button("🔍 Analyze Document Intelligence", type="primary"):
                with st.spinner("Generating document analytics report..."):
                    try:
                        summarizer = GeminiSummarizer(api_key=api_key_from_env, model_name=selected_model)
                        analytics_res = summarizer.extract_insights(target_ai_text)
                        st.session_state["analytics_output"] = analytics_res
                    except Exception as e:
                        st.error(f"Error extracting document analytics: {str(e)}")

            if st.session_state["analytics_output"]:
                st.markdown("---")
                st.markdown(st.session_state["analytics_output"])

else:
    # Empty State Display
    st.info("👆 Please upload a PDF, TXT, or MD document above to begin analysis.")
    st.markdown("""
    ### 🎯 Key Features:
    - **Multi-Format Document Parsing**: Upload PDFs, text documents, or Markdown files.
    - **Custom AI Summarization**: Choose between Executive Summaries, Technical Breakdowns, or TL;DR overviews.
    - **Context-Grounded Q&A**: Ask targeted questions with answers constrained strictly to document text.
    - **Document Analytics**: Obtain metadata, word counts, reading duration, and tone evaluations.
    """)
