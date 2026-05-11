import json
import os
from datetime import datetime
 
class HighScoreManager:
    def __init__(self, filename="highscores.json"):
        self.filename = filename
        self.scores = self.load_scores()
    
    def load_scores(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_scores(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.scores, f, indent=4, ensure_ascii=False)
    
    def add_score(self, score, player_name="Player"):
        entry = {
            "name": player_name,
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.scores.append(entry)
    
        self.scores.sort(key=lambda x: x["score"], reverse=True)
   
        self.scores = self.scores[:10]
        self.save_scores()
    
    def get_top_scores(self, limit=10):
        return self.scores[:limit]
    
    def is_high_score(self, score):
        if len(self.scores) < 10:
            return True
        return score > self.scores[-1]["score"]
    
    def get_rank(self, score):
        for i, entry in enumerate(self.scores):
            if entry["score"] <= score:
                return i + 1
        return len(self.scores) + 1