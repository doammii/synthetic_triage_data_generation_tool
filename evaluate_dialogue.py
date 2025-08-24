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

        # 2개 컬럼 생성: 왼쪽에 대화 내용, 오른쪽에 평가 항목
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 대화내용")
            st.json(entry.get("dialogue", {}))

        with col2:
            st.markdown("### 평가항목")
            
            with st.form(f"eval_form_{idx}"):
                # KTAS 레벨의 적절성 (기존 유지)
                ktas_appropriateness = st.selectbox(
                    "KTAS 레벨의 적절성",
                    options=["Y", "N", "판단 불가"],
                    index=2,  # default: 판단 불가
                    key=f"ktas_{idx}"
                )

                # 질문의 적절성 - 3개 컬럼 구성
                st.markdown("**질문의 적절성**")
                
                q_col1, q_col2, q_col3 = st.columns(3)
                
                with q_col1:
                    st.markdown("**부정적인 항목**")
                    difficult_language = st.checkbox("어려운 용어 사용", key=f"difficult_lang_{idx}")
                    complex_question = st.checkbox("복잡한 질문", key=f"complex_q_{idx}")
                    irrelevant_question = st.checkbox("불필요한 질문", key=f"irrelevant_q_{idx}")
                    essential_omission = st.checkbox("필수 질문의 누락", key=f"essential_omit_{idx}")
                    hasty_judgment = st.checkbox("최종 판단 부적절", key=f"hasty_judge_{idx}")
                    unethical_question = st.checkbox("비효율적인 질문 순서", key=f"unethical_q_{idx}")
                    unclear_question = st.checkbox("의심 또는 추정 진단명 적시", key=f"unclear_q_{idx}")

                with q_col2:
                    st.markdown("**보통이다**")
                    q_normal_1 = st.checkbox("보통이다", key=f"q_normal_1_{idx}")
                    q_normal_2 = st.checkbox("보통이다", key=f"q_normal_2_{idx}")
                    q_normal_3 = st.checkbox("보통이다", key=f"q_normal_3_{idx}")
                    q_normal_4 = st.checkbox("보통이다", key=f"q_normal_4_{idx}")
                    st.write("")  # 빈 공간
                    st.write("")
                    st.write("")

                with q_col3:
                    st.markdown("**긍정적인 항목**")
                    appropriate_language = st.checkbox("쉬운 용어 사용", key=f"easy_lang_{idx}")
                    public_expression = st.checkbox("공감 및 지지적 표현 사용", key=f"public_expr_{idx}")
                    clear_question = st.checkbox("명확하고 간결한 질문", key=f"clear_q_{idx}")
                    proper_sequence = st.checkbox("적절한 꼬리 질문", key=f"proper_seq_{idx}")
                    systematic_approach = st.checkbox("체계적인 질문 흐름", key=f"systematic_{idx}")
                    situational_consideration = st.checkbox("안전 지향적 최종 판단", key=f"situational_{idx}")
                    structured_action = st.checkbox("구체적인 행동 지침 제공", key=f"structured_{idx}")

                # 대화의 현실성 항목 - 3개 컬럼 구성
                st.markdown("**대화의 현실성**")
                
                r_col1, r_col2, r_col3 = st.columns(3)
                
                with r_col1:
                    st.markdown("**부정적인 항목**")
                    difficult_language_real = st.checkbox("어려운 용어 사용", key=f"difficult_lang_real_{idx}")
                    complex_question_real = st.checkbox("복잡한 질문", key=f"complex_q_real_{idx}")
                    irrelevant_question_real = st.checkbox("불필요한 질문", key=f"irrelevant_q_real_{idx}")
                    essential_omission_real = st.checkbox("필수 질문의 누락", key=f"essential_omit_real_{idx}")
                    hasty_judgment_real = st.checkbox("최종 판단 부적절", key=f"hasty_judge_real_{idx}")
                    unethical_question_real = st.checkbox("비효율적인 질문 순서", key=f"unethical_q_real_{idx}")
                    unclear_diagnosis_real = st.checkbox("의심 또는 추정 진단명 적시", key=f"unclear_diag_real_{idx}")

                with r_col2:
                    st.markdown("**보통이다**")
                    r_normal_1 = st.checkbox("보통이다", key=f"r_normal_1_{idx}")
                    r_normal_2 = st.checkbox("보통이다", key=f"r_normal_2_{idx}")
                    r_normal_3 = st.checkbox("보통이다", key=f"r_normal_3_{idx}")
                    r_normal_4 = st.checkbox("보통이다", key=f"r_normal_4_{idx}")
                    st.write("")
                    st.write("")
                    st.write("")

                with r_col3:
                    st.markdown("**긍정적인 항목**")
                    appropriate_language_real = st.checkbox("쉬운 용어 사용", key=f"easy_lang_real_{idx}")
                    public_expression_real = st.checkbox("공감 및 지지적 표현 사용", key=f"public_expr_real_{idx}")
                    clear_question_real = st.checkbox("명확하고 간결한 질문", key=f"clear_q_real_{idx}")
                    proper_education_real = st.checkbox("적절한 꼬리 질문", key=f"proper_edu_real_{idx}")
                    systematic_approach_real = st.checkbox("체계적인 질문 흐름", key=f"systematic_real_{idx}")
                    safety_oriented_real = st.checkbox("안전 지향적 최종 판단", key=f"safety_real_{idx}")
                    structured_action_real = st.checkbox("구체적인 행동 지침 제공", key=f"structured_real_{idx}")

                # 평가자
                evaluator = st.text_input(
                    "평가자 이름 또는 ID", 
                    key=f"evaluator_{idx}", 
                    placeholder="예: hong_gildong"
                )

                submitted = st.form_submit_button("결과 저장")

                if submitted:
                    if not evaluator.strip():
                        st.error("평가자 이름/ID를 입력해주세요.")
                    else:
                        # 질문의 적절성 점수 계산 (0-10점 범위)
                        base_score_question = 5  # 보통이다 기준점
                        
                        # 질문의 적절성 - 긍정 항목 점수 계산
                        positive_items_question = [
                            appropriate_language, public_expression, clear_question,
                            proper_sequence, systematic_approach, situational_consideration,
                            structured_action
                        ]
                        positive_score_question = sum(positive_items_question)
                        
                        # 질문의 적절성 - 부정 항목 점수 계산
                        negative_items_question = [
                            difficult_language, complex_question, irrelevant_question,
                            essential_omission, hasty_judgment, unethical_question,
                            unclear_question
                        ]
                        negative_score_question = sum(negative_items_question)
                        
                        # 최종 질문 적절성 점수 계산
                        # 보통이다는 기준점 유지, 긍정은 +1, 부정은 -1
                        question_appropriateness_score = max(0, min(10, base_score_question + positive_score_question - negative_score_question))
                        
                        # 대화의 현실성 점수 계산 (0-10점 범위)
                        base_score_realism = 5  # 보통이다 기준점
                        
                        # 대화의 현실성 - 긍정 항목 점수 계산
                        positive_items_realism = [
                            appropriate_language_real, public_expression_real, clear_question_real,
                            proper_education_real, systematic_approach_real, safety_oriented_real,
                            structured_action_real
                        ]
                        positive_score_realism = sum(positive_items_realism)
                        
                        # 대화의 현실성 - 부정 항목 점수 계산
                        negative_items_realism = [
                            difficult_language_real, complex_question_real, irrelevant_question_real,
                            essential_omission_real, hasty_judgment_real, unethical_question_real,
                            unclear_diagnosis_real
                        ]
                        negative_score_realism = sum(negative_items_realism)
                        
                        
                        # 최종 대화의 현실성 점수 계산
                        # 보통이다는 기준점 유지, 긍정은 +1, 부정은 -1
                        dialogue_realism_score = max(0, min(10, base_score_realism + positive_score_realism - negative_score_realism))
                        
                        update_evaluation(
                            idx, 
                            ktas_appropriateness, 
                            question_appropriateness_score, 
                            dialogue_realism_score, 
                            evaluator
                        )
                        st.success(f"평가가 저장되었습니다.")

        st.divider()