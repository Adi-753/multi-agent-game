from typing import List, Dict, Any
import json
from .base import BaseAgent
import os
from dotenv import load_dotenv
from .game_analyzer import GameAnalyzerAgent
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    from rag_simple import SimpleRAGKnowledgeBase
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("Warning: RAG not available, system will work without learning")

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
    
    def __init__(self, rag_enabled: bool = True):
        super().__init__("PlannerAgent")
        self.game_analyzer = GameAnalyzerAgent()
        self.game_analysis = None
        
        self.rag = None
        if rag_enabled and RAG_AVAILABLE:
            try:
                self.rag = SimpleRAGKnowledgeBase()
                self.log("RAG Knowledge Base initialized successfully")
            except Exception as e:
                self.log(f"Failed to initialize RAG: {e}", "warning")
                self.rag = None
        
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
You are a test planner for web games. Based on the game analysis below, generate 15-20 test cases in JSON format.

Game URL: {game_url}
Game Type: {game_type}
Interaction Model: {interaction_model}
Game Mechanics: {mechanics}
Features: {features}

For SumLink or number matching puzzle games:
- Focus on clicking number tiles to reach target sums
- Test stage progression and difficulty increases
- Test hint system and UI controls
- Test score tracking and best score persistence
- Test settings (sound, language)

Return ONLY a JSON array of test case objects with fields: id, name, category, steps (array), expected_outcome, priority, estimated_duration.
"""
        
    async def execute(self, *args, **kwargs):
        return await self.generate_test_cases(*args, **kwargs)
    
    async def generate_test_cases(self, game_url: str) -> List[Dict]:
        self.log("Generating test cases...")
        
        if self.rag:
            similar_games = self.rag.query_similar_games(game_url, top_k=2)
            if similar_games:
                self.log(f"Found {len(similar_games)} similar games in knowledge base")
            
            past_tests = self.rag.query_test_history(game_url, top_k=5)
            if past_tests:
                self.log(f"Retrieved {len(past_tests)} past test results")
        
        try:
            self.game_analysis = await self.game_analyzer.analyze_game(game_url)
            self.log(f"Game analyzed: {self.game_analysis.get('game_type', 'unknown')}")
            
            if self.rag:
                self.rag.store_game_analysis(game_url, self.game_analysis)
                self.log("Game analysis stored in RAG knowledge base")
        except Exception as e:
            self.log(f"Game analysis failed: {e}", "warning")
            self.game_analysis = {"game_type": "unknown", "interaction_model": "unknown"}
        
        if self.game_analysis.get('game_type') == 'number_matching_puzzle':
            return self._create_sumlink_test_cases()
        
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
        
        prompt = self.prompt_template.format(
            game_url=game_url,
            game_type=self.game_analysis.get('game_type', 'unknown'),
            interaction_model=self.game_analysis.get('interaction_model', 'unknown'),
            mechanics=json.dumps(self.game_analysis.get('mechanics', {})),
            features=', '.join(self.game_analysis.get('features', []))
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
    
    def _create_sumlink_test_cases(self) -> List[Dict]:
        self.log("Generating 20 SumLink-specific test cases based on actual game analysis")
        # These are REAL tests for the SumLink number matching puzzle game
        # Based on actual game mechanics: click tiles to reach target sum
        return [
            {
                "id": "sumlink_001",
                "name": "Verify basic number tile clicking",
                "category": "functionality",
                "steps": [
                    "Navigate to https://play.ezygamers.com/",
                    "Wait for game to load completely",
                    "Click 'Start' or 'Play' button if present",
                    "Observe the target sum displayed",
                    "Click on number tiles that add up to the target",
                    "Verify tiles are selected/highlighted",
                    "Confirm the sum is accepted automatically or via button"
                ],
                "expected_outcome": "Selected numbers highlight correctly, sum is validated, stage progresses on success",
                "priority": "High",
                "estimated_duration": 20
            },
            {
                "id": "sumlink_002",
                "name": "Test stage progression",
                "category": "functionality",
                "steps": [
                    "Complete stage 1 successfully",
                    "Verify stage counter increments",
                    "Check that stage 2 loads with new numbers",
                    "Observe if difficulty increases",
                    "Complete multiple stages"
                ],
                "expected_outcome": "Stages progress smoothly, difficulty increases, stage number updates",
                "priority": "High",
                "estimated_duration": 45
            },
            {
                "id": "sumlink_003",
                "name": "Test hint functionality",
                "category": "functionality",
                "steps": [
                    "Start a game",
                    "Look for hint button (lightbulb or 'Hint' text)",
                    "Click the hint button",
                    "Observe if numbers are highlighted or suggested",
                    "Verify hint is helpful and correct"
                ],
                "expected_outcome": "Hint button reveals valid combination, assists player correctly",
                "priority": "Medium",
                "estimated_duration": 15
            },
            {
                "id": "sumlink_004",
                "name": "Verify score tracking",
                "category": "functionality",
                "steps": [
                    "Note initial score (usually 0)",
                    "Complete one stage",
                    "Check score increases",
                    "Complete another stage",
                    "Verify score accumulates correctly"
                ],
                "expected_outcome": "Score displayed prominently, increases with each completed stage",
                "priority": "High",
                "estimated_duration": 20
            },
            {
                "id": "sumlink_005",
                "name": "Test wrong combination handling",
                "category": "error_handling",
                "steps": [
                    "Start a stage with target sum",
                    "Click numbers that don't add up to target",
                    "Try to confirm the wrong selection",
                    "Observe error feedback (shake, color change, message)",
                    "Verify tiles deselect or remain editable"
                ],
                "expected_outcome": "Wrong combinations rejected with clear visual feedback, no progression",
                "priority": "High",
                "estimated_duration": 15
            },
            {
                "id": "sumlink_006",
                "name": "Test deselecting tiles",
                "category": "functionality",
                "steps": [
                    "Click a number tile to select it",
                    "Click the same tile again",
                    "Verify it deselects/unhighlights",
                    "Select multiple tiles",
                    "Deselect each individually"
                ],
                "expected_outcome": "Tiles can be toggled on/off, selection state updates correctly",
                "priority": "High",
                "estimated_duration": 10
            },
            {
                "id": "sumlink_007",
                "name": "Test settings button",
                "category": "ui_ux",
                "steps": [
                    "Locate settings icon or button",
                    "Click settings",
                    "Verify settings modal opens",
                    "Check available options (sound, language, etc.)",
                    "Close settings and resume game"
                ],
                "expected_outcome": "Settings accessible, modal displays options, game resumes after closing",
                "priority": "Medium",
                "estimated_duration": 15
            },
            {
                "id": "sumlink_008",
                "name": "Test sound toggle",
                "category": "functionality",
                "steps": [
                    "Open settings or find sound icon",
                    "Toggle sound off",
                    "Complete a stage and verify no sound",
                    "Toggle sound on",
                    "Complete another stage and listen for sound"
                ],
                "expected_outcome": "Sound can be muted and unmuted, preference persists during session",
                "priority": "Low",
                "estimated_duration": 20
            },
            {
                "id": "sumlink_009",
                "name": "Test language selection",
                "category": "functionality",
                "steps": [
                    "Open settings",
                    "Find language option",
                    "Switch to a different language",
                    "Check UI text updates",
                    "Switch back to English"
                ],
                "expected_outcome": "Language changes apply to UI text, game remains playable",
                "priority": "Low",
                "estimated_duration": 15
            },
            {
                "id": "sumlink_010",
                "name": "Test best score persistence",
                "category": "functionality",
                "steps": [
                    "Complete several stages to get a score",
                    "Note the best score displayed",
                    "Refresh the page",
                    "Check if best score is retained",
                    "Play again and try to beat it"
                ],
                "expected_outcome": "Best score saved in browser storage, persists across sessions",
                "priority": "Medium",
                "estimated_duration": 30
            },
            {
                "id": "sumlink_011",
                "name": "Test mobile responsiveness",
                "category": "ui_ux",
                "steps": [
                    "Resize browser to mobile width (375px)",
                    "Check game board fits on screen",
                    "Test clicking tiles with touch simulation",
                    "Verify buttons are large enough",
                    "Complete a stage on mobile viewport"
                ],
                "expected_outcome": "Game fully playable on mobile, tiles and buttons appropriately sized",
                "priority": "High",
                "estimated_duration": 20
            },
            {
                "id": "sumlink_012",
                "name": "Test multiple valid combinations",
                "category": "edge_case",
                "steps": [
                    "Find a stage with multiple ways to reach target sum",
                    "Complete with first valid combination",
                    "Replay same stage if possible",
                    "Use different valid combination",
                    "Verify both are accepted"
                ],
                "expected_outcome": "Any valid combination reaching target sum is accepted",
                "priority": "Medium",
                "estimated_duration": 25
            },
            {
                "id": "sumlink_013",
                "name": "Test rapid clicking",
                "category": "edge_case",
                "steps": [
                    "Click tiles very rapidly",
                    "Try to click same tile multiple times quickly",
                    "Monitor for selection glitches",
                    "Verify selection state remains consistent"
                ],
                "expected_outcome": "No duplicate selections, state remains consistent with rapid inputs",
                "priority": "Low",
                "estimated_duration": 10
            },
            {
                "id": "sumlink_014",
                "name": "Test game restart",
                "category": "functionality",
                "steps": [
                    "Play several stages",
                    "Find restart or new game button",
                    "Click restart",
                    "Verify game resets to stage 1",
                    "Check score resets to 0"
                ],
                "expected_outcome": "Game restarts cleanly, all progress reset except best score",
                "priority": "Medium",
                "estimated_duration": 15
            },
            {
                "id": "sumlink_015",
                "name": "Test page load performance",
                "category": "performance",
                "steps": [
                    "Clear browser cache",
                    "Navigate to game URL",
                    "Measure time until game is interactive",
                    "Check for loading indicators"
                ],
                "expected_outcome": "Game loads within 3 seconds, shows loading state if needed",
                "priority": "Medium",
                "estimated_duration": 10
            },
            {
                "id": "sumlink_016",
                "name": "Test extended play session",
                "category": "performance",
                "steps": [
                    "Play continuously for 20+ stages",
                    "Monitor browser memory usage",
                    "Check for slowdowns or lag",
                    "Verify consistent responsiveness"
                ],
                "expected_outcome": "No memory leaks, performance remains stable over extended play",
                "priority": "Low",
                "estimated_duration": 180
            },
            {
                "id": "sumlink_017",
                "name": "Test browser back button behavior",
                "category": "edge_case",
                "steps": [
                    "Start playing the game",
                    "Click browser back button",
                    "Observe behavior",
                    "Use forward button if applicable"
                ],
                "expected_outcome": "Game handles navigation gracefully, either prevents back or saves state",
                "priority": "Low",
                "estimated_duration": 10
            },
            {
                "id": "sumlink_018",
                "name": "Test keyboard navigation",
                "category": "ui_ux",
                "steps": [
                    "Try using Tab to navigate elements",
                    "Try using Enter to confirm selections",
                    "Test Escape key for canceling",
                    "Check if number keys select tiles"
                ],
                "expected_outcome": "Basic keyboard support for accessibility, tab navigation works",
                "priority": "Low",
                "estimated_duration": 15
            },
            {
                "id": "sumlink_019",
                "name": "Verify game is actually playable",
                "category": "critical_functionality",
                "steps": [
                    "Navigate to play.ezygamers.com",
                    "Click Start/Continue button",
                    "Verify game board loads with number tiles",
                    "Check target sum is displayed (e.g., +5, +10)",
                    "Click tiles that add to target",
                    "Verify game accepts correct sum and progresses"
                ],
                "expected_outcome": "Game is fully playable, core mechanics work correctly",
                "priority": "Critical",
                "estimated_duration": 25
            },
            {
                "id": "sumlink_020",
                "name": "Test sum validation accuracy",
                "category": "critical_functionality",
                "steps": [
                    "Start a stage with target sum (e.g., +10)",
                    "Select tiles: 3 + 7 = 10 (correct)",
                    "Verify acceptance",
                    "Next stage: Select 5 + 2 = 7 for target +8 (incorrect)",
                    "Verify rejection",
                    "Select 4 + 4 = 8 (correct)",
                    "Verify acceptance and scoring"
                ],
                "expected_outcome": "Game correctly validates sums, accepts only correct combinations",
                "priority": "Critical",
                "estimated_duration": 30
            }
        ]
