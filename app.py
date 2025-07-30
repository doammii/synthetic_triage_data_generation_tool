import streamlit as st
from persona_input import persona_input_tab
from evaluate_dialogue import evaluate_dialogue_tab
from dialogue_list import dialogue_list_tab

st.set_page_config(page_title="응급실 대화 생성 TOOL", layout="wide")

tab = st.sidebar.radio("메뉴", ["1. 환자 페르소나 및 대화 생성", "2. 생성 대화 평가", "3. 전체 대화 확인 및 저장"])

if tab == "1. 환자 페르소나 및 대화 생성":
    persona_input_tab()

elif tab == "2. 생성 대화 평가":
    evaluate_dialogue_tab()

elif tab == "3. 전체 대화 확인 및 저장":
    dialogue_list_tab()
