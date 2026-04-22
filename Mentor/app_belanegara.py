"""
Final Project – Chatbot Edukasi Bela Negara
Jalankan dengan:
    streamlit run app_belanegara.py
"""

import os
import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI


# CONFIG & STYLING 


st.set_page_config(
    page_title="Mentor Bela Negara",
    page_icon="🇮🇩",
    layout="wide"
)

# CSS
st.markdown(
    """
    <style>
    .main {
        background: radial-gradient(circle at top left, #1b2838 0, #000000 45%, #111827 100%);
        color: #e5e7eb;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .hero-box {
        padding: 1.2rem 1.6rem;
        border-radius: 1.2rem;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.4);
    }
    .metric-card {
        padding: 0.9rem 1rem;
        border-radius: 0.9rem;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(75, 85, 99, 0.7);
        text-align: center;
        font-size: 0.9rem;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #9ca3af;
    }
    .metric-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #facc15;
    }
    .topic-pill {
        border-radius: 999px;
        border: 1px solid rgba(148, 163, 184, 0.4);
        padding: 0.35rem 0.8rem;
        font-size: 0.8rem;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: rgba(15, 23, 42, 0.85);
        margin-bottom: 0.35rem;
        cursor: default;
    }
    .topic-dot {
        width: 7px;
        height: 7px;
        border-radius: 999px;
        background: #22c55e;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


#  SIDEBAR (API KEY) 


with st.sidebar:
    st.markdown("### 🔐 Konfigurasi")
    st.markdown(
        "Masukkan **Google API Key** dari [Google AI Studio](https://aistudio.google.com/) "
        "untuk mengaktifkan chatbot."
    )
    api_key_input = st.text_input("Google API Key", type="password", key="api_key_input")
    save_key = st.button("Simpan API Key")

    if save_key:
        if not api_key_input:
            st.error("API Key tidak boleh kosong.")
        else:
            st.session_state["GOOGLE_API_KEY"] = api_key_input
            st.success("API Key tersimpan di session. Silakan mulai chat di bawah. 😊")

    # Mode interaksi
    st.markdown("---")
    st.markdown("### 🎯 Mode Interaksi")
    mode = st.radio(
        "Pilih gaya chatbot:",
        ["Ngobrol Santai", "Belajar Konsep", "Mini Kuis Cepat"],
        key="mode_radio"
    )

    st.markdown("---")
    st.markdown("### ℹ️ Tentang Chatbot")
    st.caption(
        "Chatbot ini dirancang sebagai **Mentor Bela Negara** untuk membantu masyarakat, "
        "mahasiswa, dan prajurit memahami konsep bela negara, ancaman hibrida, peran TNI, "
        "serta kontribusi warga sipil di era digital."
    )

# Pastikan API key ada
if "GOOGLE_API_KEY" not in st.session_state:
    st.info("Masukkan dan simpan Google API Key di sidebar untuk memulai percakapan.")
    st.stop()

google_api_key = st.session_state["GOOGLE_API_KEY"]

# INISIALISASI LLM 

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=google_api_key,
)


# HERO SECTION UI


col_left, col_right = st.columns([2.3, 1.2])

with col_left:
    st.markdown(
        """
        <div class="hero-box">
            <h1 style="font-size:2.2rem; font-weight:800; margin-bottom:0.4rem;">
                Mentor Bela Negara 🇮🇩
            </h1>
            <p style="font-size:0.98rem; color:#e5e7eb; line-height:1.5;">
                Chatbot edukasi untuk memahami <b>Bela Negara</b> di era disrupsi digital, 
                ancaman siber, dan perang hibrida. Tanyakan apa saja seputar nilai, 
                kebijakan, ancaman, hingga peran generasi muda dalam menjaga kedaulatan.
            </p>
            <p style="font-size:0.9rem; color:#9ca3af; margin-top:0.4rem;">
                💡 Tip: kamu bisa minta penjelasan konsep, contoh kasus, simulasi skenario,
                atau minta dibuatkan mini-kuis untuk latihan.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_right:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">Fokus Utama</div>
                <div class="metric-value">Bela Negara</div>
                <div style="font-size:0.75rem; color:#9ca3af; margin-top:0.2rem;">
                    Nilai, ancaman, peran warga negara
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">Mode</div>
                <div class="metric-value">AI Mentor</div>
                <div style="font-size:0.75rem; color:#9ca3af; margin-top:0.2rem;">
                    Edukatif, reflektif, tetap ringan
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")
    st.markdown(
        """
        <div>
            <span class="topic-pill">
                <span class="topic-dot"></span> Nilai Dasar Bela Negara
            </span><br/>
            <span class="topic-pill">
                <span class="topic-dot"></span> Ancaman Siber & Disinformasi
            </span><br/>
            <span class="topic-pill">
                <span class="topic-dot"></span> Peran Mahasiswa & Profesional
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("")

# QUICK PROMPT BUTTONS 

st.markdown("#### 🚀 Mulai dari pertanyaan cepat")

qp_col1, qp_col2, qp_col3 = st.columns(3)

quick_prompt = None

with qp_col1:
    if st.button("Apa itu Bela Negara di era digital?"):
        quick_prompt = "Jelaskan konsep bela negara di era digital dan ancaman siber, pakai bahasa ringan."
with qp_col2:
    if st.button("Peran mahasiswa dalam Bela Negara 🎓"):
        quick_prompt = "Apa saja contoh konkret peran mahasiswa dalam bela negara di kampus dan dunia digital?"
with qp_col3:
    if st.button("Coba kuis cepat Bela Negara 📝"):
        quick_prompt = "Buatkan 5 soal kuis pilihan ganda tentang nilai-nilai bela negara, sertakan kunci jawabannya."

st.markdown("---")


# MESSAGE HISTORY 


def build_system_prompt(active_mode: str) -> str:
    """Bangun system prompt sesuai mode interaksi."""
    base = (
        "Kamu adalah 'Mentor Bela Negara', seorang pendidik dan praktisi pertahanan "
        "yang memahami konteks Indonesia, UUD 1945, Pancasila, doktrin TNI, serta tantangan "
        "keamanan modern seperti perang informasi, serangan siber, dan ancaman hibrida. "
        "Gunakan bahasa Indonesia yang hangat, mudah dipahami, dan tetap bernas."
    )

    if active_mode == "Ngobrol Santai":
        extra = (
            "Gaya bicara santai, kadang boleh pakai analogi sehari-hari, tetapi tetap sopan "
            "dan menjunjung nilai-nilai kebangsaan. Jawaban 3–6 paragraf singkat."
        )
    elif active_mode == "Belajar Konsep":
        extra = (
            "Fokus pada edukasi. Susun jawaban dengan struktur yang rapi (misalnya poin-poin, "
            "langkah-langkah, atau subjudul kecil). Sertakan contoh kasus aktual di Indonesia "
            "jika relevan. Bantu pengguna benar-benar memahami konsep."
        )
    else:  # Mini Kuis Cepat
        extra = (
            "Fokus pada bentuk kuis, refleksi, atau latihan. Buat soal, studi kasus singkat, "
            "atau pertanyaan reflektif. Setelah pengguna menjawab, kamu bisa memberikan umpan balik."
        )

    closing = (
        "Jika pengguna bingung, ajak mereka untuk bertanya lebih spesifik. "
        "Jangan jawab hal di luar etika, rahasia militer, atau informasi terlarang."
    )
    return f"{base} {extra} {closing}"


if "messages_history" not in st.session_state:
    st.session_state["messages_history"] = [
        SystemMessage(build_system_prompt(mode))
    ]
messages_history = st.session_state["messages_history"]

# Tampilkan history (kecuali SystemMessage)
for message in messages_history:
    if isinstance(message, SystemMessage):
        continue
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)


# INPUT USER + LLM CALL  

# Chat input manual
chat_input = st.chat_input("Tulis pertanyaan atau topik seputar Bela Negara...")

user_prompt = None
if chat_input:
    user_prompt = chat_input
elif quick_prompt:
    user_prompt = quick_prompt

if not user_prompt:
    st.stop()

# Tampilkan prompt terbaru
with st.chat_message("user"):
    st.markdown(user_prompt)
messages_history.append(HumanMessage(user_prompt))

# Panggil LLM
with st.chat_message("assistant"):
    with st.spinner("Memikirkan jawaban terbaik untuk Bela Negara…"):
        response = llm.invoke(messages_history)
        messages_history.append(response)
        st.markdown(response.content)
