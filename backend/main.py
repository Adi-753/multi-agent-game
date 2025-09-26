import sys
import typing
from typing import Any, Dict

try:
    import pydantic.v1.typing as pv1typing
    original_evaluate = getattr(pv1typing, 'evaluate_forwardref', None)
    
    def patched_evaluate_forwardref(type_: Any, globalns: Dict[str, Any], localns: Dict[str, Any]) -> Any:
        if not hasattr(type_, '__forward_arg__'):
            return type_
        
        try:
            forward_arg = type_.__forward_arg__
            return eval(forward_arg, globalns, localns)
        except:
            return type_
    
    pv1typing.evaluate_forwardref = patched_evaluate_forwardref
except ImportError:
    pass
except AttributeError:
    pass

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List

from agents.planner import PlannerAgent
from agents.ranker import RankerAgent
from agents.orchestrator import OrchestratorAgent
from agents.analyzer import AnalyzerAgent
from services.report_generator import ReportGenerator
from models.schemas import TestPlan, ExecutionRequest, Report

app = FastAPI(title="Multi-Agent Game Tester POC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("artifacts", exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("artifacts/screenshots", exist_ok=True)

app.mount("/artifacts", StaticFiles(directory="artifacts"), name="artifacts")
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

current_plan: Dict = {}
execution_status: Dict = {"status": "idle", "progress": 0, "current_test": ""}

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

@app.get("/styles.css")
async def get_styles():
    return FileResponse("frontend/styles.css")

@app.get("/app.js")
async def get_app_js():
    return FileResponse("frontend/app.js")

@app.post("/api/generate-plan")
async def generate_plan():
    global current_plan
    
    planner = PlannerAgent()
    ranker = RankerAgent()
    
    try:
        test_cases = await planner.generate_test_cases("https://play.ezygamers.com/")
        ranked_cases = await ranker.rank_test_cases(test_cases)
        
        current_plan = {
            "id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "test_cases": ranked_cases,
            "total_cases": len(ranked_cases),
            "top_10": ranked_cases[:10]
        }
        
        return {"status": "success", "plan": current_plan}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/current-plan")
async def get_current_plan():
    if not current_plan:
        raise HTTPException(status_code=404, detail="No plan generated yet")
    return current_plan

@app.post("/api/execute-tests")
async def execute_tests(background_tasks: BackgroundTasks):
    if not current_plan:
        raise HTTPException(status_code=400, detail="No test plan available")
    
    background_tasks.add_task(run_tests_background)
    return {"status": "started", "message": "Test execution started"}

async def run_tests_background():
    global execution_status
    
    try:
        execution_status = {"status": "running", "progress": 0, "current_test": ""}
        
        orchestrator = OrchestratorAgent()
        analyzer = AnalyzerAgent()
        report_generator = ReportGenerator()
        
        top_10_tests = current_plan["top_10"]
        results = []
        
        for idx, test in enumerate(top_10_tests):
            execution_status["progress"] = (idx / len(top_10_tests)) * 100
            execution_status["current_test"] = test["name"]
            
            execution_result = await orchestrator.execute_test(test)
            analysis = await analyzer.analyze_results(execution_result)
            
            results.append(analysis)
        
        report = await report_generator.generate_report(results, current_plan)
        
        execution_status = {
            "status": "completed",
            "progress": 100,
            "current_test": "",
            "report_id": report["report_id"]
        }
        
    except Exception as e:
        execution_status = {
            "status": "error",
            "progress": 0,
            "current_test": "",
            "error": str(e)
        }

@app.get("/api/execution-status")
async def get_execution_status():
    return execution_status

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    report_path = f"reports/{report_id}.json"
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    with open(report_path, "r") as f:
        return json.load(f)

@app.get("/api/reports")
async def list_reports():
    reports = []
    if os.path.exists("reports"):
        for file in os.listdir("reports"):
            if file.endswith(".json"):
                reports.append(file.replace(".json", ""))
    return {"reports": reports}

if __name__ == "__main__":
    import uvicorn
    
    os.makedirs("artifacts", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
