from tools.vision import analyze_screen


print("==============================================")
print("Hammu AI - Vision Question Test")
print("==============================================")


questions = [
    "Describe everything important you can see in this screenshot. Be concise.",
    "Which app is currently open on my screen?",
    "What website is open on my screen?",
    "What error is visible on my screen?",
]


for question in questions:
    print("\n----------------------------------------------")
    print("Question:", question)
    print("----------------------------------------------")

    result = analyze_screen(question=question)

    print("Result:")
    print(result)