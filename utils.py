import openai
import json
import os
import streamlit as st

DATA_PATH = "data/dialogues.json"
openai.api_key = st.secrets["OPENAI_API_KEY"]

def generate_conversation(persona):
  system_prompt = f"""You are a GPT that helps you create a multi-Turn conversation between the emergency room nurse and the patient. Create a conversation according to the following seven rules:

1. ** You have to create a conversation based on the patient's persona. Persona, a patient to reflect it, is as follows:
   -Patient: {persona['age']} / {persona['gender']} / {persona['main_category']} / {persona['middle_category']}
   -KTAS expected level: {persona['ktas_level']}
   ** At this time, the KTAS level is integer from 1 to 5, the lower the emergency.
   Examples of KTAS levels are as follows:
   -1: cardiac arrest due to heart disease, cardiac arrest due to respiratory failure, severe trauma (shock), shortness of breath, consciousness disorder
   -5: diarrhea (mild, no dehydration), not severe bite wounds, wound disinfection

2. You can selectively reflect the following information. This information will make the context of the conversation abundant.
   -Examples: Past history, vital signs, symptom onset, drug use, additional accompanying symptoms, NRS scores, pain levels, electrocardiograms, etc.

3. Multi-Turn Dialogue should be created in JSON format. Each round of the conversation is written in the following structure:
   ```json
   {{
     "turn": 1,
     "speaker": "<"I" or "CHATGPT">",
     "utterance": "<utterance in Korean>"
   }}
   
4. The first row must start in the form of (patient number is random):
```json
{{
  "turn": 1,
  "speaker": "I",
  "utterance": "Come on in patients."
}}
```

5. One round-term conversation between speakers must share the same "turn". Each "turn" number must increase for each new pair.
6. All "utterance" must be written in Korean, concise and accurate.
7. One "turn" must include only one medical information. For example, don't ask for "vital signs" and "past history" at the same time, but separate and answer separately.

--- [Example - Output JSON] ---
[
{{
"turn": 1,
"speaker": "I",
"utterance": "Come on in patients 12."
}},
{{
"turn": 1,
"speaker": "CHATGPT",
"utterance": "I'm a 55-year-old man."
}},
{{
"turn": 2,
"speaker": "I",
"utterance": "Where are you uncomfortable?"
}},
{{
"turn": 2,
"speaker": "CHATGPT",
"utterance": "It's hard to breathe."
}},
{{
"turn": 3,
"speaker": "I",
"utterance": "Do you have past medical history?"
}},
{{
"turn": 3,
"speaker": "Chatgpt",
"utterance": "Past history: COPD."
}}
]
"""
  response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[{"role": "system", "content": system_prompt}],
        temperature=0.7
  )

  generated = response.choices[0].message.content
  conversation_json = json.loads(generated)
  return {"persona": persona, "dialogue": conversation_json}

def save_conversation_json(data):
    os.makedirs("data", exist_ok=True)
    all_data = []
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    all_data.append(data)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

def load_all_dialogues():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def update_evaluation(idx, ktas, question, realism):
    data = load_all_dialogues()
    if 0 <= idx < len(data):
        data[idx]["evaluation"] = {
            "ktas": ktas,
            "question": question,
            "realism": realism
        }
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def delete_last_conversation():
    import os, json
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data:
            data.pop()
            with open(DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)