from tools.vision import analyze_screen

result = analyze_screen(
    question="""
Find the Chrome address bar.

Return ONLY this format:

TARGET: <element name>
X: <center x coordinate>
Y: <center y coordinate>

If you cannot confidently identify it, return:

TARGET: NOT_FOUND
"""
)

print("==============================================")
print("Hammu AI - Visual Target Test")
print("==============================================")
print(result)