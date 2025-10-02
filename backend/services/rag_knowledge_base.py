import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import json
from datetime import datetime
import os

class RAGKnowledgeBase:
    
    def __init__(self, persist_directory="./knowledge_base"):
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.game_knowledge = self.client.get_or_create_collection(
            name="game_knowledge",
            metadata={"description": "Knowledge about game mechanics and UI"}
        )
        
        self.test_history = self.client.get_or_create_collection(
            name="test_history",
            metadata={"description": "Historical test results and patterns"}
        )
        
        self.feedback_collection = self.client.get_or_create_collection(
            name="human_feedback",
            metadata={"description": "Human feedback on test quality"}
        )
        
    def store_game_analysis(self, game_url: str, analysis: Dict[str, Any]):
        doc_id = f"game_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        document = f"""
        Game URL: {game_url}
        Game Type: {analysis.get('game_type', 'unknown')}
        
        UI Elements Found:
        {json.dumps(analysis.get('ui_elements', []), indent=2)}
        
        Game Mechanics:
        {json.dumps(analysis.get('mechanics', {}), indent=2)}
        
        Key Features:
        {', '.join(analysis.get('features', []))}
        """
        
        self.game_knowledge.add(
            documents=[document],
            metadatas=[{
                "game_url": game_url,
                "game_type": analysis.get('game_type'),
                "timestamp": datetime.now().isoformat()
            }],
            ids=[doc_id]
        )
        
        return doc_id
    
    def store_test_result(self, test_case: Dict, result: Dict, feedback: str = None):
        doc_id = f"test_{test_case['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        document = f"""
        Test Name: {test_case['name']}
        Category: {test_case.get('category')}
        
        Test Steps:
        {json.dumps(test_case.get('steps', []), indent=2)}
        
        Result: {'PASS' if result.get('success') else 'FAIL'}
        Error: {result.get('error', 'None')}
        
        Feedback: {feedback or 'No feedback provided'}
        """
        
        self.test_history.add(
            documents=[document],
            metadatas=[{
                "test_id": test_case['id'],
                "test_name": test_case['name'],
                "category": test_case.get('category'),
                "result": "pass" if result.get('success') else "fail",
                "timestamp": datetime.now().isoformat()
            }],
            ids=[doc_id]
        )
        
    def store_human_feedback(self, test_id: str, feedback_text: str, rating: int, suggestions: List[str] = None):
        doc_id = f"feedback_{test_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        document = f"""
        Test ID: {test_id}
        Rating: {rating}/5
        Feedback: {feedback_text}
        
        Suggestions:
        {json.dumps(suggestions or [], indent=2)}
        """
        
        self.feedback_collection.add(
            documents=[document],
            metadatas=[{
                "test_id": test_id,
                "rating": rating,
                "timestamp": datetime.now().isoformat()
            }],
            ids=[doc_id]
        )
        
    def query_similar_games(self, game_description: str, n_results: int = 3):
        try:
            results = self.game_knowledge.query(
                query_texts=[game_description],
                n_results=n_results
            )
            return results
        except Exception as e:
            print(f"Query error: {e}")
            return {"documents": [[]], "metadatas": [[]]}
    
    def query_successful_tests(self, category: str, n_results: int = 5):
        try:
            results = self.test_history.query(
                query_texts=[f"successful {category} tests"],
                n_results=n_results,
                where={"result": "pass"}
            )
            return results
        except Exception as e:
            print(f"Query error: {e}")
            return {"documents": [[]], "metadatas": [[]]}
    
    def get_feedback_insights(self, min_rating: int = 3):
        try:
            count = self.feedback_collection.count()
            if count == 0:
                return []
            
            all_feedback = self.feedback_collection.get()
            
            insights = []
            if all_feedback and 'metadatas' in all_feedback:
                for i, metadata in enumerate(all_feedback['metadatas']):
                    if metadata.get('rating', 0) >= min_rating:
                        insights.append({
                            'test_id': metadata.get('test_id'),
                            'rating': metadata.get('rating'),
                            'document': all_feedback['documents'][i] if i < len(all_feedback['documents']) else ''
                        })
            
            return insights
        except Exception as e:
            print(f"Feedback query error: {e}")
            return []
