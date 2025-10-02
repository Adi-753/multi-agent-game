from typing import Dict, List, Any
from .base import BaseAgent
from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup

class GameAnalyzerAgent(BaseAgent):
    
    def __init__(self):
        super().__init__("GameAnalyzerAgent")
        
    async def execute(self, *args, **kwargs):
        return await self.analyze_game(*args, **kwargs)
    
    async def analyze_game(self, game_url: str) -> Dict[str, Any]:
        self.log(f"Analyzing game at {game_url}")
        
        analysis = {
            "game_url": game_url,
            "game_type": "unknown",
            "ui_elements": [],
            "mechanics": {},
            "features": [],
            "interaction_model": "unknown"
        }
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(game_url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(3)
                
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                buttons = soup.find_all(['button', 'div'], class_=lambda x: x and ('btn' in str(x).lower() or 'button' in str(x).lower()))
                analysis["ui_elements"].extend([{
                    "type": "button",
                    "text": btn.get_text(strip=True) or btn.get('aria-label', 'Unknown'),
                    "id": btn.get('id'),
                    "class": btn.get('class')
                } for btn in buttons[:20]])
                
                inputs = soup.find_all('input')
                analysis["ui_elements"].extend([{
                    "type": "input",
                    "input_type": inp.get('type', 'text'),
                    "id": inp.get('id'),
                    "placeholder": inp.get('placeholder')
                } for inp in inputs[:10]])
                
                game_containers = soup.find_all(['div', 'canvas'], class_=lambda x: x and ('game' in str(x).lower() or 'board' in str(x).lower() or 'grid' in str(x).lower()))
                if game_containers:
                    analysis["ui_elements"].append({
                        "type": "game_container",
                        "count": len(game_containers),
                        "classes": [str(gc.get('class')) for gc in game_containers[:5]]
                    })
                
                page_text = soup.get_text().lower()
                
                if 'sumlink' in page_text or 'add numbers' in page_text:
                    analysis["game_type"] = "number_matching_puzzle"
                    analysis["mechanics"] = {
                        "primary": "click_to_select_numbers",
                        "objective": "sum_numbers_to_target",
                        "progression": "stage_based"
                    }
                    analysis["interaction_model"] = "click_based"
                    
                    if 'hint' in page_text:
                        analysis["features"].append("hint_system")
                    if 'stage' in page_text:
                        analysis["features"].append("stage_progression")
                    if 'score' in page_text:
                        analysis["features"].append("score_tracking")
                    if 'language' in page_text or 'english' in page_text:
                        analysis["features"].append("multi_language")
                    if 'sound' in page_text:
                        analysis["features"].append("sound_settings")
                    if 'best' in page_text:
                        analysis["features"].append("high_score")
                    
                elif any(word in page_text for word in ['calculate', 'equation', 'arithmetic']):
                    analysis["game_type"] = "arithmetic_puzzle"
                    analysis["mechanics"] = {
                        "primary": "input_answers",
                        "objective": "solve_equations"
                    }
                    analysis["interaction_model"] = "input_based"
                
                else:
                    if inputs:
                        analysis["interaction_model"] = "input_based"
                    elif buttons or game_containers:
                        analysis["interaction_model"] = "click_based"
                
                clickable_elements = await page.query_selector_all('[onclick], button, [role="button"], .clickable')
                analysis["mechanics"]["clickable_elements_count"] = len(clickable_elements)
                
                self.log(f"Game analysis complete: {analysis['game_type']}")
                
            except Exception as e:
                self.log(f"Error analyzing game: {str(e)}", "error")
                analysis["error"] = str(e)
            
            finally:
                await browser.close()
        
        return analysis
    
    async def get_game_specific_selectors(self, game_url: str) -> Dict[str, str]:
        self.log(f"Extracting selectors from {game_url}")
        
        selectors = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(game_url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)
                
                selectors_to_find = {
                    "start_button": ["button:has-text('Start')", "button:has-text('Play')", "button:has-text('New Game')", ".start-btn"],
                    "hint_button": ["button:has-text('Hint')", "[aria-label*='hint']", ".hint-btn"],
                    "pause_button": ["button:has-text('Pause')", "[aria-label*='pause']", ".pause-btn"],
                    "settings_button": ["button:has-text('Settings')", "[aria-label*='settings']", ".settings-btn"],
                    "game_board": [".game-board", ".board", "#game-container", "canvas"],
                    "score_display": [".score", "#score", "[class*='score']"],
                    "number_tiles": [".tile", ".number", "[class*='tile']", "[class*='number']"]
                }
                
                for selector_name, candidates in selectors_to_find.items():
                    for candidate in candidates:
                        try:
                            element = await page.query_selector(candidate)
                            if element:
                                is_visible = await element.is_visible()
                                if is_visible:
                                    selectors[selector_name] = candidate
                                    self.log(f"Found selector for {selector_name}: {candidate}")
                                    break
                        except:
                            continue
                
            except Exception as e:
                self.log(f"Error extracting selectors: {str(e)}", "error")
            
            finally:
                await browser.close()
        
        return selectors
