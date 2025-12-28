import streamlit as st
import base64

# --- 웹앱 페이지 설정 ---
st.set_page_config(
    page_title="Neon Beat Web App",
    page_icon="🎵",
    layout="centered"
)

# --- CSS: 고급 웹 UI 및 시각화 애니메이션 ---
def apply_web_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        
        /* 웹앱 전체 배경 */
        .stApp {
            background: radial-gradient(circle at center, #1a1a1a 0%, #050505 100%);
        }
        
        /* 중앙 플레이어 카드 */
        .player-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(15px);
            border-radius: 30px;
            padding: 40px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 25px 50px rgba(0,0,0,0.5);
            margin-top: 20px;
        }

        /* 시각화 이퀄라이저 */
        .visualizer-container {
            display: flex;
            justify-content: center;
            align-items: flex-end;
            height: 80px;
            gap: 6px;
            margin-bottom: 30px;
        }

        .bar {
            width: 8px;
            background: #00ff7f;
            border-radius: 4px;
            animation: bounce 1s infinite ease-in-out;
            box-shadow: 0 0 15px #00ff7f;
        }

        @keyframes bounce {
            0%, 100% { height: 10px; opacity: 0.3; }
            50% { height: 80px; opacity: 1; }
        }

        /* 곡 정보 */
        .track-name {
            font-family: 'Orbitron', sans-serif;
            color: white;
            font-size: 1.5rem;
            margin: 20px 0;
            text-align: center;
        }

        /* 오디오 플레이어 다크 모드 최적화 */
        audio {
            width: 100%;
            filter: invert(90%) hue-rotate(100deg);
        }

        /* 플레이리스트 버튼 스타일 */
        .stButton>button {
            border-radius: 12px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            color: white;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: #00ff7f;
            color: black;
            box-shadow: 0 0 20px #00ff7f;
        }
        </style>
    """, unsafe_allow_html=True)

apply_web_style()

# --- 상태 관리 ---
if 'playlist' not in st.session_state:
    st.session_state.playlist = []
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0

# --- 헤더 ---
st.markdown("<h3 style='text-align: center; color: #00ff7f; font-family: Orbitron;'>NEON BEAT SYSTEM</h3>", unsafe_allow_html=True)

# --- 음악 업로드 ---
uploaded_files = st.file_uploader("Click to upload MP3", type=['mp3'], accept_multiple_files=True)
if uploaded_files:
    for f in uploaded_files:
        if f.name not in [x.name for x in st.session_state.playlist]:
            st.session_state.playlist.append(f)

# --- 메인 플레이어 뷰 ---
st.markdown('<div class="player-card">', unsafe_allow_html=True)

if st.session_state.playlist:
    curr = st.session_state.playlist[st.session_state.current_idx]
    
    # 시각화 애니메이션 바 출력
    v_html = '<div class="visualizer-container">'
    for i in range(15):
        delay = i * 0.1
        v_html += f'<div class="bar" style="animation-delay: {delay}s"></div>'
    v_html += '</div>'
    st.markdown(v_html, unsafe_allow_html=True)
    
    st.markdown(f'<div class="track-name">{curr.name}</div>', unsafe_allow_html=True)
    
    # 오디오 플레이어
    st.audio(curr)
    
    # 다음곡/이전곡 컨트롤
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("⏮ PREV"):
            st.session_state.current_idx = (st.session_state.current_idx - 1) % len(st.session_state.playlist)
            st.rerun()
    with c3:
        if st.button("NEXT ⏭"):
            st.session_state.current_idx = (st.session_state.current_idx + 1) % len(st.session_state.playlist)
            st.rerun()
else:
    st.info("Please upload MP3 files to start the experience.")

st.markdown('</div>', unsafe_allow_html=True)

# --- 플레이리스트 ---
if st.session_state.playlist:
    st.markdown("---")
    st.markdown("#### 🎧 UP NEXT")
    for i, f in enumerate(st.session_state.playlist):
        is_playing = i == st.session_state.current_idx
        col_icon, col_btn = st.columns([0.1, 0.9])
        with col_icon:
            if is_playing: st.write("🔊")
        with col_btn:
            if st.button(f.name, key=f"p_{i}", use_container_width=True):
                st.session_state.current_idx = i
                st.rerun()
