import streamlit as st
import random

# --- 페이지 설정 ---
st.set_page_config(page_title="Neon Visualizer Audio", layout="centered")

# --- 시각화 및 스타일 CSS ---
def apply_advanced_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        
        .stApp { background-color: #050505; }
        
        /* 메인 플레이어 카드 */
        .player-card {
            background: rgba(20, 20, 20, 0.95);
            border-radius: 30px;
            padding: 40px;
            border: 1px solid #333;
            box-shadow: 0 0 50px rgba(0, 255, 127, 0.1);
            text-align: center;
        }

        /* 네온 비주얼라이저 컨테이너 */
        .visualizer-container {
            display: flex;
            justify-content: center;
            align-items: flex-end;
            height: 100px;
            gap: 5px;
            margin-bottom: 20px;
        }

        /* 이퀄라이저 바 애니메이션 */
        .bar {
            width: 10px;
            background: linear-gradient(to top, #00ff7f, #00d4ff);
            border-radius: 10px 10px 0 0;
            animation: equalize 1.2s infinite ease-in-out;
            box-shadow: 0 0 15px rgba(0, 255, 127, 0.5);
        }

        @keyframes equalize {
            0% { height: 10px; }
            50% { height: 100px; }
            100% { height: 10px; }
        }

        /* 바마다 애니메이션 속도 차이 부여 */
        .bar:nth-child(1)  { animation-duration: 0.4s; }
        .bar:nth-child(2)  { animation-duration: 0.7s; }
        .bar:nth-child(3)  { animation-duration: 0.5s; }
        .bar:nth-child(4)  { animation-duration: 0.9s; }
        .bar:nth-child(5)  { animation-duration: 0.6s; }
        .bar:nth-child(6)  { animation-duration: 0.8s; }
        .bar:nth-child(7)  { animation-duration: 0.5s; }
        .bar:nth-child(8)  { animation-duration: 0.7s; }

        /* 곡 정보 텍스트 */
        .track-info {
            font-family: 'Orbitron', sans-serif;
            color: #00ff7f;
            text-shadow: 0 0 10px rgba(0, 255, 127, 0.5);
            margin-top: 20px;
        }
        
        /* 기본 오디오 플레이어 숨기기/커스텀 */
        audio {
            filter: invert(1) hue-rotate(90deg) brightness(1.5);
            width: 100%;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_advanced_style()

# --- 상태 관리 ---
if 'playlist' not in st.session_state:
    st.session_state.playlist = []
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0

# --- UI 레이아웃 ---
st.markdown("<h1 style='text-align: center; color: white;'>NEON <span style='color: #00ff7f;'>BEAT</span> PLAYER</h1>", unsafe_allow_html=True)

# 파일 업로더
with st.expander("🎵 음악 라이브러리에 곡 추가"):
    files = st.file_uploader("MP3 파일을 업로드하세요", type=['mp3'], accept_multiple_files=True)
    if files:
        for f in files:
            if f not in st.session_state.playlist:
                st.session_state.playlist.append(f)

# 메인 플레이어 영역
st.markdown('<div class="player-card">', unsafe_allow_html=True)

if st.session_state.playlist:
    curr_file = st.session_state.playlist[st.session_state.current_idx]
    
    # 시각화 바 (CSS 애니메이션)
    # 재생 중일 때만 바가 움직이는 효과를 위해 HTML 생성
    visualizer_html = '<div class="visualizer-container">'
    for i in range(12):
        visualizer_html += '<div class="bar"></div>'
    visualizer_html += '</div>'
    st.markdown(visualizer_html, unsafe_allow_html=True)
    
    # 곡 정보
    st.markdown(f"""
        <div class="track-info">
            <div style="font-size: 0.8rem; opacity: 0.7;">NOW PLAYING</div>
            <div style="font-size: 1.4rem; font-weight: bold; margin-top:5px;">{curr_file.name}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 오디오 플레이어
    st.audio(curr_file)
    
    # 컨트롤 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⏮ PREV"):
            st.session_state.current_idx = (st.session_state.current_idx - 1) % len(st.session_state.playlist)
            st.rerun()
    with col2:
        st.write("") # 간격용
    with col3:
        if st.button("NEXT ⏭"):
            st.session_state.current_idx = (st.session_state.current_idx + 1) % len(st.session_state.playlist)
            st.rerun()
else:
    st.markdown("<p style='color: #666;'>플레이리스트가 비어 있습니다.</p>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 하단 플레이리스트
st.markdown("### 🎧 PLAYLIST")
for i, f in enumerate(st.session_state.playlist):
    is_active = i == st.session_state.current_idx
    col_a, col_b = st.columns([0.1, 0.9])
    with col_a:
        if is_active: st.markdown("🔥")
        else: st.markdown(f"{i+1}")
    with col_b:
        if st.button(f.name, key=f"p_{i}", use_container_width=True):
            st.session_state.current_idx = i
            st.rerun()
