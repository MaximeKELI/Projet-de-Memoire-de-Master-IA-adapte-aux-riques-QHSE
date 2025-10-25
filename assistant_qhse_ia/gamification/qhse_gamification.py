"""
Système de Gamification QHSE
Engagement des employés et motivation pour la sécurité
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random

class BadgeType(Enum):
    SAFETY_CHAMPION = "safety_champion"
    ZERO_ACCIDENT = "zero_accident"
    TRAINING_MASTER = "training_master"
    RISK_DETECTIVE = "risk_detective"
    TEAM_PLAYER = "team_player"
    INNOVATOR = "innovator"
    MENTOR = "mentor"
    PERFECTIONIST = "perfectionist"

class AchievementType(Enum):
    STREAK = "streak"
    MILESTONE = "milestone"
    SPECIAL = "special"
    TEAM = "team"
    INDIVIDUAL = "individual"

@dataclass
class Badge:
    badge_id: str
    name: str
    description: str
    icon: str
    points: int
    requirements: Dict
    category: str
    rarity: str  # common, rare, epic, legendary

@dataclass
class Achievement:
    achievement_id: str
    user_id: int
    badge_id: str
    earned_at: datetime
    points_earned: int
    context: Dict

@dataclass
class UserProfile:
    user_id: int
    username: str
    level: int
    total_points: int
    current_streak: int
    longest_streak: int
    badges_earned: List[str]
    achievements: List[Achievement]
    rank: str
    team_id: Optional[int] = None

@dataclass
class Challenge:
    challenge_id: str
    name: str
    description: str
    points_reward: int
    duration_days: int
    requirements: Dict
    start_date: datetime
    end_date: datetime
    participants: List[int]
    status: str  # active, completed, expired

class QHSEGamificationSystem:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.badges = {}
        self.challenges = {}
        self.leaderboards = {}
        
        self._init_database()
        self._load_badges()
        self._load_challenges()
    
    def _init_database(self):
        """Initialise la base de données de gamification"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Table des badges
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gamification_badges (
                badge_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                icon TEXT NOT NULL,
                points INTEGER NOT NULL,
                requirements TEXT NOT NULL,
                category TEXT NOT NULL,
                rarity TEXT NOT NULL
            )
        ''')
        
        # Table des profils utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_gamification_profiles (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                total_points INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                badges_earned TEXT DEFAULT '[]',
                rank TEXT DEFAULT 'Rookie',
                team_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Table des achievements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badge_id TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                points_earned INTEGER NOT NULL,
                context TEXT DEFAULT '{}',
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (badge_id) REFERENCES gamification_badges(badge_id)
            )
        ''')
        
        # Table des challenges
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gamification_challenges (
                challenge_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                points_reward INTEGER NOT NULL,
                duration_days INTEGER NOT NULL,
                requirements TEXT NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                participants TEXT DEFAULT '[]',
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des équipes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gamification_teams (
                team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                leader_id INTEGER NOT NULL,
                members TEXT DEFAULT '[]',
                total_points INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (leader_id) REFERENCES users(id)
            )
        ''')
        
        # Table des événements de points
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS points_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                points INTEGER NOT NULL,
                description TEXT NOT NULL,
                context TEXT DEFAULT '{}',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_badges(self):
        """Charge les badges depuis la base de données"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM gamification_badges')
        rows = cursor.fetchall()
        
        for row in rows:
            self.badges[row[0]] = Badge(
                badge_id=row[0],
                name=row[1],
                description=row[2],
                icon=row[3],
                points=row[4],
                requirements=json.loads(row[5]),
                category=row[6],
                rarity=row[7]
            )
        
        conn.close()
        
        # Création des badges par défaut si aucun n'existe
        if not self.badges:
            self._create_default_badges()
    
    def _create_default_badges(self):
        """Crée les badges par défaut"""
        default_badges = [
            {
                "badge_id": "safety_champion_1",
                "name": "Champion de Sécurité",
                "description": "Aucun incident pendant 30 jours consécutifs",
                "icon": "🛡️",
                "points": 100,
                "requirements": {"days_without_incident": 30},
                "category": "safety",
                "rarity": "rare"
            },
            {
                "badge_id": "training_master_1",
                "name": "Maître de la Formation",
                "description": "Compléter 10 formations QHSE",
                "icon": "🎓",
                "points": 75,
                "requirements": {"completed_trainings": 10},
                "category": "training",
                "rarity": "common"
            },
            {
                "badge_id": "risk_detective_1",
                "name": "Détective des Risques",
                "description": "Signaler 5 risques potentiels",
                "icon": "🔍",
                "points": 50,
                "requirements": {"risk_reports": 5},
                "category": "prevention",
                "rarity": "common"
            },
            {
                "badge_id": "team_player_1",
                "name": "Joueur d'Équipe",
                "description": "Participer à 5 challenges d'équipe",
                "icon": "👥",
                "points": 60,
                "requirements": {"team_challenges": 5},
                "category": "teamwork",
                "rarity": "common"
            },
            {
                "badge_id": "innovator_1",
                "name": "Innovateur",
                "description": "Proposer 3 améliorations QHSE",
                "icon": "💡",
                "points": 80,
                "requirements": {"improvement_suggestions": 3},
                "category": "innovation",
                "rarity": "rare"
            },
            {
                "badge_id": "mentor_1",
                "name": "Mentor",
                "description": "Former 5 nouveaux employés",
                "icon": "👨‍🏫",
                "points": 90,
                "requirements": {"trained_employees": 5},
                "category": "leadership",
                "rarity": "epic"
            },
            {
                "badge_id": "perfectionist_1",
                "name": "Perfectionniste",
                "description": "100% de conformité pendant 6 mois",
                "icon": "⭐",
                "points": 150,
                "requirements": {"compliance_percentage": 100, "months": 6},
                "category": "excellence",
                "rarity": "legendary"
            }
        ]
        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        for badge_data in default_badges:
            cursor.execute('''
                INSERT INTO gamification_badges 
                (badge_id, name, description, icon, points, requirements, category, rarity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                badge_data["badge_id"],
                badge_data["name"],
                badge_data["description"],
                badge_data["icon"],
                badge_data["points"],
                json.dumps(badge_data["requirements"]),
                badge_data["category"],
                badge_data["rarity"]
            ))
        
        conn.commit()
        conn.close()
        
        # Recharger les badges
        self._load_badges()
    
    def _load_challenges(self):
        """Charge les challenges depuis la base de données"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM gamification_challenges WHERE status = "active"')
        rows = cursor.fetchall()
        
        for row in rows:
            self.challenges[row[0]] = Challenge(
                challenge_id=row[0],
                name=row[1],
                description=row[2],
                points_reward=row[3],
                duration_days=row[4],
                requirements=json.loads(row[5]),
                start_date=datetime.fromisoformat(row[6]),
                end_date=datetime.fromisoformat(row[7]),
                participants=json.loads(row[8]),
                status=row[9]
            )
        
        conn.close()
    
    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Récupère le profil gamification d'un utilisateur"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_gamification_profiles WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        # Récupérer les achievements
        cursor.execute('''
            SELECT * FROM user_achievements WHERE user_id = ? ORDER BY earned_at DESC
        ''', (user_id,))
        
        achievements = []
        for ach_row in cursor.fetchall():
            achievements.append(Achievement(
                achievement_id=str(ach_row[0]),
                user_id=ach_row[1],
                badge_id=ach_row[2],
                earned_at=datetime.fromisoformat(ach_row[3]),
                points_earned=ach_row[4],
                context=json.loads(ach_row[5])
            ))
        
        conn.close()
        
        return UserProfile(
            user_id=row[0],
            username=row[1],
            level=row[2],
            total_points=row[3],
            current_streak=row[4],
            longest_streak=row[5],
            badges_earned=json.loads(row[6]),
            achievements=achievements,
            rank=row[7],
            team_id=row[8]
        )
    
    def create_user_profile(self, user_id: int, username: str) -> bool:
        """Crée un profil gamification pour un utilisateur"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_gamification_profiles 
                (user_id, username, level, total_points, current_streak, longest_streak, badges_earned, rank)
                VALUES (?, ?, 1, 0, 0, 0, '[]', 'Rookie')
            ''', (user_id, username))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Erreur création profil utilisateur {user_id}: {e}")
            return False
    
    def award_points(self, user_id: int, event_type: str, points: int, 
                    description: str, context: Dict = None) -> bool:
        """Attribue des points à un utilisateur"""
        try:
            if context is None:
                context = {}
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Enregistrer l'événement de points
            cursor.execute('''
                INSERT INTO points_events 
                (user_id, event_type, points, description, context)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, event_type, points, description, json.dumps(context)))
            
            # Mettre à jour le profil utilisateur
            cursor.execute('''
                UPDATE user_gamification_profiles 
                SET total_points = total_points + ?, last_activity = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (points, user_id))
            
            conn.commit()
            conn.close()
            
            # Vérifier les badges et niveaux
            self._check_badges_and_levels(user_id)
            
            return True
            
        except Exception as e:
            print(f"Erreur attribution points utilisateur {user_id}: {e}")
            return False
    
    def _check_badges_and_levels(self, user_id: int):
        """Vérifie et attribue les badges et niveaux"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return
        
        # Vérifier les badges
        for badge_id, badge in self.badges.items():
            if badge_id in profile.badges_earned:
                continue  # Badge déjà gagné
            
            if self._check_badge_requirements(user_id, badge):
                self._award_badge(user_id, badge_id)
        
        # Vérifier le niveau
        self._check_user_level(user_id)
    
    def _check_badge_requirements(self, user_id: int, badge: Badge) -> bool:
        """Vérifie si un utilisateur remplit les conditions d'un badge"""
        requirements = badge.requirements
        
        for req_type, req_value in requirements.items():
            if not self._check_requirement(user_id, req_type, req_value):
                return False
        
        return True
    
    def _check_requirement(self, user_id: int, req_type: str, req_value) -> bool:
        """Vérifie un type de requirement spécifique"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        if req_type == "days_without_incident":
            # Vérifier les incidents des 30 derniers jours
            since_date = datetime.now() - timedelta(days=req_value)
            cursor.execute('''
                SELECT COUNT(*) FROM incident_reports 
                WHERE reported_by = ? AND created_at >= ?
            ''', (user_id, since_date))
            incident_count = cursor.fetchone()[0]
            conn.close()
            return incident_count == 0
        
        elif req_type == "completed_trainings":
            cursor.execute('''
                SELECT COUNT(*) FROM training_participations 
                WHERE user_id = ? AND status = 'completed'
            ''', (user_id,))
            training_count = cursor.fetchone()[0]
            conn.close()
            return training_count >= req_value
        
        elif req_type == "risk_reports":
            cursor.execute('''
                SELECT COUNT(*) FROM incident_reports 
                WHERE reported_by = ? AND severity_level = 1
            ''', (user_id,))
            risk_count = cursor.fetchone()[0]
            conn.close()
            return risk_count >= req_value
        
        elif req_type == "team_challenges":
            cursor.execute('''
                SELECT COUNT(*) FROM gamification_challenges 
                WHERE JSON_EXTRACT(participants, '$') LIKE ? AND status = 'completed'
            ''', (f'%{user_id}%',))
            challenge_count = cursor.fetchone()[0]
            conn.close()
            return challenge_count >= req_value
        
        elif req_type == "improvement_suggestions":
            cursor.execute('''
                SELECT COUNT(*) FROM incident_reports 
                WHERE reported_by = ? AND ai_recommendations IS NOT NULL
            ''', (user_id,))
            suggestion_count = cursor.fetchone()[0]
            conn.close()
            return suggestion_count >= req_value
        
        elif req_type == "trained_employees":
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) FROM training_participations 
                WHERE trainer_id = ?
            ''', (user_id,))
            trained_count = cursor.fetchone()[0]
            conn.close()
            return trained_count >= req_value
        
        elif req_type == "compliance_percentage":
            # Logique complexe pour vérifier la conformité
            conn.close()
            return False  # À implémenter selon les besoins
        
        conn.close()
        return False
    
    def _award_badge(self, user_id: int, badge_id: str) -> bool:
        """Attribue un badge à un utilisateur"""
        try:
            badge = self.badges[badge_id]
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Ajouter le badge aux badges gagnés
            cursor.execute('''
                SELECT badges_earned FROM user_gamification_profiles WHERE user_id = ?
            ''', (user_id,))
            
            badges_earned = json.loads(cursor.fetchone()[0])
            badges_earned.append(badge_id)
            
            cursor.execute('''
                UPDATE user_gamification_profiles 
                SET badges_earned = ? WHERE user_id = ?
            ''', (json.dumps(badges_earned), user_id))
            
            # Enregistrer l'achievement
            cursor.execute('''
                INSERT INTO user_achievements 
                (user_id, badge_id, points_earned, context)
                VALUES (?, ?, ?, ?)
            ''', (user_id, badge_id, badge.points, json.dumps({})))
            
            # Ajouter les points
            cursor.execute('''
                UPDATE user_gamification_profiles 
                SET total_points = total_points + ?
                WHERE user_id = ?
            ''', (badge.points, user_id))
            
            conn.commit()
            conn.close()
            
            print(f"Badge {badge.name} attribué à l'utilisateur {user_id}")
            return True
            
        except Exception as e:
            print(f"Erreur attribution badge {badge_id} à {user_id}: {e}")
            return False
    
    def _check_user_level(self, user_id: int):
        """Vérifie et met à jour le niveau d'un utilisateur"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return
        
        # Calcul du niveau basé sur les points
        new_level = min(100, (profile.total_points // 1000) + 1)
        
        if new_level > profile.level:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_gamification_profiles 
                SET level = ? WHERE user_id = ?
            ''', (new_level, user_id))
            
            conn.commit()
            conn.close()
            
            print(f"Utilisateur {user_id} atteint le niveau {new_level}")
    
    def get_leaderboard(self, category: str = "all", limit: int = 10) -> List[Dict]:
        """Récupère le classement des utilisateurs"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        if category == "all":
            cursor.execute('''
                SELECT user_id, username, total_points, level, rank
                FROM user_gamification_profiles
                ORDER BY total_points DESC
                LIMIT ?
            ''', (limit,))
        elif category == "monthly":
            # Classement du mois en cours
            month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            cursor.execute('''
                SELECT u.user_id, u.username, SUM(p.points) as monthly_points, u.level, u.rank
                FROM user_gamification_profiles u
                JOIN points_events p ON u.user_id = p.user_id
                WHERE p.timestamp >= ?
                GROUP BY u.user_id
                ORDER BY monthly_points DESC
                LIMIT ?
            ''', (month_start, limit))
        elif category == "team":
            cursor.execute('''
                SELECT t.team_id, t.name, SUM(u.total_points) as team_points
                FROM gamification_teams t
                JOIN user_gamification_profiles u ON t.team_id = u.team_id
                GROUP BY t.team_id
                ORDER BY team_points DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        leaderboard = []
        for i, row in enumerate(rows):
            leaderboard.append({
                "rank": i + 1,
                "user_id": row[0],
                "username": row[1],
                "points": row[2],
                "level": row[3] if len(row) > 3 else None,
                "rank_name": row[4] if len(row) > 4 else None
            })
        
        return leaderboard
    
    def create_challenge(self, name: str, description: str, points_reward: int,
                        duration_days: int, requirements: Dict) -> str:
        """Crée un nouveau challenge"""
        challenge_id = f"challenge_{int(datetime.now().timestamp())}"
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration_days)
        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO gamification_challenges 
            (challenge_id, name, description, points_reward, duration_days, 
             requirements, start_date, end_date, participants, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, '[]', 'active')
        ''', (challenge_id, name, description, points_reward, duration_days,
              json.dumps(requirements), start_date, end_date))
        
        conn.commit()
        conn.close()
        
        # Ajouter au cache
        self.challenges[challenge_id] = Challenge(
            challenge_id=challenge_id,
            name=name,
            description=description,
            points_reward=points_reward,
            duration_days=duration_days,
            requirements=requirements,
            start_date=start_date,
            end_date=end_date,
            participants=[],
            status="active"
        )
        
        return challenge_id
    
    def join_challenge(self, user_id: int, challenge_id: str) -> bool:
        """Rejoint un challenge"""
        if challenge_id not in self.challenges:
            return False
        
        challenge = self.challenges[challenge_id]
        if user_id in challenge.participants:
            return False  # Déjà participant
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Ajouter le participant
            participants = challenge.participants + [user_id]
            cursor.execute('''
                UPDATE gamification_challenges 
                SET participants = ? WHERE challenge_id = ?
            ''', (json.dumps(participants), challenge_id))
            
            conn.commit()
            conn.close()
            
            # Mettre à jour le cache
            challenge.participants = participants
            
            return True
            
        except Exception as e:
            print(f"Erreur participation challenge {challenge_id}: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Récupère les statistiques d'un utilisateur"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return {}
        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Statistiques des 30 derniers jours
        since_date = datetime.now() - timedelta(days=30)
        
        cursor.execute('''
            SELECT event_type, SUM(points) as total_points
            FROM points_events
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY event_type
        ''', (user_id, since_date))
        
        monthly_stats = {}
        for row in cursor.fetchall():
            monthly_stats[row[0]] = row[1]
        
        # Badges par catégorie
        badges_by_category = {}
        for badge_id in profile.badges_earned:
            badge = self.badges.get(badge_id)
            if badge:
                category = badge.category
                if category not in badges_by_category:
                    badges_by_category[category] = 0
                badges_by_category[category] += 1
        
        conn.close()
        
        return {
            "profile": {
                "user_id": profile.user_id,
                "username": profile.username,
                "level": profile.level,
                "total_points": profile.total_points,
                "current_streak": profile.current_streak,
                "longest_streak": profile.longest_streak,
                "rank": profile.rank,
                "badges_count": len(profile.badges_earned)
            },
            "monthly_stats": monthly_stats,
            "badges_by_category": badges_by_category,
            "achievements_count": len(profile.achievements)
        }

# Instance globale
gamification_system = QHSEGamificationSystem('assistant_qhse_ia/database/qhse.db')
