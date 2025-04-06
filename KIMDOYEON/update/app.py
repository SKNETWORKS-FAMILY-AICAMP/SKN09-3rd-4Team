import streamlit as st
# from sentence_transformers import SentenceTransformer
import faiss  # 또는 chromadb 사용 가능
import numpy as np
import openai  # 또는 다른 LLM API
import datetime
import time
import datetime
from llm import run_llm_query, get_db_paths  # 외부 함수 호출

###########################
# 페이지 기본 구성 설정

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="보험 AI 챗봇", page_icon="💬")

st.title("🤖💬 보험 상담 챗봇")

# --- 챗봇 응답 생성 함수 (외부 LLM 함수 호출) ---
def get_bot_response(user_text, ins_name, ins_type):
    # 사용자가 택한 보험사 정보 -> DB 주소 설정
    faiss_path, meta_path = get_db_paths(ins_name, ins_type)

    # 사용자의 질문 & DB 주소 -> 응답 생성
    llm_response = run_llm_query(user_text, faiss_path, meta_path)

    return llm_response





###########################
# 사이드바 (보험사 입력 및 정보) 설정

# --- 사이드바 설정 ---
st.sidebar.header("보험 정보 선택")

# 보험사 및 상품 카테고리 목록
ins_name_list = ["AXA손해보험", "KB손해보험", "롯데손해보험", "하나손해보험"]
ins_type_list = ["", "자동차 보험", "일반 보험", "장기 보험"]

# 보험사 & 상품 선택 (각 1개만 선택)
ins_name = st.sidebar.selectbox("✅ 보험사 선택", ins_name_list)
ins_type = st.sidebar.selectbox("📦 보험 상품 선택", ins_type_list)

# 장기 보험일 경우 하위 카테고리 표시 (선택만 출력)
# if ins_type == "장기 보험":
#     sub_type = st.sidebar.selectbox("🔹 장기 보험 하위 카테고리", ["상해질병", "연금 저축", "기타"])
#     st.sidebar.markdown(f"선택한 하위 카테고리: **{sub_type}**")

# 선택한_보험사 = st.sidebar.multiselect("✅ 보험사 선택", 보험사_목록)
# 선택한_카테고리 = st.sidebar.selectbox("📦 보험 상품 선택", 보험_카테고리_목록)
# if 선택한_카테고리 == "장기 보험":
#     st.sidebar.selectbox("장기 보험 하위 카테고리",["상해질병","연금 저축","기타"])


# ---- 보험사 정보 ----
insurance_companies = {
    "하나손해보험": {
        "홈페이지": "https://www.hanainsure.co.kr/",
        "계약조회": "https://www.hanainsure.co.kr/w/myeducar/contractManage/insCrAllList",
        "보험금청구": "https://www.hanainsure.co.kr/w/myeducar/contractManage/renewalPrem",
        "연락처":"1566-3000"
    },
    "롯데손해보험": {
        "홈페이지": "https://www.lotteins.co.kr/web/main.jsp",
        "계약조회": "https://www.lotteins.co.kr/web/main.jsp#none",
        "보험금청구": "https://www.lotteins.co.kr/web/main.jsp#none",
        "연락처":"1588-3344"
    },
    "KB손해보험": {
        "홈페이지": "https://www.kbinsure.co.kr/main.ec?mdmn=0101",
        "계약조회": "https://www.kbinsure.co.kr/CG101010001.ec?mdmn=0202",
        "보험금청구": "https://www.kbinsure.co.kr/CG212010002.ec?mdmn=0202",
        "연락처":"1544-0114"
    },
    "AXA손해보험": {
        "홈페이지": "https://www.axa.co.kr/ActionControler.action?screenID=SHCM0000&actionID=I01",
        "계약조회": "https://www.axa.co.kr/ActionControler.action?screenID=SHOM0000&actionID=I03",
        "보험금청구": "https://www.axa.co.kr/ActionControler.action?screenID=SHOM0000&actionID=I03",
        "연락처":"1566-2266"
    }
}

# --- 사이드바 고객센터 안내 ---
if ins_name:
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"{ins_name} 바로가기")

    ins_link = insurance_companies[ins_name]  # 링크 정보 가져오기

    st.sidebar.link_button("🏠 홈페이지 이동", ins_link['홈페이지'])
    st.sidebar.link_button("📄 계약 조회하기", ins_link['계약조회'])
    st.sidebar.link_button("💰 보험금 청구하기", ins_link['보험금청구'])
    
    st.sidebar.markdown(f"📞 고객센터: **{ins_link['연락처']}**")


# ---- 피드백 기능 (선택사항) ----
st.sidebar.divider()
st.sidebar.subheader("🙋 챗봇 응답이 도움이 되었나요?")
# col1, col2 = st.sidebar.columns(2)
# with col1:
st.sidebar.button("도움이 되었어요 👍")
# with col2:
st.sidebar.button("잘 모르겠어요 👎")

# --- 도움말 안내 ---
st.sidebar.divider()
st.sidebar.markdown("<small>💡 정확한 보장을 위해 **보험사 공식 사이트**나 **상담사**를 통해 추가 문의하시는 걸 추천드립니다.</small>",
                    unsafe_allow_html=True)






###########################
# 채팅방 설정

# FAQ 사전 설정 (보험 타입별 2개)
faq_dict = {
    "자동차 보험": [
        "교통사고가 나면 보험 처리는 어떻게 하나요?",
        "렌터카 운전 중 사고 시 보장되나요?"
    ],
    "일반 보험": [
        "여행 중 물건을 잃어버리면 보장받을 수 있나요?",
        "일상생활 중 사고도 보장되나요?"
    ],
    "장기 보험": [
        "암 진단금은 얼마까지 받을 수 있나요?",
        "상해 입원 시 보험금 청구 방법은?"
    ]
}



# --- 세션 상태 초기화 ---
if "chat_hist" not in st.session_state:
    st.session_state.chat_hist = [
        {"role": "assistant", "content": "안녕하세요! 보험 AI 챗봇 보미입니다 😊\n\n먼저 왼쪽에서 보험사와 상품을 선택하고 '선택 완료' 버튼을 눌러주세요."}
    ]

if "ins_selected" not in st.session_state:
    st.session_state.ins_selected = False


if "fb_list" not in st.session_state:
    st.session_state.fb_list = []


# --- 사이드바 선택 ---
st.sidebar.header("보험 정보 선택")
ins_name_list = ["AXA손해보험", "KB손해보험", "롯데손해보험", "하나손해보험"]
ins_type_list = ["", "자동차 보험", "일반 보험", "장기 보험"]

ins_name = st.sidebar.selectbox("✅ 보험사 선택", ins_name_list)
ins_type = st.sidebar.selectbox("📦 보험 상품 선택", ins_type_list)

# 선택 완료 버튼
if st.sidebar.button("✅ 선택 완료"):
    if ins_name and ins_type:
        st.session_state.ins_selected = True
        st.session_state.chat_hist.append({
            "role": "assistant",
            "content": f"보험사: {ins_name}, 상품: {ins_type} 선택 완료 ✅\n\n이제 궁금한 점을 입력해주세요!"
        })

###########################
# 채팅방 작동


# --- 채팅 UI ---
st.title("🤖 보험 상담 챗봇 보미")

# 대화 출력
for chat in st.session_state.chat_hist:
    with st.chat_message(chat["role"], avatar=("👩‍🦰" if chat["role"] == "user" else "🤖")):
        st.markdown(chat["content"])

# --- 질문 입력창 및 FAQ 추천 ---
if st.session_state.ins_selected:
    if ins_type in faq_dict:
        st.markdown("#### 자주 묻는 질문")
        for q in faq_dict[ins_type]:
            if st.button(q):
                st.session_state.pending_question = q

    user_text = st.chat_input("궁금한 점을 입력해 주세요.", key="chat_input")

    if "pending_question" in st.session_state:
        user_text = st.session_state.pending_question
        del st.session_state.pending_question

    if user_text:
        # 사용자 질문 출력
        st.session_state.chat_hist.append({"role": "user", "content": user_text})
        with st.chat_message("user", avatar="👩‍🦰"):
            st.markdown(user_text)

        # 챗봇 응답 자리 표시
        with st.chat_message("assistant", avatar="🤖"):
            msg_area = st.empty()
            msg_area.markdown("...")

        # 답변 생성
        bot_text = get_bot_response(user_text, ins_name, ins_type)

        # 답변 출력
        msg_area.markdown(bot_text)
        st.session_state.chat_hist.append({"role": "assistant", "content": bot_text})

        # 👉 피드백 버튼
        col1, col2 = st.columns([1, 8])
        with col1:
            if st.button("👍 좋아요", key=f"like_{len(st.session_state.chat_hist)}"):
                st.session_state.fb_list.append({
                    "question": user_text,
                    "answer": bot_text,
                    "fb_type": "like"
                })
            if st.button("👎 싫어요", key=f"dislike_{len(st.session_state.chat_hist)}"):
                st.session_state.fb_list.append({
                    "question": user_text,
                    "answer": bot_text,
                    "fb_type": "dislike"
                })

# JSON 저장 버튼
if st.session_state.fb_list:
    if st.button("💾 피드백 JSON 저장"):
        file_name = "feedback_log.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(st.session_state.fb_list, f, ensure_ascii=False, indent=2)
        st.success(f"✅ 피드백이 '{file_name}' 파일로 저장되었습니다.")



# # 대화 기록 초기화
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []


# for chat in st.session_state.chat_history:
#     role = chat["role"]
#     name = "사용자" if role == "user" else "보미"
#     icon = "👩‍🦰" if role == "user" else "🤖"
    
#     # Streamlit이 인식하는 기본 역할 키워드 사용 ("user" or "assistant")
#     with st.chat_message("user" if role == "user" else "assistant", avatar=icon):
#         st.markdown(f"{chat['content']}")


# # 사용자 입력창
# if 선택한_보험사 and 선택한_카테고리:
#     user_input = st.chat_input("예: 제주도에서 렌터카 사고가 났을 때 보장받을 수 있나요?")
    
#     # 사용자 메세지 받음
#     if user_input:
#         # 사용자 메세지 출력
#         st.session_state.chat_history.append({"role": "user", "content": user_input})
#         with st.chat_message("user", avatar="👨‍🦰"):
#             st.markdown(user_input)


#         # 답변 자리 예약: "..." 출력
#         placeholder = st.empty()
#         with placeholder.container():
#             with st.chat_message("assistant", avatar="🤖"):
#                 msg_area = st.empty()
#                 msg_area.markdown("...")  # 로딩 중 표시

#         # 실제 답변 생성 중...
#         # time.sleep(0.5)
#         답변 = 챗봇응답생성(user_input, 선택한_보험사, 선택한_카테고리)
#         while not 답변:
#             time.sleep(0.1)

#         # "..." → 실제 답변으로 교체
#         placeholder.empty()  # 이전 assistant 메시지 제거
#         with st.chat_message("assistant", avatar="🤖"):
#             st.markdown(답변)

#         # 기록에 답변 추가
#         st.session_state.chat_history.append({"role": "assistant", "content": 답변})

# else:
#     st.info("⛔ 왼쪽 사이드바에서 보험사와 상품을 먼저 선택해주세요!")





















# # --- 세션 상태 초기화 ---
# if "history" not in st.session_state:
#     st.session_state.chat_history = []





# # 대화창 출력 (최신이 아래로)
# for chat in st.session_state.chat_history:
#     with st.chat_message("👤 사용자" if chat["role"] == "user" else "🤖 보미", 
#                          avatar="🧍" if chat["role"] == "user" else "🤖"):
#         st.markdown(chat["content"])

# # 사용자 입력창 (하단 고정)
# if 선택한_보험사 and 선택한_카테고리:
#     user_input = st.chat_input("예: 제주도에서 렌터카 사고가 났을 때 보장받을 수 있나요?")
#     if user_input:
#         # 사용자 입력 저장
#         st.session_state.chat_history.append({"role": "user", "content": user_input})

#         # 답변 생성 (응답 함수는 미리 정의되어 있다고 가정)
#         with st.spinner("보미가 답변을 생각하는 중이에요..."):
#             답변 = 챗봇응답생성(user_input, 선택한_보험사, 선택한_카테고리)
#         st.session_state.chat_history.append({"role": "bomi", "content": 답변})

# else:
#     st.info("👉 왼쪽 사이드바에서 보험사와 상품을 먼저 선택해주세요!")

# if not 선택한_보험사 and user_input:       # 왼쪽 선택 요청
#     st.toast("왼쪽 사이드바에서 보험사와 상품을 먼저 선택해주세요", icon="⛔")

#------------------------------------------------------------------
# # --- 질문 입력 창 ---
# with st.form("chat_form", clear_on_submit=True):
#     질문 = st.text_input("✍️ 보험에 대해 궁금한 점을 입력해주세요:")
#     제출 = st.form_submit_button("질문하기")

# # --- 질문 제출 처리 ---
# if 제출 and 질문.strip():
#     답변 = 챗봇응답생성(질문, 선택한_보험사, 선택한_카테고리)

#     # 대화 기록 저장
#     timestamp = f"{datetime.datetime.today().hour} : {datetime.datetime.today().minute}"
#     st.session_state.history.append({
#         "질문": 질문,
#         "답변": 답변,
#         "시간": timestamp
#     })
# # --- 대화 내용 표시 ---
# if st.session_state.history:
#     st.subheader("📜 대화 기록")
#     for idx, 대화 in enumerate(reversed(st.session_state.history)):
#         with st.chat_message("user"):
#             st.markdown(f"**{대화['시간']}**<br>{대화['질문']}", unsafe_allow_html=True)
#         with st.chat_message("assistant"):
#             st.markdown(대화["답변"])




# # 대화창 출력 (최신이 아래로)
# for chat in st.session_state.chat_history:
#     with st.chat_message("👤 사용자" if chat["role"] == "user" else "🤖 보미", avatar="🧍" if chat["role"] == "user" else "🤖"):
#         st.markdown(chat["content"])

# # 사용자 입력창 (하단 고정)
# if 선택한_보험사 and 선택한_카테고리:
#     user_input = st.chat_input("무엇이 궁금하신가요?")

#     if user_input:
#         # 사용자 입력 저장
#         st.session_state.chat_history.append({"role": "user", "content": user_input})

#         # 답변 생성 (응답 함수는 미리 정의되어 있다고 가정)
#         with st.spinner("보미가 답변을 생각하는 중이에요..."):
#             답변 = 챗봇응답생성(user_input, 선택한_보험사, 선택한_카테고리)
#         st.session_state.chat_history.append({"role": "bomi", "content": 답변})
# else:
#     st.info("👉 왼쪽 사이드바에서 보험사와 상품을 먼저 선택해주세요!")



# if not 선택한_보험사 and user_input:       # 왼쪽 선택 요청
#     st.toast("왼쪽 사이드바에서 보험사와 상품을 먼저 선택해주세요", icon="⛔")


# # --- 세션 상태 초기화 ---
# if "history" not in st.session_state:
#     st.session_state.history = []


# # --- 질문 입력 창 ---
# with st.form("chat_form", clear_on_submit=True):
#     질문 = st.text_input("✍️ 보험에 대해 궁금한 점을 입력해주세요:", placeholder="예: 제주도에서 렌터카 사고가 났을 때 보장받을 수 있나요?")
#     제출 = st.form_submit_button("질문하기")


# # --- 질문 제출 처리 ---
# if 제출 and 질문.strip():
#     답변 = 챗봇응답생성(질문, 선택한_보험사, 선택한_카테고리)

#     # 대화 기록 저장
#     timestamp = datetime.time()#.strftime("%H:%M:%S")
#     st.session_state.history.append({
#         "질문": 질문,
#         "답변": 답변,
#         "시간": timestamp
#     })


# # ---- 대화 기록 표시 ----
# if st.session_state.history:
#     st.subheader("📜 대화 기록")
#     for idx, 대화 in enumerate(reversed(st.session_state.history)):
#         with st.chat_message("user"):
#             st.markdown(f"**{대화['시간']}**<br>{대화['질문']}", unsafe_allow_html=True)
#         with st.chat_message("assistant"):
#             st.markdown(대화["답변"])

