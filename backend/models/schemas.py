from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class TestStep(BaseModel):
    step_index: int
    description: str
    expected_outcome: Optional[str] = None

class TestCase(BaseModel):
    id: str
    name: str
    category: str
    steps: List[str]
    expected_outcome: str
    priority: str
    estimated_duration: int
    score: Optional[float] = None
    rank: Optional[int] = None

class TestPlan(BaseModel):
    id: str
    test_cases: List[TestCase]
    total_cases: int
    top_10: List[TestCase]

class ExecutionRequest(BaseModel):
    test_plan_id: str
    execute_top_n: int = 10

class TestResult(BaseModel):
    test_id: str
    test_name: str
    verdict: str
    consensus: Dict
    cross_validation: Dict
    reproducibility_score: float
    artifact_analysis: Dict
    triage_notes: List[str]
    evidence: Dict
    timestamp: datetime

class Report(BaseModel):
    report_id: str
    timestamp: datetime
    test_plan_id: str
    total_planned_tests: int
    tests_executed: int
    summary: Dict
    test_results: List[TestResult]
    metadata: Dict
    recommendations: List[str]