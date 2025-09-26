import traceback
import sys

print("Testing imports...")

try:
    print("1. Importing FastAPI...")
    from fastapi import FastAPI
    print("   ✓ FastAPI imported successfully")
except Exception as e:
    print(f"   ✗ Error importing FastAPI: {e}")
    traceback.print_exc()

try:
    print("2. Importing agents.planner...")
    from agents.planner import PlannerAgent
    print("   ✓ PlannerAgent imported successfully")
except Exception as e:
    print(f"   ✗ Error importing PlannerAgent: {e}")
    traceback.print_exc()

try:
    print("3. Importing all agents...")
    from agents.ranker import RankerAgent
    from agents.orchestrator import OrchestratorAgent
    from agents.analyzer import AnalyzerAgent
    print("   ✓ All agents imported successfully")
except Exception as e:
    print(f"   ✗ Error importing agents: {e}")
    traceback.print_exc()

try:
    print("4. Importing services...")
    from services.report_generator import ReportGenerator
    print("   ✓ ReportGenerator imported successfully")
except Exception as e:
    print(f"   ✗ Error importing ReportGenerator: {e}")
    traceback.print_exc()

try:
    print("5. Importing models...")
    from models.schemas import TestPlan, ExecutionRequest, Report
    print("   ✓ Models imported successfully")
except Exception as e:
    print(f"   ✗ Error importing models: {e}")
    traceback.print_exc()

print("\nImport test complete!")
