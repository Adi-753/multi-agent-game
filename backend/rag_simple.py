import json
import os
from typing import List, Dict, Any
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
from pathlib import Path

class SimpleRAGKnowledgeBase:
    def __init__(self, persist_directory: str = "./knowledge_base"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.game_knowledge_file = self.persist_directory / "game_knowledge.json"
        self.test_history_file = self.persist_directory / "test_history.json"
        self.feedback_file = self.persist_directory / "feedback.json"
        self.embeddings_file = self.persist_directory / "embeddings.pkl"
        
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Embedding model loaded successfully")
        
        self.game_knowledge = self._load_json(self.game_knowledge_file)
        self.test_history = self._load_json(self.test_history_file)
        self.feedback = self._load_json(self.feedback_file)
        self.embeddings = self._load_embeddings()
    
    def _load_json(self, filepath: Path) -> List[Dict]:
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_json(self, filepath: Path, data: List[Dict]):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_embeddings(self) -> Dict:
        if self.embeddings_file.exists():
            with open(self.embeddings_file, 'rb') as f:
                return pickle.load(f)
        return {
            'game_knowledge': [],
            'test_history': [],
            'feedback': []
        }
    
    def _save_embeddings(self):
        with open(self.embeddings_file, 'wb') as f:
            pickle.dump(self.embeddings, f)
    
    def _create_embedding(self, text: str) -> np.ndarray:
        return self.embedding_model.encode(text)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def store_game_analysis(self, game_url: str, analysis: Dict[str, Any]):
        """Store game analysis with embeddings"""
        entry = {
            'id': f"game_{len(self.game_knowledge)}",
            'game_url': game_url,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat(),
            'game_type': analysis.get('game_type', 'unknown'),
            'features': analysis.get('features', []),
            'mechanics': analysis.get('mechanics', {})
        }
        
        text_for_embedding = f"""
        Game URL: {game_url}
        Game Type: {analysis.get('game_type', 'unknown')}
        Features: {', '.join(analysis.get('features', []))}
        Mechanics: {json.dumps(analysis.get('mechanics', {}))}
        Interaction Model: {analysis.get('interaction_model', 'unknown')}
        """
        
        embedding = self._create_embedding(text_for_embedding)
        self.embeddings['game_knowledge'].append(embedding)
        
        self.game_knowledge.append(entry)
        self._save_json(self.game_knowledge_file, self.game_knowledge)
        self._save_embeddings()
        
        print(f"✓ Stored game analysis for {game_url}")
        return entry['id']
    
    def store_test_result(self, test_id: str, result: Dict[str, Any], game_url: str):
        """Store test execution results"""
        entry = {
            'id': f"test_{len(self.test_history)}",
            'test_id': test_id,
            'game_url': game_url,
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'status': result.get('status', 'unknown'),
            'duration': result.get('duration', 0),
            'errors': result.get('errors', [])
        }
        
        text_for_embedding = f"""
        Test ID: {test_id}
        Game URL: {game_url}
        Status: {result.get('status', 'unknown')}
        Test Name: {result.get('name', 'unknown')}
        Category: {result.get('category', 'unknown')}
        Errors: {', '.join(result.get('errors', []))}
        """
        
        embedding = self._create_embedding(text_for_embedding)
        self.embeddings['test_history'].append(embedding)
        
        self.test_history.append(entry)
        self._save_json(self.test_history_file, self.test_history)
        self._save_embeddings()
        
        print(f"✓ Stored test result for {test_id}")
        return entry['id']
    
    def store_feedback(self, test_id: str, feedback_text: str, context: Dict[str, Any]):
        """Store human feedback"""
        entry = {
            'id': f"feedback_{len(self.feedback)}",
            'test_id': test_id,
            'feedback': feedback_text,
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'game_url': context.get('game_url', 'unknown')
        }
        
        text_for_embedding = f"""
        Test ID: {test_id}
        Feedback: {feedback_text}
        Game URL: {context.get('game_url', 'unknown')}
        Context: {json.dumps(context)}
        """
        
        embedding = self._create_embedding(text_for_embedding)
        self.embeddings['feedback'].append(embedding)
        
        self.feedback.append(entry)
        self._save_json(self.feedback_file, self.feedback)
        self._save_embeddings()
        
        print(f"✓ Stored feedback for {test_id}")
        return entry['id']
    
    def query_similar_games(self, game_url: str, top_k: int = 3) -> List[Dict]:
        if not self.game_knowledge or not self.embeddings['game_knowledge']:
            return []
        
        query_text = f"Game URL: {game_url}"
        query_embedding = self._create_embedding(query_text)
        
        similarities = []
        for idx, embedding in enumerate(self.embeddings['game_knowledge']):
            similarity = self._cosine_similarity(query_embedding, embedding)
            similarities.append((idx, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in similarities[:top_k]]
        
        return [self.game_knowledge[idx] for idx in top_indices if idx < len(self.game_knowledge)]
    
    def query_test_history(self, game_url: str, top_k: int = 5) -> List[Dict]:
        if not self.test_history or not self.embeddings['test_history']:
            return []
        
        query_text = f"Game URL: {game_url} test results"
        query_embedding = self._create_embedding(query_text)
        
        similarities = []
        for idx, embedding in enumerate(self.embeddings['test_history']):
            similarity = self._cosine_similarity(query_embedding, embedding)
            similarities.append((idx, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in similarities[:top_k]]
        
        return [self.test_history[idx] for idx in top_indices if idx < len(self.test_history)]
    
    def query_feedback(self, query: str, top_k: int = 3) -> List[Dict]:
        if not self.feedback or not self.embeddings['feedback']:
            return []
        
        query_embedding = self._create_embedding(query)
        
        similarities = []
        for idx, embedding in enumerate(self.embeddings['feedback']):
            similarity = self._cosine_similarity(query_embedding, embedding)
            similarities.append((idx, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in similarities[:top_k]]
        
        return [self.feedback[idx] for idx in top_indices if idx < len(self.feedback)]
    
    def get_learning_insights(self, game_url: str) -> Dict[str, Any]:
        similar_games = self.query_similar_games(game_url, top_k=3)
        test_history = self.query_test_history(game_url, top_k=10)
        
        insights = {
            'total_tests': len([t for t in self.test_history if t.get('game_url') == game_url]),
            'successful_tests': len([t for t in self.test_history if t.get('game_url') == game_url and t.get('status') == 'passed']),
            'failed_tests': len([t for t in self.test_history if t.get('game_url') == game_url and t.get('status') == 'failed']),
            'similar_games_count': len(similar_games),
            'feedback_count': len([f for f in self.feedback if f.get('context', {}).get('game_url') == game_url]),
            'recent_tests': test_history[:5],
            'game_knowledge_entries': len([g for g in self.game_knowledge if g.get('game_url') == game_url])
        }
        
        return insights
    
    def clear_all_data(self):
        self.game_knowledge = []
        self.test_history = []
        self.feedback = []
        self.embeddings = {
            'game_knowledge': [],
            'test_history': [],
            'feedback': []
        }
        
        self._save_json(self.game_knowledge_file, self.game_knowledge)
        self._save_json(self.test_history_file, self.test_history)
        self._save_json(self.feedback_file, self.feedback)
        self._save_embeddings()
        
        print("✓ All knowledge base data cleared")
