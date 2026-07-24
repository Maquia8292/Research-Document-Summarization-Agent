# 📚 Research & Document Summarization Agent

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini API](https://img.shields.io/badge/Google%20Gemini-API-8E44AD.svg)](https://aistudio.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI-powered document intelligence agent built with **Python**, **Google Gemini API**, and **Streamlit**. Upload PDF, TXT, or Markdown documents to extract structured text, generate customizable summaries, extract key takeaways, analyze document tone and complexity, and interact with your documents using grounded Q&A.

---

## 🌟 Key Features

- 📄 **Multi-Format Document Parsing**: Full text extraction and metadata computation for PDF and TXT/Markdown files.
- ⚡ **AI Summarization Engine**: Generate customizable summaries including *Executive Summary*, *Detailed Technical Summary*, *Actionable Bullet Points*, or *TL;DR Quick Overview*.
- 🔑 **Key Takeaways & Concept Extraction**: Automatically isolate top takeaways, core technical terminology, and domain keywords.
- 💬 **Interactive Grounded Q&A Chat**: Ask questions directly about the document with responses constrained to extracted content and context memory.
- 📊 **Document Analytics & Insights**: Evaluate document tone, complexity level, target audience, and subject matter breakdown.
- 📥 **Export Capabilities**: One-click download of generated summaries and key point reports in Markdown (`.md`) format.
- 🎨 **Modern Glassmorphic UI**: Beautiful, responsive interface with custom CSS styling and dark-mode compatibility.

---

## 🏗️ Architecture & Project Structure

```
Research-Document-Summarizer/
├── app.py                   # Streamlit UI, state management, tab routing & styling
├── document_parser.py       # PDF & TXT text extraction, metadata, and document stats
├── summarizer.py            # Gemini API integration wrapper (Summaries, Key Points, Q&A, Insights)
├── requirements.txt         # Project dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Excluded files and secret credentials
└── README.md                # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites

Ensure you have Python 3.9+ installed on your system.

### 2. Clone Repository & Navigate

```bash
git clone https://github.com/0ANSHKUMARSINGH4/Research-Document-Summarization-Agent.git
cd Research-Document-Summarization-Agent
```

### 3. Set Up Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API Key

Option A: Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Option B: Enter your Gemini API key directly in the application sidebar when running.

### 6. Launch Application

```bash
streamlit run app.py
```

The web app will open automatically in your browser at `http://localhost:8501`.

---

## 🧪 Usage Workflow

1. **Upload Document**: Drag & drop your PDF or TXT file into the file uploader.
2. **Review Metadata**: Inspect page count, word count, character count, and estimated reading time.
3. **Generate Summary**: Select your desired summary mode (Executive, Technical, Bullet Points, TL;DR) and click **Generate Summary**.
4. **Extract Key Points**: Click **Extract Key Points** to generate core takeaways and domain tags.
5. **Interactive Q&A**: Navigate to the Q&A tab to ask questions or click suggested question chips.
6. **Download Reports**: Export your summaries and key point lists using the download buttons.

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more details.
