from db_manager import get_anonymous_session

FORBIDDEN_WORDS = {"hack", "exploit", "illegal", "malware", "phishing", "scam", "hate"}

def validate_chat_request(text: str, email: str=None, session_id: str=None):
    if not email and not session_id:
        return {"error": "Either email or session_id is required"}
    
    if session_id and not email:
        session = get_anonymous_session(session_id)
        if isinstance(session, dict) and "api_calls" in session and session["api_calls"] >= 5:
            return {
                "error": "You've reached the maximum number of free API calls. Please register to continue.",
                "limit_reached": True
            }
    
    text_lower = text.lower()
    for word in FORBIDDEN_WORDS:
        if word in text_lower:
            return {"error": f"Your message contains forbidden content", "forbidden": True}
    
    return None