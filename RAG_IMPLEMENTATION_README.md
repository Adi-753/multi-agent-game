# RAG-Based Trainable Multi-Agent Game Tester

## 🚀 Overview

This is a **fully trainable, learning AI system** for automated game testing. Unlike simple automation scripts, this system:

- **Learns** from experience using RAG (Retrieval-Augmented Generation)
- **Adapts** test strategies based on game type detection
- **Remembers** past test results and patterns
- **Incorporates** human feedback to improve
- **Generates** game-specific test cases automatically

## ✨ Key Features

### 1. **RAG Knowledge Base**
- Persistent vector database for storing game knowledge
- Semantic search across game analyses, test results, and feedback
- No external dependencies (uses simple file-based storage)
- Sentence-Transformers for embeddings

### 2. **Game Analyzer Agent**
- Automatically inspects games using Playwright
- Detects game type (e.g., SumLink = number_matching_puzzle)
- Identifies UI elements, features, and interaction patterns
- Stores analysis for future reference

### 3. **Adaptive Test Planner**
- Generates game-specific test cases
- For SumLink: 18 click-based tests (not arithmetic input tests)
- Uses RAG to retrieve relevant past knowledge
- Improves over time with more data

### 4. **Learning & Feedback Loop**
- Stores all test execution results
- Captures human feedback on test accuracy
- Queries past experiences for similar games
- Provides learning insights and statistics

## 📦 Installation

### Prerequisites
- Python 3.10+
- pip

### Setup Steps

1. **Clone the repository** (if not already done)
   ```bash
   cd game-tester-poc
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   playwright install
   ```

5. **Configure environment variables**
   ```bash
   # Copy the example .env file
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   
   # Edit .env and add your OpenAI API key (optional)
   OPENAI_API_KEY=your_key_here
   GAME_URL=https://play.ezygamers.com/
   ```

## 🧪 Testing the System

### Quick RAG Demonstration

Run the comprehensive RAG test to see learning in action:

```bash
python test_rag_learning.py
```

This will:
1. Initialize the RAG knowledge base
2. Analyze the game and store knowledge
3. Generate SumLink-specific test cases
4. Simulate test execution and store results
5. Store human feedback
6. Query the knowledge base
7. Show learning insights

**Expected Output:**
```
============================================================
TESTING RAG-BASED LEARNING SYSTEM
============================================================

📌 Game URL: https://play.ezygamers.com/
🎯 Target: Demonstrate trainable, learning AI system

------------------------------------------------------------
STEP 1: Initialize RAG Knowledge Base
------------------------------------------------------------
Loading embedding model...
Embedding model loaded successfully
✓ RAG Knowledge Base initialized
  - Storage directory: ./knowledge_base
  - Using Sentence-Transformers for embeddings

... (continues with full demonstration)
```

### Run the Full Web Application

```bash
# Start the backend server
python backend/main.py

# Open browser to http://localhost:8000
```

The web UI provides:
- Test case generation
- Test execution
- Results viewing
- RAG insights dashboard (via API)

## 🔧 Configuration

### Game URL Configuration

All game URL references are centralized in `.env`:

```env
GAME_URL=https://play.ezygamers.com/
```

To test a different game:
1. Edit the `.env` file
2. Change `GAME_URL` to your target game
3. Restart the application

### RAG Configuration

```env
RAG_PERSIST_DIRECTORY=./knowledge_base
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 📊 RAG Knowledge Base Structure

```
knowledge_base/
├── game_knowledge.json     # Game analyses
├── test_history.json       # Test execution results
├── feedback.json           # Human feedback
└── embeddings.pkl          # Vector embeddings
```

### Data Schema

**Game Knowledge:**
```json
{
  "id": "game_0",
  "game_url": "https://play.ezygamers.com/",
  "game_type": "number_matching_puzzle",
  "features": ["hint_system", "stage_progression", "score_tracking"],
  "mechanics": {
    "primary": "click_to_select_numbers",
    "objective": "sum_numbers_to_target"
  },
  "timestamp": "2025-01-10T12:00:00"
}
```

**Test History:**
```json
{
  "id": "test_0",
  "test_id": "sumlink_001",
  "game_url": "https://play.ezygamers.com/",
  "status": "passed",
  "duration": 18,
  "timestamp": "2025-01-10T12:05:00"
}
```

**Feedback:**
```json
{
  "id": "feedback_0",
  "test_id": "sumlink_003",
  "feedback": "Hint button uses lightbulb icon, not text",
  "context": {"category": "selector_issue"},
  "timestamp": "2025-01-10T12:10:00"
}
```

## 🎯 How It Works

### 1. Game Analysis
```python
analyzer = GameAnalyzerAgent()
analysis = await analyzer.analyze_game(game_url)
# Detects: game_type, features, mechanics, UI elements
```

### 2. Knowledge Storage
```python
rag = SimpleRAGKnowledgeBase()
rag.store_game_analysis(game_url, analysis)
# Creates embeddings and stores in vector DB
```

### 3. Adaptive Test Generation
```python
planner = PlannerAgent(rag_enabled=True)
test_cases = await planner.generate_test_cases(game_url)
# Retrieves past knowledge
# Generates game-specific tests
```

### 4. Test Execution & Learning
```python
# Execute tests
result = await executor.execute_test(test_case)

# Store result
rag.store_test_result(test_id, result, game_url)

# Add human feedback
rag.store_feedback(test_id, "Needs better selector", context)
```

### 5. Knowledge Retrieval
```python
# Find similar games
similar = rag.query_similar_games(game_url)

# Get test history
history = rag.query_test_history(game_url)

# Search feedback
feedback = rag.query_feedback("selector issue")

# Get insights
insights = rag.get_learning_insights(game_url)
```

## 📈 API Endpoints

### RAG Insights
```
GET /api/rag/insights
```

Returns learning statistics:
```json
{
  "available": true,
  "game_url": "https://play.ezygamers.com/",
  "insights": {
    "total_tests": 10,
    "successful_tests": 8,
    "failed_tests": 2,
    "feedback_count": 3,
    "knowledge_entries": 1
  }
}
```

### Submit Feedback
```
POST /api/rag/feedback
```

Body:
```json
{
  "test_id": "sumlink_003",
  "feedback": "Test needs update...",
  "context": {"category": "improvement"}
}
```

### Get Configuration
```
GET /api/config
```

Returns current settings:
```json
{
  "game_url": "https://play.ezygamers.com/",
  "rag_available": true
}
```

## 🤖 Agent Architecture

```
┌─────────────────────┐
│   User Request      │
└──────────┬──────────┘
           │
┌──────────▼──────────────┐
│  Orchestrator Agent     │
│  (Coordinates flow)     │
└──────────┬──────────────┘
           │
    ┌──────┴──────────┐
    │                 │
┌───▼──────────┐  ┌──▼──────────────┐
│ Game         │  │ Test Planner    │
│ Analyzer     │◄─┤ (RAG-enhanced)  │
│              │  │                 │
└───┬──────────┘  └──┬──────────────┘
    │                │
    │          ┌─────▼─────────┐
    │          │ Test Executor │
    │          │ (Playwright)  │
    │          └─────┬─────────┘
    │                │
    │          ┌─────▼─────────┐
    │          │ Test Analyzer │
    │          │ (Results)     │
    │          └─────┬─────────┘
    │                │
    └────────────────▼──────────┐
              ┌──────────────────┤
              │ RAG Knowledge    │
              │ Base (Learning)  │
              └──────────────────┘
```

## 🆚 Before vs After

| Feature | Before | After (with RAG) |
|---------|--------|------------------|
| Test Cases | Static, hardcoded | Dynamic, game-aware |
| Learning | None | Persistent across sessions |
| Adaptability | Manual updates | Self-adapting |
| Game Understanding | None | Automatic analysis |
| Feedback | Ignored | Stored & retrieved |
| Similar Games | Can't detect | Semantic search finds them |
| Improvement | Requires code changes | Learns from data |

## 💡 Example: SumLink vs Generic Tests

### Before (Generic - Wrong for SumLink):
```json
{
  "id": "test_001",
  "name": "Verify basic addition puzzle solving",
  "steps": [
    "Enter the correct answer (8) in the input field",
    "Click Submit or press Enter"
  ]
}
```
❌ SumLink is click-based, not input-based!

### After (SumLink-Specific - Correct):
```json
{
  "id": "sumlink_001",
  "name": "Verify basic number tile clicking",
  "steps": [
    "Observe the target sum displayed",
    "Click on number tiles that add up to the target",
    "Verify tiles are selected/highlighted",
    "Confirm the sum is accepted"
  ]
}
```
✅ Matches actual game mechanics!

## 🔄 Continuous Improvement Workflow

1. **First Run**: System analyzes game, generates initial tests
2. **Test Execution**: Results stored in RAG
3. **Human Feedback**: Corrections/improvements added
4. **Next Run**: System retrieves past knowledge
5. **Better Tests**: Generates improved tests based on learning
6. **Repeat**: System gets smarter with each iteration

## 🎓 Learning Examples

### Scenario 1: Selector Issues
- **Initial Test**: Fails to find hint button
- **Feedback**: "Hint uses lightbulb icon, not text"
- **Learning**: RAG stores this for future hint tests
- **Next Time**: System queries feedback before generating hint tests

### Scenario 2: Similar Games
- **New Game**: Another number matching puzzle
- **RAG Query**: Finds similar game (SumLink)
- **Result**: Applies SumLink test patterns automatically
- **Benefit**: No manual test writing needed

### Scenario 3: Pattern Recognition
- **Observation**: Click-based games always need tile tests
- **Storage**: Pattern stored in test_history
- **Application**: Future click games get similar tests
- **Evolution**: System builds testing strategies over time

## 🐛 Troubleshooting

### RAG not initializing
```
Warning: RAG not available - sentence_transformers not found
```
**Solution**: Install dependencies
```bash
pip install sentence-transformers torch
```

### Embeddings slow on first run
- **Normal**: Sentence-Transformers downloads model first time
- **Wait**: ~5 minutes for model download
- **Subsequent runs**: Fast (model cached)

### Knowledge base growing large
```bash
# Clear all stored knowledge (use with caution)
python -c "from backend.rag_simple import SimpleRAGKnowledgeBase; SimpleRAGKnowledgeBase().clear_all_data()"
```

## 📚 Key Dependencies

- **FastAPI**: Backend server
- **Playwright**: Browser automation
- **Sentence-Transformers**: Text embeddings
- **NumPy**: Vector operations
- **BeautifulSoup4**: HTML parsing
- **LangChain** (optional): LLM integration
- **OpenAI** (optional): GPT-3.5 for advanced test generation

## 🚀 Next Steps

1. **Run the RAG demonstration**:
   ```bash
   python test_rag_learning.py
   ```

2. **Start the web application**:
   ```bash
   python backend/main.py
   ```

3. **Generate and execute tests**:
   - Open http://localhost:8000
   - Click "Generate Test Plan"
   - Click "Execute Top 10 Tests"
   - View results and reports

4. **Check RAG insights**:
   ```bash
   curl http://localhost:8000/api/rag/insights
   ```

5. **Add feedback** (via API or future UI):
   ```bash
   curl -X POST http://localhost:8000/api/rag/feedback \
     -H "Content-Type: application/json" \
     -d '{"test_id":"sumlink_001","feedback":"Great test!","context":{}}'
   ```

## 📝 Summary

This system demonstrates:
- ✅ **True multi-agent architecture**
- ✅ **Trainable AI with RAG**
- ✅ **Game-specific test generation**
- ✅ **Persistent learning across sessions**
- ✅ **Human feedback integration**
- ✅ **Adaptive test strategies**
- ✅ **Knowledge retrieval and reuse**

**This is NOT basic automation** - it's an AI system that learns, adapts, and improves over time!

---

For questions or issues, refer to:
- `GAME_ANALYZER_README.md` - Game analyzer details
- `RECRUITER_RESPONSE.md` - Capabilities explanation
- `test_rag_learning.py` - Working demonstration

**Developed with multi-agent AI architecture and RAG-based learning**
