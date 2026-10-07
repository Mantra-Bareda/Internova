import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import requests

GROQ_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3-32b",
    "qwen/qwen3.6-27b"
]

def call_groq_with_fallback(prompt, system_prompt="You are an expert career counselor. Output ONLY valid JSON."):
    api_key = os.environ.get("GROQ_API_KEY", os.environ.get("OPENROUTER_API_KEY", "fake-key"))
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    for model in GROQ_MODELS:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                content = content.replace('```json', '').replace('```', '').strip()
                return json.loads(content)
            else:
                print(f"Model {model} failed: {response.status_code}")
        except Exception as e:
            print(f"Model {model} error: {e}")
            
    raise Exception("All Groq fallback models failed.")



# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Use the recommended model for text and chat
model = genai.GenerativeModel('gemini-3.1-flash-lite')

def generate_career_dashboard(resume_text):
    """Generates the Roadmap, Skill Score, and 'Why Not Hired' report."""
    prompt = f"""
    You are an expert career counselor and tech recruiter. Analyze the following candidate data:
    Resume Extract: {resume_text}
    
    Provide a comprehensive analysis in valid JSON format with exactly these keys:
    1. "roadmap": A 3-step actionable plan (list of strings).
    2. "skill_score": An integer out of 100 based on market demand for these skills.
    3. "skills_to_improve": A list of objects, each containing:
       - "skill": The name of a skill they need to learn or improve.
       - "learning_links": A list of 2-3 real URLs (e.g., YouTube search links, freeCodeCamp, or official docs) to learn it.
    4. "internship_recommended": Boolean (true if skill_score is 70 or above, indicating they should find an internship to build their portfolio, else false).
    5. "portfolio_design_rating": A string rating (e.g., "6/10") judging the resume's structural/visual appeal based on the text extract.
    6. "portfolio_suggestions": A list of website URLs (like Novoresume, Canva, GitHub Pages) to build a better looking portfolio.
    7. "why_not_hired": A blunt, constructive 2-paragraph analysis on gaps in their profile and why they might be failing interviews.
    
    Output ONLY valid JSON.
    """
    response = model.generate_content(prompt)
    
    # Strip markdown code blocks if the model wrapped the JSON
    raw_text = response.text.replace('```json', '').replace('```', '').strip()
    
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "roadmap": ["Error generating roadmap. Please try again."],
            "skill_score": 0,
            "skills_to_improve": [],
            "internship_recommended": False,
            "portfolio_design_rating": "N/A",
            "portfolio_suggestions": [],
            "why_not_hired": "Could not parse AI response."
        }

def generate_mock_interview_response(chat_history_str, new_user_message):
    """Simulates a demanding but fair virtual manager."""
    system_instruction = """
    You are 'Alex', a demanding but fair engineering manager conducting a mock interview/1-on-1.
    You expect concise, technical answers. If the user gives a vague answer, push back and ask for an example.
    Keep your responses to 1-2 short paragraphs.
    """
    
    prompt = f"{system_instruction}\n\nPrevious Conversation:\n{chat_history_str}\n\nCandidate says: {new_user_message}\n\nManager Alex responds:"
    
    response = model.generate_content(prompt)
    return response.text

def find_internships_for_user(resume_text, old_analysis_json=None):
    """Generates internship recommendations based on the resume."""
    if old_analysis_json:
        prompt = f"""
        Analyze the following UPDATED resume. 
        Previous AI Advice Given (for context): {old_analysis_json}
        
        First, check if the skills were updated according to the previous recommendations.
        If yes, suggest NEW internships and NEW skills to work on. Also, for each internship, suggest 1-2 free/paid courses the user should do to prepare.
        
        Provide the output in valid JSON format with exactly these keys:
        - "overall_readiness": object with "ready_for_internship" (boolean), "skill_score" (integer), "action_required" (string).
        - "next_steps": list of 3 actionable steps (strings).
        - "personalized_message": string with a short encouraging message (mentioning their progress if they applied feedback).
        - "internships": list of 3-5 objects, each with "title" (string), "company" (string), "difficulty" (string), "description" (string), "reason" (string), "link" (string), and "courses" (list of objects with "name" string, "type" string like 'free'/'paid', and "link" URL).
        - "skill_recommendations": list of 3 NEW objects, each with "skill", "priority", "estimated_time", "learning_resources" (list of 2 URLs).
        
        Updated Resume:
        {resume_text}
        """
    else:
        prompt = f"""
        Analyze the following resume and recommend 3-5 suitable internship roles or specific types of companies.
        Provide the output in valid JSON format with exactly these keys:
        - "overall_readiness": object with "ready_for_internship" (boolean), "skill_score" (integer out of 100), "action_required" (string).
        - "next_steps": list of 3 actionable steps (strings).
        - "personalized_message": string with a short encouraging message.
        - "internships": list of 3-5 objects, each with "title" (string), "company" (string, type of company), "difficulty" (string: beginner, intermediate, advanced), "description" (string), "reason" (string, why it matches), "link" (string, e.g., 'https://linkedin.com/jobs/search/?keywords=internship'), and "courses" (list of objects with "name" string, "type" string like 'free'/'paid', and "link" URL).
        - "skill_recommendations": list of 3 objects, each with "skill" (string), "priority" (string: high, medium, low), "estimated_time" (string), "learning_resources" (list of 2 URLs).
        
        Resume:
        {resume_text}
        """
    response = model.generate_content(prompt)
    raw_text = response.text.replace('```json', '').replace('```', '').strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "overall_readiness": {"ready_for_internship": False, "skill_score": 0, "action_required": "Error parsing AI response."},
            "next_steps": ["Please try generating again."],
            "personalized_message": "An error occurred while generating internships.",
            "internships": [],
            "skill_recommendations": []
        }

def generate_mock_interview_questions(resume_text, role_type):
    """Generates mock interview questions for a specific role."""
    prompt = f"""
    Based on the following resume, generate 5 mock interview questions tailored for a '{role_type}' role.
    Provide the output in valid JSON format with exactly these keys:
    - "role_context": A short string describing the role and what companies look for.
    - "questions": A list of 5 objects, each containing:
        - "category": string (e.g., Technical, Behavioral, Core).
        - "difficulty": string (easy, medium, hard).
        - "question": The actual interview question.
        - "hint": A short hint to help them think.
        - "sample_answer": A sample good answer based on their resume.
        - "what_interviewer_looks_for": What the interviewer is evaluating.
    - "interview_tips": A list of 3-5 general interview tips (strings).
    
    Resume:
    {resume_text}
    """
    response = model.generate_content(prompt)
    raw_text = response.text.replace('```json', '').replace('```', '').strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "role_context": "Error parsing AI response.",
            "questions": [],
            "interview_tips": ["Try generating again."]
        }

def generate_roadmap_chat_response(resume_text, chat_history, message):
    """Simulates an AI advisor for career roadmap discussion."""
    system_instruction = """
    You are an expert career AI advisor. You are having a chat with a candidate about their career roadmap.
    Keep responses concise, helpful, and actionable.
    """
    prompt = f"{system_instruction}\n\nCandidate Resume:\n{resume_text}\n\nPrevious Chat:\n{chat_history}\n\nCandidate: {message}\n\nAdvisor:"
    response = model.generate_content(prompt)
    return response.text

def generate_career_alignment(resume_text):
    """Generates career alignment insights."""
    prompt = f"""
    Analyze the following resume and provide career alignment insights.
    Provide valid JSON with exactly these keys:
    - "recommended_paths": List of 3 objects, each with "role" (string), "match_percentage" (integer), "reasoning" (string), "missing_skills" (list of strings).
    - "ai_vulnerability": Object with "risk_score" (integer 0-100), "risk_level" (string: HIGH, MEDIUM, LOW), "analysis" (string), "future_proofing_advice" (string).
    - "market_scope": Object with "hiring_demand" (string, e.g., "High", "Growing"), "growth_trajectory" (string).
    
    Resume:
    {resume_text}
    """
    response = model.generate_content(prompt)
    raw_text = response.text.replace('```json', '').replace('```', '').strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "recommended_paths": [],
            "ai_vulnerability": {"risk_score": 0, "risk_level": "UNKNOWN", "analysis": "Error parsing AI response.", "future_proofing_advice": ""},
            "market_scope": {"hiring_demand": "Unknown", "growth_trajectory": ""}
        }

def generate_career_options(resume_text):
    """Generates 3 possible career paths based on the resume."""
    prompt = f"""
    Analyze the resume and suggest 3 possible career paths or specializations.
    Return ONLY valid JSON as a list of strings representing the titles of these career paths.
    
    Resume:
    {resume_text}
    """
    response = model.generate_content(prompt)
    raw_text = response.text.replace('```json', '').replace('```', '').strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return ["Software Engineer", "Data Analyst", "Product Manager"]

def generate_specific_roadmap(resume_text, selected_option):
    """Generates an HTML roadmap for a specific career path."""
    prompt = f"""
    The candidate has selected the career path: {selected_option}.
    Based on their resume, generate a step-by-step roadmap to achieve this goal.
    Return the roadmap as HTML formatted text (e.g., using <ul>, <li>, <h3> tags). Do NOT wrap it in markdown code blocks like ```html.
    
    Resume:
    {resume_text}
    """
    response = model.generate_content(prompt)
    return response.text.replace('```html', '').replace('```', '').strip()

def generate_version_comparison(old_resume_text, old_analysis_json, new_resume_text):
    """Generates a contextual comparison using Groq AI with fallbacks. If it's a good update, generates a new review."""
    system_prompt = "You are a strict but encouraging career coach evaluating a revised draft of a candidate's resume. Output ONLY valid JSON."
    
    analysis_prompt = f"""
    Old Resume Extract:
    {old_resume_text}
    
    Old AI Advice (JSON):
    {old_analysis_json}
    
    New Revised Resume Extract:
    {new_resume_text}
    
    Compare the new resume against the old resume and the old AI advice to see if the user applied the recommended changes.
    Are the updates good enough to be considered a proper improvement?
    Provide a comprehensive analysis in valid JSON format with exactly these keys:
    1. "is_good": Boolean (true if they properly applied the feedback and made a good update, false if they missed a lot or made trivial changes).
    2. "applied_feedback": List of strings (praising what they fixed based on the old advice).
    3. "ignored_feedback": List of strings (calling out what they missed or failed to fix).
    4. "score_change": String (e.g., "+15", "-5", "No Change").
    5. "new_skill_score": Integer (out of 100).
    6. "next_steps": List of strings (new actionable roadmap steps).
    """
    
    try:
        comparison_result = call_groq_with_fallback(analysis_prompt, system_prompt)
        
        if comparison_result.get("is_good", False):
            # It's good! Ask Groq for a new review.
            new_review_prompt = f"""
            You are an expert career counselor and tech recruiter. Analyze the following updated candidate resume.
            
            Previous AI Advice Given to Candidate (for context):
            {old_analysis_json}
            
            New Updated Resume Extract: 
            {new_resume_text}
            
            Please provide a comprehensive re-analysis in valid JSON format with exactly these keys:
            1. "roadmap": A 3-step actionable plan (list of strings).
            2. "skill_score": An integer out of 100 based on market demand for these skills.
            3. "skills_to_improve": A list of objects, each containing:
               - "skill": The name of a skill they need to learn or improve.
               - "learning_links": A list of 2-3 real URLs (e.g., YouTube search links, freeCodeCamp, or official docs) to learn it.
            4. "internship_recommended": Boolean (true if skill_score is 70 or above).
            5. "portfolio_design_rating": A string rating (e.g., "6/10") judging the resume's structural/visual appeal.
            6. "portfolio_suggestions": A list of website URLs (like Novoresume, Canva, GitHub Pages) to build a better looking portfolio.
            7. "why_not_hired": A blunt, constructive 2-paragraph analysis on gaps in their profile and why they might be failing interviews.
            """
            response = model.generate_content(new_review_prompt)
            raw_text = response.text.replace('```json', '').replace('```', '').strip()
            new_review = json.loads(raw_text)
            new_review['is_good'] = True
            new_review['score_change'] = comparison_result.get('score_change', '+0')
            return new_review
        else:
            # Not good enough, just return the comparison
            comparison_result['is_good'] = False
            return comparison_result
            
    except Exception as e:
        print(f"Error in Groq comparison: {e}")
        return {
            "score_change": "No Change",
            "new_skill_score": 0,
            "applied_feedback": ["Error analyzing update."],
            "ignored_feedback": ["Could not reach AI models."],
            "next_steps": ["Please try again."],
            "is_good": False
        }
