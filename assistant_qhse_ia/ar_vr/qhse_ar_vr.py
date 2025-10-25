"""
Système de Réalité Augmentée/Virtuelle QHSE
Formation immersive et inspection assistée
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid
import math

class ARVRType(Enum):
    TRAINING = "training"
    INSPECTION = "inspection"
    SIMULATION = "simulation"
    GUIDANCE = "guidance"
    EMERGENCY = "emergency"

class DeviceType(Enum):
    MOBILE_AR = "mobile_ar"
    VR_HEADSET = "vr_headset"
    HOLOLENS = "hololens"
    TABLET = "tablet"

@dataclass
class ARVRScene:
    scene_id: str
    name: str
    description: str
    scene_type: ARVRType
    device_type: DeviceType
    content: Dict
    duration_minutes: int
    difficulty_level: int
    created_at: datetime

@dataclass
class ARVRSession:
    session_id: str
    user_id: int
    scene_id: str
    device_type: DeviceType
    start_time: datetime
    end_time: Optional[datetime]
    progress_percentage: float
    score: Optional[float]
    interactions: List[Dict]
    completed: bool = False

class QHSEARVRSystem:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.scenes = {}
        self.active_sessions = {}
        
        self._init_database()
        self._load_scenes()
        self._create_default_scenes()
    
    def _init_database(self):
        """Initialise la base de données AR/VR"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Table des scènes AR/VR
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arvr_scenes (
                scene_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                scene_type TEXT NOT NULL,
                device_type TEXT NOT NULL,
                content TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                difficulty_level INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des sessions AR/VR
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arvr_sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                scene_id TEXT NOT NULL,
                device_type TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                progress_percentage REAL DEFAULT 0.0,
                score REAL,
                interactions TEXT DEFAULT '[]',
                completed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (scene_id) REFERENCES arvr_scenes(scene_id)
            )
        ''')
        
        # Table des objets 3D
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arvr_objects (
                object_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                object_type TEXT NOT NULL,
                model_url TEXT NOT NULL,
                position TEXT NOT NULL,
                rotation TEXT NOT NULL,
                scale TEXT NOT NULL,
                properties TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des interactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arvr_interactions (
                interaction_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                object_id TEXT,
                position TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data TEXT DEFAULT '{}',
                FOREIGN KEY (session_id) REFERENCES arvr_sessions(session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_scenes(self):
        """Charge les scènes depuis la base de données"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM arvr_scenes')
        rows = cursor.fetchall()
        
        for row in rows:
            self.scenes[row[0]] = ARVRScene(
                scene_id=row[0],
                name=row[1],
                description=row[2],
                scene_type=ARVRType(row[3]),
                device_type=DeviceType(row[4]),
                content=json.loads(row[5]),
                duration_minutes=row[6],
                difficulty_level=row[7],
                created_at=datetime.fromisoformat(row[8])
            )
        
        conn.close()
    
    def _create_default_scenes(self):
        """Crée les scènes par défaut"""
        if self.scenes:
            return  # Scènes déjà créées
        
        default_scenes = [
            {
                "scene_id": "safety_training_1",
                "name": "Formation Sécurité - Équipements de Protection",
                "description": "Apprentissage des EPI en réalité virtuelle",
                "scene_type": ARVRType.TRAINING,
                "device_type": DeviceType.VR_HEADSET,
                "content": self._create_safety_training_content(),
                "duration_minutes": 30,
                "difficulty_level": 2
            },
            {
                "scene_id": "inspection_ar_1",
                "name": "Inspection AR - Zone de Production",
                "description": "Inspection assistée par réalité augmentée",
                "scene_type": ARVRType.INSPECTION,
                "device_type": DeviceType.MOBILE_AR,
                "content": self._create_inspection_ar_content(),
                "duration_minutes": 45,
                "difficulty_level": 3
            },
            {
                "scene_id": "emergency_simulation_1",
                "name": "Simulation d'Évacuation d'Urgence",
                "description": "Simulation d'évacuation en cas d'incendie",
                "scene_type": ARVRType.SIMULATION,
                "device_type": DeviceType.VR_HEADSET,
                "content": self._create_emergency_simulation_content(),
                "duration_minutes": 20,
                "difficulty_level": 4
            },
            {
                "scene_id": "equipment_guidance_1",
                "name": "Guide d'Utilisation - Machine Complexe",
                "description": "Instructions pas à pas pour utiliser une machine",
                "scene_type": ARVRType.GUIDANCE,
                "device_type": DeviceType.HOLOLENS,
                "content": self._create_equipment_guidance_content(),
                "duration_minutes": 15,
                "difficulty_level": 2
            }
        ]
        
        for scene_data in default_scenes:
            self.create_scene(
                scene_data["scene_id"],
                scene_data["name"],
                scene_data["description"],
                scene_data["scene_type"],
                scene_data["device_type"],
                scene_data["content"],
                scene_data["duration_minutes"],
                scene_data["difficulty_level"]
            )
    
    def _create_safety_training_content(self) -> Dict:
        """Crée le contenu pour la formation sécurité"""
        return {
            "environment": {
                "type": "industrial_workshop",
                "lighting": "bright",
                "ambient_sounds": ["machinery", "safety_alerts"]
            },
            "objects": [
                {
                    "id": "helmet_1",
                    "type": "safety_helmet",
                    "position": {"x": 0, "y": 1.5, "z": 0},
                    "interactive": True,
                    "instructions": "Placez le casque de sécurité sur votre tête",
                    "points": 10
                },
                {
                    "id": "gloves_1",
                    "type": "safety_gloves",
                    "position": {"x": 1, "y": 1, "z": 0},
                    "interactive": True,
                    "instructions": "Enfilez les gants de protection",
                    "points": 10
                },
                {
                    "id": "safety_glasses_1",
                    "type": "safety_glasses",
                    "position": {"x": -1, "y": 1.2, "z": 0},
                    "interactive": True,
                    "instructions": "Mettez les lunettes de sécurité",
                    "points": 10
                }
            ],
            "hazards": [
                {
                    "id": "hazard_1",
                    "type": "falling_object",
                    "position": {"x": 2, "y": 3, "z": 1},
                    "warning": "Attention aux objets qui tombent !",
                    "prevention": "Portez toujours un casque de sécurité"
                }
            ],
            "checkpoints": [
                {
                    "id": "checkpoint_1",
                    "position": {"x": 0, "y": 0, "z": 2},
                    "description": "Vérifiez votre équipement de protection",
                    "required_objects": ["helmet_1", "gloves_1", "safety_glasses_1"]
                }
            ]
        }
    
    def _create_inspection_ar_content(self) -> Dict:
        """Crée le contenu pour l'inspection AR"""
        return {
            "environment": {
                "type": "production_floor",
                "ar_markers": ["machine_1", "safety_zone_1", "emergency_exit_1"]
            },
            "inspection_points": [
                {
                    "id": "inspection_1",
                    "name": "Vérification des protections machine",
                    "position": {"x": 0, "y": 0, "z": 0},
                    "ar_overlay": "safety_check_overlay",
                    "checklist": [
                        "Protections en place",
                        "Boutons d'arrêt d'urgence accessibles",
                        "Signalisation visible"
                    ]
                },
                {
                    "id": "inspection_2",
                    "name": "Contrôle des extincteurs",
                    "position": {"x": 5, "y": 0, "z": 0},
                    "ar_overlay": "fire_safety_overlay",
                    "checklist": [
                        "Extincteur en place",
                        "Pression correcte",
                        "Date de péremption valide"
                    ]
                }
            ],
            "ar_objects": [
                {
                    "id": "safety_info_1",
                    "type": "info_panel",
                    "position": {"x": 0, "y": 2, "z": 0},
                    "content": "Zone de sécurité - Portez vos EPI"
                }
            ]
        }
    
    def _create_emergency_simulation_content(self) -> Dict:
        """Crée le contenu pour la simulation d'urgence"""
        return {
            "environment": {
                "type": "office_building",
                "lighting": "emergency_red",
                "ambient_sounds": ["fire_alarm", "evacuation_instructions"]
            },
            "scenario": {
                "type": "fire_evacuation",
                "time_limit": 300,  # 5 minutes
                "objectives": [
                    "Identifier les sorties de secours",
                    "Suivre le plan d'évacuation",
                    "Aider les collègues en difficulté"
                ]
            },
            "evacuation_route": [
                {"position": {"x": 0, "y": 0, "z": 0}, "instruction": "Sortez de votre bureau"},
                {"position": {"x": 5, "y": 0, "z": 0}, "instruction": "Dirigez-vous vers l'escalier de secours"},
                {"position": {"x": 10, "y": 0, "z": 0}, "instruction": "Descendez au rez-de-chaussée"},
                {"position": {"x": 15, "y": 0, "z": 0}, "instruction": "Sortez du bâtiment"}
            ],
            "hazards": [
                {
                    "id": "smoke_1",
                    "position": {"x": 3, "y": 1, "z": 0},
                    "effect": "reduced_visibility",
                    "avoidance_required": True
                }
            ]
        }
    
    def _create_equipment_guidance_content(self) -> Dict:
        """Crée le contenu pour le guide d'équipement"""
        return {
            "equipment": {
                "name": "Presse Hydraulique",
                "model": "PH-5000",
                "safety_level": "high"
            },
            "steps": [
                {
                    "step": 1,
                    "instruction": "Vérifiez que la zone est dégagée",
                    "ar_highlight": {"x": 0, "y": 0, "z": 0},
                    "duration": 30
                },
                {
                    "step": 2,
                    "instruction": "Portez vos équipements de protection",
                    "ar_highlight": {"x": 0, "y": 1.5, "z": 0},
                    "duration": 60
                },
                {
                    "step": 3,
                    "instruction": "Activez le bouton de démarrage",
                    "ar_highlight": {"x": 1, "y": 1, "z": 0},
                    "duration": 15
                }
            ],
            "safety_checks": [
                "Vérification des protections",
                "Contrôle des boutons d'arrêt",
                "Test de fonctionnement"
            ]
        }
    
    def create_scene(self, scene_id: str, name: str, description: str,
                    scene_type: ARVRType, device_type: DeviceType,
                    content: Dict, duration_minutes: int, difficulty_level: int) -> bool:
        """Crée une nouvelle scène AR/VR"""
        try:
            scene = ARVRScene(
                scene_id=scene_id,
                name=name,
                description=description,
                scene_type=scene_type,
                device_type=device_type,
                content=content,
                duration_minutes=duration_minutes,
                difficulty_level=difficulty_level,
                created_at=datetime.now()
            )
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO arvr_scenes
                (scene_id, name, description, scene_type, device_type, content, duration_minutes, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scene_id, name, description, scene_type.value, device_type.value,
                json.dumps(content), duration_minutes, difficulty_level
            ))
            
            conn.commit()
            conn.close()
            
            self.scenes[scene_id] = scene
            return True
            
        except Exception as e:
            print(f"Erreur création scène {scene_id}: {e}")
            return False
    
    def start_session(self, user_id: int, scene_id: str, device_type: DeviceType) -> str:
        """Démarre une session AR/VR"""
        if scene_id not in self.scenes:
            raise ValueError("Scène non trouvée")
        
        session_id = str(uuid.uuid4())
        
        session = ARVRSession(
            session_id=session_id,
            user_id=user_id,
            scene_id=scene_id,
            device_type=device_type,
            start_time=datetime.now(),
            end_time=None,
            progress_percentage=0.0,
            score=None,
            interactions=[]
        )
        
        # Sauvegarde en base
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO arvr_sessions
            (session_id, user_id, scene_id, device_type, start_time, progress_percentage, interactions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, user_id, scene_id, device_type.value,
            session.start_time, 0.0, json.dumps([])
        ))
        
        conn.commit()
        conn.close()
        
        self.active_sessions[session_id] = session
        return session_id
    
    def end_session(self, session_id: str, score: float = None) -> bool:
        """Termine une session AR/VR"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.now()
        session.score = score
        session.completed = True
        
        # Calcul du pourcentage de progression
        scene = self.scenes[session.scene_id]
        total_duration = scene.duration_minutes * 60  # en secondes
        actual_duration = (session.end_time - session.start_time).total_seconds()
        session.progress_percentage = min(100.0, (actual_duration / total_duration) * 100)
        
        # Mise à jour en base
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE arvr_sessions
            SET end_time = ?, progress_percentage = ?, score = ?, interactions = ?, completed = ?
            WHERE session_id = ?
        ''', (
            session.end_time, session.progress_percentage, score,
            json.dumps(session.interactions), True, session_id
        ))
        
        conn.commit()
        conn.close()
        
        # Retrait des sessions actives
        del self.active_sessions[session_id]
        
        return True
    
    def record_interaction(self, session_id: str, interaction_type: str,
                          object_id: str = None, position: Dict = None,
                          data: Dict = None) -> bool:
        """Enregistre une interaction utilisateur"""
        if session_id not in self.active_sessions:
            return False
        
        if data is None:
            data = {}
        
        interaction = {
            "interaction_id": str(uuid.uuid4()),
            "interaction_type": interaction_type,
            "object_id": object_id,
            "position": position or {"x": 0, "y": 0, "z": 0},
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Ajout à la session
        self.active_sessions[session_id].interactions.append(interaction)
        
        # Sauvegarde en base
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO arvr_interactions
            (interaction_id, session_id, interaction_type, object_id, position, data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            interaction["interaction_id"], session_id, interaction_type,
            object_id, json.dumps(position or {}), json.dumps(data)
        ))
        
        # Mise à jour des interactions de la session
        cursor.execute('''
            UPDATE arvr_sessions
            SET interactions = ?
            WHERE session_id = ?
        ''', (json.dumps(self.active_sessions[session_id].interactions), session_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_scene_content(self, scene_id: str) -> Dict:
        """Récupère le contenu d'une scène"""
        if scene_id not in self.scenes:
            return {}
        
        return self.scenes[scene_id].content
    
    def get_user_sessions(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Récupère les sessions d'un utilisateur"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, sc.name as scene_name, sc.scene_type, sc.difficulty_level
            FROM arvr_sessions s
            JOIN arvr_scenes sc ON s.scene_id = sc.scene_id
            WHERE s.user_id = ?
            ORDER BY s.start_time DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            sessions.append({
                "session_id": row[0],
                "scene_name": row[10],
                "scene_type": row[11],
                "difficulty_level": row[12],
                "start_time": row[4],
                "end_time": row[5],
                "progress_percentage": row[6],
                "score": row[7],
                "completed": bool(row[9])
            })
        
        return sessions
    
    def get_scene_statistics(self, scene_id: str) -> Dict:
        """Récupère les statistiques d'une scène"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Statistiques générales
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sessions,
                AVG(progress_percentage) as avg_progress,
                AVG(score) as avg_score,
                COUNT(CASE WHEN completed = 1 THEN 1 END) as completed_sessions
            FROM arvr_sessions
            WHERE scene_id = ?
        ''', (scene_id,))
        
        stats = cursor.fetchone()
        
        # Sessions récentes
        cursor.execute('''
            SELECT start_time, progress_percentage, score, completed
            FROM arvr_sessions
            WHERE scene_id = ?
            ORDER BY start_time DESC
            LIMIT 10
        ''', (scene_id,))
        
        recent_sessions = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_sessions": stats[0] or 0,
            "average_progress": round(stats[1] or 0, 2),
            "average_score": round(stats[2] or 0, 2),
            "completion_rate": round((stats[3] or 0) / max(1, stats[0] or 1) * 100, 2),
            "recent_sessions": [
                {
                    "start_time": row[0],
                    "progress_percentage": row[1],
                    "score": row[2],
                    "completed": bool(row[3])
                }
                for row in recent_sessions
            ]
        }
    
    def generate_training_report(self, user_id: int, days: int = 30) -> Dict:
        """Génère un rapport de formation AR/VR"""
        since_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                s.scene_id,
                sc.name as scene_name,
                sc.scene_type,
                COUNT(*) as session_count,
                AVG(s.progress_percentage) as avg_progress,
                AVG(s.score) as avg_score,
                COUNT(CASE WHEN s.completed = 1 THEN 1 END) as completed_count
            FROM arvr_sessions s
            JOIN arvr_scenes sc ON s.scene_id = sc.scene_id
            WHERE s.user_id = ? AND s.start_time >= ?
            GROUP BY s.scene_id, sc.name, sc.scene_type
        ''', (user_id, since_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        total_sessions = sum(row[3] for row in rows)
        total_completed = sum(row[6] for row in rows)
        
        return {
            "period": {
                "days": days,
                "start_date": since_date.isoformat(),
                "end_date": datetime.now().isoformat()
            },
            "summary": {
                "total_sessions": total_sessions,
                "completed_sessions": total_completed,
                "completion_rate": round(total_completed / max(1, total_sessions) * 100, 2),
                "average_progress": round(sum(row[4] for row in rows) / max(1, len(rows)), 2),
                "average_score": round(sum(row[5] for row in rows) / max(1, len(rows)), 2)
            },
            "scenes": [
                {
                    "scene_id": row[0],
                    "scene_name": row[1],
                    "scene_type": row[2],
                    "session_count": row[3],
                    "average_progress": round(row[4], 2),
                    "average_score": round(row[5], 2),
                    "completed_count": row[6]
                }
                for row in rows
            ]
        }

# Instance globale
ar_vr_system = QHSEARVRSystem('assistant_qhse_ia/database/qhse.db')
