"""
GARDA - Sentra-Cyber
Versi deploy-ready untuk Streamlit Community Cloud.

Jalankan lokal:
    streamlit run app_garda_sentra_cyber.py
"""

from pathlib import Path
import base64

import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="GARDA - Sentra-Cyber",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "logo_kemhan.png"
BANNER_PATH = BASE_DIR / "banner_sentra_cyber.png"


# =========================================================
# HELPERS
# =========================================================
def image_to_base64(image_path: Path) -> str:
    if not image_path.exists():
        return ""
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")


def get_api_key() -> str:
    return st.secrets.get("GOOGLE_API_KEY", "")


def get_llm(api_key: str):
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=api_key,
    )


def build_system_prompt(active_mode: str) -> str:
    base = (
        "Kamu adalah GARDA, asisten edukasi keamanan informasi dengan nama sistem Sentra-Cyber "
        "untuk pegawai Pusat Data dan Informasi Kementerian Pertahanan. "
        "Fokus pada security awareness, perilaku aman, klasifikasi informasi, anti-phishing, "
        "password dan MFA, keamanan perangkat, komunikasi kerja, etika digital, "
        "dan respons insiden tingkat pengguna.\n\n"
        "ATURAN:\n"
        "- Gunakan Bahasa Indonesia yang jelas, rapi, dan mudah dipahami.\n"
        "- Perkenalkan diri sebagai GARDA bila relevan.\n"
        "- Utamakan edukasi, mitigasi, pencegahan, dan pelaporan aman.\n"
        "- Hindari memberi instruksi ofensif, eksploitasi, bypass keamanan, pencurian akses, atau hal yang dapat disalahgunakan.\n"
        "- Jika pengguna meminta konfigurasi internal, kredensial, arsitektur sensitif, atau SOP rahasia, tolak dengan sopan dan arahkan ke jalur resmi.\n"
        "- Untuk insiden, sarankan langkah aman tingkat pengguna dan eskalasi ke tim terkait.\n"
        "- Bila relevan, gunakan checklist, contoh realistis, dan ringkasan langkah.\n"
    )

    if active_mode == "Ngobrol Santai":
        style = "Gunakan nada santai-profesional, sederhana, dan langsung ke inti."
    elif active_mode == "Belajar Konsep":
        style = "Jawaban terstruktur: definisi, alasan penting, contoh, do and don't, dan ringkasan."
    else:
        style = "Gunakan format simulasi atau mini kuis. Sajikan skenario singkat, pertanyaan, lalu beri penjelasan singkat."

    return base + "\nGAYA JAWABAN: " + style


def start_or_update_system_prompt(mode: str):
    system_prompt = SystemMessage(content=build_system_prompt(mode))
    if "messages_history" not in st.session_state:
        st.session_state["messages_history"] = [system_prompt]
    elif not st.session_state["messages_history"]:
        st.session_state["messages_history"] = [system_prompt]
    elif isinstance(st.session_state["messages_history"][0], SystemMessage):
        st.session_state["messages_history"][0] = system_prompt
    else:
        st.session_state["messages_history"].insert(0, system_prompt)


def risk_level_from_answers(
    suspicious_link: bool,
    urgent_tone: bool,
    asks_credentials: bool,
    unknown_sender: bool,
):
    score = sum([suspicious_link, urgent_tone, asks_credentials, unknown_sender])
    if score >= 3:
        return "Tinggi", "Jangan klik, jangan balas, dokumentasikan, dan laporkan segera."
    if score == 2:
        return "Sedang", "Tahan tindakan, verifikasi lewat kanal resmi, lalu laporkan bila perlu."
    return "Rendah", "Tetap hati-hati dan lakukan verifikasi sebelum bertindak."


def badge(text: str):
    st.markdown(
        f'<span class="garda-badge">{text}</span>',
        unsafe_allow_html=True,
    )


# =========================================================
# SESSION STATE
# =========================================================
if "messages_history" not in st.session_state:
    st.session_state["messages_history"] = []
if "quiz_index" not in st.session_state:
    st.session_state["quiz_index"] = 0
if "quiz_score" not in st.session_state:
    st.session_state["quiz_score"] = 0
if "quiz_answered" not in st.session_state:
    st.session_state["quiz_answered"] = {}
if "chat_started" not in st.session_state:
    st.session_state["chat_started"] = False


# =========================================================
# ASSET
# =========================================================
logo_b64 = image_to_base64(LOGO_PATH)
banner_b64 = image_to_base64(BANNER_PATH)


# =========================================================
# QUIZ DATA
# =========================================================
QUIZ_DATA = [
    {
        "question": "Kamu menerima email dari alamat yang mirip domain resmi instansi dan diminta login segera karena akun akan diblokir. Apa tanda paling kuat bahwa ini patut dicurigai?",
        "options": [
            "Ada urgensi berlebihan dan domain pengirim mirip tapi tidak persis sama",
            "Email menggunakan salam formal",
            "Pesan dikirim pada jam kerja",
            "Ada logo instansi di bagian atas",
        ],
        "correct": 0,
        "explain": "Red flag utama adalah domain yang mirip tetapi tidak sama, ditambah tekanan waktu agar korban bertindak tanpa verifikasi.",
    },
    {
        "question": "Jika laptop kerja hilang di perjalanan dinas, langkah pertama yang paling tepat adalah...",
        "options": [
            "Menunggu sampai kembali ke kantor",
            "Segera melapor ke atasan atau tim TI/keamanan dan mengganti kredensial terkait",
            "Membeli laptop baru lalu lanjut bekerja",
            "Menghapus riwayat chat pribadi saja",
        ],
        "correct": 1,
        "explain": "Respon awal harus cepat: laporkan, amankan akun, dan eskalasi agar risiko penyalahgunaan dapat diminimalkan.",
    },
    {
        "question": "Mana praktik berbagi file yang paling aman untuk dokumen kerja internal?",
        "options": [
            "Mengirim file ke email pribadi agar mudah dibuka dari rumah",
            "Mengunggah ke platform resmi yang memiliki kontrol akses sesuai kebutuhan",
            "Mengirim ke grup umum tanpa pembatasan",
            "Menyimpan di flashdisk tanpa perlindungan apa pun",
        ],
        "correct": 1,
        "explain": "Dokumen internal sebaiknya dibagi lewat kanal resmi dengan pembatasan akses sesuai prinsip need-to-know.",
    },
]


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --bg: #f4f8fc;
        --surface: #ffffff;
        --surface-2: #f8fbff;
        --line: #d6e2ee;
        --line-soft: #e7eef6;
        --text: #0f2740;
        --muted: #5c7288;
        --primary: #0f4c81;
        --primary-2: #1d4ed8;
        --soft-blue: #e9f3ff;
        --success-bg: #eaf8ef;
        --warn-bg: #fff6db;
        --danger-bg: #fdecec;
        --shadow: 0 10px 30px rgba(15, 39, 64, 0.06);
        --radius: 20px;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(59,130,246,0.08), transparent 20%),
            radial-gradient(circle at top right, rgba(20,184,166,0.08), transparent 18%),
            linear-gradient(180deg, #f8fbff 0%, #f2f7fc 100%);
        color: var(--text);
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    html, body, p, div, span, label, li {
        color: var(--text);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #eef5fb 0%, #e8f1fa 100%) !important;
        border-right: 1px solid var(--line);
    }

    section[data-testid="stSidebar"] * {
        color: var(--text) !important;
    }

    section[data-testid="stSidebar"] .stCaption {
        color: var(--muted) !important;
    }

    .stButton > button {
        background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.18);
    }

    .stButton > button:hover {
        background: linear-gradient(180deg, #1d4ed8 0%, #1e40af 100%) !important;
        color: white !important;
    }

    .stRadio label, .stCheckbox label {
        color: var(--text) !important;
    }

    div[data-testid="metric-container"] {
        background: var(--surface) !important;
        border: 1px solid var(--line) !important;
        border-radius: 16px !important;
        padding: 12px !important;
        box-shadow: var(--shadow);
    }

    div[data-testid="metric-container"] * {
        color: var(--text) !important;
    }

    div[data-testid="stTabs"] button {
        font-weight: 700 !important;
        color: var(--text) !important;
    }

    div[data-testid="stChatMessage"] {
        background: #ffffff !important;
        border: 1px solid var(--line-soft) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 20px rgba(15, 39, 64, 0.04);
    }

    div[data-testid="stChatMessage"] * {
        color: var(--text) !important;
    }

    .stInfo {
        background: #eaf4ff !important;
        color: #0f4c81 !important;
    }

    .stSuccess {
        background: var(--success-bg) !important;
        color: #166534 !important;
    }

    .stError {
        background: var(--danger-bg) !important;
        color: #991b1b !important;
    }

    .garda-chip {
        display: inline-block;
        padding: 0.38rem 0.85rem;
        border-radius: 999px;
        background: var(--soft-blue);
        border: 1px solid #cfe3fb;
        color: var(--primary);
        font-weight: 700;
        font-size: 0.85rem;
        margin-top: 0.15rem;
    }

    .garda-badge {
        display: inline-block;
        padding: 0.42rem 0.85rem;
        border-radius: 999px;
        background: #ffffff;
        border: 1px solid #d6e4f2;
        color: var(--text);
        font-weight: 600;
        font-size: 0.82rem;
        margin: 0 0.4rem 0.45rem 0;
    }

    .section-soft {
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        border: 1px solid var(--line);
        border-radius: var(--radius);
        padding: 1.25rem;
        box-shadow: var(--shadow);
    }

    .hero-title {
        font-size: 2.35rem;
        font-weight: 800;
        line-height: 1.05;
        color: #0d2f4f;
        margin: 0;
    }

    .hero-text {
        color: #29455f !important;
        line-height: 1.75;
        font-size: 1rem;
        margin-top: 0.8rem;
    }

    .muted-text {
        color: var(--muted) !important;
        line-height: 1.7;
    }

    .mini-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--text);
        margin-bottom: 0.45rem;
    }

    .info-list {
        margin-top: 0.4rem;
        color: #29455f !important;
        line-height: 1.95;
    }

    .metric-kicker {
        font-size: 0.82rem;
        color: var(--muted) !important;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .metric-big {
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--text);
        margin-bottom: 0.2rem;
    }

    .metric-desc {
        color: var(--muted) !important;
        font-size: 0.82rem;
        line-height: 1.5;
    }

    .warn-box {
        margin-top: 1rem;
        padding: 0.95rem 1rem;
        border-left: 4px solid #d97706;
        background: var(--warn-bg);
        border-radius: 14px;
        color: #7c4a03 !important;
        line-height: 1.65;
    }

    .footer-note {
        margin-top: 1rem;
        text-align: center;
        color: var(--muted) !important;
        font-size: 0.84rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=95)

    st.markdown("## GARDA")
    st.caption("Sistem edukasi keamanan informasi Sentra-Cyber")

    st.markdown("---")
    st.markdown("### 🎯 Mode Interaksi")
    mode = st.radio(
        "Pilih gaya chatbot:",
        ["Ngobrol Santai", "Belajar Konsep", "Simulasi & Mini Kuis"],
        key="mode_radio",
    )

    st.markdown("---")
    st.markdown("### 📌 Fokus Edukasi")
    st.caption("• Phishing dan social engineering")
    st.caption("• Klasifikasi informasi")
    st.caption("• Password, MFA, dan keamanan akun")
    st.caption("• Respons insiden tingkat pengguna")

    st.markdown("---")
    st.markdown("### 🧭 Status Sesi")
    msg_count = max(len(st.session_state["messages_history"]) - 1, 0)
    st.metric("Percakapan", msg_count)
    st.metric("Skor mini kuis", st.session_state["quiz_score"])

    if st.button("Reset chat", use_container_width=True):
        st.session_state["messages_history"] = []
        st.session_state["chat_started"] = False
        st.rerun()


api_key = get_api_key()
if not api_key:
    st.error("Secret GOOGLE_API_KEY belum ditemukan. Tambahkan di Settings → Secrets pada Streamlit Cloud.")
    st.stop()

start_or_update_system_prompt(mode)
llm = get_llm(api_key)


# =========================================================
# BANNER
# =========================================================
if BANNER_PATH.exists():
    st.image(str(BANNER_PATH), use_container_width=True)
else:
    st.info("Banner belum ditemukan. Simpan file banner di folder yang sama dengan nama: banner_sentra_cyber.png")

st.markdown("")


# =========================================================
# TOP SECTION
# =========================================================
left, right = st.columns([1.8, 1.0], gap="large")

with left:
    with st.container(border=True):
        top1, top2 = st.columns([0.12, 0.88], gap="medium")

        with top1:
            if LOGO_PATH.exists():
                st.image(str(LOGO_PATH), width=78)

        with top2:
            st.markdown(
                """
                <div class="hero-title">GARDA 🛡️</div>
                <div class="garda-chip">Sistem: Sentra-Cyber</div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div class="hero-text">
                Pendamping belajar keamanan informasi untuk pegawai. Fokus pada
                <b>anti-phishing</b>, <b>klasifikasi informasi</b>,
                <b>kebiasaan kerja aman</b>, dan <b>respons insiden</b>
                dalam konteks penggunaan sehari-hari.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="muted-text">
                GARDA membantu edukasi keamanan informasi secara praktis, ringan,
                dan mudah dipahami untuk mendukung budaya kerja yang aman di lingkungan Pusdatin.
            </div>
            """,
            unsafe_allow_html=True,
        )

        b1, b2, b3, b4 = st.columns(4)
        with b1:
            badge("🔎 Anti-Phishing")
        with b2:
            badge("🔐 Password & MFA")
        with b3:
            badge("📂 Klasifikasi Informasi")
        with b4:
            badge("🚨 Respons Insiden")

        st.markdown(
            """
            <div class="warn-box">
                <b>Catatan:</b> GARDA digunakan untuk edukasi dan awareness.
                Untuk insiden nyata, tetap gunakan jalur pelaporan resmi dan koordinasi dengan tim terkait.
            </div>
            """,
            unsafe_allow_html=True,
        )

with right:
    m1, m2 = st.columns(2)

    with m1:
        st.markdown(
            """
            <div class="section-soft">
                <div class="metric-kicker">Nama Sistem</div>
                <div class="metric-big">Sentra-Cyber</div>
                <div class="metric-desc">Pusat edukasi awareness dan praktik aman.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m2:
        st.markdown(
            f"""
            <div class="section-soft">
                <div class="metric-kicker">Mode Aktif</div>
                <div class="metric-big">{mode}</div>
                <div class="metric-desc">Respons mengikuti gaya interaksi yang dipilih.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")

    st.markdown(
        """
        <div class="section-soft">
            <div class="mini-title">🧠 Ide Interaktif</div>
            <div class="muted-text">Coba salah satu jalur berikut:</div>
            <div class="info-list">
                • Analisis email atau WA yang mencurigakan<br>
                • Minta checklist kebiasaan aman harian<br>
                • Simulasikan akun dicurigai diambil alih<br>
                • Kerjakan mini kuis awareness
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("")


# =========================================================
# TABS
# =========================================================
chat_tab, simulator_tab, checklist_tab, quiz_tab = st.tabs(
    ["💬 Chat GARDA", "🧪 Cek Risiko", "📋 Checklist", "🎯 Mini Kuis"]
)


# =========================================================
# CHAT TAB
# =========================================================
with chat_tab:
    st.markdown("#### Mulai dari pertanyaan cepat")

    qp1, qp2, qp3, qp4 = st.columns(4)
    quick_prompt = None

    with qp1:
        if st.button("Kenali phishing", use_container_width=True):
            quick_prompt = (
                "Perkenalkan diri sebagai GARDA lalu berikan panduan praktis mengenali "
                "email atau WA phishing yang menyasar pegawai, lengkap dengan red flag yang umum."
            )

    with qp2:
        if st.button("Berbagi file aman", use_container_width=True):
            quick_prompt = (
                "Perkenalkan diri sebagai GARDA lalu jelaskan cara berbagi dokumen kerja "
                "dengan aman berdasarkan prinsip klasifikasi informasi dan need-to-know."
            )

    with qp3:
        if st.button("Akun dicurigai diambil alih", use_container_width=True):
            quick_prompt = (
                "Perkenalkan diri sebagai GARDA lalu buat simulasi singkat jika akun email kerja "
                "dicurigai diambil alih, termasuk langkah aman tingkat pengguna dan pelaporan."
            )

    with qp4:
        if st.button("Checklist harian", use_container_width=True):
            quick_prompt = (
                "Perkenalkan diri sebagai GARDA lalu buat checklist harian keamanan informasi "
                "untuk pegawai kantor dalam format yang singkat dan praktis."
            )

    st.markdown("---")

    for message in st.session_state["messages_history"]:
        if isinstance(message, SystemMessage):
            continue

        role = "user" if isinstance(message, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(message.content)

    user_prompt = st.chat_input("Tulis pertanyaan seputar keamanan informasi di lingkungan kerja...")
    final_prompt = user_prompt or quick_prompt

    if final_prompt:
        st.session_state["chat_started"] = True

        with st.chat_message("user"):
            st.markdown(final_prompt)

        st.session_state["messages_history"].append(HumanMessage(content=final_prompt))

        with st.chat_message("assistant"):
            with st.spinner("GARDA sedang menyusun jawaban..."):
                try:
                    response = llm.invoke(st.session_state["messages_history"])
                    if not isinstance(response, AIMessage):
                        response = AIMessage(content=str(response))

                    st.session_state["messages_history"].append(response)
                    st.markdown(response.content)

                except Exception as e:
                    err = str(e)

                    if "429" in err or "ResourceExhausted" in err or "quota" in err.lower():
                        st.info(
                            "Kuota API sedang mencapai batas. "
                            "Tunggu sekitar 20–30 detik lalu coba lagi. "
                            "Jika masih muncul, cek limit aktif di Google AI Studio atau billing project Anda."
                        )
                    else:
                        st.error(f"Terjadi kesalahan: {err}")


# =========================================================
# RISK TAB
# =========================================================
with simulator_tab:
    st.markdown("#### Cek cepat risiko phishing atau social engineering")
    st.caption("Tandai gejala yang muncul pada email, chat, atau pesan yang kamu terima.")

    a1, a2 = st.columns(2)

    with a1:
        suspicious_link = st.checkbox("Ada tautan atau lampiran yang tidak biasa")
        urgent_tone = st.checkbox("Nada pesan mendesak, mengancam, atau terlalu menekan")

    with a2:
        asks_credentials = st.checkbox("Meminta password, OTP, kode MFA, atau data sensitif")
        unknown_sender = st.checkbox("Pengirim tidak dikenal atau domainnya mencurigakan")

    if st.button("Analisis risiko", type="primary"):
        level, advice = risk_level_from_answers(
            suspicious_link,
            urgent_tone,
            asks_credentials,
            unknown_sender,
        )

        c1, c2 = st.columns([1, 2])

        with c1:
            st.metric("Level Risiko", level)

        with c2:
            st.success(advice)
            st.markdown(
                "**Langkah aman berikutnya:** verifikasi lewat kanal resmi, jangan klik tautan sembarang, simpan bukti seperlunya, dan laporkan bila indikasinya kuat."
            )

    st.markdown("---")
    st.markdown("#### Skenario cepat")

    scenario = st.selectbox(
        "Pilih skenario",
        [
            "Email hadiah atau undian",
            "WA mengaku atasan minta transfer atau data",
            "Pop-up reset password mendadak",
            "Permintaan file internal dari pihak luar",
        ],
    )

    scenario_map = {
        "Email hadiah atau undian": "Waspadai janji hadiah, urgensi, dan permintaan klik. Verifikasi sumbernya, jangan masukkan kredensial, dan cek domain pengirim.",
        "WA mengaku atasan minta transfer atau data": "Jangan langsung patuh. Verifikasi identitas lewat nomor resmi atau panggilan balik. Waspadai tekanan waktu dan permintaan di luar prosedur.",
        "Pop-up reset password mendadak": "Tutup pop-up bila mencurigakan. Akses portal resmi secara manual lewat alamat yang benar, bukan dari tautan yang muncul tiba-tiba.",
        "Permintaan file internal dari pihak luar": "Periksa klasifikasi dokumen dan kewenangan penerima. Gunakan prinsip need-to-know dan eskalasi bila ragu.",
    }

    st.info(scenario_map[scenario])


# =========================================================
# CHECKLIST TAB
# =========================================================
with checklist_tab:
    st.markdown("#### Checklist praktik aman harian")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Sebelum mulai kerja**")
        st.checkbox("Perangkat terkunci dengan password/PIN yang kuat", key="cl1")
        st.checkbox("MFA aktif pada akun penting", key="cl2")
        st.checkbox("Jaringan yang digunakan aman dan terpercaya", key="cl3")
        st.checkbox("Aplikasi inti sudah diperbarui", key="cl4")

        st.markdown("**Saat bekerja**")
        st.checkbox("Memeriksa alamat pengirim sebelum membuka link/lampiran", key="cl5")
        st.checkbox("Tidak membagikan data melebihi kebutuhan", key="cl6")
        st.checkbox("Menggunakan kanal resmi untuk berbagi file", key="cl7")
        st.checkbox("Mengunci layar saat meninggalkan meja", key="cl8")

    with col_b:
        st.markdown("**Saat menerima pesan mencurigakan**")
        st.checkbox("Tidak panik dan tidak terburu-buru merespons", key="cl9")
        st.checkbox("Melakukan verifikasi melalui kanal resmi", key="cl10")
        st.checkbox("Tidak memberikan OTP, password, atau kode MFA", key="cl11")
        st.checkbox("Menyimpan bukti dan melaporkan bila perlu", key="cl12")

        st.markdown("**Sebelum selesai kerja**")
        st.checkbox("Logout dari perangkat bersama", key="cl13")
        st.checkbox("Dokumen sensitif tidak tertinggal terbuka", key="cl14")
        st.checkbox("File kerja tersimpan di repositori resmi", key="cl15")
        st.checkbox("Perangkat dibawa/diamankan dengan baik", key="cl16")

    checked = sum(int(st.session_state.get(f"cl{i}", False)) for i in range(1, 17))
    st.progress(checked / 16)
    st.caption(f"Checklist selesai: {checked}/16")


# =========================================================
# QUIZ TAB
# =========================================================
with quiz_tab:
    st.markdown("#### Mini kuis awareness")
    q_idx = st.session_state["quiz_index"]
    quiz = QUIZ_DATA[q_idx]

    with st.container(border=True):
        st.caption(f"Pertanyaan {q_idx + 1} dari {len(QUIZ_DATA)}")
        st.markdown(f"**{quiz['question']}**")

    selected = st.radio(
        "Pilih jawaban",
        quiz["options"],
        key=f"quiz_radio_{q_idx}",
    )

    if st.button("Cek jawaban", use_container_width=True):
        selected_idx = quiz["options"].index(selected)
        already = st.session_state["quiz_answered"].get(q_idx, False)

        if selected_idx == quiz["correct"]:
            st.success("Benar. " + quiz["explain"])
            if not already:
                st.session_state["quiz_score"] += 1
        else:
            st.error(
                "Belum tepat. "
                + quiz["explain"]
                + f" Jawaban yang benar: **{quiz['options'][quiz['correct']]}**"
            )

        st.session_state["quiz_answered"][q_idx] = True

    nq1, nq2, nq3 = st.columns([1, 1, 2])

    with nq1:
        if st.button("← Sebelumnya", use_container_width=True, disabled=q_idx == 0):
            st.session_state["quiz_index"] -= 1
            st.rerun()

    with nq2:
        if st.button("Berikutnya →", use_container_width=True, disabled=q_idx >= len(QUIZ_DATA) - 1):
            st.session_state["quiz_index"] += 1
            st.rerun()

    with nq3:
        st.info(f"Skor saat ini: {st.session_state['quiz_score']}/{len(QUIZ_DATA)}")


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <div class="footer-note">
        GARDA - Sentra-Cyber membantu awareness keamanan informasi.
        Untuk permintaan internal sensitif atau insiden nyata, gunakan kanal resmi organisasi.
    </div>
    """,
    unsafe_allow_html=True,
)