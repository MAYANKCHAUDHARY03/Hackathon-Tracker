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
