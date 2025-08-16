import streamlit as st
from utils import load_all_dialogues, update_evaluation

def evaluate_dialogue_tab():
    st.header("[생성된 대화 평가]")

    data = load_all_dialogues()
    if data:
        toc_lines = [f"- [대화 {i+1}](#대화-{i+1})" for i in range(len(data))]
        st.markdown("### 목차")
        st.markdown("\n".join(toc_lines))
        st.divider()

    for idx, entry in enumerate(data):
        st.markdown(f'<a name="대화-{idx+1}"></a>', unsafe_allow_html=True)
        st.subheader(f"대화 {idx+1}")

        st.json(entry.get("dialogue", {}))

        with st.form(f"eval_form_{idx}"):
            ktas_score = st.selectbox(
                "KTAS 레벨의 적절성",
                options=["Y", "N", "판단 불가"],
                index=2,  # default: 판단 불가
                key=f"ktas_{idx}"
            )

            question_score = st.number_input(
                "질문의 적절성 (1~10)", min_value=1, max_value=10, key=f"question_{idx}"
            )
            realism_score = st.number_input(
                "전체 대화의 현실성 (1~10)", min_value=1, max_value=10, key=f"realism_{idx}"
            )
            evaluator = st.text_input(
                "평가자 이름 또는 ID", key=f"evaluator_{idx}", placeholder="예: hong_gildong"
            )

            submitted = st.form_submit_button("결과 저장")

            if submitted:
                if not evaluator.strip():
                    st.error("평가자 이름/ID를 입력해주세요.")
                else:
                    update_evaluation(idx, ktas_score, question_score, realism_score, evaluator)
                    st.success("평가가 저장되었습니다.")

