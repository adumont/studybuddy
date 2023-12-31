import streamlit as st
from pydantic import BaseModel, constr, validator
from typing import List
from langchain.docstore.document import Document
from itertools import permutations
from random import randint


@st.cache_resource(ttl=300)
def loadp(filename):
    from pickle import load

    obj = None

    with open(filename, "rb") as f:
        obj = load(f)

    return obj


@st.cache_resource
def get_order_permitations():
    return [list(p) for p in permutations([0, 1, 2, 3])]


class PossibleAnswer(BaseModel):
    answer: constr(min_length=1)
    explanation: constr(min_length=1)
    is_correct: bool


class Question4Choices(BaseModel):
    question: str
    answers: List[PossibleAnswer]

    @validator("answers")
    def validate_answers(cls, v):
        if len(v) != 4:
            raise ValueError("Answers list must have exactly 4 elements")
        return v


def init_session_state(key: str, default: any = None):
    if key not in st.session_state:
        st.session_state[key] = default


def set_session_state(key: str, value: any):
    st.session_state[key] = value

def get_asignatura():
    return st.session_state["asignatura_seleccionada"]

# init_session_state(key="current_chunk", default=0)
# init_session_state(key="current_question", default=0)
# init_session_state(key="current_answer", default=-1)
init_session_state(key="ver_mas_info", default={"tema": -1, "question": -1})
init_session_state(key="asignatura_seleccionada", default="GEOGRAFIA")

asignatura = get_asignatura()
corpus = loadp(f"{asignatura}.pkl")

order_permitations = get_order_permitations()

# Show lista de temas (chunks)
chunk_list = [f"{i} - {c['title']}" for i, c in enumerate(corpus["chunks"])]

if "user_responses" not in st.session_state:
    st.session_state["user_responses"] = []
    for cn, chunk in enumerate(corpus["chunks"]):
        q = len(chunk["questions"])
        st.session_state["user_responses"].append(
            [{"order": randint(0, 15), "user_answer": -1} for _ in range(q)]
        )

# with st.expander(label="user_responses", expanded=False):
#     st.write(st.session_state["user_responses"])


with st.sidebar:
    st.write("Elige una asignatura:")
    asignatura_seleccionada = st.selectbox(
        label="Asignaturas:", options=["GEOGRAFIA"], key="asignatura_seleccionada"
    )

    st.write("Elige un tema en la lista siguiente:")
    tema_seleccionado = st.selectbox(
        label="Temas:", options=chunk_list, key="tema_seleccionado"
    )
    st.info(
        "Aplicacion desarrollada por [Alexandre Dumont](https://adumont.github.io/)"
    )

tema_n = chunk_list.index(tema_seleccionado)

chunk = corpus["chunks"][tema_n]
# st.write(chunk["chunk"].page_content)

# st.write(chunk["questions"])


def answer_clicked(tema, question, answer):
    # reset the "Ver mas"
    st.session_state["ver_mas_info"] = {"tema": -1, "question": -1}

    if st.session_state["user_responses"][tema][question]["user_answer"] == answer:
        st.session_state["user_responses"][tema][question]["user_answer"] = -1
    else:
        st.session_state["user_responses"][tema][question]["user_answer"] = answer


def answer_button_type(tema, question, answer):
    return (
        "primary"
        if st.session_state["user_responses"][tema][question]["user_answer"] == answer
        else "secondary"
    )


def get_question_order(tema, question):
    order = st.session_state["user_responses"][tema][question]["order"]
    return order_permitations[order]


def ver_mas_info(tema_n, qn):
    if st.session_state["ver_mas_info"] == {"tema": tema_n, "question": qn}:
        st.session_state["ver_mas_info"] = {"tema": -1, "question": -1}
    else:
        st.session_state["ver_mas_info"] = {"tema": tema_n, "question": qn}


st.write(f"""## {chunk["title"]}""")

for qn, question in enumerate(chunk["questions"]):
    with st.expander(label=f"Question {qn}", expanded=True):
        st.write(f"""**{question["question"].question}**""")

        order = get_question_order(tema_n, qn)
        answers = question["question"].answers

        # st.write(question["question"])
        # st.write(st.session_state["ver_mas_info"])

        nums_icons = ["1️⃣", "2️⃣", "3️⃣", "4️⃣" ]

        for i, an in enumerate(order):
            answer = answers[an]
            # one button for each possible answer
            st.button(
                f"{nums_icons[i]} {answer.answer}",
                key=f"{qn}-{an}",
                on_click=answer_clicked,
                args=(tema_n, qn, an),
                type=answer_button_type(tema_n, qn, an),
            )
            if st.session_state["user_responses"][tema_n][qn]["user_answer"] == an:
                if answer.is_correct:
                    st.info(f"✅ {answer.explanation}")
                else:
                    st.error(f"⚠️ {answer.explanation}")

                # Show more...
                if st.session_state["ver_mas_info"] == {
                    "tema": tema_n,
                    "question": qn,
                }:
                    # user clicked the "Ver mas" button
                    st.write(f"""**Fact: {question["fact"]}**""")
                    st.write(f"""**Lesson**: {chunk["chunk"].page_content}""")

                else:
                    # Show "ver mas" button
                    st.button(
                        label="📒Leer mas...",
                        key=f"ver-mas-{tema_n}-{qn}",
                        on_click=ver_mas_info,
                        args=(tema_n, qn),
                        type="secondary",
                    )
