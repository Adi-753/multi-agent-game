import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

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
except:
    pass

from backend.agents.game_analyzer import GameAnalyzerAgent
from backend.agents.planner import PlannerAgent
from backend.rag_simple import SimpleRAGKnowledgeBase
from dotenv import load_dotenv

load_dotenv()

GAME_URL = os.getenv("GAME_URL", "https://play.ezygamers.com/")

async def test_rag_learning():
    print("=" * 70)
    print("TESTING RAG-BASED LEARNING SYSTEM")
    print("="  * 70)
    
    print(f"\n📌 Game URL: {GAME_URL}")
    print(f"🎯 Target: Demonstrate trainable, learning AI system\n")
    
    print("-" * 70)
    print("STEP 1: Initialize RAG Knowledge Base")
    print("-" * 70)
    
    rag = SimpleRAGKnowledgeBase()
    print("✓ RAG Knowledge Base initialized")
    print(f"  - Storage directory: ./knowledge_base")
    print(f"  - Using Sentence-Transformers for embeddings")
    
    print("\n" + "-" * 70)
    print("STEP 2: Analyze Game and Store Knowledge")
    print("-" * 70)
    
    analyzer = GameAnalyzerAgent()
    analysis = await analyzer.analyze_game(GAME_URL)
    
    print(f"\n🎮 Game Analysis:")
    print(f"  - Game Type: {analysis.get('game_type', 'unknown')}")
    print(f"  - Interaction Model: {analysis.get('interaction_model', 'unknown')}")
    print(f"  - Features Detected: {len(analysis.get('features', []))}")
    print(f"  - UI Elements Found: {len(analysis.get('ui_elements', []))}")
    
    if analysis.get('features'):
        print(f"\n  📋 Features:")
        for feature in analysis.get('features', [])[:5]:
            print(f"    • {feature}")
    
    print("\n📦 Storing game analysis in RAG knowledge base...")
    knowledge_id = rag.store_game_analysis(GAME_URL, analysis)
    print(f"✓ Stored as: {knowledge_id}")
    
    print("\n" + "-" * 70)
    print("STEP 3: Generate Tests with RAG-Enhanced Planner")
    print("-" * 70)
    
    planner = PlannerAgent(rag_enabled=True)
    print("✓ Planner agent initialized with RAG")
    
    test_cases = await planner.generate_test_cases(GAME_URL)
    
    print(f"\n🧪 Generated {len(test_cases)} test cases")
    
    sumlink_tests = [tc for tc in test_cases if 'sumlink' in tc['id']]
    generic_tests = [tc for tc in test_cases if 'sumlink' not in tc['id']]
    
    if sumlink_tests:
        print(f"  ✓ {len(sumlink_tests)} SumLink-specific tests (click-based)")
    if generic_tests:
        print(f"  • {len(generic_tests)} generic tests (fallback)")
    
    print(f"\n📝 Sample SumLink Test Cases:")
    for i, tc in enumerate(sumlink_tests[:3], 1):
        print(f"\n  {i}. {tc['name']}")
        print(f"     ID: {tc['id']}")
        print(f"     Category: {tc['category']}")
        print(f"     Priority: {tc['priority']}")
        print(f"     First step: {tc['steps'][0] if tc['steps'] else 'N/A'}")
    
    print("\n" + "-" * 70)
    print("STEP 4: Simulate Test Execution and Store Results")
    print("-" * 70)
    
    simulated_results = [
        {
            "test_id": "sumlink_001",
            "name": "Verify basic number tile clicking",
            "status": "passed",
            "duration": 18,
            "category": "functionality",
            "errors": []
        },
        {
            "test_id": "sumlink_002",
            "name": "Test stage progression",
            "status": "passed",
            "duration": 42,
            "category": "functionality",
            "errors": []
        },
        {
            "test_id": "sumlink_003",
            "name": "Test hint functionality",
            "status": "failed",
            "duration": 12,
            "category": "functionality",
            "errors": ["Hint button not found in DOM"]
        }
    ]
    
    print("\n📊 Storing test results in RAG...")
    for result in simulated_results:
        result_id = rag.store_test_result(result["test_id"], result, GAME_URL)
        status_icon = "✓" if result["status"] == "passed" else "✗"
        print(f"  {status_icon} {result['test_id']}: {result['status']} ({result['duration']}s)")
    
    print("\n" + "-" * 70)
    print("STEP 5: Store Human Feedback")
    print("-" * 70)
    
    feedback_examples = [
        {
            "test_id": "sumlink_003",
            "feedback": "Hint button actually exists but uses a lightbulb icon without text. Update selector to find it by icon class.",
            "context": {"category": "selector_issue", "game_url": GAME_URL}
        },
        {
            "test_id": "sumlink_001",
            "feedback": "Test is accurate. Number tiles are correctly identified and clickable.",
            "context": {"category": "validation", "game_url": GAME_URL}
        }
    ]
    
    print("\n💬 Storing human feedback...")
    for fb in feedback_examples:
        feedback_id = rag.store_feedback(fb["test_id"], fb["feedback"], fb["context"])
        print(f"  ✓ {fb['test_id']}: \"{fb['feedback'][:50]}...\"")
    
    print("\n" + "-" * 70)
    print("STEP 6: Query RAG Knowledge Base")
    print("-" * 70)
    
    print("\n🔍 Querying similar games...")
    similar_games = rag.query_similar_games(GAME_URL, top_k=3)
    if similar_games:
        print(f"  Found {len(similar_games)} similar game(s)")
        for game in similar_games:
            print(f"  • {game['game_url']} - {game['game_type']}")
    else:
        print("  No similar games found yet (first run)")
    
    print("\n🔍 Querying test history...")
    test_history = rag.query_test_history(GAME_URL, top_k=5)
    print(f"  Found {len(test_history)} relevant test result(s)")
    for test in test_history:
        print(f"  • {test['test_id']}: {test['status']}")
    
    print("\n🔍 Querying feedback...")
    feedback_results = rag.query_feedback("hint button selector", top_k=2)
    print(f"  Found {len(feedback_results)} relevant feedback(s)")
    for fb in feedback_results:
        print(f"  • {fb['test_id']}: \"{fb['feedback'][:60]}...\"")
    
    print("\n" + "-" * 70)
    print("STEP 7: Get Learning Insights")
    print("-" * 70)
    
    insights = rag.get_learning_insights(GAME_URL)
    
    print(f"\n📈 Learning Statistics:")
    print(f"  • Total Tests: {insights['total_tests']}")
    print(f"  • Successful: {insights['successful_tests']}")
    print(f"  • Failed: {insights['failed_tests']}")
    print(f"  • Feedback Count: {insights['feedback_count']}")
    print(f"  • Knowledge Entries: {insights['game_knowledge_entries']}")
    
    if insights['recent_tests']:
        print(f"\n  📋 Recent Test Results:")
        for test in insights['recent_tests'][:3]:
            print(f"    • {test['test_id']}: {test['status']} ({test.get('duration', 0)}s)")
    
    print("\n" + "=" * 70)
    print("SUMMARY: RAG Learning System Capabilities")
    print("=" * 70)
    
    print("\n" + "=" * 70)
    print("Test completed! RAG knowledge persisted to ./knowledge_base/")
    print("Run this script again to see the system retrieve past knowledge.")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_rag_learning())
