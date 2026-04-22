"""
Final Project – Chatbot Edukasi Keamanan Informasi (Pusdatin Kemhan)
Jalankan dengan:
    streamlit run app_infosec_pusdatin.py
"""

import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI


# =========================
# CONFIG & STYLING
# =========================

st.set_page_config(
    page_title="Mentor Keamanan Informasi Pusdatin",
    page_icon="🛡️",
    layout="wide"
)

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


# =========================
# SIDEBAR (API KEY + MODE)
# =========================

with st.sidebar:
    st.markdown("### 🔐 Konfigurasi")
    st.markdown(
        "Masukkan **Google API Key** dari Google AI Studio untuk mengaktifkan chatbot.\n\n"
        "Catatan: API key hanya disimpan di **session** (sementara) pada browser."
    )

    api_key_input = st.text_input("Google API Key", type="password", key="api_key_input")
    save_key = st.button("Simpan API Key")

    if save_key:
        if not api_key_input:
            st.error("API Key tidak boleh kosong.")
        else:
            st.session_state["GOOGLE_API_KEY"] = api_key_input
            st.success("API Key tersimpan di session. Silakan mulai chat di bawah. 😊")

    st.markdown("---")
    st.markdown("### 🎯 Mode Interaksi")
    mode = st.radio(
        "Pilih gaya chatbot:",
        ["Ngobrol Santai", "Belajar Konsep", "Simulasi & Mini Kuis"],
        key="mode_radio"
    )

    st.markdown("---")
    st.markdown("### ℹ️ Tentang Chatbot")
    st.caption(
        "Chatbot ini adalah **mentor edukasi keamanan informasi** untuk pegawai Pusdatin Kemhan. "
        "Fokus pada *security awareness*, tata kelola informasi, praktik aman sehari-hari, "
        "dan respons insiden. Tidak menggantikan SOP resmi/briefing internal."
    )

# Pastikan API key ada
if "GOOGLE_API_KEY" not in st.session_state:
    st.info("Masukkan dan simpan Google API Key di sidebar untuk memulai percakapan.")
    st.stop()

google_api_key = st.session_state["GOOGLE_API_KEY"]


# =========================
# INISIALISASI LLM
# =========================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=google_api_key,
)


# =========================
# HERO SECTION UI
# =========================

col_left, col_right = st.columns([2.3, 1.2])

with col_left:
    st.markdown(
        """
        <div class="hero-box">
            <h1 style="font-size:2.2rem; font-weight:800; margin-bottom:0.4rem;">
                Mentor Keamanan Informasi Pusdatin 🛡️
            </h1>
            <p style="font-size:0.98rem; color:#e5e7eb; line-height:1.5;">
                Chatbot edukasi untuk membantu pegawai memahami praktik aman: <b>klasifikasi informasi</b>,
                <b>anti-phishing</b>, <b>password & MFA</b>, <b>keamanan perangkat</b>, serta
                <b>respons insiden</b>. Tanya apa saja seputar kebiasaan aman bekerja dan risiko umum.
            </p>
            <p style="font-size:0.9rem; color:#9ca3af; margin-top:0.4rem;">
                💡 Tip: kamu bisa minta checklist harian, contoh skenario, latihan identifikasi phishing,
                atau mini-kuis untuk menguji pemahaman.
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
                <div class="metric-value">InfoSec</div>
                <div style="font-size:0.75rem; color:#9ca3af; margin-top:0.2rem;">
                    Awareness & kebiasaan aman
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
                    Edukatif, praktis, aman
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
                <span class="topic-dot"></span> Klasifikasi & Penanganan Informasi
            </span><br/>
            <span class="topic-pill">
                <span class="topic-dot"></span> Anti-Phishing & Social Engineering
            </span><br/>
            <span class="topic-pill">
                <span class="topic-dot"></span> Respons Insiden & Pelaporan
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("")


# =========================
# QUICK PROMPT BUTTONS
# =========================

st.markdown("#### 🚀 Mulai dari pertanyaan cepat")

qp_col1, qp_col2, qp_col3 = st.columns(3)
quick_prompt = None

with qp_col1:
    if st.button("Cara mengenali phishing & hoaks internal"):
        quick_prompt = (
            "Berikan panduan praktis mengenali email/WA phishing dan social engineering "
            "yang menyasar pegawai, beserta contoh red flag yang umum."
        )
with qp_col2:
    if st.button("Klasifikasi informasi & cara berbagi aman"):
        quick_prompt = (
            "Jelaskan konsep klasifikasi informasi (mis. publik/internal/rahasia) dan "
            "prinsip berbagi data yang aman di lingkungan kerja."
        )
with qp_col3:
    if st.button("Simulasi insiden: akun dicurigai diambil alih"):
        quick_prompt = (
            "Buat simulasi singkat jika ada indikasi akun email kerja diambil alih. "
            "Berikan langkah respons aman tingkat pengguna (bukan langkah hacking), "
            "serta apa yang harus dilaporkan."
        )

st.markdown("---")


# =========================
# SYSTEM PROMPT (MODE-BASED)
# =========================

def build_system_prompt(active_mode: str) -> str:
    base = (
        "Kamu adalah 'Mentor Keamanan Informasi Pusdatin', fasilitator edukasi keamanan informasi "
        "untuk pegawai Pusat Data dan Informasi Kementerian Pertahanan. Fokusmu adalah "
        "security awareness, perilaku aman, dan tata kelola informasi sehari-hari.\n\n"
        "PRINSIP JAWABAN:\n"
        "- Gunakan Bahasa Indonesia yang jelas, tegas, dan mudah dipahami.\n"
        "- Utamakan praktik aman: phishing/social engineering, kata sandi & MFA, keamanan perangkat, "
        "penanganan data, keamanan komunikasi, etika digital, dan pelaporan insiden.\n"
        "- Berikan contoh situasi kerja yang realistis tanpa menyebut detail internal sensitif.\n"
        "- Jika pengguna meminta SOP internal, konfigurasi sistem spesifik, arsitektur, kredensial, "
        "atau informasi rahasia: tolak dengan sopan dan arahkan ke kanal resmi/atasan/Tim Keamanan.\n"
        "- Jangan memberikan instruksi teknis yang dapat disalahgunakan (mis. eksploitasi, bypass, "
        "mencuri akses). Jika ada pertanyaan ofensif, alihkan ke pencegahan & mitigasi.\n"
        "- Jika ada insiden, sarankan langkah aman tingkat pengguna dan segera eskalasi ke tim terkait.\n\n"
        "OUTPUT STYLE:\n"
        "- Ringkas, actionable, dan berorientasi checklist bila memungkinkan.\n"
    )

    if active_mode == "Ngobrol Santai":
        extra = (
            "Gaya santai tapi tetap profesional. Pakai analogi seperlunya. "
            "Jawaban 3–7 paragraf pendek atau poin-poin singkat."
        )
    elif active_mode == "Belajar Konsep":
        extra = (
            "Gaya mengajar terstruktur: definisi → alasan penting → contoh → do & don't → ringkasan. "
            "Gunakan subjudul kecil dan bullet points."
        )
    else:  # Simulasi & Mini Kuis
        extra = (
            "Fokus latihan: berikan skenario, pertanyaan reflektif/kuis (pilihan ganda/benar-salah), "
            "lalu minta pengguna menjawab. Setelah itu beri umpan balik dan tips."
        )

    closing = (
        "\n\nJika pertanyaan kurang jelas, ajukan 1–2 pertanyaan klarifikasi singkat. "
        "Tetap patuhi kebijakan keamanan dan kerahasiaan."
    )
    return f"{base}{extra}{closing}"


# =========================
# MESSAGE HISTORY
# =========================

if "messages_history" not in st.session_state:
    st.session_state["messages_history"] = [SystemMessage(build_system_prompt(mode))]

# Jika mode berubah, update system prompt di awal history agar konsisten
# (cara sederhana: ganti elemen pertama jika itu SystemMessage)
if isinstance(st.session_state["messages_history"][0], SystemMessage):
    st.session_state["messages_history"][0] = SystemMessage(build_system_prompt(mode))

messages_history = st.session_state["messages_history"]

# Tampilkan history (kecuali SystemMessage)
for message in messages_history:
    if isinstance(message, SystemMessage):
        continue
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)


# =========================
# INPUT USER + LLM CALL
# =========================

chat_input = st.chat_input("Tulis pertanyaan seputar keamanan informasi di lingkungan kerja...")

user_prompt = None
if chat_input:
    user_prompt = chat_input
elif quick_prompt:
    user_prompt = quick_prompt

if not user_prompt:
    st.stop()

with st.chat_message("user"):
    st.markdown(user_prompt)
messages_history.append(HumanMessage(user_prompt))

with st.chat_message("assistant"):
    with st.spinner("Menyusun jawaban edukasi keamanan informasi…"):
        response = llm.invoke(messages_history)
        messages_history.append(response)
        st.markdown(response.content)