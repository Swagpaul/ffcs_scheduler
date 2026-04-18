import os
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()

class AIRanker:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            self.client = Groq(api_key=api_key)
        else:
            self.client = None

    def rank_and_explain(self, timetables, preferences=None):
        if not self.client:
            return {"error": "GROQ_API_KEY not found. Please add it to your .env file."}

        # Select top 10 by score to send to AI
        top_candidates = sorted(timetables, key=lambda x: x['score'], reverse=True)[:10]
        
        prompt = f"""
        You are an expert academic advisor helping a student pick the best FFCS timetable.
        I have generated several valid timetables. Rank the top 5 and provide a concise explanation for each.
        
        Input Timetables (JSON):
        {json.dumps(top_candidates, indent=2)}
        
        User Preferences:
        {preferences if preferences else "Not specified"}
        
        Your Task:
        1. Identify the top 5 timetables.
        2. For each, explain WHY it is good (e.g., professor quality, slot distribution, compactness).
        3. Mention any trade-offs made (e.g., "Has top professors but early morning classes").
        
        Return the response in a structured JSON format:
        {{
            "rankings": [
                {{
                    "rank": 1,
                    "timetable_id": ID,
                    "explanation": "...",
                    "pros": ["...", "..."],
                    "cons": ["...", "..."]
                }},
                ...
            ],
            "overall_summary": "..."
        }}
        """

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful academic assistant."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            return {"error": str(e)}
