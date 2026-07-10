from typing import TypedDict

from langgraph.graph import StateGraph, END

from gemini import generate
from prompts import build_prompt


class State(TypedDict):
    feature: str
    prompt: str
    difficulty: str
    full_prompt: str
    response: str


def normalize_node(state: State):
    feature = (state.get("feature") or "Explain").strip()
    prompt = (state.get("prompt") or "").strip()
    difficulty = (state.get("difficulty") or "Beginner").strip() or "Beginner"

    if feature == "Questions":
        feature = "Explain"

    return {
        **state,
        "feature": feature,
        "prompt": prompt,
        "difficulty": difficulty,
    }


def prompt_node(state: State):
    full_prompt = build_prompt(
        state["feature"],
        state["prompt"],
        state["difficulty"]
    )

    return {
        **state,
        "full_prompt": full_prompt,
    }


def ai_node(state: State):
    response = generate(state["full_prompt"])

    return {
        **state,
        "response": response,
    }


builder = StateGraph(State)

builder.add_node("normalize", normalize_node)
builder.add_node("build_prompt", prompt_node)
builder.add_node("ai", ai_node)

builder.set_entry_point("normalize")

builder.add_edge("normalize", "build_prompt")
builder.add_edge("build_prompt", "ai")
builder.add_edge("ai", END)

graph = builder.compile()


def run_ai(feature, prompt, difficulty):

    result = graph.invoke(
        {
            "feature": feature,
            "prompt": prompt,
            "difficulty": difficulty,
            "full_prompt": "",
            "response": "",
        }
    )

    return result["response"]
