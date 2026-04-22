"""
Versi UI yang lebih interaktif untuk:
Mentor Keamanan Informasi Pusdatin

Jalankan dengan:
    streamlit run app_infosec_pusdatin_improved.py
"""

import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI


# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Mentor Keamanan Informasi Pusdatin",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================
# STYLING
# =========================
st.markdown(
    """
    <style>
    :root {
        --bg-1: #07111f;
        --bg-2: #0d1b2a;
        --card: rgba(11, 24, 41, 0.88);
        --line: rgba(148, 163, 184, 0.18);
        --soft: #93c5fd;
        --text: #e5eefb;
        --muted: #94a3b8;
        --accent: #22c55e;
        --warn: #facc15;
        --danger: #fb7185;
    }

    .stApp {
        background:
            radial-gradient(circle at 0% 0%, rgba(37,99,235,.18), transparent 24%),
            radial-gradient(circle at 100% 0%, rgba(34,197,94,.10), transparent 22%),
            linear-gradient(135deg, var(--bg-1) 0%, #091523 38%, var(--bg-2) 100%);
        color: var(--text);
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    .hero {
        background: linear-gradient(135deg, rgba(15,23,42,.92), rgba(9,18,32,.86));
        border: 1px solid rgba(96,165,250,.18);
        border-radius: 24px;
        padding: 1.5rem 1.5rem 1.2rem 1.5rem;
        box-shadow: 0 20px 60px rgba(0,0,0,.28);
        position: relative;
        overflow: hidden;
    }

    .hero:before {
        content: "";
        position: absolute;
        right: -60px;
        top: -60px;
        width: 220px;
        height: 220px;
        background: radial-gradient(circle, rgba(59,130,246,.22), transparent 60%);
    }

    .hero h1 {
        font-size: 2.3rem;
        line-height: 1.1;
        margin: 0 0 .5rem 0;
        font-weight: 800;
        color: #f8fbff;
    }

    .hero p {
        color: #d7e2f1;
        margin-bottom: .7rem;
        font-size: 0.98rem;
        line-height: 1.6;
    }

    .badge-row {
        display: flex;
        gap: .5rem;
        flex-wrap: wrap;
        margin-top: .35rem;
    }

    .badge-pill {
        border-radius: 999px;
        padding: .36rem .75rem;
        font-size: .8rem;
        border: 1px solid rgba(148,163,184,.22);
        background: rgba(15, 23, 42, .9);
        color: #d9e6f5;
    }

    .glass {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 1rem 1rem .9rem 1rem;
        box-shadow: 0 16px 50px rgba(0,0,0,.2);
    }

    .metric-card {
        background: linear-gradient(180deg, rgba(15,23,42,.95), rgba(8,15,27,.88));
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: .95rem 1rem;
        min-height: 114px;
    }

    .metric-kicker {
        color: var(--muted);
        font-size: .8rem;
        margin-bottom: .25rem;
    }

    .metric-value {
        font-size: 1.35rem;
        font-weight: 800;
        color: #f8fbff;
        margin-bottom: .15rem;
    }

    .metric-sub {
        font-size: .78rem;
        color: #b8c7da;
        line-height: 1.45;
    }

    .alert-box {
        border-left: 4px solid #facc15;
        background: rgba(250, 204, 21, .08);
        border-radius: 14px;
        padding: .85rem 1rem;
        color: #f8fafc;
        margin-top: .75rem;
    }

    .mini-title {
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: .35rem;
        color: #f8fbff;
    }

    .small-muted {
        color: var(--muted);
        font-size: .84rem;
    }

    .score-box {
        border-radius: 16px;
        padding: .9rem 1rem;
        background: linear-gradient(180deg, rgba(12, 20, 35, .96), rgba(7, 13, 24, .92));
        border: 1px solid var(--line);
    }

    div[data-testid="stChatMessage"] {
        border-radius: 18px;
        border: 1px solid rgba(148,163,184,.12);
        background: rgba(9,15,28,.35);
        padding: .35rem .35rem .1rem .35rem;
    }

    div[data-testid="stTabs"] button {
        font-weight: 600;
    }

    .footer-note {
        margin-top: 1rem;
        color: #93a6bf;
        font-size: .8rem;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# SESSION STATE
# =========================
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


# =========================
# HELPERS
# =========================
def build_system_prompt(active_mode: str) -> str:
    base = (
        "Kamu adalah 'Mentor Keamanan Informasi Pusdatin', fasilitator edukasi keamanan informasi "
        "untuk pegawai Pusat Data dan Informasi Kementerian Pertahanan. Fokus pada security awareness, "
        "perilaku aman, klasifikasi informasi, anti-phishing, password dan MFA, keamanan perangkat, "
        "komunikasi kerja, etika digital, dan respons insiden tingkat pengguna.\n\n"
        "ATURAN: \n"
        "- Gunakan Bahasa Indonesia yang jelas, rapi, dan mudah dipahami.\n"
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
        style = (
            "Gunakan format simulasi atau mini kuis. Sajikan skenario singkat, pertanyaan, lalu tunggu atau beri penjelasan singkat."
        )

    return base + "\nGAYA JAWABAN: " + style


def get_llm(api_key: str):
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)


def start_or_update_system_prompt(mode: str):
    system_prompt = SystemMessage(build_system_prompt(mode))
    if not st.session_state["messages_history"]:
        st.session_state["messages_history"] = [system_prompt]
    elif isinstance(st.session_state["messages_history"][0], SystemMessage):
        st.session_state["messages_history"][0] = system_prompt
    else:
        st.session_state["messages_history"].insert(0, system_prompt)


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


def risk_level_from_answers(suspicious_link: bool, urgent_tone: bool, asks_credentials: bool, unknown_sender: bool):
    score = sum([suspicious_link, urgent_tone, asks_credentials, unknown_sender])
    if score >= 3:
        return "Tinggi", "Jangan klik, jangan balas, dokumentasikan, dan laporkan segera."
    if score == 2:
        return "Sedang", "Tahan tindakan, verifikasi lewat kanal resmi, lalu laporkan bila perlu."
    return "Rendah", "Tetap hati-hati dan lakukan verifikasi sebelum bertindak."


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("### 🔐 Konfigurasi")
    st.caption(
        "Masukkan Google API Key dari Google AI Studio. Kunci hanya disimpan sementara di session browser."
    )

    api_key_input = st.text_input("Google API Key", type="password", key="api_key_input")
    if st.button("Simpan API Key", use_container_width=True):
        if not api_key_input:
            st.error("API Key tidak boleh kosong.")
        else:
            st.session_state["GOOGLE_API_KEY"] = api_key_input
            st.success("API Key tersimpan.")

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


if "GOOGLE_API_KEY" not in st.session_state:
    st.info("Simpan Google API Key di sidebar untuk mengaktifkan mentor AI.")
    st.stop()

start_or_update_system_prompt(mode)
llm = get_llm(st.session_state["GOOGLE_API_KEY"])


# =========================
# HERO
# =========================
left, right = st.columns([1.9, 1.1], gap="large")

with left:
    st.markdown(
        """
        <div class="hero">
            <h1>Mentor Keamanan Informasi Pusdatin 🛡️</h1>
            <p>
                Pendamping belajar keamanan informasi untuk pegawai. Fokus pada <b>anti-phishing</b>,
                <b>klasifikasi informasi</b>, <b>kebiasaan kerja aman</b>, dan <b>respons insiden</b>
                dalam konteks penggunaan sehari-hari.
            </p>
            <p class="small-muted">
                Kamu bisa bertanya bebas, mencoba simulasi, mengecek risiko pesan mencurigakan,
                atau mengerjakan mini kuis singkat.
            </p>
            <div class="badge-row">
                <span class="badge-pill">🔎 Anti-Phishing</span>
                <span class="badge-pill">🔐 Password & MFA</span>
                <span class="badge-pill">📂 Klasifikasi Informasi</span>
                <span class="badge-pill">🚨 Respons Insiden</span>
            </div>
            <div class="alert-box">
                <b>Catatan:</b> Aplikasi ini untuk edukasi dan awareness. Untuk insiden nyata, tetap gunakan
                jalur pelaporan resmi dan koordinasi dengan tim terkait.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-kicker">Fokus Utama</div>
                <div class="metric-value">InfoSec</div>
                <div class="metric-sub">Awareness, perilaku aman, dan mitigasi praktis.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with rc2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-kicker">Mode Aktif</div>
                <div class="metric-value">{mode}</div>
                <div class="metric-sub">Respons mengikuti gaya interaksi yang dipilih.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="glass">
            <div class="mini-title">🧠 Ide Interaktif</div>
            <div class="small-muted">Coba salah satu jalur berikut:</div>
            <div style="margin-top:.6rem; line-height:1.9;">
                <div>• Analisis email atau WA yang mencurigakan</div>
                <div>• Minta checklist kebiasaan aman harian</div>
                <div>• Simulasikan akun dicurigai diambil alih</div>
                <div>• Kerjakan mini kuis awareness</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(" ")


# =========================
# MAIN TABS
# =========================
chat_tab, simulator_tab, checklist_tab, quiz_tab = st.tabs(
    ["💬 Chat Mentor", "🧪 Cek Risiko", "📋 Checklist", "🎯 Mini Kuis"]
)


# =========================
# CHAT TAB
# =========================
with chat_tab:
    st.markdown("#### Mulai dari pertanyaan cepat")
    qp1, qp2, qp3, qp4 = st.columns(4)
    quick_prompt = None

    with qp1:
        if st.button("Kenali phishing", use_container_width=True):
            quick_prompt = "Berikan panduan praktis mengenali email atau WA phishing yang menyasar pegawai, lengkap dengan red flag yang umum."
    with qp2:
        if st.button("Berbagi file aman", use_container_width=True):
            quick_prompt = "Jelaskan cara berbagi dokumen kerja dengan aman berdasarkan prinsip klasifikasi informasi dan need-to-know."
    with qp3:
        if st.button("Akun dicurigai diambil alih", use_container_width=True):
            quick_prompt = "Buat simulasi singkat jika akun email kerja dicurigai diambil alih, termasuk langkah aman tingkat pengguna dan pelaporan."
    with qp4:
        if st.button("Checklist harian", use_container_width=True):
            quick_prompt = "Buat checklist harian keamanan informasi untuk pegawai kantor dalam format yang singkat dan praktis."

    st.markdown("---")

    # render chat history
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
        st.session_state["messages_history"].append(HumanMessage(final_prompt))

        with st.chat_message("assistant"):
            with st.spinner("Menyusun jawaban..."):
                response = llm.invoke(st.session_state["messages_history"])
                if not isinstance(response, AIMessage):
                    response = AIMessage(content=str(response))
                st.session_state["messages_history"].append(response)
                st.markdown(response.content)


# =========================
# RISK CHECKER TAB
# =========================
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
            suspicious_link, urgent_tone, asks_credentials, unknown_sender
        )
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(
                f"""
                <div class="score-box">
                    <div class="metric-kicker">Level Risiko</div>
                    <div class="metric-value">{level}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
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


# =========================
# CHECKLIST TAB
# =========================
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

    checked = sum(
        int(st.session_state.get(k, False))
        for k in [f"cl{i}" for i in range(1, 17)]
    )
    st.progress(checked / 16)
    st.caption(f"Checklist selesai: {checked}/16")


# =========================
# QUIZ TAB
# =========================
with quiz_tab:
    st.markdown("#### Mini kuis awareness")
    q_idx = st.session_state["quiz_index"]
    quiz = QUIZ_DATA[q_idx]

    st.markdown(
        f"""
        <div class="score-box">
            <div class="metric-kicker">Pertanyaan {q_idx + 1} dari {len(QUIZ_DATA)}</div>
            <div class="metric-value" style="font-size:1.05rem;">{quiz['question']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
        if st.button(
            "Berikutnya →",
            use_container_width=True,
            disabled=q_idx >= len(QUIZ_DATA) - 1,
        ):
            st.session_state["quiz_index"] += 1
            st.rerun()
    with nq3:
        st.info(f"Skor saat ini: {st.session_state['quiz_score']}/{len(QUIZ_DATA)}")


st.markdown(
    "<div class='footer-note'>Mentor edukasi ini membantu awareness. Untuk permintaan internal sensitif atau insiden nyata, gunakan kanal resmi organisasi.</div>",
    unsafe_allow_html=True,
)
