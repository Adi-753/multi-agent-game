import json
import os
from datetime import datetime
from typing import Dict, List
import aiofiles

class ReportGenerator:
    def __init__(self):
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    async def generate_report(self, test_results: List[Dict], test_plan: Dict) -> Dict:
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        summary = self._calculate_summary(test_results)
        
        report = {
            "report_id": report_id,
            "timestamp": datetime.now().isoformat(),
            "test_plan_id": test_plan.get("id"),
            "total_planned_tests": test_plan.get("total_cases", 0),
            "tests_executed": len(test_results),
            "summary": summary,
            "test_results": test_results,
            "metadata": {
                "game_url": "https://play.ezygamers.com/",
                "execution_type": "multi-agent",
                "agents_used": self._count_unique_agents(test_results)
            },
            "recommendations": self._generate_recommendations(test_results)
        }
        
        report_path = os.path.join(self.reports_dir, f"{report_id}.json")
        async with aiofiles.open(report_path, 'w') as f:
            await f.write(json.dumps(report, indent=2))
        
        return report
    
    def _calculate_summary(self, test_results: List[Dict]) -> Dict:
        verdicts = [r.get("verdict", "UNKNOWN") for r in test_results]
        
        summary = {
            "total_tests": len(test_results),
            "passed": verdicts.count("PASS"),
            "failed": verdicts.count("FAIL"),
            "flaky": verdicts.count("FLAKY"),
            "inconclusive": verdicts.count("INCONCLUSIVE"),
            "needs_review": verdicts.count("NEEDS_REVIEW"),
            "average_reproducibility": self._calculate_avg_reproducibility(test_results),
            "tests_with_errors": sum(1 for r in test_results if r.get("artifact_analysis", {}).get("errors_detected", False)),
            "tests_with_warnings": sum(1 for r in test_results if r.get("artifact_analysis", {}).get("warnings_detected", False))
        }
        
        if summary["total_tests"] > 0:
            summary["pass_rate"] = round((summary["passed"] / summary["total_tests"]) * 100, 2)
        else:
            summary["pass_rate"] = 0
        
        return summary
    
    def _calculate_avg_reproducibility(self, test_results: List[Dict]) -> float:
        scores = [r.get("reproducibility_score", 0) for r in test_results]
        return round(sum(scores) / len(scores), 2) if scores else 0
    
    def _count_unique_agents(self, test_results: List[Dict]) -> int:
        agents = set()
        for result in test_results:
            for exec_summary in result.get("evidence", {}).get("execution_summary", []):
                agent_id = exec_summary.get("agent_id")
                if agent_id:
                    agents.add(agent_id)
        return len(agents)
    
    def _generate_recommendations(self, test_results: List[Dict]) -> List[str]:
        recommendations = []
        
        verdicts = [r.get("verdict", "UNKNOWN") for r in test_results]
        fail_rate = verdicts.count("FAIL") / len(verdicts) if verdicts else 0
        
        if fail_rate > 0.3:
            recommendations.append("High failure rate detected - review game functionality")
        
        flaky_count = verdicts.count("FLAKY")
        if flaky_count > 0:
            recommendations.append(f"{flaky_count} flaky tests detected - improve test stability")
        
        low_repro_tests = [r for r in test_results if r.get("reproducibility_score", 1) < 0.7]
        if low_repro_tests:
            recommendations.append(f"{len(low_repro_tests)} tests have low reproducibility - investigate test design")
        
        error_tests = [r for r in test_results if r.get("artifact_analysis", {}).get("errors_detected", False)]
        if error_tests:
            recommendations.append(f"Console errors detected in {len(error_tests)} tests - check application logs")
        
        if not recommendations:
            recommendations.append("All tests completed successfully with good stability")
        
        return recommendations