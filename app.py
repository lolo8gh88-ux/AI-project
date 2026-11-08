import os
import json
import re
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

st.set_page_config(
    page_title="CyberAgent AI",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# تنسيق بصري منظم وأنيق للتقارير والواجهة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        background-color: #131314;
        color: #E3E3E3;
        direction: rtl;
        text-align: right;
    }
    .main-header {
        font-size: 24px;
        font-weight: 700;
        color: #F1F1F1;
        margin-bottom: 4px;
        text-align: center;
    }
    .sub-title {
        font-size: 14px;
        color: #8E918F;
        margin-bottom: 24px;
        text-align: center;
    }
    .upload-box {
        background-color: #1E1F20;
        border: 1px solid #2E2F31;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }
    
    /* تنسيق بطاقة التقرير المنسقة */
    .report-card {
        background-color: #1E1F20;
        border: 1px solid #333538;
        border-radius: 10px;
        padding: 18px;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .report-title {
        font-size: 16px;
        font-weight: 700;
        color: #F1F1F1;
        border-bottom: 1px solid #2E2F31;
        padding-bottom: 8px;
        margin-bottom: 14px;
    }
    .report-row {
        margin-bottom: 8px;
        font-size: 14px;
    }
    .badge-danger {
        background-color: #4A1D1D;
        color: #F87171;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 600;
    }
    .badge-success {
        background-color: #163828;
        color: #4ADE80;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 600;
    }
    .reasons-list {
        background-color: #161718;
        border-radius: 6px;
        padding: 12px 18px;
        margin-top: 10px;
    }
    .reasons-list li {
        margin-bottom: 6px;
        color: #C4C7C5;
    }

    .stButton>button {
        background-color: #A8C7FA;
        color: #040E1B;
        border-radius: 20px;
        border: none;
        padding: 8px 16px;
        font-weight: 600;
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #7C9FDC;
        color: #040E1B;
    }
    .stTextInput>div>div>input {
        background-color: #1E1F20;
        color: #E3E3E3;
        border: 1px solid #444746;
        border-radius: 8px;
    }
    </style
