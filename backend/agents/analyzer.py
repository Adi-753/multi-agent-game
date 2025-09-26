from typing import Dict, List
from .base import BaseAgent
import asyncio
from datetime import datetime

class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("AnalyzerAgent")
        
    async def execute(self, *args, **kwargs):
        return await self.analyze_results(*args, **kwargs)
    
    async def analyze_results(self, execution_result: Dict) -> Dict:
        self.log(f"Analyzing results for test: {execution_result['test_name']}")
        
        consensus = execution_result.get("consensus", {})
        executions = execution_result.get("executions", [])
        
        cross_validation = self._cross_validate_results(executions)
        
        reproducibility = self._calculate_reproducibility(executions)
        
        artifact_analysis = self._analyze_artifacts(execution_result.get("aggregated_artifacts", {}))
        
        triage_notes = self._generate_triage_notes(
            consensus, cross_validation, reproducibility, artifact_analysis
        )
        
        verdict = self._determine_verdict(consensus, cross_validation, reproducibility)
        
        analysis_result = {
            "test_id": execution_result["test_id"],
            "test_name": execution_result["test_name"],
            "verdict": verdict,
            "consensus": consensus,
            "cross_validation": cross_validation,
            "reproducibility_score": reproducibility,
            "artifact_analysis": artifact_analysis,
            "triage_notes": triage_notes,
            "evidence": self._collect_evidence(execution_result),
            "timestamp": datetime.now().isoformat()
        }
        
        return analysis_result
    
    def _cross_validate_results(self, executions: List[Dict]) -> Dict:
        if len(executions) < 2:
            return {"validated": False, "reason": "Insufficient executions for cross-validation"}
        
        step_counts = [len(e.get("steps_completed", [])) for e in executions]
        consistent_steps = all(count == step_counts[0] for count in step_counts)
        
        errors = [e.get("error") for e in executions if e.get("error")]
        consistent_errors = len(set(errors)) <= 1 if errors else True
        
        return {
            "validated": consistent_steps and consistent_errors,
            "consistent_steps": consistent_steps,
            "consistent_errors": consistent_errors,
            "step_variance": max(step_counts) - min(step_counts) if step_counts else 0
        }
    
    def _calculate_reproducibility(self, executions: List[Dict]) -> float:
        if not executions:
            return 0.0
        
        success_results = [e for e in executions if e.get("success", False)]
        
        if not success_results:
            return 0.0
        
        base_score = len(success_results) / len(executions)
        
        if len(success_results) > 1:
            step_counts = [len(e.get("steps_completed", [])) for e in success_results]
            if step_counts:
                avg_steps = sum(step_counts) / len(step_counts)
                variance = sum((x - avg_steps) ** 2 for x in step_counts) / len(step_counts)
                consistency_factor = 1 / (1 + variance)
                base_score *= consistency_factor
        
        return round(base_score, 2)
    
    def _analyze_artifacts(self, artifacts: Dict) -> Dict:
        analysis = {
            "screenshot_count": len(artifacts.get("all_screenshots", [])),
            "log_count": len(artifacts.get("all_logs", [])),
            "errors_detected": False,
            "warnings_detected": False,
            "performance_issues": False
        }
        
        logs = artifacts.get("all_logs", [])
        for log in logs:
            if log.get("type") == "error":
                analysis["errors_detected"] = True
            elif log.get("type") == "warning":
                analysis["warnings_detected"] = True
        
        exec_times = artifacts.get("execution_times", [])
        if exec_times:
            analysis["avg_execution_time"] = len(exec_times)
        
        return analysis
    
    def _generate_triage_notes(self, consensus: Dict, cross_validation: Dict, 
                               reproducibility: float, artifact_analysis: Dict) -> List[str]:
        """Generate actionable triage notes"""
        notes = []
        
        if consensus.get("confidence", 0) < 0.5:
            notes.append("Low confidence in test results - investigate flakiness")
        
        if consensus.get("status") == "fail":
            notes.append(f"Test failed in {consensus.get('total_count', 0) - consensus.get('success_count', 0)} out of {consensus.get('total_count', 0)} executions")
        
        if not cross_validation.get("validated", True):
            notes.append("Cross-validation failed - results inconsistent across agents")
        
        if cross_validation.get("step_variance", 0) > 0:
            notes.append(f"Step completion variance detected: {cross_validation['step_variance']} steps")
        
        if reproducibility < 0.7:
            notes.append(f"Low reproducibility score ({reproducibility}) - test may be unstable")
        
        if artifact_analysis.get("errors_detected"):
            notes.append("Console errors detected during execution")
        
        if artifact_analysis.get("warnings_detected"):
            notes.append("Console warnings detected - review for potential issues")
        
        return notes
    
    def _determine_verdict(self, consensus: Dict, cross_validation: Dict, 
                          reproducibility: float) -> str:
        if consensus.get("status") == "fail":
            return "FAIL"
        
        if not cross_validation.get("validated", True):
            return "INCONCLUSIVE"
        
        if reproducibility < 0.5:
            return "FLAKY"
        
        if consensus.get("confidence", 0) >= 0.8 and reproducibility >= 0.7:
            return "PASS"
        
        return "NEEDS_REVIEW"
    
    def _collect_evidence(self, execution_result: Dict) -> Dict:
        evidence = {
            "execution_count": execution_result.get("execution_count", 0),
            "key_screenshots": [],
            "critical_logs": [],
            "execution_summary": []
        }
        
        artifacts = execution_result.get("aggregated_artifacts", {})
        screenshots = artifacts.get("all_screenshots", [])
        if screenshots:
            evidence["key_screenshots"] = [screenshots[0], screenshots[-1]] if len(screenshots) > 1 else screenshots
        
        logs = artifacts.get("all_logs", [])
        evidence["critical_logs"] = [log for log in logs if log.get("type") in ["error", "warning"]][:5]
        
        for exec in execution_result.get("executions", []):
            evidence["execution_summary"].append({
                "agent_id": exec.get("agent_id"),
                "success": exec.get("success", False),
                "steps_completed": len(exec.get("steps_completed", [])),
                "error": exec.get("error")
            })
        
        return evidence