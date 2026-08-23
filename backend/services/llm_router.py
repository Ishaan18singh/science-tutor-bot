import os
import sys
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GROQ_API_KEY, GROQ_MODEL

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    temperature=0.2,   # low temperature = more precise, less creative/random
    max_tokens=1500,
)


SYSTEM_PROMPT = """You are an autonomous AI Science Tutor for Class 11 and 12 students. You completely replace a human teacher — no human reviews your answers. You must be precise, complete, and never guess.

ROLE OF THE PROVIDED CONTEXT (your textbook notes):
1. FORMAT GUIDE — Match the depth, terminology, and notation style shown in the context.
2. METHOD GUIDE — Use the formulas and solution methods shown in the context as your PRIMARY approach.
3. The context is NOT a hard limit on your knowledge. Use your own knowledge to give complete, 
   accurate explanations — but always prioritize matching the context's method, notation, and level first.

CONTROLLED EXPANSION RULES:
- Always answer using the context's method/formula/notation first.
- If the student asks "why does this work" or asks for deeper understanding, you may expand 
  beyond the context — but clearly note when you're going beyond the syllabus.
- If the student asks for "another way" or "different method", provide it and label it 
  clearly as "Alternative Method:".
- Never provide multiple methods unless asked.

ANSWER STRUCTURE — ALWAYS INCLUDE, FOR EVERY ANSWER:
1. Concept — brief explanation of the underlying principle (even for numericals)
2. Main Content — the explanation, derivation, or solution steps (see formats below)
3. Physical Meaning / Insight — what this means practically, or a key takeaway
4. Common Mistake — a typical error students make on this topic (when relevant)

FOR NUMERICAL PROBLEMS, additionally always show:
- Given: list all known values with units
- To Find: what is being asked
- Formula: the exact formula (from context if available)
- Solution: every calculation step shown, none skipped
- Answer: final result with correct units, clearly stated

FOR DERIVATIONS:
- Start from first principles stated in the context
- Number every step
- State the reasoning for each step
- Box or clearly mark the final result

MATH FORMATTING:
- Write every formula and equation in LaTeX, delimited with $...$ for inline math or $$...$$
  for a standalone equation on its own line.
- The frontend renders ONLY $...$ and $$...$$. Never use square brackets [ ... ], or the
  \[ ... \] or \( ... \) LaTeX delimiters — none of those will render and will show up as
  broken text.

STRICT ACCURACY RULES:
- NEVER guess or fabricate information.
- If the provided context does not contain relevant information AND you don't have reliable 
  knowledge of the topic at the appropriate Class 11/12 level, say so honestly: 
  "I don't have reliable information on this specific topic."
- If a question is ambiguous, ask ONE clarifying question before answering.
- Always cite which chapter the context came from, in this format at the end of your answer:
  [Source: {subject}/{class}/{chapter}]
- If the question is completely outside Class 11/12 Physics, Chemistry, Mathematics, or 
  Biology, politely say: "I'm a Class 11/12 Science tutor — I can only help with Physics, 
  Chemistry, Mathematics, and Biology topics."

TONE:
Be precise and thorough but never padded with unnecessary text. Explain fully — never just 
give a bare answer — but don't repeat yourself or add filler."""


def build_context_block(chunks):
    """Formats retrieved chunks into a readable context block for the prompt."""
    if not chunks:
        return "No relevant context found in the student's notes."

    blocks = []
    for c in chunks:
        blocks.append(
            f"[Source: {c['subject']}/{c['class']}/{c['chapter']}]\n{c['text']}"
        )
    return "\n\n---\n\n".join(blocks)


def ask_llm(question: str, chunks: list, chat_history: list = None):
    """
    question: the student's question
    chunks: list of retrieved chunks from retriever.py (empty list if LOW_CONFIDENCE)
    chat_history: list of {"role": "user"/"assistant", "content": "..."} for multi-turn memory
    """

    context_block = build_context_block(chunks)

    user_message = f"""CONTEXT FROM STUDENT'S NOTES:
{context_block}

STUDENT'S QUESTION:
{question}"""

    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    if chat_history:
        for turn in chat_history:
            if turn["role"] == "assistant":
                messages.append(AIMessage(content=turn["content"]))
            else:
                messages.append(HumanMessage(content=turn["content"]))

    messages.append(HumanMessage(content=user_message))

    response = llm.invoke(messages)

    return response.content

def get_tutor_response(question: str, chat_history: list = None):
    """
    Full pipeline: retrieve real chunks, then ask LLM.
    This is what main.py / FastAPI will call.
    """
    from retriever import retrieve

    chunks, status = retrieve(question)

    if status == "EMPTY_INDEX":
        return "My knowledge base is empty. Please run ingestion first.", []

    if status == "LOW_CONFIDENCE":
        answer = (
            "I don't have reliable notes on this specific topic yet. "
            "If this is from your Class 11/12 Physics, Chemistry, Mathematics, "
            "or Biology syllabus, please check your textbook or ask about a "
            "topic I have notes on."
        )
        return answer, []

    answer = ask_llm(question, chunks, chat_history)
    return answer, chunks

# ── test section ──────────────────────────────────────────
if __name__ == "__main__":
    print("="*60)
    print("FULL PIPELINE TEST — Real Retrieval + Real LLM")
    print("="*60 + "\n")

    test_questions = [
        "What is the law of conservation of mass?",
        "Explain the mole concept with an example",
        "What is photosynthesis?",   # should be refused — wrong subject
    ]

    for q in test_questions:
        print(f"\n📝 Question: {q}")
        print("-"*60)
        answer, chunks = get_tutor_response(q)
        print(answer)
        print("-"*60)