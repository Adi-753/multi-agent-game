from typing import Dict, List
from .base import BaseAgent
from .executor import ExecutorAgent
import asyncio
import random

class OrchestratorAgent(BaseAgent):
    """Agent responsible for coordinating multiple executor agents"""
    
    def __init__(self):
        super().__init__("OrchestratorAgent")   
        self.executor_pool_size = 3 
        
    async def execute(self, *args, **kwargs):
        return await self.execute_test(*args, **kwargs)
    
    async def execute_test(self, test_case: Dict) -> Dict:
        """Execute a test case using multiple executor agents"""
        self.log(f"Orchestrating test: {test_case['name']}")
        
        executors = [ExecutorAgent(f"exec_{i}") for i in range(self.executor_pool_size)]
        
        tasks = []
        for executor in executors:
            task = executor.execute_test(test_case, "https://play.ezygamers.com/")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = [r for r in results if not isinstance(r, Exception)]
        
        aggregated_result = {
            "test_id": test_case["id"],
            "test_name": test_case["name"],
            "executions": valid_results,
            "execution_count": len(valid_results),
            "consensus": self._calculate_consensus(valid_results),
            "aggregated_artifacts": self._aggregate_artifacts(valid_results)
        }
        
        self.log(f"Completed orchestration with {len(valid_results)} successful executions")
        return aggregated_result
    
    def _calculate_consensus(self, results: List[Dict]) -> Dict:
        if not results:
            return {"status": "no_results", "confidence": 0}
        
        success_count = sum(1 for r in results if r.get("success", False))
        total_count = len(results)
        
        confidence = success_count / total_count
        status = "pass" if confidence > 0.5 else "fail"
        
        return {
            "status": status,
            "confidence": confidence,
            "success_count": success_count,
            "total_count": total_count
        }
    
    def _aggregate_artifacts(self, results: List[Dict]) -> Dict:
        aggregated = {
            "all_screenshots": [],
            "all_logs": [],
            "execution_times": []
        }
        
        for result in results:
            artifacts = result.get("artifacts", {})
            aggregated["all_screenshots"].extend(artifacts.get("screenshots", []))
            aggregated["all_logs"].extend(artifacts.get("console_logs", []))
            
            if result.get("start_time") and result.get("end_time"):
                aggregated["execution_times"].append({
                    "agent_id": result.get("agent_id"),
                    "start": result["start_time"],
                    "end": result["end_time"]
                })
        
        return aggregated