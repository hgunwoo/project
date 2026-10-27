import streamlit as st
import datetime
import time

# -----------------------------------------------------------------------------
# 1. 페이지 세팅
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="스터디플래너 AI",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. 세션 상태 초기화
# -----------------------------------------------------------------------------
if "subjects" not in st.session_state:
    st.session_state.subjects = []

if "student_info" not in st.session_state:
    st.session_state.student_info = {
        "school": "",
        "grade": "",
        "class_num": "",
        "name": "",
        "exam_date": None
    }

if "theme" not in st.session_state:
    st.session_state.theme = "다크 모드"

if "stopwatch" not in st.session_state:
    st.session_state.stopwatch = {
        "active_sub_id": None,
        "running": False,
        "start_time": 0,
        "accumulated": 0
    }

# -----------------------------------------------------------------------------
# 3. 실시간 테마(CSS) 동적 적용 & 그라데이션 스타일링 극대화
# -----------------------------------------------------------------------------
current_theme = st.session_state.theme

if current_theme == "라이트 모드":
    bg_css = "background-color: #F8FAFC; color: #0F172A;"
    card_css = "background: #FFFFFF; color: #0F172A; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);"
    header_gradient = "linear-gradient(135deg, #6366F1 0%, #A855F7 100%)"
    total_gradient = "linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%)"
elif current_theme == "파스텔 모드":
    bg_css = "background-color: #FDF4F5; color: #4A4E69;"
    card_css = "background: #FFFFFF; color: #4A4E69; border: 1px solid #F4ACB7; box-shadow: 0 4px 10px rgba(244,172,183,0.2);"
    header_gradient = "linear-gradient(135deg, #FFB5A7 0%, #FCD5CE 100%)"
    total_gradient = "linear-gradient(135deg, #F4ACB7 0%, #FFCAD4 50%, #B5E2FA 100%)"
else:  # 다크 모드 (기본)
    bg_css = "background-color: #0F172A; color: #F8FAFC;"
    card_css = "background: rgba(30, 41, 59, 0.7); color: #F8FAFC; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(12px);"
    header_gradient = "linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)"
    total_gradient = "linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #EC4899 100%)"

st.markdown(f"""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * {{ font-family: 'Pretendard', -apple-system, sans-serif; }}
    
    .stApp {{ {bg_css} }}
    
    .ios-card {{
        {card_css}
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.2s ease;
    }}
    .ios-card:hover {{ transform: translateY(-2px); }}
    
    .banner-box {{
        background: {header_gradient};
        color: white;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.4);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    /* 그라데이션 타이틀 & 카드 스타일 */
    .gradient-total-card {{
        background: {total_gradient};
        color: white;
        border-radius: 20px;
        padding: 20px 28px;
        margin-top: 10px;
        margin-bottom: 25px;
        box-shadow: 0 12px 30px -8px rgba(124, 58, 237, 0.45);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    .gradient-header-text {{
        background: {header_gradient};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 22px;
        display: inline-block;
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. 사이드바 (설정 & 과목 추가)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ 스터디 설정")
    
    st.session_state.theme = st.selectbox(
        "🎨 앱 테마 선택", 
        ["다크 모드", "라이트 모드", "파스텔 모드"], 
        index=["다크 모드", "라이트 모드", "파스텔 모드"].index(st.session_state.theme)
    )

    with st.expander("👤 학생 및 지필고사 정보", expanded=True):
        school = st.text_input("학교명", value=st.session_state.student_info["school"], placeholder="예: OO고등학교")
        col_g, col_c = st.columns(2)
        with col_g:
            grade = st.text_input("학년", value=st.session_state.student_info["grade"], placeholder="예: 2학년")
        with col_c:
            class_num = st.text_input("반", value=st.session_state.student_info["class_num"], placeholder="예: 8반")
        name = st.text_input("이름", value=st.session_state.student_info["name"], placeholder="예: 한건우")
        
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
            st.success("정보가 저장되었습니다.")
            st.rerun()

    st.markdown("---")
    st.subheader("➕ 과목 등록")
    with st.form("add_subject_form", clear_on_submit=True):
        sub_name = st.text_input("과목명", placeholder="예: 수학 II, 영어")
        target_hours = st.number_input("목표 공부 시간 (시간)", min_value=1, max_value=300, value=10)
        sub_color = st.color_picker("과목 대표 색상", value="#6366F1")
        
        btn_add = st.form_submit_button("과목 등록하기", use_container_width=True)
        if btn_add:
            if not sub_name.strip():
                st.error("과목 이름을 입력해 주세요.")
            else:
                new_id = max([s["id"] for s in st.session_state.subjects], default=0) + 1
                st.session_state.subjects.append({
                    "id": new_id,
                    "name": sub_name,
                    "target_hours": target_hours,
                    "logged_seconds": 0,
                    "color": sub_color
                })
                st.success(f"'{sub_name}' 등록 완료!")
                st.rerun()

# -----------------------------------------------------------------------------
# 5. 그래픽 메인 배너
# -----------------------------------------------------------------------------
QUOTES = [
    "“지금 자면 꿈을 꾸지만, 지금 공부하면 꿈을 이룬다.”",
    "“성공은 매일 반복되는 작은 노력들의 합이다.”",
    "“오늘 흘린 땀은 내일의 배신을 하지 않는다.”",
    "“포기하고 싶을 때, 왜 시작했는지 생각하라.”"
]
quote_index = int(time.time() // 10) % len(QUOTES)

info = st.session_state.student_info
student_str = f"{info['school']} {info['grade']} {info['class_num']} {info['name']}".strip()
if not student_str:
    student_str = "사이드바에서 학생 정보와 지필고사 일을 설정하세요."

exam_d = info["exam_date"]
if exam_d is None:
    d_day_text = "D-Day 미설정"
else:
    today = datetime.date.today()
    d_day_val = (exam_d - today).days
    d_day_text = f"D-{d_day_val}" if d_day_val > 0 else ("D-DAY" if d_day_val == 0 else f"D+{abs(d_day_val)}")

st.markdown(f"""
<div class="banner-box">
    <div>
        <h1 style="margin: 0; font-size: 28px; font-weight: 800;">🍎 스터디플래너 AI</h1>
        <p style="margin: 6px 0 0 0; opacity: 0.9; font-size: 15px;">🏫 <b>{student_str}</b></p>
        <p style="margin: 10px 0 0 0; background: rgba(255,255,255,0.2); padding: 6px 14px; border-radius: 12px; font-size: 13px; display: inline-block;">
            💬 {QUOTES[quote_index]}
        </p>
    </div>
    <div style="text-align: right;">
        <div style="font-size: 14px; opacity: 0.85;">지필고사 카운트다운</div>
        <div style="font-size: 38px; font-weight: 900; letter-spacing: -1px;">{d_day_text}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. 그라데이션 커스텀 스타일이 전면 적용된 메인 영역
# -----------------------------------------------------------------------------
# [섹션 제목] 그라데이션 적용 텍스트
st.markdown('<div class="gradient-header-text">📊 오늘의 공부 타임라인 & 과목 스톱워치</div>', unsafe_allow_html=True)

if not st.session_state.subjects:
    st.info("등록된 과목이 없습니다. 왼쪽 사이드바에서 과목을 먼저 등록해 보세요!")
else:
    total_sec = sum(s.get("logged_seconds", 0) for s in st.session_state.subjects)
    
    sw = st.session_state.stopwatch
    if sw["running"]:
        live_elapsed = int(time.time() - sw["start_time"])
    else:
        live_elapsed = 0

    grand_total_sec = total_sec + sw["accumulated"] + live_elapsed
    g_h, g_m, g_s = grand_total_sec // 3600, (grand_total_sec % 3600) // 60, grand_total_sec % 60

    # [TOTAL TIME] 화려한 그라데이션 패널 카드
    st.markdown(f"""
    <div class="gradient-total-card">
        <div>
            <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.9; font-weight: 600;">Cumulative Time Today</div>
            <div style="font-size: 34px; font-weight: 900; font-family: monospace; letter-spacing: 1px; margin-top: 2px;">
                ⏱️ TOTAL TIME: {g_h:02d}시간 {g_m:02d}분 {g_s:02d}초
            </div>
        </div>
        <div style="background: rgba(255, 255, 255, 0.2); padding: 8px 18px; border-radius: 14px; font-size: 14px; font-weight: 700; backdrop-filter: blur(10px);">
            🔥 열공 중!
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    # [좌측] 과목별 누적 타임라인
    with col_left:
        st.markdown('<div class="gradient-header-text" style="font-size: 18px; margin-bottom: 12px;">⏱️ 과목별 누적 타임라인</div>', unsafe_allow_html=True)
        for sub in st.session_state.subjects:
            s_sec = sub.get("logged_seconds", 0)
            
            if sw["running"] and sw["active_sub_id"] == sub["id"]:
                s_sec += sw["accumulated"] + live_elapsed
            elif not sw["running"] and sw["active_sub_id"] == sub["id"]:
                s_sec += sw["accumulated"]

            s_h, s_m, s_s = s_sec // 3600, (s_sec % 3600) // 60, s_sec % 60
            bg_color = sub.get("color", "#6366F1")
            target_sec = sub["target_hours"] * 3600
            pct = min(round((s_sec / target_sec) * 100, 1), 100.0)

            st.markdown(f"""
            <div class="ios-card" style="border-left: 6px solid {bg_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; font-size: 17px;">{sub['name']}</span>
                    <span style="font-family: monospace; font-size: 18px; font-weight: 700; color: {bg_color};">
                        {s_h:02d}:{s_m:02d}:{s_s:02d}
                    </span>
                </div>
                <div style="margin-top: 10px; font-size: 12px; opacity: 0.8;">
                    목표: {sub['target_hours']}시간 중 {pct}% 달성
                </div>
            </div>
            """, unsafe_allow_html=True)

    # [우측] 파이썬 완전 연동 실시간 스톱워치
    with col_right:
        st.markdown('<div class="gradient-header-text" style="font-size: 18px; margin-bottom: 12px;">▶️ 실시간 과목 스톱워치</div>', unsafe_allow_html=True)
        
        sub_names = [s["name"] for s in st.session_state.subjects]
        selected_sub_name = st.selectbox("공부할 과목 선택", sub_names)
        selected_sub = next(s for s in st.session_state.subjects if s["name"] == selected_sub_name)
        sub_id = selected_sub["id"]

        is_current_active = (sw["active_sub_id"] == sub_id)
        current_display_sec = 0
        
        if is_current_active:
            current_display_sec = sw["accumulated"] + (int(time.time() - sw["start_time"]) if sw["running"] else 0)
        
        disp_h = current_display_sec // 3600
        disp_m = (current_display_sec % 3600) // 60
        disp_s = current_display_sec % 60

        # 실시간 스톱워치 디스플레이
        st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.08); border: 2px dashed #6366F1; border-radius: 20px; padding: 20px; text-align: center; margin-bottom: 15px;">
            <div style="font-size: 13px; opacity: 0.8; margin-bottom: 5px;">측정 중인 과목: <b>{selected_sub['name']}</b></div>
            <div style="font-size: 42px; font-weight: 900; font-family: monospace; color: #6366F1;">
                {disp_h:02d}:{disp_m:02d}:{disp_s:02d}
            </div>
        </div>
        """, unsafe_allow_html=True)

        btn_c1, btn_c2, btn_c3 = st.columns(3)

        with btn_c1:
            if not (sw["running"] and is_current_active):
                if st.button("▶️ 공부 시작", use_container_width=True):
                    if sw["active_sub_id"] != sub_id:
                        sw["active_sub_id"] = sub_id
                        sw["accumulated"] = 0
                    sw["running"] = True
                    sw["start_time"] = time.time()
                    st.rerun()
            else:
                if st.button("⏸️ 일시정지", use_container_width=True):
                    sw["accumulated"] += int(time.time() - sw["start_time"])
                    sw["running"] = False
                    st.rerun()

        with btn_c2:
            if st.button("💾 공부 기록 반영", use_container_width=True):
                if is_current_active:
                    if sw["running"]:
                        sw["accumulated"] += int(time.time() - sw["start_time"])
                        sw["running"] = False
                    selected_sub["logged_seconds"] += sw["accumulated"]
                    sw["accumulated"] = 0
                    sw["active_sub_id"] = None
                    st.success("공부 시간이 누적 기록에 성공적으로 저장되었습니다!")
                    st.rerun()
                else:
                    st.warning("측정된 공부 시간이 없습니다.")

        with btn_c3:
            if st.button("🗑️ 과목 삭제", use_container_width=True):
                if sw["active_sub_id"] == sub_id:
                    sw["running"] = False
                    sw["active_sub_id"] = None
                    sw["accumulated"] = 0
                st.session_state.subjects = [s for s in st.session_state.subjects if s["id"] != sub_id]
                st.rerun()

        if sw["running"]:
            time.sleep(1)
            st.rerun()

# -----------------------------------------------------------------------------
# 7. Gemini AI 맞춤 학습 피드백
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown('<div class="gradient-header-text" style="font-size: 20px; margin-bottom: 15px;">🤖 AI 맞춤 공부 진단</div>', unsafe_allow_html=True)
if st.button("현재 학습 데이터 기반 AI 코칭받기"):
    if not st.session_state.subjects:
        st.warning("과목을 먼저 등록해 주세요.")
    else:
        st.success("📊 학습 진행 데이터 분석 결과:")
        for s in st.session_state.subjects:
            s_sec = s.get("logged_seconds", 0)
            target = s.get("target_hours", 10)
            hrs = round(s_sec / 3600, 1)
            pct = min(round((hrs / target) * 100, 1), 100.0)
            st.write(f"- **{s['name']}**: 목표 {target}시간 중 현재 **{hrs}시간**({pct}%) 달성하였습니다.")
