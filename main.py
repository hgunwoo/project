import streamlit as st
import datetime
import time

# -----------------------------------------------------------------------------
# 1. 페이지 및 초기 상태 세팅
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ALL CLE - 스터디플래너 AI",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화 (초기 상태: 데이터 없음)
if "subjects" not in st.session_state:
    st.session_state.subjects = []  # 기본 과목 없음

if "student_info" not in st.session_state:
    st.session_state.student_info = {
        "school": "고등학교",
        "grade": "2학년",
        "class_num": "8반",
        "name": "한건우",
        "exam_date": datetime.date.today() + datetime.timedelta(days=14)
    }

if "settings" not in st.session_state:
    st.session_state.settings = {
        "theme": "다크 모드",
        "language": "한국어",
        "bgm": "선택 안함"
    }

# 타이머 상태 관리 {subject_id: {"running": Bool, "start_time": float, "elapsed": int}}
if "timers" not in st.session_state:
    st.session_state.timers = {}

# -----------------------------------------------------------------------------
# 2. 명언 데이터 및 BGM 링크
# -----------------------------------------------------------------------------
QUOTES = [
    "“지금 자면 꿈을 꾸지만, 지금 공부하면 꿈을 이룬다.”",
    "“성공은 매일 반복되는 작은 노력들의 합이다.”",
    "“오늘 흘린 땀은 내일의 배신을 하지 않는다.”",
    "“시작하는 방법은 말하기를 그만두고 행동하는 것이다.”",
    "“미래는 오늘 당신이 무엇을 하느냐에 따라 달려있다.”",
    "“포기하고 싶을 때, 왜 시작했는지 생각하라.”"
]

BGM_LINKS = {
    "선택 안함": None,
    "☕ 잔잔한 카페 소음 (Lofi Beat)": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
    "🌧️ 집중을 돕는 빗소리 (White Noise)": "https://www.youtube.com/watch?v=mPZkdNFkNps",
    "🎻 집중력 향상 모차르트 클래식": "https://www.youtube.com/watch?v=RBumgq5yvrA",
    "🌲 숲속 자연의 소리": "https://www.youtube.com/watch?v=xNN7iTA57jM"
}

# -----------------------------------------------------------------------------
# 3. 사이드바 (설정, 프로필, BGM, 과목 추가)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ 올클 스터디 설정")
    
    # 지필고사 및 학생 정보
    with st.expander("👤 프로필 & 지필고사 설정", expanded=True):
        school = st.text_input("학교명", st.session_state.student_info["school"])
        col_g, col_c = st.columns(2)
        with col_g:
            grade = st.selectbox("학년", ["1학년", "2학년", "3학년"], index=1)
        with col_c:
            class_num = st.text_input("반", st.session_state.student_info["class_num"])
        name = st.text_input("이름", st.session_state.student_info["name"])
        
        # 통합 지필고사 D-Day 설정
        exam_date = st.date_input("🗓️ 지필고사 시작일", value=st.session_state.student_info["exam_date"])
        
        if st.button("설정 저장", use_container_width=True):
            st.session_state.student_info = {
                "school": school,
                "grade": grade,
                "class_num": class_num,
                "name": name,
                "exam_date": exam_date
            }
            st.success("학생 정보 및 시험일이 저장되었습니다!")

    # 앱 환경 설정 (테마, 언어)
    with st.expander("🎨 환경 및 테마 설정"):
        theme = st.selectbox("앱 테마", ["다크 모드", "라이트 모드", "파스텔 핑크", "딥 블루"], index=0)
        lang = st.selectbox("언어 (Language)", ["한국어", "English", "日本語"], index=0)
        st.session_state.settings["theme"] = theme
        st.session_state.settings["language"] = lang

    # 잔잔한 BGM 오디오 플레이어
    st.markdown("---")
    st.subheader("🎵 집중 BGM 플레이어")
    selected_bgm = st.selectbox("공부할 때 들을 BGM", list(BGM_LINKS.keys()))
    if selected_bgm != "선택 안함":
        st.video(BGM_LINKS[selected_bgm])

    # 과목 추가 폼
    st.markdown("---")
    st.subheader("➕ 과목 추가하기")
    with st.form("add_subject_form", clear_on_submit=True):
        sub_name = st.text_input("과목명", placeholder="예: 수학 II, 영어, 한국사")
        target_hours = st.number_input("목표 공부 시간 (시간 단위)", min_value=1, max_value=300, value=10)
        
        btn_add = st.form_submit_button("과목 등록하기", use_container_width=True)
        if btn_add:
            if not sub_name.strip():
                st.error("과목 이름을 입력해주세요.")
            else:
                new_id = max([s["id"] for s in st.session_state.subjects], default=0) + 1
                st.session_state.subjects.append({
                    "id": new_id,
                    "name": sub_name,
                    "target_hours": target_hours,
                    "logged_seconds": 0
                })
                st.success(f"'{sub_name}' 과목이 추가되었습니다.")
                st.rerun()

# -----------------------------------------------------------------------------
# 4. 메인 화면 상단 (10초 자동 변경 명언 + 통합 D-Day 헤더)
# -----------------------------------------------------------------------------
# 10초마다 명언 로테이션
quote_index = int(time.time() // 10) % len(QUOTES)
st.info(f"💬 {QUOTES[quote_index]}")

# 지필고사 D-Day 계산
today = datetime.date.today()
exam_d = st.session_state.student_info["exam_date"]
d_day_val = (exam_d - today).days

if d_day_val > 0:
    d_day_text = f"D-{d_day_val}"
elif d_day_val == 0:
    d_day_text = "D-DAY (오늘!)"
else:
    d_day_text = f"D+{abs(d_day_val)}"

# 상단 올클 헤더
c_head1, c_head2 = st.columns([3, 1])
with c_head1:
    st.title("⏱️ 올클 (ALL CLE) 스터디플래너")
    info = st.session_state.student_info
    st.caption(f"🏫 {info['school']} {info['grade']} {info['class_num']} **{info['name']}** 학생의 플래너")
with c_head2:
    st.metric("🎯 지필고사 D-Day", d_day_text, delta=f"시험일: {exam_d.strftime('%m/%d')}")

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. 과목별 타이머 & 진행도 자동 집계 메인 영역
# -----------------------------------------------------------------------------
st.subheader("📚 나의 공부 과목 & 타이머 관리")

if not st.session_state.subjects:
    st.warning("등록된 과목이 없습니다. 왼쪽 사이드바에서 지필고사 과목을 추가하고 타이머로 공부를 시작해 보세요!")
else:
    for idx, sub in enumerate(st.session_state.subjects):
        sub_id = sub["id"]
        
        # 타이머 데이터 초기화
        if sub_id not in st.session_state.timers:
            st.session_state.timers[sub_id] = {"running": False, "start_time": 0}

        # 공부 시간 연산 (초 -> 시간/분/초)
        logged_sec = sub["logged_seconds"]
        target_sec = sub["target_hours"] * 3600
        progress_pct = min(round((logged_sec / target_sec) * 100, 1), 100.0)
        
        hrs = logged_sec // 3600
        mins = (logged_sec % 3600) // 60
        secs = logged_sec % 60
        time_str = f"{hrs:02d}시간 {mins:02d}분 {secs:02d}초"

        with st.expander(f"📖 **{sub['name']}** | 진행률: {progress_pct}% ({hrs}시간 {mins}분 / {sub['target_hours']}시간)", expanded=True):
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                st.progress(progress_pct / 100)
                st.write(f"⏱️ **누적 공부 시간**: `{time_str}` (목표: {sub['target_hours']}시간)")
                
                # 타이머 조작 버튼
                t_col1, t_col2, t_col3 = st.columns(3)
                
                is_running = st.session_state.timers[sub_id]["running"]
                
                with t_col1:
                    if not is_running:
                        if st.button("▶️ 공부 시작", key=f"start_{sub_id}", use_container_width=True):
                            st.session_state.timers[sub_id]["running"] = True
                            st.session_state.timers[sub_id]["start_time"] = time.time()
                            st.rerun()
                    else:
                        if st.button("⏸️ 일시정지", key=f"pause_{sub_id}", use_container_width=True):
                            now = time.time()
                            elapsed = int(now - st.session_state.timers[sub_id]["start_time"])
                            sub["logged_seconds"] += elapsed
                            st.session_state.timers[sub_id]["running"] = False
                            st.rerun()
                
                with t_col2:
                    if st.button("⏹️ 타이머 초기화", key=f"reset_{sub_id}", use_container_width=True):
                        sub["logged_seconds"] = 0
                        st.session_state.timers[sub_id]["running"] = False
                        st.rerun()
                        
                with t_col3:
                    if st.button("🗑️ 과목 삭제", key=f"del_{sub_id}", use_container_width=True):
                        st.session_state.subjects.pop(idx)
                        st.session_state.timers.pop(sub_id, None)
                        st.rerun()
                        
                if is_running:
                    st.caption("🔥 공부 시간이 측정 중입니다! 다 마치면 [일시정지]를 눌러 기록을 반영해 주세요.")

            with col_right:
                st.markdown("**🎯 과목목표 수정**")
                new_target = st.number_input("목표시간 변경", min_value=1, max_value=300, value=sub["target_hours"], key=f"target_input_{sub_id}")
                if new_target != sub["target_hours"]:
                    sub["target_hours"] = new_target
                    st.rerun()

# -----------------------------------------------------------------------------
# 6. Gemini AI 피드백
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("🤖 올클 AI 피드백")
if st.button("현재 공부 진행 상황 AI 진단받기"):
    if not st.session_state.subjects:
        st.warning("과목을 먼저 등록해주세요.")
    else:
        st.success("📊 학습 진행률 및 지필고사 D-Day를 바탕으로 한 맞춤 피드백:")
        for s in st.session_state.subjects:
            p = round((s['logged_seconds'] / (s['target_hours'] * 3600)) * 100, 1)
            if d_day_val <= 7 and p < 40:
                st.write(f"- 🚨 **{s['name']}**: 시험이 7일 남았으나 진행률이 {p}%입니다. 타이머를 켜고 핵심 문제 위주로 공부하세요!")
            elif p >= 80:
                st.write(f"- 🎉 **{s['name']}**: 진행률 {p}% 달성! 실전 문제 풀이로 마무리하세요.")
            else:
                st.write(f"- 📘 **{s['name']}**: 진행률 {p}%. 지금처럼 매일 스톱워치를 측정하며 꾸준히 학습하세요.")
