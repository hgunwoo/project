import streamlit as st
import datetime
import time
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# 1. 페이지 세팅 및 아이폰 감성 CSS 스타일링
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="스터디플래너 AI",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# iOS 스타일 테마 CSS 적용
st.markdown("""
<style>
    /* 전체 폰트 및 배경 깔끔하게 설정 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    /* 카드 및 컨테이너 iOS 글래스모피즘 디자인 */
    .ios-card {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .ios-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.25);
    }
    
    /* 아이폰 Badge 디자인 */
    .ios-badge {
        background: linear-gradient(135deg, #6366F1 0%, #a855f7 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
    }
    
    /* 애니메이션 들어간 텍스트 */
    .quote-box {
        background: rgba(99, 102, 241, 0.1);
        border-left: 4px solid #6366F1;
        padding: 12px 18px;
        border-radius: 12px;
        font-size: 15px;
        font-weight: 500;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

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

# -----------------------------------------------------------------------------
# 3. 사이드바 (설정 & 과목 추가)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ 스터디 설정")
    
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
            st.success("설정이 저장되었습니다.")
            st.rerun()

    st.markdown("---")
    st.subheader("➕ 과목 등록")
    with st.form("add_subject_form", clear_on_submit=True):
        sub_name = st.text_input("과목명", placeholder="예: 수학 II, 영어")
        target_hours = st.number_input("목표 공부 시간 (시간)", min_value=1, max_value=300, value=10)
        sub_color = st.color_picker("과목 테마 색상", value="#6366F1")
        
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
# 4. 헤더 및 D-Day 영역
# -----------------------------------------------------------------------------
QUOTES = [
    "“지금 자면 꿈을 꾸지만, 지금 공부하면 꿈을 이룬다.”",
    "“성공은 매일 반복되는 작은 노력들의 합이다.”",
    "“오늘 흘린 땀은 내일의 배신을 하지 않는다.”",
    "“시작하는 방법은 말하기를 그만두고 행동하는 것이다.”",
    "“포기하고 싶을 때, 왜 시작했는지 생각하라.”"
]
quote_index = int(time.time() // 10) % len(QUOTES)
st.markdown(f'<div class="quote-box">💬 {QUOTES[quote_index]}</div>', unsafe_allow_html=True)

info = st.session_state.student_info
student_str = f"{info['school']} {info['grade']} {info['class_num']} {info['name']}".strip()
if not student_str:
    student_str = "사이드바에서 학생 정보를 설정해 주세요."

exam_d = info["exam_date"]
if exam_d is None:
    d_day_text = "미설정"
    delta_sub = "시험일을 설정해 주세요"
else:
    today = datetime.date.today()
    d_day_val = (exam_d - today).days
    d_day_text = f"D-{d_day_val}" if d_day_val > 0 else ("D-DAY" if d_day_val == 0 else f"D+{abs(d_day_val)}")
    delta_sub = f"시험일: {exam_d.strftime('%m/%d')}"

c_head1, c_head2 = st.columns([3, 1])
with c_head1:
    st.title("🍎 스터디플래너 AI")
    st.caption(f"🏫 **{student_str}**")
with c_head2:
    st.metric("🎯 지필고사 D-Day", d_day_text, delta=delta_sub)

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. 메인 레이아웃: 과목 타임라인 + 아이폰 스타일 실시간 스톱워치
# -----------------------------------------------------------------------------
st.subheader("📊 오늘의 공부 타임라인 & 과목 스톱워치")

if not st.session_state.subjects:
    st.warning("등록된 과목이 없습니다. 왼쪽 사이드바에서 지필고사 공부 과목을 등록해 보세요!")
else:
    total_sec = sum(s.get("logged_seconds", 0) for s in st.session_state.subjects)
    total_h = total_sec // 3600
    total_m = (total_sec % 3600) // 60
    
    st.markdown(f"### 📅 TOTAL TIME: **{total_h}시간 {total_m}분**")
    
    col_left, col_right = st.columns([1, 1])
    
    # [좌측] 과목별 누적 공부 시간 목록
    with col_left:
        st.markdown("#### ⏱️ 과목별 누적 기록")
        for sub in st.session_state.subjects:
            s_sec = sub.get("logged_seconds", 0)
            s_h, s_m, s_s = s_sec // 3600, (s_sec % 3600) // 60, s_sec % 60
            bg_color = sub.get("color", "#6366F1")
            
            st.markdown(
                f"""
                <div class="ios-card" style="border-left: 6px solid {bg_color}; padding: 14px 18px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; font-size: 17px;">{sub['name']}</span>
                        <span style="font-family: monospace; font-size: 18px; font-weight: 600;">{s_h:02d}:{s_m:02d}:{s_s:02d}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # [우측] 아이폰 애니메이션 적용 실시간 초 단위 스톱워치 (JavaScript 기반)
    with col_right:
        st.markdown("#### ▶️ 실시간 스톱워치")
        selected_sub_name = st.selectbox("공부할 과목 선택", [s["name"] for s in st.session_state.subjects])
        selected_sub = next(s for s in st.session_state.subjects if s["name"] == selected_sub_name)
        
        # HTML/JS 실시간 카운팅 위젯
        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .timer-container {{
                    background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 24px;
                    padding: 24px;
                    text-align: center;
                    color: white;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                }}
                .display {{
                    font-size: 44px;
                    font-weight: 700;
                    font-family: monospace;
                    letter-spacing: 2px;
                    margin: 15px 0;
                    color: #A855F7;
                    text-shadow: 0 0 20px rgba(168, 85, 247, 0.4);
                }}
                .btn-group {{
                    display: flex;
                    gap: 10px;
                    justify-content: center;
                }}
                .ios-btn {{
                    border: none;
                    border-radius: 14px;
                    padding: 12px 24px;
                    font-weight: 600;
                    font-size: 15px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }}
                .start-btn {{ background: #10B981; color: white; }}
                .pause-btn {{ background: #EF4444; color: white; }}
                .reset-btn {{ background: rgba(255,255,255,0.2); color: white; }}
                .ios-btn:active {{ transform: scale(0.95); }}
            </style>
        </head>
        <body>
            <div class="timer-container">
                <div style="font-size: 14px; opacity: 0.8;">현재 측정과목: <b>{selected_sub['name']}</b></div>
                <div class="display" id="time-display">00:00:00</div>
                <div class="btn-group">
                    <button class="ios-btn start-btn" onclick="startTimer()">▶ 공부 시작</button>
                    <button class="ios-btn pause-btn" onclick="pauseTimer()">⏸ 일시정지</button>
                    <button class="ios-btn reset-btn" onclick="resetTimer()">⏹ 리셋</button>
                </div>
            </div>

            <script>
                let timer = null;
                let seconds = 0;

                function updateDisplay() {{
                    let hrs = Math.floor(seconds / 3600);
                    let mins = Math.floor((seconds % 3600) / 60);
                    let secs = seconds % 60;
                    document.getElementById('time-display').innerText = 
                        String(hrs).padStart(2, '0') + ':' + 
                        String(mins).padStart(2, '0') + ':' + 
                        String(secs).padStart(2, '0');
                }}

                function startTimer() {{
                    if (!timer) {{
                        timer = setInterval(() => {{
                            seconds++;
                            updateDisplay();
                        }}, 1000);
                    }}
                }}

                function pauseTimer() {{
                    if (timer) {{
                        clearInterval(timer);
                        timer = null;
                    }}
                }}

                function resetTimer() {{
                    pauseTimer();
                    seconds = 0;
                    updateDisplay();
                }}
            </script>
        </body>
        </html>
        """
        components.html(html_code, height=220)

        # 수동 저장 또는 타이머 결과 반영 버튼
        add_sec = st.number_input("측정한 시간 저장하기 (초 단위)", min_value=0, max_value=86400, value=0, step=60)
        if st.button("💾 측정된 시간 공부 기록에 반영", use_container_width=True):
            if add_sec > 0:
                selected_sub["logged_seconds"] += add_sec
                st.success(f"{add_sec}초가 성공적으로 추가되었습니다!")
                st.rerun()

        if st.button("🗑️ 과목 삭제", use_container_width=True):
            st.session_state.subjects = [s for s in st.session_state.subjects if s["id"] != selected_sub["id"]]
            st.rerun()

# -----------------------------------------------------------------------------
# 6. Gemini AI 학습 분석
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("🤖 AI 맞춤 공부 진단")
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
