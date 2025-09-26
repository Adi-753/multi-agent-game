from typing import Dict, List, Any
from .base import BaseAgent
from playwright.async_api import async_playwright, Page
import asyncio
import base64
import json
from datetime import datetime
import os

class ExecutorAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(f"ExecutorAgent_{agent_id}")
        self.agent_id = agent_id
        
    async def execute(self, *args, **kwargs):
        return await self.execute_test(*args, **kwargs)
    
    async def execute_test(self, test_case: Dict, game_url: str) -> Dict:
        self.log(f"Executing test: {test_case['name']}")
        
        artifacts = {
            "screenshots": [],
            "dom_snapshots": [],
            "console_logs": [],
            "network_logs": [],
            "timestamps": []
        }
        
        result = {
            "test_id": test_case["id"],
            "test_name": test_case["name"],
            "agent_id": self.agent_id,
            "start_time": datetime.now().isoformat(),
            "artifacts": artifacts,
            "steps_completed": [],
            "error": None,
            "success": False
        }
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            page.on("console", lambda msg: artifacts["console_logs"].append({
                "type": msg.type,
                "text": msg.text,
                "timestamp": datetime.now().isoformat()
            }))
            
            page.on("request", lambda req: artifacts["network_logs"].append({
                "type": "request",
                "url": req.url,
                "method": req.method,
                "timestamp": datetime.now().isoformat()
            }))
            
            page.on("response", lambda res: artifacts["network_logs"].append({
                "type": "response",
                "url": res.url,
                "status": res.status,
                "timestamp": datetime.now().isoformat()
            }))
            
            try:
                await page.goto(game_url, wait_until="networkidle")
                await asyncio.sleep(2)  
                
                for idx, step in enumerate(test_case.get("steps", [])):
                    self.log(f"Executing step {idx + 1}: {step}")
                    
                    screenshot_path = await self._capture_screenshot(page, test_case["id"], idx)
                    artifacts["screenshots"].append(screenshot_path)
                    
                    dom_snapshot = await self._capture_dom(page)
                    artifacts["dom_snapshots"].append(dom_snapshot)
                    
                    await self._execute_step(page, step)
                    
                    result["steps_completed"].append({
                        "step_index": idx,
                        "step_description": step,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    artifacts["timestamps"].append(datetime.now().isoformat())
                    
                    await asyncio.sleep(1)
                
                final_screenshot = await self._capture_screenshot(page, test_case["id"], "final")
                artifacts["screenshots"].append(final_screenshot)
                
                result["success"] = True
                result["end_time"] = datetime.now().isoformat()
                
            except Exception as e:
                self.log(f"Error during test execution: {str(e)}", "error")
                result["error"] = str(e)
                result["success"] = False
                
                try:
                    error_screenshot = await self._capture_screenshot(page, test_case["id"], "error")
                    artifacts["screenshots"].append(error_screenshot)
                except:
                    pass
                
            finally:
                await browser.close()
        
        return result
    
    async def _execute_step(self, page: Page, step: str) -> None:
        step_lower = step.lower()
        
        if "navigate" in step_lower or "go to" in step_lower:
            pass
        elif "click" in step_lower:
            if "start" in step_lower:
                try:
                    await page.click("button:has-text('Start')", timeout=5000)
                except:
                    await page.click("button:has-text('Play')", timeout=5000)
            elif "submit" in step_lower:
                await page.click("button[type='submit']", timeout=5000)
            else:
                await page.click(f"button:has-text('{self._extract_button_text(step)}')")
        elif "enter" in step_lower or "type" in step_lower or "input" in step_lower:
            value = self._extract_value(step)
            await page.fill("input[type='text']", value)
        elif "wait" in step_lower:
            wait_time = self._extract_wait_time(step)
            await asyncio.sleep(wait_time)
        elif "solve" in step_lower:
            await self._solve_puzzle(page, step)
        
    async def _capture_screenshot(self, page: Page, test_id: str, step_idx: Any) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_id}_{step_idx}_{timestamp}.png"
        filepath = os.path.join("artifacts", "screenshots", filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        await page.screenshot(path=filepath)
        
        return filepath
    
    async def _capture_dom(self, page: Page) -> Dict:
        dom_content = await page.content()
        return {
            "html": dom_content[:1000],
            "timestamp": datetime.now().isoformat(),
            "url": page.url
        }
    
    def _extract_button_text(self, step: str) -> str:
        if "start" in step.lower():
                        return "Start"
        elif "submit" in step.lower():
            return "Submit"
        return "Click"
    
    def _extract_value(self, step: str) -> str:
        import re
        numbers = re.findall(r'\d+', step)
        return numbers[0] if numbers else "10"
    
    def _extract_wait_time(self, step: str) -> int:
        import re
        numbers = re.findall(r'\d+', step)
        return int(numbers[0]) if numbers else 2
    
    async def _solve_puzzle(self, page: Page, step: str) -> None:
        try:
            if "addition" in step.lower() or "+" in step:
                puzzle_text = await page.inner_text("body")
                import re
                numbers = re.findall(r'\d+\s*\+\s*\d+', puzzle_text)
                if numbers:
                    parts = numbers[0].split('+')
                    answer = str(int(parts[0]) + int(parts[1]))
                    await page.fill("input[type='text']", answer)
            elif "subtraction" in step.lower() or "-" in step:
                pass
        except:
            await page.fill("input[type='text']", "42")