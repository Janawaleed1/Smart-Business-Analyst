import ollama


MODEL_NAME = "deepseek-r1:1.5b"


def ask_llm(prompt):
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


if __name__ == "__main__":
    prompt = "What is the purpose of a business analyst?"

    answer = ask_llm(prompt)

    print("AI Response:")
    print(answer)