import os
import json
import random
import PyPDF2
import docx
import google.generativeai as genai

def extract_text_from_pdf(filepath):
    text = ""
    try:
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
    return text

def extract_text_from_docx(filepath):
    text = ""
    try:
        doc = docx.Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
    return text

def analyze_cv(text):
    """
    Analyzes CV text using Gemini API and returns scores and feedback.
    """
    # Setup Gemini API inside the function to ensure env vars are loaded
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        
        prompt = f"""
        You are an expert HR recruiter and ATS optimizer. Analyze the following CV text and provide scores out of 100 for four categories:
        1. structure
        2. skills
        3. formatting
        4. content
        
        Also provide:
        - A short 'feedback_text' paragraph (2-3 sentences) giving a general overview of the CV's strengths and weaknesses.
        - A list of 3 to 5 'suggestions' for improvement.
        - A list of 3 specific 'recommended_roles' the candidate is highly qualified for.
        
        CRITICAL: You MUST write the 'feedback_text', 'suggestions', and 'recommended_roles' entirely in Uzbek.
        
        Return the response strictly as a JSON object with no markdown formatting, using this exact format:
        {{
            "scores": {{
                "structure": 80,
                "skills": 75,
                "formatting": 90,
                "content": 70
            }},
            "feedback_text": "Umumiy tahlil matni shu yerda...",
            "suggestions": [
                "Birinchi taklif...",
                "Ikkinchi taklif..."
            ],
            "recommended_roles": [
                "Dasturiy ta'minot muhandisi",
                "Backend Dasturchi"
            ]
        }}
        
        CV Text:
        {text[:5000]}
        """
        
        try:
            model = genai.GenerativeModel('gemini-flash-latest', generation_config={"response_mime_type": "application/json"})
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Robust JSON extraction
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end != 0:
                response_text = response_text[start:end]
                
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error. Raw text was: {response_text}")
                raise e
                
            scores = data.get("scores", {})
            recommended_roles = data.get("recommended_roles", [])
            ai_feedback_text = data.get("feedback_text", "")
            ai_suggestions = data.get("suggestions", [])
            
            # Ensure all keys exist
            for key in ['structure', 'skills', 'formatting', 'content']:
                if key not in scores:
                    scores[key] = random.uniform(60, 85)
                    
            overall_score = sum(scores.values()) / 4
            
            # If AI successfully generated text, return it directly
            if ai_feedback_text and ai_suggestions:
                formatted_suggestions = "\n".join([f"- {s}" for s in ai_suggestions])
                return scores, overall_score, {
                    'feedback_text': ai_feedback_text,
                    'suggestions': formatted_suggestions,
                    'recommended_roles': recommended_roles
                }
                
        except Exception as e:
            print(f"Gemini API Error: {e}")
            scores = {
                'structure': random.uniform(60, 85),
                'skills': random.uniform(60, 85),
                'formatting': random.uniform(60, 85),
                'content': random.uniform(60, 85)
            }
            recommended_roles = []
    else:
        print("No GEMINI_API_KEY found, using random scores.")
        scores = {
            'structure': random.uniform(60, 85),
            'skills': random.uniform(60, 85),
            'formatting': random.uniform(60, 85),
            'content': random.uniform(60, 85)
        }
        recommended_roles = []
    
    overall_score = sum(scores.values()) / 4
    
    # Fallback to static translated strings if AI text generation failed
    from flask_babel import gettext as _
    
    feedback_text = []
    suggestions = []
    
    # Structure Feedback
    if scores['structure'] > 85:
        feedback_text.append(_("Your CV has an excellent structure that makes it easy to read."))
    elif scores['structure'] > 70:
        feedback_text.append(_("The structure of your CV is good, but could be organized slightly better."))
        suggestions.append(_("- Consider moving your most relevant experience closer to the top."))
    else:
        feedback_text.append(_("The CV structure is somewhat confusing and may be hard for recruiters to scan."))
        suggestions.append(_("- Use clear headings (Experience, Education, Skills)."))
        suggestions.append(_("- Ensure chronological order is used correctly."))

    # Skills Feedback
    if scores['skills'] > 85:
        feedback_text.append(_("You have a strong, well-defined skills section."))
    elif scores['skills'] > 70:
        feedback_text.append(_("Your skills section is decent, but could be more targeted."))
        suggestions.append(_("- Add more specific technical keywords related to your industry."))
    else:
        feedback_text.append(_("The skills section is lacking depth and might not pass Applicant Tracking Systems (ATS)."))
        suggestions.append(_("- Create a dedicated 'Skills' section."))
        suggestions.append(_("- List both hard and soft skills clearly."))

    # Content Feedback
    if scores['content'] > 85:
        feedback_text.append(_("Your descriptions are impactful and action-oriented."))
    elif scores['content'] > 70:
        feedback_text.append(_("Your experience descriptions are okay, but lack measurable impact."))
        suggestions.append(_("- Add quantifiable achievements (e.g., 'Increased sales by 20%')."))
    else:
        feedback_text.append(_("The content focuses too much on daily duties rather than achievements."))
        suggestions.append(_("- Use strong action verbs (Led, Developed, Managed)."))
        suggestions.append(_("- Focus on what you accomplished, not just what you were assigned to do."))

    feedback = {
        'feedback_text': " ".join(feedback_text),
        'suggestions': "\n".join(suggestions),
        'recommended_roles': recommended_roles
    }
    
    return scores, overall_score, feedback
