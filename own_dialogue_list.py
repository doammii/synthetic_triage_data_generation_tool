import streamlit as st
import pandas as pd
import json
import os

OWN_DATA_PATH = "data/own_dialogues.json"

def load_own_dialogues():
    if not os.path.exists(OWN_DATA_PATH):
        return []
    with open(OWN_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_own_dialogues(data):
    os.makedirs(os.path.dirname(OWN_DATA_PATH), exist_ok=True)
    with open(OWN_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_own_evaluation(idx, ktas, question, realism, evaluator):
    data = st.session_state.get("own_dialogues", [])
    if 0 <= idx < len(data):
        data[idx]["evaluation"] = {
            "ktas": ktas,
            "question": question,
            "realism": realism,
            "evaluator": evaluator
        }
        st.session_state["own_dialogues"] = data
        save_own_dialogues(data)

def read_csv_any_encoding(uploaded_file):
    encodings = ["utf-8", "utf-8-sig", "cp949", "euc-kr", "latin1"]
    last_err = None
    for enc in encodings:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc, sep=None, engine="python")
            return df
        except Exception as e:
            last_err = e
            continue
    # CSV 실패 시 엑셀 시도
    try:
        uploaded_file.seek(0)
        return pd.read_excel(uploaded_file)
    except Exception as e2:
        raise RuntimeError(f"파일을 읽지 못했습니다. 시도 인코딩={encodings}, 마지막 오류={last_err}, 엑셀 오류={e2}")

# --------- Main Tab: 업로드 & 평가 ---------
def upload_and_evaluate_tab():
    st.header("[자체 대화 업로드 및 평가]")

    st.markdown("CSV를 업로드하면 각 행의 대화를 확인하고 평가할 수 있습니다.")
    uploaded = st.file_uploader("CSV 파일 업로드", type=["csv", "xlsx"], accept_multiple_files=False)

    if "own_dialogues" not in st.session_state:
        st.session_state["own_dialogues"] = load_own_dialogues()

    if uploaded is not None:
        try:
            df = read_csv_any_encoding(uploaded)
        except Exception as e:
            st.error(f"파일을 읽는 중 오류: {e}")
            return

        dialogue_col = None
        for cand in ["dialogue", "생성한 대화", "대화", "챗GPT와 대화한 내용", "contents"]:
            if cand in df.columns:
                dialogue_col = cand
                break

        if dialogue_col is None:
            st.error("업로드한 파일에서 대화 컬럼을 찾지 못했습니다. 예: 'dialogue', '생성한 대화', '대화'")
            return

        own_list = []
        for _, row in df.iterrows():
            raw = row.get(dialogue_col, "")
            parsed = None
            if isinstance(raw, str):
                s = raw.strip()
                if s.startswith("{") or s.startswith("["):
                    try:
                        parsed = json.loads(s)
                    except Exception:
                        parsed = None
            item = {
                "dialogue": parsed if parsed is not None else raw,
                "source": "업로드",
                "evaluation": {}
            }
            own_list.append(item)

        st.session_state["own_dialogues"] = own_list
        save_own_dialogues(own_list)
        st.success(f"업로드 완료: {len(own_list)}개 대화가 로드되었습니다.")

    data = st.session_state.get("own_dialogues", [])

    if not data:
        st.info("업로드한 데이터가 없습니다. CSV를 업로드해 주세요.")
        if os.path.exists(OWN_DATA_PATH) and st.button("이전에 저장한 자체 대화 불러오기"):
            st.session_state["own_dialogues"] = load_own_dialogues()
        return

    toc_lines = [f"- [대화 {i+1}](#own-대화-{i+1})" for i in range(len(data))]
    st.markdown("### 목차")
    st.markdown("\n".join(toc_lines))
    st.divider()

    # 페이지네이션(옵션)
    with st.expander("표시 범위 설정", expanded=False):
        page_size = st.number_input("페이지 크기", min_value=1, max_value=50, value=10, step=1, key="own_page_size")
        page = st.number_input("페이지 번호 (1부터)", min_value=1, value=1, step=1, key="own_page_no")
    start = (page - 1) * page_size
    end = min(start + page_size, len(data))
    if start >= len(data):
        st.warning("페이지 범위를 벗어났습니다. 페이지 번호를 줄여주세요.")
        return

    # 행별 표시 + 평가 폼
    for idx in range(start, end):
        entry = data[idx]

        st.markdown(f'<a name="own-대화-{idx+1}"></a>', unsafe_allow_html=True)
        st.subheader(f"대화 {idx+1}")

        # 2개 컬럼 생성: 왼쪽에 대화 내용, 오른쪽에 평가 항목
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 대화내용")
            dlg = entry.get("dialogue", {})
            if isinstance(dlg, (dict, list)):
                pretty = json.dumps(dlg, ensure_ascii=False, indent=2)
                st.code(pretty, language="json")  
            else:
                st.code(str(dlg))

        with col2:
            st.markdown("### 평가항목")
            
            prev = entry.get("evaluation", {}) or {}
            prev_ktas = prev.get("ktas", "판단 불가")
            prev_eval = prev.get("evaluator", "")
            
            with st.form(f"own_eval_form_{idx}"):
                # KTAS 레벨의 적절성 (기존 유지)
                ktas_appropriateness = st.selectbox(
                    "KTAS 레벨의 적절성",
                    options=["Y", "N", "판단 불가"],
                    index=["Y", "N", "판단 불가"].index(prev_ktas) if prev_ktas in ["Y", "N", "판단 불가"] else 2,
                    key=f"own_ktas_{idx}"
                )

                # 질문의 적절성 - 3개 컬럼 구성
                st.markdown("**질문의 적절성**")
                
                q_col1, q_col2, q_col3 = st.columns(3)
                
                with q_col1:
                    st.markdown("**부정적인 항목**")
                    difficult_language = st.checkbox("어려운 용어 사용", key=f"own_difficult_lang_{idx}")
                    complex_question = st.checkbox("복잡한 질문", key=f"own_complex_q_{idx}")
                    irrelevant_question = st.checkbox("불필요한 질문", key=f"own_irrelevant_q_{idx}")
                    essential_omission = st.checkbox("필수 질문의 누락", key=f"own_essential_omit_{idx}")
                    hasty_judgment = st.checkbox("최종 판단 부적절", key=f"own_hasty_judge_{idx}")
                    unethical_question = st.checkbox("비효율적인 질문 순서", key=f"own_unethical_q_{idx}")
                    unclear_question = st.checkbox("의심 또는 추정 진단명 적시", key=f"own_unclear_q_{idx}")

                with q_col2:
                    st.markdown("**보통이다**")
                    q_normal_1 = st.checkbox("보통이다", key=f"own_q_normal_1_{idx}")
                    q_normal_2 = st.checkbox("보통이다", key=f"own_q_normal_2_{idx}")
                    q_normal_3 = st.checkbox("보통이다", key=f"own_q_normal_3_{idx}")
                    q_normal_4 = st.checkbox("보통이다", key=f"own_q_normal_4_{idx}")
                    # 마지막 3개 행에는 보통이다 옵션 없음
                    st.write("")  # 빈 공간
                    st.write("")  # 빈 공간
                    st.write("")  # 빈 공간

                with q_col3:
                    st.markdown("**긍정적인 항목**")
                    appropriate_language = st.checkbox("쉬운 용어 사용", key=f"own_easy_lang_{idx}")
                    public_expression = st.checkbox("공감 및 지지적 표현 사용", key=f"own_public_expr_{idx}")
                    clear_question = st.checkbox("명확하고 간결한 질문", key=f"own_clear_q_{idx}")
                    proper_sequence = st.checkbox("적절한 꼬리 질문", key=f"own_proper_seq_{idx}")
                    systematic_approach = st.checkbox("체계적인 질문 흐름", key=f"own_systematic_{idx}")
                    situational_consideration = st.checkbox("안전 지향적 최종 판단", key=f"own_situational_{idx}")
                    structured_action = st.checkbox("구체적인 행동 지침 제공", key=f"own_structured_{idx}")

                # 대화의 현실성 항목 - 3개 컬럼 구성
                st.markdown("**대화의 현실성**")
                
                r_col1, r_col2, r_col3 = st.columns(3)
                
                with r_col1:
                    st.markdown("**부정적인 항목**")
                    difficult_language_real = st.checkbox("어려운 용어 사용", key=f"own_difficult_lang_real_{idx}")
                    complex_question_real = st.checkbox("복잡한 질문", key=f"own_complex_q_real_{idx}")
                    irrelevant_question_real = st.checkbox("불필요한 질문", key=f"own_irrelevant_q_real_{idx}")
                    essential_omission_real = st.checkbox("필수 질문의 누락", key=f"own_essential_omit_real_{idx}")
                    hasty_judgment_real = st.checkbox("최종 판단 부적절", key=f"own_hasty_judge_real_{idx}")
                    unethical_question_real = st.checkbox("비효율적인 질문 순서", key=f"own_unethical_q_real_{idx}")
                    unclear_diagnosis_real = st.checkbox("의심 또는 추정 진단명 적시", key=f"own_unclear_diag_real_{idx}")

                with r_col2:
                    st.markdown("**보통이다**")
                    r_normal_1 = st.checkbox("보통이다", key=f"own_r_normal_1_{idx}")
                    r_normal_2 = st.checkbox("보통이다", key=f"own_r_normal_2_{idx}")
                    r_normal_3 = st.checkbox("보통이다", key=f"own_r_normal_3_{idx}")
                    r_normal_4 = st.checkbox("보통이다", key=f"own_r_normal_4_{idx}")
                    # 마지막 3개 행에는 보통이다 옵션 없음
                    st.write("")  
                    st.write("") 
                    st.write("") 

                with r_col3:
                    st.markdown("**긍정적인 항목**")
                    appropriate_language_real = st.checkbox("쉬운 용어 사용", key=f"own_easy_lang_real_{idx}")
                    public_expression_real = st.checkbox("공감 및 지지적 표현 사용", key=f"own_public_expr_real_{idx}")
                    clear_question_real = st.checkbox("명확하고 간결한 질문", key=f"own_clear_q_real_{idx}")
                    proper_education_real = st.checkbox("적절한 꼬리 질문", key=f"own_proper_edu_real_{idx}")
                    systematic_approach_real = st.checkbox("체계적인 질문 흐름", key=f"own_systematic_real_{idx}")
                    safety_oriented_real = st.checkbox("안전 지향적 최종 판단", key=f"own_safety_real_{idx}")
                    structured_action_real = st.checkbox("구체적인 행동 지침 제공", key=f"own_structured_real_{idx}")

                # 평가자
                evaluator = st.text_input(
                    "평가자 이름 또는 ID", 
                    value=prev_eval, 
                    placeholder="예: hong_gildong", 
                    key=f"own_evaluator_{idx}"
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
                        
                        # 최종 질문 적절성 점수 계산 (0-10 범위로 제한)
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
                        
                        # 최종 대화의 현실성 점수 계산 (0-10 범위로 제한)
                        dialogue_realism_score = max(0, min(10, base_score_realism + positive_score_realism - negative_score_realism))
                        
                        update_own_evaluation(
                            idx, 
                            ktas_appropriateness, 
                            question_appropriateness_score, 
                            dialogue_realism_score, 
                            evaluator
                        )
                        st.success(f"평가가 저장되었습니다.")

        st.divider()

# --------- Main Tab: 대화 리스트 확인 ---------
def own_dialogue_list_tab():
    st.header("[자체 대화 전체 확인 및 저장]")

    if "own_dialogues" not in st.session_state:
        st.session_state["own_dialogues"] = load_own_dialogues()

    data = st.session_state.get("own_dialogues", [])

    if not data:
        st.info("표시할 자체 대화가 없습니다. 먼저 '대화 업로드 및 평가' 탭에서 CSV를 업로드하세요.")
        if os.path.exists(OWN_DATA_PATH) and st.button("저장된 자체 대화 불러오기", use_container_width=True):
            st.session_state["own_dialogues"] = load_own_dialogues()
            st.success("저장된 자체 대화를 불러왔습니다.")
        return

    # 표용 rows 구성
    rows = []
    for i, entry in enumerate(data):
        dlg = entry.get("dialogue", {})
        conv_str = json.dumps(dlg, ensure_ascii=False) if isinstance(dlg, (dict, list)) else str(dlg)

        evals = entry.get("evaluation", {}) or {}
        rows.append({
            "__idx": i,  # 내부 인덱스 (삭제용)
            "대화 출처": "자체",
            "대화": conv_str,
            "평가자": evals.get("evaluator", ""),
            "KTAS 레벨의 적절성": evals.get("ktas", ""),
            "질문의 적절성": evals.get("question", ""),
            "전체 대화의 현실성": evals.get("realism", ""),
            "삭제": False
        })

    df = pd.DataFrame(rows)
    edited = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "__idx": st.column_config.NumberColumn("__idx", help="내부 인덱스", disabled=True, required=True),
            "삭제": st.column_config.CheckboxColumn("삭제"),
            "대화": st.column_config.TextColumn("대화", help="원문 JSON/텍스트", width="large"),
        },
        disabled=["__idx"]
    )

    col_del, col_csv = st.columns([1, 1])

    # 선택 행 삭제
    with col_del:
        if st.button("선택 행 삭제", use_container_width=True):
            del_rows = edited[edited["삭제"] == True]
            if del_rows.empty:
                st.warning("삭제할 행을 선택하세요.")
            else:
                to_delete = set(del_rows["__idx"].tolist())
                new_data = [entry for j, entry in enumerate(data) if j not in to_delete]
                st.session_state["own_dialogues"] = new_data
                save_own_dialogues(new_data)
                st.success(f"{len(to_delete)}개 행을 삭제했습니다.")
                st.rerun()

    # CSV 내보내기
    with col_csv:
        export_df = edited.drop(columns=["__idx", "삭제"])
        csv = export_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "CSV 파일로 내보내기",
            csv,
            file_name="자체_대화_데이터.csv",
            mime="text/csv",
            use_container_width=True
        )