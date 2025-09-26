# 🎮 Multi-Agent Game Tester POC

An intelligent automated testing framework for web-based puzzle games using multi-agent architecture powered by LangChain and Playwright.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![Playwright](https://img.shields.io/badge/Playwright-1.40.0-red.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.1.16-orange.svg)

## 📌 Overview

This Proof of Concept (POC) demonstrates a sophisticated multi-agent testing system designed for automated testing of web-based puzzle games. The system currently targets the EzyGamers Number Puzzle game but can be easily configured for other games.

### 🎯 Key Features

- **🤖 AI-Powered Test Generation**: Creates 20+ comprehensive test cases using LangChain
- **📊 Intelligent Test Ranking**: Prioritizes tests based on importance and coverage
- **🚀 Parallel Multi-Agent Execution**: Multiple agents work simultaneously for faster testing
- **📸 Comprehensive Artifact Collection**: Screenshots, DOM snapshots, console logs, network traces
- **✅ Cross-Agent Validation**: Ensures reliability through consensus-based validation
- **📋 Detailed Reporting**: JSON reports with verdicts, evidence, and reproducibility metrics

## 🏗️ System Architecture

```
┌─────────────────┐
│     Web UI      │
└────────┬────────┘
         │
┌────────▼────────┐
│ FastAPI Backend │
└────────┬────────┘
         │
┌────────▼────────┐
│  PlannerAgent   │──► Generates 20+ test cases
└────────┬────────┘
         │
┌────────▼────────┐
│  RankerAgent    │──► Ranks and selects top 10
└────────┬────────┘
         │
┌────────▼────────┐
│OrchestratorAgent│──► Coordinates parallel execution
└────────┬────────┘
         │
    ┌────┴────┬──────────┐
    │         │          │
┌───▼──┐ ┌───▼──┐ ┌─────▼────┐
│Exec 1│ │Exec 2│ │  Exec 3  │──► Run tests with Playwright
└───┬──┘ └───┬──┘ └─────┬────┘
    │         │          │
    └────┬────┴──────────┘
         │
┌────────▼────────┐
│ AnalyzerAgent   │──► Validates results
└────────┬────────┘
         │
┌────────▼────────┐
│Report Generator │──► Creates JSON reports
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (optional, for enhanced AI features)

### Installation & Running

1. **Clone the repository**
```bash
git clone <repository-url>
cd game-tester-poc
```

2. **Run the application**

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

3. **Access the UI**
Open your browser and navigate to: `http://localhost:8000`

## 📖 Usage Guide

### Step 1: Generate Test Plan
Click **"Generate Test Plan (20+ tests)"** to create test cases:
- 5 Functionality tests
- 5 Edge case tests  
- 4 Error handling tests
- 3 UI/UX tests
- 3 Performance tests

### Step 2: Execute Tests
Click **"Execute Top 10 Tests"** to run the highest-priority tests:
- Parallel execution with 3 agents
- Real-time progress monitoring
- Automatic artifact collection

### Step 3: View Results
- Check pass/fail statistics
- Access detailed reports
- Download captured artifacts

## 🧪 Test Categories

| Category | Count | Description |
|----------|-------|-------------|
| **Functionality** | 5 | Core game mechanics |
| **Edge Cases** | 5 | Boundary conditions |
| **Error Handling** | 4 | Invalid inputs |
| **UI/UX** | 3 | Interface interactions |
| **Performance** | 3 | Speed and responsiveness |

## 🛠️ Configuration

### Environment Variables

Create `backend/.env`:
```env
# Optional: For AI-powered test generation
OPENAI_API_KEY=sk-your-api-key-here

# Optional: Configure game URL
GAME_URL=https://your-game.com/

# Server configuration
PORT=8000
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/generate-plan` | Generate 20+ test cases |
| `GET` | `/api/current-plan` | Get current test plan |
| `POST` | `/api/execute-tests` | Execute top 10 tests |
| `GET` | `/api/execution-status` | Check progress |
| `GET` | `/api/reports` | List all reports |


## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port already in use | Change port in `backend/main.py` |
| Browser not found | Run `playwright install chromium` |
| Module errors | Run `pip install -r backend/requirements.txt` |
| Wrong game tested | Check URLs in 3 locations mentioned above |

## ✅ Verification

Run verification script:
```bash
python test_app.py
```

## 🙏 Acknowledgments

Built with:
- FastAPI for backend API
- LangChain for AI integration  
- Playwright for browser automation
- Love for automated testing ❤️

---

## 🎯 Quick Reference

```bash
# Start application:
Windows: start.bat
Linux/Mac: ./start.sh

# Manual start:
cd backend && python main.py
```

---

*Built for automated game testing - easily adaptable to any web-based puzzle game!*