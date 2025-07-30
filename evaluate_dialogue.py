import streamlit as st
import json
from utils import load_all_dialogues, update_evaluation

def evaluate_dialogue_tab():
    st.header("[생성된 대화 평가]")

    data = load_all_dialogues()
    for idx, entry in enumerate(data):
        st.subheader(f"대화 {idx+1}")
        st.json(entry["dialogue"])

        with st.form(f"eval_form_{idx}"):
            ktas_score = st.number_input("KTAS 레벨의 적절성 (1~10)", min_value=1, max_value=10, key=f"ktas_{idx}")
            question_score = st.number_input("질문의 적절성 (1~10)", min_value=1, max_value=10, key=f"question_{idx}")
            realism_score = st.number_input("전체 대화의 현실성 (1~10)", min_value=1, max_value=10, key=f"realism_{idx}")
            
            submitted = st.form_submit_button("결과 저장")
            
            if submitted:
                update_evaluation(idx, ktas_score, question_score, realism_score)
                st.success("평가가 저장되었습니다.")

