import streamlit as st
import datetime
import pandas as pd

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 초기화
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="스터디플래너 AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if "subjects" not in st.session_state:
    st.session_state.subjects = [
        {
            "id": 1,
            "name": "국어",
            "exam_date": datetime.date.today() + datetime.timedelta(days=14),
            "target_score": 90,
            "target_hours": 20,
            "logged_minutes": 180,
            "color": "#3B82F6"
        },
        {
            "id": 2,
            "name": "수학",
            "exam_date": datetime.date.today() + datetime.timedelta(days=18),
            "target_score": 95,
            "target_hours": 30,
            "logged_minutes": 450,
            "color": "#10B981"
        },
        {
            "id": 3,
            "name": "영어",
            "exam_date": datetime.date.today() + datetime.timedelta(days=21),
            "target_score": 88,
            "target_hours": 15,
            "logged_minutes": 120,
            "color": "#F59E0B"
        }
    ]

if "school_info" not in st.session_state:
    st.session_state.school_info = {
        "school": "고등학교",
        "grade": "2학년",
        "class_num": "8반",
        "student_name": "한건우"
    }

# -----------------------------------------------------------------------------
# 2. 사이드바 (설정 및 과목 추가)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ 설정 및 과목 관리")
    
    # 테마/프로필 정보
    with st.expander("👤 학생 정보 설정", expanded=False):
        school = st.text_input("학교명", st.session_state.school_info["school"])
        grade = st.selectbox("학년", ["1학년", "2학년", "3학년"], index=1)
        class_num = st.text_input("반", st.session_state.school_info["class_num"])
        name = st.text_input("이름", st.session_state.school_info["student_name"])
        
        if st.button("학생 정보 저장"):
            st.session_state.school_info = {
                "school": school,
                "grade": grade,
                "class_num": class_num,
                "student_name": name
            }
            st.success("정보가 저장되었습니다!")

    st.markdown("---")
    st.subheader("➕ 새 과목 추가")
    
    with st.form("add_subject_form", clear_on_submit=True):
        new_name = st.text_input("과목 이름", placeholder="예: 물리학 I")
        new_date = st.date_input("시험일 (D-Day)", value=datetime.date.today() + datetime.timedelta(days=10))
        new_score = st.number_input("목표 점수 (점)", min_value=0, max_value=100, value=90)
        new_hours = st.number_input("목표 공부 시간 (시간)", min_value=1, max_value=200, value=10)
        
        submit = st.form_submit_button("과목 추가하기")
        if submit:
            if new_name.strip() == "":
                st.error("과목 이름을 입력해주세요.")
            else:
                new_id = max([s["id"] for s in st.session_state.subjects], default=0) + 1
                st.session_state.subjects.append({
                    "id": new_id,
                    "name": new_name,
                    "exam_date": new_date,
                    "target_score": new_score,
                    "target_hours": new_hours,
                    "logged_minutes": 0,
                    "color": "#8B5CF6"
                })
                st.success(f"'{new_name}' 과목이 추가되었습니다!")
                st.rerun()

# -----------------------------------------------------------------------------
# 3. 메인 화면
# -----------------------------------------------------------------------------
st.title("📚 스터디플래너 AI")
st.caption(f"📍 {st.session_state.school_info['school']} {st.session_state.school_info['grade']} {st.session_state.school_info['class_num']} {st.session_state.school_info['student_name']} 학생의 맞춤 플래너")

# 전체 요약 통계
col1, col2, col3, col4 = st.columns(4)

total_target_hours = sum(s["target_hours"] for s in st.session_state.subjects)
total_logged_hours = round(sum(s["logged_minutes"] for s in st.session_state.subjects) / 60, 1)
overall_progress = round((total_logged_hours / total_target_hours * 100), 1) if total_target_hours > 0 else 0

with col1:
    st.metric("등록 과목 수", f"{len(st.session_state.subjects)}개")
with col2:
    st.metric("총 목표 공부시간", f"{total_target_hours}시간")
with col3:
    st.metric("현재 달성 공부시간", f"{total_logged_hours}시간")
with col4:
    st.metric("전체 달성률", f"{overall_progress}%")

st.markdown("---")

# -----------------------------------------------------------------------------
# 4. 과목 목록 카드 및 진행률
# -----------------------------------------------------------------------------
st.subheader("📖 과목별 학습 현황")

if not st.session_state.subjects:
    st.info("왼쪽 사이드바에서 새 과목을 추가해 보세요!")
else:
    for idx, sub in enumerate(st.session_state.subjects):
        with st.container():
            today = datetime.date.today()
            d_day = (sub["exam_date"] - today).days
            d_day_str = f"D-{d_day}" if d_day > 0 else ("D-Day" if d_day == 0 else f"D+{abs(d_day)}")
            
            logged_hours = round(sub["logged_minutes"] / 60, 1)
            progress = min(round((logged_hours / sub["target_hours"]) * 100, 1), 100.0)
            
            c1, c2, c3 = st.columns([3, 2, 1])
            
            with c1:
                st.markdown(f"### {sub['name']}  `{d_day_str}`")
                st.write(f"📅 **시험일**: {sub['exam_date'].strftime('%Y-%m-%d')} | 🎯 **목표 점수**: {sub['target_score']}점")
                st.write(f"⏱️ **공부 시간**: {logged_hours}시간 / {sub['target_hours']}시간")
                st.progress(progress / 100)
                st.caption(f"학습 진행률: {progress}%")
                
            with c2:
                st.markdown("**⏱️ 공부 시간 기록 (분 단위)**")
                add_mins = st.number_input("추가할 시간(분)", min_value=5, max_value=300, step=5, key=f"add_min_{sub['id']}")
                if st.button("공부 시간 더하기", key=f"btn_add_{sub['id']}"):
                    sub["logged_minutes"] += add_mins
                    st.success(f"{add_mins}분이 추가되었습니다.")
                    st.rerun()

            with c3:
                st.markdown("**✏️ 과목 설정**")
                if st.button("삭제", key=f"del_{sub['id']}", type="secondary"):
                    st.session_state.subjects.pop(idx)
                    st.rerun()

            st.markdown("---")

# -----------------------------------------------------------------------------
# 5. AI 학습 가이드 코칭
# -----------------------------------------------------------------------------
st.subheader("💡 Gemini AI 학습 코칭")

if st.button("🤖 AI 학습 진단 및 조언 받기"):
    if not st.session_state.subjects:
        st.warning("등록된 과목이 없습니다.")
    else:
        st.info("📊 과목별 진행 상황을 분석하는 중입니다...")
        
        # 가상 AI 피드백 생성
        advice = []
        for s in st.session_state.subjects:
            d_day = (s["exam_date"] - datetime.date.today()).days
            progress = (s["logged_minutes"] / 60) / s["target_hours"] * 100
            
            if d_day <= 7 and progress < 50:
                advice.append(f"⚠️ **{s['name']}**: 시험이 일주일 남았지만 진행률이 {progress:.0f}%입니다. 개념 핵심 요약 중심으로 집중 학습이 필요합니다.")
            elif progress >= 80:
                advice.append(f"✅ **{s['name']}**: 목표 달성률({progress:.0f}%)이 높습니다! 기출문제 풀이 및 오답 노트 위주로 정리하세요.")
            else:
                advice.append(f"📘 **{s['name']}**: 차근차근 계획대로 진행 중입니다. 매일 1~2시간씩 꾸준히 유지하세요.")
                
        for a in advice:
            st.write(a)
