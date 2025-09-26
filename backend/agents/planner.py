from typing import List, Dict
import json
from .base import BaseAgent
import os
from dotenv import load_dotenv

try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from langchain.schema import HumanMessage
except ImportError:
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from langchain.schema import HumanMessage

load_dotenv()

class PlannerAgent(BaseAgent):
    
    def __init__(self):
        super().__init__("PlannerAgent")
        
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key and api_key != "OPENAI_API_KEY":
            self.llm = ChatOpenAI(
                temperature=0.7,
                model="gpt-3.5-turbo",
                openai_api_key=api_key
            )
            self.use_llm = True
        else:
            self.llm = None
            self.use_llm = False
            self.log("No valid OpenAI API key found, will use predefined test cases", "warning")
        
        self.prompt_template =  """
                                    Game URL: {game_url}
                                    Game Type: {game_description}
                                """
        
    async def execute(self, *args, **kwargs):
        return await self.generate_test_cases(*args, **kwargs)
    
    async def generate_test_cases(self, game_url: str) -> List[Dict]:
        self.log("Generating test cases...")
        
        if self.use_llm:
            try:
                return await self._generate_with_langchain(game_url)
            except Exception as e:
                self.log(f"LangChain generation failed: {e}, using predefined tests", "warning")
                return self._create_comprehensive_test_cases()
        else:
            return self._create_comprehensive_test_cases()
    
    async def _generate_with_langchain(self, game_url: str) -> List[Dict]:
        self.log("Using LangChain to generate test cases...")
        
        game_description = """Number/Math Puzzle Game with:
- Arithmetic operations (addition, subtraction, multiplication, division)
- Progressive difficulty levels
- Timer-based challenges
- Score tracking system
- Hint functionality"""
        
        prompt = self.prompt_template.format(
            game_url=game_url,
            game_description=game_description
        )
        
        message = HumanMessage(content=prompt)
        response = await self.llm.agenerate([[message]])
        
        content = response.generations[0][0].text
        
        try:
            import re
            json_match = re.search(r'$$.*$$', content, re.DOTALL)
            if json_match:
                test_cases = json.loads(json_match.group())
                self.log(f"Successfully generated {len(test_cases)} test cases with LangChain")
                
                if len(test_cases) < 20:
                    predefined = self._create_comprehensive_test_cases()
                    test_cases.extend(predefined[len(test_cases):20])
                elif len(test_cases) > 20:
                    test_cases = test_cases[:20]
                
                return test_cases
            else:
                raise ValueError("Could not find JSON array in response")
                
        except Exception as e:
            self.log(f"Failed to parse LangChain response: {e}", "error")
            return self._create_comprehensive_test_cases()
    
    def _create_comprehensive_test_cases(self) -> List[Dict]:
        self.log("Using predefined test cases")
        return [
            {
                "id": "test_001",
                "name": "Verify basic addition puzzle solving",
                "category": "functionality",
                "steps": [
                    "Navigate to https://play.ezygamers.com/",
                    "Wait for game to load completely",
                    "Click on 'Start Game' or 'Play' button",
                    "When presented with an addition puzzle (e.g., 5 + 3)",
                    "Enter the correct answer (8) in the input field",
                    "Click Submit or press Enter"
                ],
                "expected_outcome": "Answer is accepted, score increases by appropriate points, next puzzle loads automatically",
                "priority": "High",
                "estimated_duration": 15
            },
            {
                "id": "test_002",
                "name": "Test subtraction puzzle functionality",
                "category": "functionality",
                "steps": [
                    "Continue from previous test or start new game",
                    "Wait for a subtraction puzzle (e.g., 10 - 4)",
                    "Calculate and enter correct answer (6)",
                    "Submit the answer",
                    "Observe score and progression"
                ],
                "expected_outcome": "Subtraction answer processed correctly, score updates, game progresses",
                "priority": "High",
                "estimated_duration": 12
            },
            {
                "id": "test_003",
                "name": "Verify multiplication puzzle mechanics",
                "category": "functionality",
                "steps": [
                    "Progress through game to multiplication level",
                    "Identify multiplication puzzle (e.g., 7 × 8)",
                    "Calculate correct answer (56)",
                    "Enter answer in input field",
                    "Submit and check feedback"
                ],
                "expected_outcome": "Multiplication works correctly, proper feedback displayed",
                "priority": "High",
                "estimated_duration": 15
            },
            {
                "id": "test_004",
                "name": "Test division puzzle with decimals",
                "category": "functionality",
                "steps": [
                    "Navigate to division puzzle level",
                    "Solve division problem (e.g., 15 ÷ 4)",
                    "Enter decimal answer (3.75)",
                    "Submit answer",
                    "Check acceptance and scoring"
                ],
                "expected_outcome": "Division with decimals handled correctly",
                "priority": "High",
                "estimated_duration": 18
            },
            {
                "id": "test_005",
                "name": "Verify timer countdown functionality",
                "category": "functionality",
                "steps": [
                    "Start a new timed challenge",
                    "Observe timer display",
                    "Let timer count down without answering",
                    "Wait for timeout",
                    "Check game behavior on timeout"
                ],
                "expected_outcome": "Timer displays correctly and timeout is handled gracefully",
                "priority": "Medium",
                "estimated_duration": 30
            },
            # Edge Cases (5)
            {
                "id": "test_006",
                "name": "Handle negative number results",
                "category": "edge_case",
                "steps": [
                    "Find subtraction with negative result (e.g., 3 - 7)",
                    "Calculate answer (-4)",
                    "Enter negative sign and number",
                    "Submit answer",
                    "Verify acceptance"
                ],
                "expected_outcome": "Negative numbers handled correctly with proper validation",
                "priority": "High",
                "estimated_duration": 15
            },
            {
                "id": "test_007",
                "name": "Test maximum number limits",
                "category": "edge_case",
                "steps": [
                    "Test with very large numbers (>9999)",
                    "Enter large number answer",
                    "Check display formatting",
                    "Verify calculation accuracy",
                    "Submit and check processing"
                ],
                "expected_outcome": "Large numbers display and calculate correctly without overflow",
                "priority": "Medium",
                "estimated_duration": 20
            },
            {
                "id": "test_008",
                "name": "Verify zero handling in operations",
                "category": "edge_case",
                "steps": [
                    "Test multiplication by zero",
                    "Test addition with zero",
                    "Test subtraction resulting in zero",
                    "Verify each case",
                    "Check scoring for zero answers"
                ],
                "expected_outcome": "Zero handled correctly in all operations",
                "priority": "High",
                "estimated_duration": 10
            },
            {
                "id": "test_009",
                "name": "Test decimal precision boundaries",
                "category": "edge_case",
                "steps": [
                    "Find division with repeating decimal",
                    "Enter answer with many decimal places",
                    "Test different rounding approaches",
                    "Submit variations",
                    "Check acceptance criteria"
                ],
                                "expected_outcome": "Clear decimal precision rules applied consistently",
                "priority": "Medium",
                "estimated_duration": 15
            },
            {
                "id": "test_010",
                "name": "Rapid answer submission stress test",
                "category": "edge_case",
                "steps": [
                    "Solve puzzle correctly",
                    "Click submit multiple times rapidly",
                    "Enter new answer and submit quickly",
                    "Monitor for duplicate submissions",
                    "Check score consistency"
                ],
                "expected_outcome": "No duplicate scoring, system handles rapid inputs gracefully",
                "priority": "Medium",
                "estimated_duration": 20
            },
            # Error Handling (4)
            {
                "id": "test_011",
                "name": "Test alphabetic character input",
                "category": "error_handling",
                "steps": [
                    "Click on answer input field",
                    "Type letters instead of numbers",
                    "Attempt to submit",
                    "Check error message or validation"
                ],
                "expected_outcome": "Letters rejected with clear error message",
                "priority": "High",
                "estimated_duration": 10
            },
            {
                "id": "test_012",
                "name": "Test special characters input",
                "category": "error_handling",
                "steps": [
                    "Enter special characters (!@#$%^&*)",
                    "Try various symbol combinations",
                    "Attempt submission",
                    "Verify input handling"
                ],
                "expected_outcome": "Special characters handled appropriately with validation",
                "priority": "Medium",
                "estimated_duration": 12
            },
            {
                "id": "test_013",
                "name": "Test empty answer submission",
                "category": "error_handling",
                "steps": [
                    "Leave answer field completely empty",
                    "Click submit button",
                    "Check validation message",
                    "Verify form doesn't submit"
                ],
                "expected_outcome": "Empty submission prevented with appropriate message",
                "priority": "High",
                "estimated_duration": 8
            },
            {
                "id": "test_014",
                "name": "Test browser refresh recovery",
                "category": "error_handling",
                "steps": [
                    "Start a game session",
                    "Refresh the browser page",
                    "Check game state recovery",
                    "Verify score persistence"
                ],
                "expected_outcome": "Graceful recovery or clear restart after refresh",
                "priority": "Medium",
                "estimated_duration": 25
            },
            # UI/UX Tests (3)
            {
                "id": "test_015",
                "name": "Test all interactive elements",
                "category": "ui_ux",
                "steps": [
                    "Click all visible buttons",
                    "Check hover states on buttons",
                    "Verify click feedback animations",
                    "Test keyboard navigation",
                    "Check focus indicators"
                ],
                "expected_outcome": "All interactive elements responsive with proper visual feedback",
                "priority": "Medium",
                "estimated_duration": 15
            },
            {
                "id": "test_016",
                "name": "Test mobile viewport responsiveness",
                "category": "ui_ux",
                "steps": [
                    "Resize browser to mobile width (375px)",
                    "Check layout adaptation",
                    "Test touch interaction simulation",
                    "Verify text readability",
                    "Check button sizes for touch"
                ],
                "expected_outcome": "Game fully playable on mobile viewport with proper scaling",
                "priority": "Medium",
                "estimated_duration": 20
            },
            {
                "id": "test_017",
                "name": "Test keyboard accessibility",
                "category": "ui_ux",
                "steps": [
                    "Navigate using only Tab key",
                    "Submit answer with Enter key",
                    "Use Escape key for cancellation",
                    "Test screen reader compatibility"
                ],
                "expected_outcome": "Full keyboard navigation possible, accessibility standards met",
                "priority": "Low",
                "estimated_duration": 15
            },
            # Performance Tests (3)
            {
                "id": "test_018",
                "name": "Test initial page load performance",
                "category": "performance",
                "steps": [
                    "Clear browser cache",
                    "Navigate to game URL",
                    "Measure time to interactive",
                    "Check resource loading"
                ],
                "expected_outcome": "Game loads and becomes interactive within 3 seconds",
                "priority": "High",
                "estimated_duration": 10
            },
            {
                "id": "test_019",
                "name": "Test puzzle generation speed",
                "category": "performance",
                "steps": [
                    "Complete 10 puzzles in succession",
                    "Measure time between submissions",
                    "Monitor for increasing delays",
                    "Check for UI lag"
                ],
                "expected_outcome": "Consistent puzzle generation time, no performance degradation",
                "priority": "Medium",
                "estimated_duration": 30
            },
            {
                "id": "test_020",
                "name": "Test extended play session stability",
                "category": "performance",
                "steps": [
                    "Play continuously for 5 minutes",
                    "Monitor browser memory usage",
                    "Check for memory leaks",
                    "Verify consistent performance"
                ],
                "expected_outcome": "No significant memory increase or performance degradation",
                "priority": "Low",
                "estimated_duration": 300
            }
        ]