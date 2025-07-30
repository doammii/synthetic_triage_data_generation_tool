import streamlit as st
import pandas as pd
from utils import load_all_dialogues
import json

def dialogue_list_tab():
    st.header("[전체 대화 리스트 확인 및 저장]")

    data = load_all_dialogues()
    rows = []
    for entry in data:
        conv_str = json.dumps(entry["dialogue"], ensure_ascii=False)
        evals = entry.get("evaluation", {"ktas": "", "question": "", "realism": ""})
        persona = entry.get("persona", {})

        rows.append({
            "생성한 대화": conv_str,
            "KTAS 레벨의 적절성": evals["ktas"],
            "질문의 적절성": evals["question"],
            "전체 대화의 현실성": evals["realism"],
            "나이": persona.get("age", ""),
            "성별": persona.get("gender", ""),
            "대분류": persona.get("main_category", ""),
            "중분류": persona.get("middle_category", ""),
            "KTAS 레벨": persona.get("ktas_level", "")
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("CSV 파일로 내보내기", csv, file_name="응급실_대화_데이터.csv", mime="text/csv")
