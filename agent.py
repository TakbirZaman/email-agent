import os
import json
import google.generativeai as genai

API_KEY = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=API_KEY)

MOCK_EMAILS = [
    {"id": "e1", "from": "boss@company.com", "subject": "Q3 Report Review",
     "body": "Can you review the Q3 financial report and send feedback by Friday?"},
    {"id": "e2", "from": "client@acme.com", "subject": "Meeting Rescheduled",
     "body": "Need to reschedule Thursday 2pm call to Friday 3pm. Please confirm."},
    {"id": "e3", "from": "dev@team.com", "subject": "Bug in Production",
     "body": "Critical: Login endpoint returning 500 errors since last deploy. Needs immediate fix."},
    {"id": "e4", "from": "hr@company.com", "subject": "Team Lunch Tomorrow",
     "body": "Reminder: team lunch tomorrow at 1pm. No action needed, just show up!"},
    {"id": "e5", "from": "partner@startup.io", "subject": "Integration Proposal",
     "body": "Can you draft a technical spec for our API integration and share it by next week?"},
]

def analyze_emails():
    model = genai.GenerativeModel("gemini-1.5-flash-8b")
    tasks = []
    skipped = []

    print("\n🤖 Email Agent Starting")
    print("=" * 40)

    for email in MOCK_EMAILS:
        print(f"\n📧 Analyzing: {email['subject']}")
        prompt = f"""Analyze this email and decide if it needs action.

From: {email['from']}
Subject: {email['subject']}
Body: {email['body']}

Reply in this exact JSON format only, no extra text:
{{
  "needs_action": true or false,
  "task_title": "short task title if needs_action is true, else empty string",
  "priority": "urgent/high/medium/low if needs_action is true, else empty string",
  "due": "due date like Friday or Next Monday if mentioned, else empty string",
  "reason": "why this does or does not need action"
}}"""

        try:
            response = model.generate_content(prompt)
            text = response.text.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            result = json.loads(text)

            if result.get("needs_action"):
                tasks.append({
                    "title": result.get("task_title", email["subject"]),
                    "priority": result.get("priority", "medium"),
                    "due": result.get("due", ""),
                    "from": email["from"]
                })
                print(f"  ✅ Task: {result.get('task_title')} [{result.get('priority')}]")
            else:
                skipped.append(email["subject"])
                print(f"  🔕 Skipped: {result.get('reason')}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("\n" + "=" * 40)
    print(f"📋 SUMMARY: {len(tasks)} tasks created, {len(skipped)} skipped\n")

    if tasks:
        print("TASKS:")
        for t in tasks:
            due = f" | due: {t['due']}" if t['due'] else ""
            print(f"  [{t['priority'].upper()}] {t['title']}{due}")
            print(f"         from: {t['from']}")

    if skipped:
        print("\nSKIPPED:")
        for s in skipped:
            print(f"  - {s}")

if __name__ == "__main__":
    if not API_KEY:
        print("GEMINI_API_KEY not set.")
    else:
        analyze_emails()
