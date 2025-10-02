import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.agents.game_analyzer import GameAnalyzerAgent
from backend.agents.planner import PlannerAgent

async def test_analyzer():
    print("=" * 60)
    print("Testing Game Analyzer Agent")
    print("=" * 60)
    
    analyzer = GameAnalyzerAgent()
    game_url = "https://play.ezygamers.com/"
    
    print(f"\nAnalyzing game: {game_url}")
    analysis = await analyzer.analyze_game(game_url)
    
    print("\n--- Game Analysis Results ---")
    print(f"Game Type: {analysis.get('game_type', 'unknown')}")
    print(f"Interaction Model: {analysis.get('interaction_model', 'unknown')}")
    print(f"Features: {', '.join(analysis.get('features', []))}")
    print(f"Mechanics: {analysis.get('mechanics', {})}")
    print(f"UI Elements Found: {len(analysis.get('ui_elements', []))}")
    
    if 'error' in analysis:
        print(f"\nError: {analysis['error']}")
    
    print("\n" + "=" * 60)
    print("Testing Test Planner Agent")
    print("=" * 60)
    
    planner = PlannerAgent()
    print(f"\nGenerating test cases for: {game_url}")
    test_cases = await planner.generate_test_cases(game_url)
    
    print(f"\n--- Generated {len(test_cases)} Test Cases ---")
    for i, tc in enumerate(test_cases[:5], 1):
        print(f"\n{i}. {tc['name']}")
        print(f"   ID: {tc['id']}")
        print(f"   Category: {tc['category']}")
        print(f"   Priority: {tc['priority']}")
        print(f"   Steps: {len(tc['steps'])} steps")
        print(f"   Duration: {tc['estimated_duration']}s")
    
    if len(test_cases) > 5:
        print(f"\n... and {len(test_cases) - 5} more test cases")
    
    sumlink_tests = [tc for tc in test_cases if 'sumlink' in tc['id']]
    if sumlink_tests:
        print(f"\n✓ {len(sumlink_tests)} SumLink-specific tests generated!")
    
    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_analyzer())
