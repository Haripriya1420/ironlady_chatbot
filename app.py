from flask import Flask, render_template, request, jsonify
import re
from transformers import pipeline

app = Flask(__name__)

# Initialize HuggingFace text-generation pipeline (free)
generator = pipeline("text-generation", model="gpt2")  # GPT-2 is free

# Predefined FAQs
FAQS = {
    "duration": "Program duration varies by track (e.g., 8–12 weeks). Please check the specific program page for exact dates.",
    "mode": "Programs are primarily online with live, interactive sessions.",
    "certificate": "Yes, a certificate is provided upon successful completion.",
    "mentors": "Sessions are led by experienced industry mentors and certified coaches.",
    "eligibility": "Typically open to students, recent graduates, and early professionals. See program page for criteria.",
    "fees": "Fees vary by program. Scholarships/discounts may be available.",
    "apply": "Apply via the Iron Lady website application form on the program page.",
    "principles": "Iron Lady’s leadership principles are taught through Business War Tactics, which include: Shameless Pitching, Strategic Maximization, and Cultivating Unwavering Confidence.",
    "programs": "Iron Lady offers various programs including the 2-Day Transformational Masterclass (Business War Tactics), Career Acceleration Programs, and specialized leadership tracks for women professionals.",
    "vision": "Iron Lady’s vision is to empower women to lead with confidence, resilience, and influence in every sphere of life."
}

# Keywords for rule-based FAQ
KEYWORDS = {
    "duration": ["duration", "how long", "length", "weeks", "months"],
    "mode": ["mode", "online", "offline", "hybrid", "format", "class"],
    "certificate": ["certificate", "certification", "proof"],
    "mentors": ["mentor", "mentors", "coach", "trainer", "faculty", "instructor"],
    "eligibility": ["eligibility", "prerequisite", "who can apply", "requirements", "criteria"],
    "fees": ["fee", "fees", "cost", "price", "tuition"],
    "apply": ["apply", "application", "enroll", "enrol", "registration", "register"],
    "principles": ["principles", "values", "leadership", "tactics", "philosophy"],
    "programs": ["programs", "courses", "offerings", "tracks", "classes"],
    "vision": ["vision", "mission", "goal", "objective", "aim"]
}

# Normalize user input
def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()

# Rule-based response
def chatbot_response(user_input: str) -> str:
    text = normalize(user_input)
    for key, words in KEYWORDS.items():
        for w in words:
            if w in text:
                return FAQS[key]
    return None

# AI fallback using HuggingFace GPT-2
def ai_fallback(user_input: str) -> str:
    try:
        prompt = f"Answer briefly this FAQ about Iron Lady programs: {user_input}"
        result = generator(prompt, max_length=100, do_sample=True, temperature=0.7)
        answer = result[0]['generated_text'].replace(prompt, "").strip()
        # Avoid extremely long or irrelevant output
        if len(answer) > 200:
            answer = answer[:200] + "..."
        return answer if answer else "Sorry, I don’t have an answer to that yet."
    except Exception as e:
        print("HuggingFace Error:", e)
        return "Sorry, I don’t have an answer to that yet."

# Flask routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "")

    # Try FAQ first
    reply = chatbot_response(user_message)
    # Use AI fallback if no FAQ match
    if reply is None:
        reply = ai_fallback(user_message)

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
