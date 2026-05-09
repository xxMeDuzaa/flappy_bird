# server/score_manager.py
import os

class ScoreManager:
    def __init__(self, high_score_file="flappy_highscore.txt"):
        self.high_score_file = high_score_file
        self.current_score = 0
        self.high_score = self._load_high_score()
        
    def _load_high_score(self):
        if os.path.exists(self.high_score_file):
            with open(self.high_score_file, 'r') as file:
                try:
                    return int(file.read())
                except:
                    return 0
        return 0
        
    def _save_high_score(self):
        with open(self.high_score_file, 'w') as file:
            file.write(str(self.high_score))
            
    def add_score(self, points=1):
        self.current_score += points
        if self.current_score > self.high_score:
            self.high_score = self.current_score
            self._save_high_score()
            return True  # Nuevo récord
        return False
        
    def reset_score(self):
        self.current_score = 0
        
    def get_current_score(self):
        return self.current_score
        
    def get_high_score(self):
        return self.high_score