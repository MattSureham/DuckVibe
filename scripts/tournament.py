#!/usr/bin/env python3
"""
DevForge - Tournament System
Compare different feature implementations using TrueSkill ratings
"""

import os
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class TrueSkillRating:
    """Simplified TrueSkill implementation"""
    
    def __init__(self, mu=25.0, sigma=25.0/3):
        self.mu = mu
        self.sigma = sigma
    
    def update_rating(self, winner_rating, loser_rating, draw=False):
        winner_mu, winner_sigma = winner_rating['mu'], winner_rating['sigma']
        loser_mu, loser_sigma = loser_rating['mu'], loser_rating['sigma']
        
        if not draw:
            winner_mu += 1.0
            loser_mu -= 1.0
        
        winner_sigma = max(1.0, winner_sigma * 0.95)
        loser_sigma = max(1.0, loser_sigma * 0.95)
        
        return (
            {'mu': winner_mu, 'sigma': winner_sigma},
            {'mu': loser_mu, 'sigma': loser_sigma}
        )
    
    def conservative_rating(self, rating):
        return rating['mu'] - 3 * rating['sigma']

class Tournament:
    def __init__(self, config_path="config/.env"):
        self.projects_dir = Path("projects")
        self.data_file = Path("data/tournament.json")
        self.trueskill = TrueSkillRating()
        
        self.data = self._load_data()
    
    def _load_data(self):
        if self.data_file.exists():
            with open(self.data_file) as f:
                return json.load(f)
        return {"features": {}, "matches": [], "created_at": datetime.now().isoformat()}
    
    def _save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def register_feature(self, feature_id: str, feature_type: str = "ai"):
        """Register a feature in the tournament"""
        if feature_id not in self.data["features"]:
            self.data["features"][feature_id] = {
                "id": feature_id,
                "type": feature_type,
                "rating": {"mu": 25.0, "sigma": 8.33},
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0
            }
            self._save_data()
            print(f"✅ Registered {feature_type} feature: {feature_id}")
    
    def run_match(self, feature1_id: str, feature2_id: str) -> Dict:
        """Run head-to-head match"""
        self.register_feature(feature1_id)
        self.register_feature(feature2_id)
        
        print(f"\n⚔️  Match: {feature1_id} vs {feature2_id}")
        
        # Load feature specs
        feat1 = self._load_feature(feature1_id)
        feat2 = self._load_feature(feature2_id)
        
        # Simulate judgment (with position bias control)
        result = self._judge_match(feat1, feat2)
        
        # Update ratings
        self._update_ratings(feature1_id, feature2_id, result)
        
        # Record match
        match_record = {
            "id": f"match_{len(self.data['matches']) + 1:05d}",
            "feature1": feature1_id,
            "feature2": feature2_id,
            "winner": result.get('winner'),
            "is_draw": result.get('is_draw', False),
            "timestamp": datetime.now().isoformat()
        }
        self.data["matches"].append(match_record)
        self._save_data()
        
        return result
    
    def _load_feature(self, feature_id: str):
        feature_path = self.projects_dir / feature_id
        if (feature_path / "feature_spec.json").exists():
            with open(feature_path / "feature_spec.json") as f:
                return json.load(f)
        return None
    
    def _judge_match(self, feat1: Dict, feat2: Dict) -> Dict:
        """Judge match with position bias control"""
        # Round 1
        result1 = self._single_judgment(feat1, feat2)
        # Round 2 (swapped)
        result2 = self._single_judgment(feat2, feat1)
        
        winner1 = result1.get('winner')
        winner2 = "feature1" if result2.get('winner') == "feature2" else "feature2"
        
        if winner1 == winner2:
            actual_winner = feat1.get('id') if winner1 == "feature1" else feat2.get('id')
            is_draw = False
        else:
            actual_winner = None
            is_draw = True
        
        return {
            "winner": actual_winner,
            "is_draw": is_draw
        }
    
    def _single_judgment(self, feat_first: Dict, feat_second: Dict) -> Dict:
        """Single judgment round"""
        # Score based on test results
        score1 = feat_first.get('test_results', {}).get('summary', {}).get('overall_score', 50)
        score2 = feat_second.get('test_results', {}).get('summary', {}).get('overall_score', 50)
        
        if score1 > score2:
            return {"winner": "feature1"}
        else:
            return {"winner": "feature2"}
    
    def _update_ratings(self, f1_id: str, f2_id: str, result: Dict):
        """Update TrueSkill ratings"""
        f1 = self.data["features"][f1_id]
        f2 = self.data["features"][f2_id]
        
        winner_id = result.get('winner')
        is_draw = result.get('is_draw', False)
        
        f1["matches_played"] += 1
        f2["matches_played"] += 1
        
        if is_draw:
            f1["draws"] += 1
            f2["draws"] += 1
        elif winner_id == f1_id:
            f1["wins"] += 1
            f2["losses"] += 1
        else:
            f1["losses"] += 1
            f2["wins"] += 1
        
        winner_rating = f1["rating"] if winner_id == f1_id else f2["rating"]
        loser_rating = f2["rating"] if winner_id == f1_id else f1["rating"]
        
        new_winner, new_loser = self.trueskill.update_rating(
            winner_rating, loser_rating, draw=is_draw
        )
        
        if winner_id == f1_id:
            f1["rating"] = new_winner
            f2["rating"] = new_loser
        else:
            f1["rating"] = new_loser
            f2["rating"] = new_winner
        
        self._save_data()
    
    def get_leaderboard(self) -> List[Dict]:
        """Get tournament leaderboard"""
        features = list(self.data["features"].values())
        
        features.sort(
            key=lambda f: self.trueskill.conservative_rating(f["rating"]),
            reverse=True
        )
        
        return [
            {
                "rank": i + 1,
                "id": f["id"],
                "type": f["type"],
                "mu": round(f["rating"]["mu"], 2),
                "sigma": round(f["rating"]["sigma"], 2),
                "conservative": round(self.trueskill.conservative_rating(f["rating"]), 2),
                "matches": f["matches_played"],
                "wins": f["wins"],
                "win_rate": round(f["wins"] / max(1, f["matches_played"]) * 100, 1)
            }
            for i, f in enumerate(features)
        ]
    
    def display_leaderboard(self):
        """Display leaderboard"""
        leaderboard = self.get_leaderboard()
        
        print("\n" + "=" * 80)
        print("🏆 TOURNAMENT LEADERBOARD")
        print("=" * 80)
        print(f"{'Rank':<6} {'Feature ID':<25} {'Type':<8} {'Rating':<10} {'Matches':<8} {'Win %':<8}")
        print("-" * 80)
        
        for entry in leaderboard[:20]:
            print(f"{entry['rank']:<6} {entry['id']:<25} {entry['type']:<8} "
                  f"{entry['conservative']:<10} {entry['matches']:<8} {entry['win_rate']:<8}")
        
        print("=" * 80)

if __name__ == "__main__":
    import sys
    
    tournament = Tournament()
    
    if len(sys.argv) < 2:
        tournament.display_leaderboard()
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "leaderboard":
        tournament.display_leaderboard()
    elif command == "match" and len(sys.argv) >= 4:
        tournament.run_match(sys.argv[2], sys.argv[3])
    elif command == "register" and len(sys.argv) >= 3:
        ftype = sys.argv[3] if len(sys.argv) > 3 else "ai"
        tournament.register_feature(sys.argv[2], ftype)
    else:
        print("Usage: python3 tournament.py [leaderboard|match|register]")
