import ollama


response = ollama.chat(
    model="deepseek-r1:1.5b",
    messages=[
        {
            "role": "user",
            "content": "Hello! Introduce yourself in one short sentence."
        }
    ]
)

print(response["message"]["content"])