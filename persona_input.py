import streamlit as st
from utils import generate_conversation, save_conversation_json, delete_last_conversation

def persona_input_tab():
    st.header("[환자 페르소나 설정 및 대화 생성]")

    with st.form("persona_form"):
        age = st.radio("나이", ["15세 미만", "15세 이상"])
        gender = st.radio("성별", ["남성", "여성"])
        main_category = st.selectbox("대분류 (주증상)", [
            "1. 심혈관계", "2. 귀", "3. 입, 목", "4. 코", "5. 환경손상", "6. 소화기계",
            "7. 비뇨기계 / 남성생식계", "8. 정신건강", "9. 신경계", "10. 임신 / 여성생식계",
            "11. 눈", "12. 근골격계", "13. 호흡기계", "14. 피부", "15. 물질오용",
            "16. 몸통외상", "17. 일반"
        ])
        middle_category = st.text_input("중분류 (직접 입력)")
        ktas_level = st.radio("KTAS 레벨", [1, 2, 3, 4, 5], horizontal=True)

        submitted = st.form_submit_button("대화 생성")

    if submitted:
        persona = {
            "age": age, "gender": gender,
            "main_category": main_category,
            "middle_category": middle_category,
            "ktas_level": ktas_level
        }
        conversation_json = generate_conversation(persona)
        st.session_state.last_generated = conversation_json
        st.json(conversation_json)
        save_conversation_json(conversation_json)
        st.success("대화가 생성되어 저장되었습니다.")

    if "last_generated" in st.session_state:
        if st.button("대화 삭제"):
            delete_last_conversation()
            st.success("만들어진 대화가 삭제되었습니다.")
            del st.session_state["last_generated"]
