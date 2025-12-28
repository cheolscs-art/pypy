import streamlit as st
import os

# --- 1. 페이지 및 스타일 설정 (Denon Antique 테마) ---
st.set_page_config(page_title="DENON Antique Audio System", layout="centered")

# 사용자 정의 CSS로 레트로 느낌 구현
st.markdown("""
    <style>
    .stApp {
        background-color: #2d2d2d;
    }
    .main-panel {
        background-color: #d4c8b4;
        padding: 20px;
        border-radius: 10px;
        border: 4px solid #a89f8e;
    }
    .lcd-display {
        background-color: #000000;
        color: #00ff00;
        font-family: 'Courier New', Courier, monospace;
        padding: 15px;
        border: 4px inset #555;
        margin-bottom: 20px;
        text-align: center;
        border-radius: 5px;
    }
    .lcd-title {
        font-size: 1.2em;
        font-weight: bold;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .lcd-time {
        font-size: 2em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    /* 버튼 스타일 조정 */
    .stButton > button {
        background-color: #e0d5c5;
        color: black;
        border: 2px solid #999;
        font-weight: bold;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #cbbba6;
        border-color: #0078d7;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 세션 상태 관리 (플레이리스트 및 현재 곡) ---
if 'playlist' not in st.session_state:
    st.session_state.playlist = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

# --- 3. 로직 함수 ---
def next_song():
    if st.session_state.playlist and st.session_state.current_index < len(st.session_state.playlist) - 1:
        st.session_state.current_index += 1

def prev_song():
    if st.session_state.playlist and st.session_state.current_index > 0:
        st.session_state.current_index -= 1

def clear_playlist():
    st.session_state.playlist = []
    st.session_state.current_index = 0

# --- 4. UI 구성 ---

# 제목
st.title("DENON Antique Audio System")

# 파일 업로더 (Tkinter의 filedialog 대체)
uploaded_files = st.file_uploader("ADD SONGS (MP3, WAV, OGG)", type=['mp3', 'wav', 'ogg'], accept_multiple_files=True)

# 파일이 업로드되면 플레이리스트에 추가
if uploaded_files:
    for uploaded_file in uploaded_files:
        # 중복 방지: 파일명이 이미 있는지 확인
        if uploaded_file not in st.session_state.playlist:
            st.session_state.playlist.append(uploaded_file)

# 메인 패널 시작
with st.container():
    st.markdown('<div class="main-panel">', unsafe_allow_html=True)

    # 현재 재생 중인 곡 정보 가져오기
    current_song_name = "INSERT DISC"
    current_file = None
    
    if st.session_state.playlist:
        # 인덱스 안전 장치
        if st.session_state.current_index >= len(st.session_state.playlist):
            st.session_state.current_index = 0
            
        current_file = st.session_state.playlist[st.session_state.current_index]
        current_song_name = current_file.name.upper()

    # LCD 디스플레이 (HTML/CSS로 구현)
    st.markdown(f"""
        <div class="lcd-display">
            <div class="lcd-time">-- : --</div>
            <div class="lcd-title">TRACK {st.session_state.current_index + 1}: {current_song_name}</div>
            <div style="font-size: 0.8em; color: #00aa00; margin-top:5px;">{'I' * 24}</div>
        </div>
    """, unsafe_allow_html=True)

    # 컨트롤 버튼 (컬럼으로 배치)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        st.button("◀◀ PREV", on_click=prev_song)
    with col2:
        # Streamlit은 자동 재생 제어가 까다로우므로 플레이 버튼은 오디오 위젯으로 대체됨
        st.button("STOP ■", on_click=lambda: None) 
    with col3:
        st.button("NEXT ▶▶", on_click=next_song)
    with col4:
        if st.button("CLEAR"):
            clear_playlist()

    st.markdown("---")

    # 오디오 플레이어 (Pygame 대신 st.audio 사용)
    if current_file:
        st.audio(current_file, format='audio/mp3')
        st.caption("Volume is controlled by your device system.")
    else:
        st.info("Please add music files above.")

    st.markdown('</div>', unsafe_allow_html=True) # 메인 패널 닫기

# --- 5. 플레이리스트 목록 표시 ---
with st.expander("TRACK LIST", expanded=True):
    if st.session_state.playlist:
        for idx, file in enumerate(st.session_state.playlist):
            # 현재 재생 중인 곡 강조
            prefix = "▶ " if idx == st.session_state.current_index else f"{idx+1}. "
            if st.button(f"{prefix}{file.name}", key=f"song_{idx}"):
                st.session_state.current_index = idx
                st.rerun()
    else:
        st.write("No tracks loaded.")
