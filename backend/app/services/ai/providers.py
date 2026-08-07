from typing import Dict, Any, List
from .base import AIProviderAdapter
from .privacy import AIPrivacyFilter

class MockAIProvider(AIProviderAdapter):
    """
    Mock AI Provider used for deterministic testing and placeholder execution.
    """
    
    async def generate_project_summary(self, project_data: Dict[str, Any]) -> str:
        safe_data = AIPrivacyFilter.filter_dict(project_data)
        AIPrivacyFilter.audit_log("MockAI", "generate_project_summary", len(str(safe_data)))
        
        return "This is an AI-generated summary of the project."
        
    async def analyze_project_health(self, project_data: Dict[str, Any], tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        safe_project = AIPrivacyFilter.filter_dict(project_data)
        safe_tasks = AIPrivacyFilter.filter_list(tasks)
        AIPrivacyFilter.audit_log("MockAI", "analyze_project_health", len(str(safe_project)) + len(str(safe_tasks)))
        
        # Deterministic risk calculation
        open_tasks = [t for t in safe_tasks if t.get('status') != 'done']
        high_priority = [t for t in open_tasks if t.get('priority') == 'high']
        
        risk_score = min(100, len(open_tasks) * 5 + len(high_priority) * 10)
        
        return {
            "health_status": "at_risk" if risk_score > 50 else "healthy",
            "risk_score": risk_score,
            "recommendations": [
                "Review high priority tasks",
                "Ensure requirements are met"
            ] if risk_score > 50 else ["Keep up the good work"]
        }

class GeminiAIProvider(AIProviderAdapter):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        try:
            from google import genai
            self.client = genai.Client(api_key=api_key)
        except ImportError:
            self.client = None
            
    async def generate_project_summary(self, project_data: Dict[str, Any]) -> str:
        if not self.client:
            return "Gemini library not installed. Falling back to simple summary."
            
        safe_data = AIPrivacyFilter.filter_dict(project_data)
        AIPrivacyFilter.audit_log("GeminiAI", "generate_project_summary", len(str(safe_data)))
        
        prompt = f"Summarize this hackathon project in two concise paragraphs based on this data: {safe_data}"
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            return f"Failed to generate summary: {str(e)}"
            
    async def analyze_project_health(self, project_data: Dict[str, Any], tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not self.client:
            return {"health_status": "unknown", "risk_score": 0, "recommendations": ["Install google-genai"]}
            
        safe_project = AIPrivacyFilter.filter_dict(project_data)
        safe_tasks = AIPrivacyFilter.filter_list(tasks)
        AIPrivacyFilter.audit_log("GeminiAI", "analyze_project_health", len(str(safe_project)) + len(str(safe_tasks)))
        
        prompt = f"""
        Analyze the health of this project based on its tasks. 
        Project: {safe_project}
        Tasks: {safe_tasks}
        
        Return exactly valid JSON with three keys:
        - health_status (string: 'healthy', 'at_risk', 'critical')
        - risk_score (integer 0-100)
        - recommendations (list of 2-3 short string recommendations)
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            import json
            return json.loads(response.text)
        except Exception as e:
            return {"health_status": "error", "risk_score": 0, "recommendations": [f"Error: {str(e)}"]}

class AIProviderFactory:
    @staticmethod
    def get_provider(provider_type: str, api_key: str) -> AIProviderAdapter:
        if provider_type == "gemini" and api_key:
            return GeminiAIProvider(api_key)
        return MockAIProvider(api_key)
