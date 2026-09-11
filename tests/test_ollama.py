import ollama

print("Connecting to Ollama...")

response = ollama.chat(
    model="llama3.1:8b",
    messages=[
        {
            "role": "user",
            "content": "Say hello to Hammad in one short sentence."
        }
    ]
)

print("\nOllama Response:")
print(response["message"]["content"])