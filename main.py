import streamlit as st
import datetime
import time
from google import genai

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
    st.session_state.theme = "라이트 모드"

if "stopwatch" not in st.session_state:
    st.session_state.stopwatch = {
        "active_sub_id": None,
        "running": False,
        "start_time": 0,
        "accumulated": 0
    }

if "omr_results" not in st.session_state:
    st.session_state.omr_results = {}

# -----------------------------------------------------------------------------
# 3. 테마 별 동적 적용 (라이트 모드 & 파스텔 모드)
# -----------------------------------------------------------------------------
current_theme = st.session_state.theme

if current_theme == "파스텔 모드":
    bg_css = "background-color: #FDF4F5; color: #33272A;"
    card_css = "background: #FFFFFF; color: #33272A; border: 1px solid #F4ACB7; box-shadow: 0 4px 12px rgba(244,172,183,0.25);"
    text_color = "#33272A"
    sub_text_color = "#5C4D51"
    header_gradient = "linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%)"
    total_gradient = "linear-gradient(135deg, #FFB5A7 0%, #FFCAD4 50%, #B5E2FA 100%)"
    timer_box_bg = "background: #FFF0F3; border: 2px dashed #FFB5A7;"
    timer_text_color = "#E07A5F"
else:  # 라이트 모드 (기본)
    bg_css = "background-color: #F8FAFC; color: #0F172A;"
    card_css = "background: #FFFFFF; color: #0F172A; border: 1px solid #E2E8F0; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);"
    text_color = "#0F172A"
    sub_text_color = "#475569"
    header_gradient = "linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)"
    total_gradient = "linear-gradient(135deg, #2563EB 0%, #7C3AED 50%, #DB2777 100%)"
    timer_box_bg = "background: #EFF6FF; border: 2px dashed #3B82F6;"
    timer_text_color = "#1D4ED8"

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
        color: white !important;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    .gradient-total-card {{
        background: {total_gradient};
        color: white !important;
        border-radius: 20px;
        padding: 20px 28px;
        margin-top: 10px;
        margin-bottom: 25px;
        box-shadow: 0 12px 30px -8px rgba(37, 99, 235, 0.35);
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
    
    .quote-animated {{
        animation: fadeIn 1s ease-in-out;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(4px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .danger-badge-high {{ background: #DC2626; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 12px; }}
    .danger-badge-mid {{ background: #D97706; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 12px; }}
    .danger-badge-low {{ background: #059669; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 12px; }}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. 사이드바 (테마 설정, 학생 정보, BGM 백색소음 플레이어, 과목 추가)
# -----------------------------------------------------------------------------
def on_theme_change():
    st.session_state.theme = st.session_state.theme_select

with st.sidebar:
    st.title("⚙️ 스터디 설정")
    
    # 테마 선택
    st.selectbox(
        "🎨 앱 테마 선택", 
        ["라이트 모드", "파스텔 모드"], 
        index=0 if st.session_state.theme == "라이트 모드" else 1,
        key="theme_select",
        on_change=on_theme_change
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
            st.success("학생 정보가 저장되었습니다!")
            st.rerun()

    # --- 🎧 집중 BGM / 백색소음 ---
    st.markdown("---")
    st.subheader("🎧 집중 BGM & 백색소음")
    bgm_dict = {
        "끄기 🔇": None,
        "🎹 잔잔한 피아노 음악": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "🌧️ 차분한 빗소리": "https://assets.mixkit.co/active_storage/sfx/2515/2515-preview.mp3",
        "🌊 잔잔한 파도 소리": "https://assets.mixkit.co/active_storage/sfx/1188/1188-preview.mp3",
        "🔥 따뜻한 모닥불 소리": "https://assets.mixkit.co/active_storage/sfx/2670/2670-preview.mp3",
        "☕ 아늑한 카페 소음": "https://assets.mixkit.co/active_storage/sfx/350/350-preview.mp3"
    }
    
    selected_bgm = st.selectbox("배경음 선택", list(bgm_dict.keys()))
    if bgm_dict[selected_bgm]:
        st.audio(bgm_dict[selected_bgm], format="audio/mp3", loop=True)

    # 과목 등록
    st.markdown("---")
    st.subheader("➕ 과목 등록")
    with st.form("add_subject_form", clear_on_submit=True):
        sub_name = st.text_input("과목명", placeholder="예: 수학 II, 영어")
        target_hours = st.number_input("목표 공부 시간 (시간)", min_value=1, max_value=300, value=10)
        sub_color = st.color_picker("과목 대표 색상", value="#2563EB")
        
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
# 5. 메인 헤더 배너
# -----------------------------------------------------------------------------
QUOTES = [
    "“지금 자면 꿈을 꾸지만, 지금 공부하면 꿈을 이룬다.”",
    "“성공은 매일 반복되는 작은 노력들의 합이다.”",
    "“오늘 흘린 땀은 내일의 배신을 하지 않는다.”",
    "“포기하고 싶을 때, 왜 시작했는지 생각하라.”",
    "“오늘 할 수 있는 일에 집중하는 것이 미래를 만드는 길이다.”"
]
quote_index = int(time.time() // 5) % len(QUOTES)

info = st.session_state.student_info

info_parts = [
    info["school"].strip() if info["school"] else "",
    info["grade"].strip() if info["grade"] else "",
    info["class_num"].strip() if info["class_num"] else "",
    info["name"].strip() if info["name"] else ""
]
student_str = " ".join([p for p in info_parts if p])

if not student_str:
    student_str = "사이드바에서 학생 정보와 지필고사 일을 설정하세요."
else:
    student_str = f"🏫 {student_str}"

exam_d = info["exam_date"]
if exam_d is None:
    d_day_text = "D-Day 미설정"
    d_day_val = 14
else:
    today = datetime.date.today()
    d_day_val = (exam_d - today).days
    d_day_text = f"D-{d_day_val}" if d_day_val > 0 else ("D-DAY" if d_day_val == 0 else f"D+{abs(d_day_val)}")

st.markdown(f"""
<div class="banner-box">
    <div>
        <h1 style="margin: 0; font-size: 28px; font-weight: 800; color: white;">🍎 스터디플래너 AI</h1>
        <p style="margin: 6px 0 0 0; opacity: 0.95; font-size: 15px; color: white;"><b>{student_str}</b></p>
        <p class="quote-animated" style="margin: 10px 0 0 0; background: rgba(255,255,255,0.2); padding: 6px 14px; border-radius: 12px; font-size: 13px; display: inline-block; color: white;">
            💬 {QUOTES[quote_index]}
        </p>
    </div>
    <div style="text-align: right; color: white;">
        <div style="font-size: 14px; opacity: 0.9;">지필고사 카운트다운</div>
        <div style="font-size: 38px; font-weight: 900; letter-spacing: -1px; color: white;">{d_day_text}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. 메인 기능 탭
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["⏱️ 스톱워치 & 타임라인", "🚨 AI 벼락치기 위험도 계산기", "📝 OMR 가채점 & 오답 진단"])

# TAB 1: 스톱워치 & 타임라인
with tab1:
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

        st.markdown(f"""
        <div class="gradient-total-card">
            <div>
                <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.9; font-weight: 600; color: white;">Cumulative Time Today</div>
                <div style="font-size: 34px; font-weight: 900; font-family: monospace; letter-spacing: 1px; margin-top: 2px; color: white;">
                    ⏱️ TOTAL TIME: {g_h:02d}시간 {g_m:02d}분 {g_s:02d}초
                </div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.25); color: white; padding: 8px 18px; border-radius: 14px; font-size: 14px; font-weight: 700;">
                🔥 열공 중!
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1])

        # 좌측: 과목별 누적 타임라인 + 과목 수정/삭제 기능
        with col_left:
            st.markdown('<div class="gradient-header-text" style="font-size: 18px; margin-bottom: 12px;">⏱️ 과목별 누적 타임라인</div>', unsafe_allow_html=True)
            for sub in st.session_state.subjects:
                s_sec = sub.get("logged_seconds", 0)
                
                if sw["running"] and sw["active_sub_id"] == sub["id"]:
                    s_sec += sw["accumulated"] + live_elapsed
                elif not sw["running"] and sw["active_sub_id"] == sub["id"]:
                    s_sec += sw["accumulated"]

                s_h, s_m, s_s = s_sec // 3600, (s_sec % 3600) // 60, s_sec % 60
                bg_color = sub.get("color", "#2563EB")
                target_sec = sub["target_hours"] * 3600
                pct = min(round((s_sec / target_sec) * 100, 1), 100.0)

                st.markdown(f"""
                <div class="ios-card" style="border-left: 6px solid {bg_color}; padding-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; font-size: 17px; color: {text_color};">{sub['name']}</span>
                        <span style="font-family: monospace; font-size: 18px; font-weight: 700; color: {bg_color};">
                            {s_h:02d}:{s_m:02d}:{s_s:02d}
                        </span>
                    </div>
                    <div style="margin-top: 10px; font-size: 13px; color: {sub_text_color};">
                        목표: {sub['target_hours']}시간 중 {pct}% 달성
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 카드별 수정 / 삭제 옵션
                with st.expander(f"✏️ '{sub['name']}' 정보 수정 및 삭제"):
                    edit_name = st.text_input("과목명 변경", value=sub["name"], key=f"edit_name_{sub['id']}")
                    edit_target = st.number_input("목표 시간 변경 (시간)", min_value=1, max_value=300, value=int(sub["target_hours"]), key=f"edit_target_{sub['id']}")
                    edit_color = st.color_picker("색상 변경", value=sub.get("color", "#2563EB"), key=f"edit_color_{sub['id']}")
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button("수정 저장", key=f"save_btn_{sub['id']}", use_container_width=True):
                            sub["name"] = edit_name
                            sub["target_hours"] = edit_target
                            sub["color"] = edit_color
                            st.success("수정되었습니다.")
                            st.rerun()
                    with c_btn2:
                        if st.button("과목 삭제 🗑️", key=f"del_btn_{sub['id']}", use_container_width=True):
                            if sw["active_sub_id"] == sub["id"]:
                                sw["running"] = False
                                sw["active_sub_id"] = None
                                sw["accumulated"] = 0
                            st.session_state.subjects = [s for s in st.session_state.subjects if s["id"] != sub["id"]]
                            st.success("삭제되었습니다.")
                            st.rerun()

        # 우측: 실시간 과목 스톱워치 (삭제 버튼 제거)
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

            st.markdown(f"""
            <div style="{timer_box_bg} border-radius: 20px; padding: 20px; text-align: center; margin-bottom: 15px;">
                <div style="font-size: 13px; color: {sub_text_color}; margin-bottom: 5px;">측정 중인 과목: <b style="color: {text_color};">{selected_sub['name']}</b></div>
                <div style="font-size: 42px; font-weight: 900; font-family: monospace; color: {timer_text_color};">
                    {disp_h:02d}:{disp_m:02d}:{disp_s:02d}
                </div>
            </div>
            """, unsafe_allow_html=True)

            btn_c1, btn_c2 = st.columns(2)

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
                        st.success("공부 시간이 누적 기록에 저장되었습니다!")
                        st.rerun()
                    else:
                        st.warning("측정된 공부 시간이 없습니다.")

        # --- 과목별 공부 시간 일일 분석 그래프 ---
        st.markdown("---")
        st.markdown('<div class="gradient-header-text" style="font-size: 18px; margin-bottom: 12px;">📈 과목별 일일 공부 시간 분석 (분 단위)</div>', unsafe_allow_html=True)
        
        chart_data = {}
        for sub in st.session_state.subjects:
            sec = sub.get("logged_seconds", 0)
            if sw["running"] and sw["active_sub_id"] == sub["id"]:
                sec += sw["accumulated"] + live_elapsed
            elif not sw["running"] and sw["active_sub_id"] == sub["id"]:
                sec += sw["accumulated"]
            
            # 분 단위 연산 (소수점 1자리)
            chart_data[sub["name"]] = round(sec / 60, 1)

        st.bar_chart(chart_data)

        if sw["running"]:
            time.sleep(1)
            st.rerun()

# TAB 2: AI 벼락치기 위험도 계산기
with tab2:
    st.markdown('<div class="gradient-header-text">🚨 AI 벼락치기 위험도 진단 및 분석기</div>', unsafe_allow_html=True)
    st.caption("남은 D-Day와 목표 시간 대비 달성률을 알고리즘으로 연산하여 과목별 위험 지수를 측정합니다.")

    if not st.session_state.subjects:
        st.info("등록된 과목이 없습니다. 사이드바에서 과목을 먼저 등록해 보세요.")
    else:
        for sub in st.session_state.subjects:
            target_sec = sub["target_hours"] * 3600
            logged_sec = sub.get("logged_seconds", 0)
            
            progress_ratio = min(logged_sec / target_sec, 1.0) if target_sec > 0 else 0
            safe_dday = max(d_day_val, 1)
            risk_score = min(round((1.0 - progress_ratio) * (10 / safe_dday) * 100, 1), 100.0)
            
            if risk_score >= 70:
                badge_html = '<span class="danger-badge-high">🚨 위험도 비상</span>'
            elif risk_score >= 40:
                badge_html = '<span class="danger-badge-mid">⚠️ 주의 필요</span>'
            else:
                badge_html = '<span class="danger-badge-low">✅ 안전권</span>'

            st.markdown(f"""
            <div class="ios-card" style="border-left: 6px solid {sub.get('color', '#2563EB')};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 800; font-size: 18px; color: {text_color};">{sub['name']}</span>
                    <div>{badge_html}</div>
                </div>
                <div style="margin-top: 10px;">
                    <div style="font-size: 14px; color: {sub_text_color};">
                        벼락치기 위험 지수: <b style="font-size: 18px; color: #DB2777;">{risk_score}%</b>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# TAB 3: OMR 가채점 & 오답 진단
with tab3:
    st.markdown('<div class="gradient-header-text">📝 시험 후 OMR 가채점 & 오답 패턴 진단</div>', unsafe_allow_html=True)
    st.caption("시험 종료 후 가채점을 진행하고, 자주 틀리는 오답 이유를 분석합니다.")

    if not st.session_state.subjects:
        st.info("등록된 과목이 없습니다. 사이드바에서 과목을 먼저 등록해 보세요.")
    else:
        target_omr_sub = st.selectbox("가채점할 과목 선택", [s["name"] for s in st.session_state.subjects])
        
        col_omr1, col_omr2 = st.columns([1, 1])
        
        with col_omr1:
            st.markdown("#### 📥 가채점 점수 및 오답 유형 입력")
            with st.form("omr_form"):
                score_input = st.number_input("시험 가채점 점수 (점)", min_value=0, max_value=100, value=85)
                error_types = st.multiselect(
                    "주요 틀린 원인 (복수 선택)",
                    ["개념 이해 부족", "시간 부족으로 찍음", "계산/단순 실수", "문제 잘못 읽음", "고난도 응용 문제"]
                )
                submit_omr = st.form_submit_button("가채점 데이터 등록", use_container_width=True)
                
                if submit_omr:
                    st.session_state.omr_results[target_omr_sub] = {
                        "score": score_input,
                        "errors": error_types
                    }
                    st.success(f"'{target_omr_sub}' 채점 결과가 저장되었습니다!")

        with col_omr2:
            st.markdown("#### 🩺 저장된 OMR 리포트")
            if target_omr_sub in st.session_state.omr_results:
                res = st.session_state.omr_results[target_omr_sub]
                st.markdown(f"""
                <div class="ios-card">
                    <h3 style="margin: 0; color: #2563EB;">🎯 {target_omr_sub} 채점 결과</h3>
                    <p style="font-size: 20px; font-weight: 800; margin-top: 8px; color: {text_color};">점수: {res['score']}점</p>
                    <hr style="opacity: 0.2; margin: 10px 0;">
                    <p style="font-size: 14px; color: {sub_text_color};"><b>주요 감점 요인:</b> {', '.join(res['errors']) if res['errors'] else '없음'}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("왼쪽 폼에서 가채점 결과를 등록하면 저장됩니다.")

# -----------------------------------------------------------------------------
# 7. Gemini API 기반 1:1 맞춤 피드백
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown('<div class="gradient-header-text" style="font-size: 20px; margin-bottom: 15px;">🤖 실시간 Gemini AI 1:1 맞춤 피드백</div>', unsafe_allow_html=True)

if st.button("✨ Gemini AI 실시간 맞춤 조언 및 학습 처방전 받기", use_container_width=True):
    if not st.session_state.subjects:
        st.warning("과목을 먼저 등록해 주세요.")
    else:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        
        if not api_key:
            st.error("⚠️ Streamlit Secrets 설정에 'GEMINI_API_KEY'가 설정되지 않았습니다. 관리자 설정(Secrets)을 확인해주세요.")
        else:
            with st.spinner("🧠 Gemini AI가 학습 데이터를 분석하여 맞춤 처방전을 생성 중입니다..."):
                data_summary = []
                for s in st.session_state.subjects:
                    logged_h = round(s.get("logged_seconds", 0) / 3600, 1)
                    target_h = s.get("target_hours", 10)
                    omr = st.session_state.omr_results.get(s["name"], None)
                    omr_str = f", OMR가채점점수: {omr['score']}점, 주요감점원인: {', '.join(omr['errors'])}" if omr else ""
                    data_summary.append(f"- 과목: {s['name']} (목표: {target_h}시간 중 현재 {logged_h}시간 달성{omr_str})")
                
                prompt = f"""
                당신은 고등학생을 위한 친절하고 명확한 전문 학습 코치 AI입니다.
                다음 학생의 지필고사 학습 데이터를 기반으로 동기부여와 함께 실질적이고 구체적인 과목별 맞춤 공부 조언을 제공해 주세요.

                [학생 정보]
                - 학생: {student_str}
                - 지필고사 카운트다운: {d_day_text} (D-Day)
                - 과목별 학습 현황:
                {chr(10).join(data_summary)}

                [작성 지침]
                1. 고정 템플릿 멘트를 피하고 학생 맞춤형으로 작성하세요.
                2. 현재 남아있는 D-Day 대비 진척도가 부족한 과목을 우선 짚어주고, 공부 순서 및 전략을 제시하세요.
                3. OMR 오답 원인(계산 실수, 시간 부족 등)이 있다면 실용적인 꿀팁을 포함해 주세요.
                4. 고등학생 친화적인 어조로 용기를 북돋아 주도록 3~4문단 정도로 작성해 주세요.
                """

                client = genai.Client(api_key=api_key)
                response = None
                max_retries = 3
                
                for attempt in range(max_retries):
                    try:
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=prompt,
                        )
                        break
                    except Exception as e:
                        if "503" in str(e) and attempt < max_retries - 1:
                            time.sleep(2)
                            continue
                        else:
                            st.error(f"AI 조언 생성 중 오류가 발생했습니다: {e}")
                            break

                if response and hasattr(response, 'text'):
                    st.markdown(f"""
                    <div class="ios-card" style="border-left: 6px solid #8B5CF6; margin-top: 15px;">
                        <h4 style="margin-top:0; color:#8B5CF6;">🤖 Gemini AI의 맞춤 학습 처방전</h4>
                        <div style="line-height: 1.7; font-size: 15px;">
                            {response.text}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
