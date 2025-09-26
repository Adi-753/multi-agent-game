from typing import List, Dict
from .base import BaseAgent
import asyncio

class RankerAgent(BaseAgent):
    
    def __init__(self):
        super().__init__("RankerAgent")
        
    async def execute(self, *args, **kwargs):
        return await self.rank_test_cases(*args, **kwargs)
    
    async def rank_test_cases(self, test_cases: List[Dict]) -> List[Dict]:
        self.log("Ranking test cases...")
        
        priority_scores = {"High": 3, "Medium": 2, "Low": 1}
        category_scores = {
            "functionality": 3,
            "error_handling": 2.5,
            "edge_case": 2,
            "ui_ux": 1.5,
            "performance": 1
        }
        
        for test in test_cases:
            priority_score = priority_scores.get(test.get("priority", "Medium"), 2)
            category_score = category_scores.get(test.get("category", "functionality"), 2)
            
            duration = test.get("estimated_duration", 20)
            duration_score = 3 if duration < 15 else 2 if duration < 30 else 1
            
            test["score"] = (priority_score * 0.4 + 
                           category_score * 0.4 + 
                           duration_score * 0.2)
        
        ranked_cases = sorted(test_cases, key=lambda x: x["score"], reverse=True)
        
        for idx, test in enumerate(ranked_cases):
            test["rank"] = idx + 1
        
        self.log(f"Ranked {len(ranked_cases)} test cases")
        return ranked_cases