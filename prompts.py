def build_prompt(feature, topic, difficulty):

    if feature == "Explain":
        return f"Explain {topic} at {difficulty} level in clear markdown with: Simple Explanation, Key Points, Real Life Example, Summary. Keep it concise."

    elif feature == "Notes":
        return f"Create concise study notes on {topic}. Use headings, bullet points, and important facts."

    elif feature == "Quiz":
        return f"Generate a {difficulty} quiz on {topic}. Give 10 MCQs, 4 options each, and the answer after every question. Keep each question and explanation short."

    elif feature == "Flashcards":
        return f"Create at least 10 flashcards for {topic}. Format each as Q: and A:. Keep them short and study-friendly."

    else:
        return f"Answer this educational question at {difficulty} level: {topic}. Be clear, direct, and concise."
