import streamlit as st
import datetime
import time

# -----------------------------------------------------------------------------
# 1. 페이지 및 초기 상태 세팅
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="스터디플래너 AI",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 완전 초기화 (유저가 직접 입력하도록 기본값 제거)
if "subjects" not in st.session_state:
    st.session_state.subjects = []

if "student_info" not in st.session_state:
    st.session_state.student_info = {
        "school": "",
        "grade": "",
        "class_num": "",
        "name": "",
        "exam_date": None  # 초기 상태에는 시험일 미설정
    }

if "settings" not in st.session_state:
    st.session_state.settings = {
        "theme": "다크 모드",
        "language": "한국어"
    }

# 타이머 상태 관리
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

COLOR_OPTIONS = ["#6366F1", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#06B6D4"]

# -----------------------------------------------------------------------------
# 3. 사이드바 (설정, 프로필, BGM, 과목 추가)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ 스터디 설정")
    
    # 지필고사 및 학생 정보
    with st.expander("👤 프로필 & 지필고사 설정", expanded=True):
        school = st.text_input("학교명", value=st.session_state.student_info["school"], placeholder="예: OO고등학교")
        col_g, col_c = st.columns(2)
        with col_g:
            grade = st.text_input("학년", value=st.session_state.student_info["grade"], placeholder="예: 2학년")
        with col_c:
            class_num = st.text_input("반", value=st.session_state.student_info["class_num"], placeholder="예: 8반")
        name = st.text_input("이름", value=st.session_state.student_info["name"], placeholder="예: 한건우")
        
        # 지필고사 D-Day 선택 (초기값 없음)
        st.markdown("**🗓️ 지필고사 시작일 설정**")
        set_exam = st.checkbox("시험일 지정하기", value=(st.session_state.student_info["exam_date"] is not None))
        if set_exam:
            curr_val = st.session_state.student_info["exam_date"] or datetime.date.today()
            exam_date = st.date_input("시험 날짜", value=curr_val)
        else:
            exam_date = None
        
        if st.button("설정 저장", use_container_width=True):
            st.session_state.student_info = {
                "school": school,
                "grade": grade,
                "class_num": class_num,
                "name": name,
                "exam_date": exam_date
            }
            st.success("설정이 저장되었습니다!")
            st.rerun()

    # 앱 환경 설정
    with st.expander("🎨 환경 및 테마 설정"):
        theme = st.selectbox("앱 테마", ["다크 모드", "라이트 모드", "퍼플 모드"], index=0)
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
        target_hours = st.number_input("목표 공부 시간 (시간)", min_value=1, max_value=300, value=10)
        sub_color = st.color_picker("과목 테마 색상", value="#6366F1")
        
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
                    "logged_seconds": 0,
                    "color": sub_color
                })
                st.success(f"'{sub_name}' 과목이 추가되었습니다.")
                st.rerun()

# -----------------------------------------------------------------------------
# 4. 메인 화면 상단 (명언 + 통합 D-Day 헤더)
# -----------------------------------------------------------------------------
# 10초마다 명언 자동 전환
quote_index = int(time.time() // 10) % len(QUOTES)
st.info(f"💬 {QUOTES[quote_index]}")

# 정보 표시 및 D-Day 연산
info = st.session_state.student_info
student_str = f"{info['school']} {info['grade']} {info['class_num']} {info['name']}".strip()
if not student_str:
    student_str = "사이드바에서 학생 정보를 설정해 주세요."

exam_d = info["exam_date"]
if exam_d is None:
    d_day_text = "미설정"
    delta_sub = "사이드바에서 지필고사 일을 지정하세요"
else:
    today = datetime.date.today()
    d_day_val = (exam_d - today).days
    if d_day_val > 0:
        d_day_text = f"D-{d_day_val}"
    elif d_day_val == 0:
        d_day_text = "D-DAY"
    else:
        d_day_text = f"D+{abs(d_day_val)}"
    delta_sub = f"시험일: {exam_d.strftime('%m/%d')}"

c_head1, c_head2 = st.columns([3, 1])
with c_head1:
    st.title("⏱️ 스터디플래너 AI")
    st.caption(f"🏫 **{student_str}**")
with c_head2:
    st.metric("🎯 지필고사 D-Day", d_day_text, delta=delta_sub)

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. 올클 스터디 앱 스타일: 타임라인 및 과목 스톱워치
# -----------------------------------------------------------------------------
st.subheader("📊 오늘의 공부 타임라인 & 과목 스톱워치")

if not st.session_state.subjects:
    st.warning("등록된 과목이 없습니다. 왼쪽 사이드바에서 지필고사 공부 과목을 등록해 보세요!")
else:
    # 전체 누적 공부시간 계산
    total_sec = sum(s["logged_seconds"] for s in st.session_state.subjects)
    total_h = total_sec // 3600
    total_m = (total_sec % 3600) // 60
    
    st.markdown(f"### 📅 TOTAL TIME: **{total_h}시간 {total_m}분**")
    
    col_left, col_right = st.columns([1, 1])
    
    # [왼쪽] 올클 스타일의 과목별 시간 기록 목록
    with col_left:
        st.markdown("#### ⏱️ 과목별 누적 공부 시간")
        for sub in st.session_state.subjects:
            s_sec = sub["logged_seconds"]
            s_h = s_sec // 3600
            s_m = (s_sec % 3600) // 60
            s_s = s_sec % 60
            
            # 올클 앱 스타일 컬러 태그와 시간 레이아웃
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; margin-bottom: 8px; border-radius: 8px; background-color: rgba(255, 255, 255, 0.05); border-left: 6px solid {sub['color']};">
                    <span style="font-weight: bold; font-size: 16px;">{sub['name']}</span>
                    <span style="font-family: monospace; font-size: 16px;">{s_h:02d}:{s_m:02d}:{s_s:02d}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    # [오른쪽] 스톱워치 측정 및 과목 조작
    with col_right:
        st.markdown("#### ▶️ 스톱워치 측정")
        selected_sub_name = st.selectbox("공부할 과목 선택", [s["name"] for s in st.session_state.subjects])
        selected_sub = next(s for s in st.session_state.subjects if s["name"] == selected_sub_name)
        sub_id = selected_sub["id"]

        if sub_id not in st.session_state.timers:
            st.session_state.timers[sub_id] = {"running": False, "start_time": 0}

        is_running = st.session_state.timers[sub_id]["running"]

        btn_c1, btn_c2, btn_c3 = st.columns(3)
        with btn_c1:
            if not is_running:
                if st.button("▶️ 공부 시작", key=f"start_{sub_id}", use_container_width=True):
                    st.session_state.timers[sub_id]["running"] = True
                    st.session_state.timers[sub_id]["start_time"] = time.time()
                    st.rerun()
            else:
                if st.button("⏸️ 일시정지 및 저장", key=f"pause_{sub_id}", use_container_width=True):
                    now = time.time()
                    elapsed = int(now - st.session_state.timers[sub_id]["start_time"])
                    selected_sub["logged_seconds"] += elapsed
                    st.session_state.timers[sub_id]["running"] = False
                    st.rerun()

        with btn_c2:
            if st.button("⏹️ 시간 초기화", key=f"reset_{sub_id}", use_container_width=True):
                selected_sub["logged_seconds"] = 0
                st.session_state.timers[sub_id]["running"] = False
                st.rerun()

        with btn_c3:
            if st.button("🗑️ 과목 삭제", key=f"del_{sub_id}", use_container_width=True):
                st.session_state.subjects = [s for s in st.session_state.subjects if s["id"] != sub_id]
                st.session_state.timers.pop(sub_id, None)
                st.rerun()

        if is_running:
            st.warning(f"🔥 [{selected_sub['name']}] 공부 시간을 측정 중입니다! 공부를 마치면 '일시정지 및 저장'을 눌러주세요.")

# -----------------------------------------------------------------------------
# 6. Gemini AI 맞춤 피드백
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("🤖 AI 맞춤 공부 진단")
if st.button("현재 학습 데이터 기반 AI 코칭받기"):
    if not st.session_state.subjects:
        st.warning("과목을 먼저 등록해 주세요.")
    else:
        st.success("📊 학습 진행 데이터 분석 결과:")
        for s in st.session_state.subjects:
            hrs = round(s["logged_seconds"] / 3600, 1)
            pct = min(round((hrs / s["target_hours"]) * 100, 1), 100.0)
            st.write(f"- **{s['name']}**: 목표 {s['target_hours']}시간 중 현재 **{hrs}시간**({pct}%) 달성하였습니다.")
