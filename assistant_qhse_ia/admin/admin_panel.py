"""
Panel d'administration QHSE
Interface de gestion complète pour les administrateurs
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import pandas as pd

class QHSEAdminPanel:
    """Panel d'administration spécialisé QHSE"""
    
    def __init__(self, db_path: str = 'assistant_qhse_ia/database/qhse.db'):
        self.db_path = db_path
        self.admin_features = self.load_admin_features()
    
    def load_admin_features(self) -> Dict:
        """Charge les fonctionnalités d'administration"""
        return {
            'user_management': {
                'name': 'Gestion des Utilisateurs',
                'description': 'Gestion des comptes et permissions',
                'icon': 'bi-people',
                'permissions': ['admin', 'manager']
            },
            'system_config': {
                'name': 'Configuration Système',
                'description': 'Paramètres généraux du système',
                'icon': 'bi-gear',
                'permissions': ['admin']
            },
            'ml_models': {
                'name': 'Modèles IA',
                'description': 'Gestion des modèles d\'intelligence artificielle',
                'icon': 'bi-robot',
                'permissions': ['admin']
            },
            'compliance_management': {
                'name': 'Conformité Réglementaire',
                'description': 'Gestion des réglementations et audits',
                'icon': 'bi-shield-check',
                'permissions': ['admin', 'compliance_manager']
            },
            'training_management': {
                'name': 'Gestion des Formations',
                'description': 'Planification et suivi des formations',
                'icon': 'bi-book',
                'permissions': ['admin', 'training_manager']
            },
            'equipment_management': {
                'name': 'Gestion des Équipements',
                'description': 'Inventaire et inspections d\'équipements',
                'icon': 'bi-tools',
                'permissions': ['admin', 'maintenance_manager']
            },
            'reports_management': {
                'name': 'Gestion des Rapports',
                'description': 'Configuration et planification des rapports',
                'icon': 'bi-file-earmark-text',
                'permissions': ['admin', 'manager']
            },
            'notifications_config': {
                'name': 'Configuration Notifications',
                'description': 'Paramètres des alertes et notifications',
                'icon': 'bi-bell',
                'permissions': ['admin']
            }
        }
    
    def get_system_overview(self) -> Dict:
        """Récupère un aperçu général du système"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Statistiques générales
        stats = {}
        
        # Utilisateurs
        cursor.execute("SELECT COUNT(*) as total, role, COUNT(*) as count FROM users GROUP BY role")
        user_stats = {row['role']: row['count'] for row in cursor.fetchall()}
        stats['users'] = {
            'total': sum(user_stats.values()),
            'by_role': user_stats
        }
        
        # Incidents
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN severity_level = 'critical' THEN 1 END) as critical,
                COUNT(CASE WHEN status = 'open' THEN 1 END) as open,
                COUNT(CASE WHEN created_at > datetime('now', '-7 days') THEN 1 END) as last_week
            FROM incident_reports
        """)
        incident_stats = dict(cursor.fetchone())
        stats['incidents'] = incident_stats
        
        # Formations
        cursor.execute("""
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(DISTINCT tp.user_id) as trained_users,
                COUNT(CASE WHEN tp.status = 'completed' THEN 1 END) as completed
            FROM training_sessions ts
            LEFT JOIN training_participations tp ON ts.id = tp.session_id
            WHERE ts.start_date > datetime('now', '-30 days')
        """)
        training_stats = dict(cursor.fetchone())
        stats['training'] = training_stats
        
        # Workflows
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'overdue' THEN 1 END) as overdue
            FROM qhse_workflows
            WHERE created_at > datetime('now', '-30 days')
        """)
        workflow_stats = dict(cursor.fetchone())
        stats['workflows'] = workflow_stats
        
        # Performance du système
        stats['performance'] = self.get_system_performance()
        
        conn.close()
        
        return stats
    
    def get_system_performance(self) -> Dict:
        """Récupère les métriques de performance du système"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Temps de réponse moyen des API (simulation)
        performance = {
            'api_response_time': 150,  # ms
            'database_size': self.get_database_size(),
            'active_users': self.get_active_users_count(),
            'system_uptime': self.get_system_uptime(),
            'error_rate': 0.02,  # 2%
            'cpu_usage': 45,  # %
            'memory_usage': 68,  # %
            'disk_usage': 23  # %
        }
        
        conn.close()
        return performance
    
    def get_database_size(self) -> str:
        """Calcule la taille de la base de données"""
        import os
        try:
            size_bytes = os.path.getsize(self.db_path)
            size_mb = size_bytes / (1024 * 1024)
            return f"{size_mb:.2f} MB"
        except:
            return "N/A"
    
    def get_active_users_count(self) -> int:
        """Compte les utilisateurs actifs (dernière connexion < 7 jours)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simulation - dans un vrai système, on aurait une table de sessions
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        conn.close()
        return total_users  # Simulation: tous les utilisateurs sont "actifs"
    
    def get_system_uptime(self) -> str:
        """Calcule le temps de fonctionnement du système"""
        # Simulation - dans un vrai système, on trackerait le démarrage
        uptime_hours = 72  # 3 jours
        days = uptime_hours // 24
        hours = uptime_hours % 24
        return f"{days}j {hours}h"
    
    def get_user_management_data(self) -> List[Dict]:
        """Récupère les données de gestion des utilisateurs"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        users = cursor.execute("""
            SELECT 
                u.*,
                COUNT(ir.id) as incident_count,
                COUNT(tp.id) as training_count,
                MAX(ir.created_at) as last_incident
            FROM users u
            LEFT JOIN incident_reports ir ON u.id = ir.user_id
            LEFT JOIN training_participations tp ON u.id = tp.user_id
            GROUP BY u.id
            ORDER BY u.created_at DESC
        """).fetchall()
        
        conn.close()
        
        return [dict(user) for user in users]
    
    def create_user(self, username: str, email: str, password: str, role: str) -> bool:
        """Crée un nouvel utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Vérifier si l'utilisateur existe déjà
            existing = cursor.execute(
                "SELECT id FROM users WHERE username = ? OR email = ?", 
                (username, email)
            ).fetchone()
            
            if existing:
                return False
            
            # Créer l'utilisateur
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            """, (username, email, f"pbkdf2:sha256:260000$hash${password}", role))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Erreur création utilisateur: {e}")
            return False
        finally:
            conn.close()
    
    def update_user_role(self, user_id: int, new_role: str) -> bool:
        """Met à jour le rôle d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE users SET role = ?, updated_at = ? WHERE id = ?",
                (new_role, datetime.now(), user_id)
            )
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            print(f"Erreur mise à jour rôle: {e}")
            return False
        finally:
            conn.close()
    
    def get_ml_models_status(self) -> List[Dict]:
        """Récupère le statut des modèles d'IA"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        models = cursor.execute("""
            SELECT 
                mm.*,
                COUNT(p.id) as prediction_count,
                MAX(p.created_at) as last_prediction
            FROM ml_models mm
            LEFT JOIN predictions p ON mm.id = p.model_id
            GROUP BY mm.id
            ORDER BY mm.training_date DESC
        """).fetchall()
        
        conn.close()
        
        return [dict(model) for model in models]
    
    def retrain_model(self, model_id: int) -> Dict:
        """Relance l'entraînement d'un modèle"""
        # Simulation du processus d'entraînement
        import time
        import random
        
        # Simuler le temps d'entraînement
        training_time = random.randint(30, 120)  # secondes
        
        return {
            'model_id': model_id,
            'status': 'training_started',
            'estimated_time': training_time,
            'started_at': datetime.now().isoformat()
        }
    
    def get_compliance_status(self) -> Dict:
        """Récupère le statut de conformité réglementaire"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Récupérer les réglementations
        regulations = cursor.execute("""
            SELECT 
                r.*,
                COUNT(ca.id) as audit_count,
                MAX(ca.audit_date) as last_audit,
                AVG(ca.score) as avg_score
            FROM regulations r
            LEFT JOIN compliance_audits ca ON r.id = ca.regulation_id
            GROUP BY r.id
            ORDER BY r.name
        """).fetchall()
        
        # Calculer le taux de conformité global
        total_regulations = len(regulations)
        compliant_regulations = len([r for r in regulations if r['avg_score'] and r['avg_score'] >= 80])
        compliance_rate = (compliant_regulations / total_regulations * 100) if total_regulations > 0 else 0
        
        # Audits à venir
        upcoming_audits = cursor.execute("""
            SELECT ca.*, r.name as regulation_name
            FROM compliance_audits ca
            JOIN regulations r ON ca.regulation_id = r.id
            WHERE ca.audit_date > datetime('now')
            ORDER BY ca.audit_date ASC
            LIMIT 5
        """).fetchall()
        
        conn.close()
        
        return {
            'compliance_rate': compliance_rate,
            'total_regulations': total_regulations,
            'compliant_regulations': compliant_regulations,
            'regulations': [dict(reg) for reg in regulations],
            'upcoming_audits': [dict(audit) for audit in upcoming_audits]
        }
    
    def get_training_management_data(self) -> Dict:
        """Récupère les données de gestion des formations"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Formations disponibles
        trainings = cursor.execute("""
            SELECT t.*, COUNT(ts.id) as session_count
            FROM trainings t
            LEFT JOIN training_sessions ts ON t.id = ts.training_id
            GROUP BY t.id
            ORDER BY t.name
        """).fetchall()
        
        # Sessions à venir
        upcoming_sessions = cursor.execute("""
            SELECT 
                ts.*,
                t.name as training_name,
                u.username as instructor_name,
                COUNT(tp.id) as participant_count
            FROM training_sessions ts
            JOIN trainings t ON ts.training_id = t.id
            JOIN users u ON ts.instructor_id = u.id
            LEFT JOIN training_participations tp ON ts.id = tp.session_id
            WHERE ts.start_date > datetime('now')
            GROUP BY ts.id
            ORDER BY ts.start_date ASC
            LIMIT 10
        """).fetchall()
        
        # Statistiques de formation
        stats = cursor.execute("""
            SELECT 
                COUNT(DISTINCT ts.id) as total_sessions,
                COUNT(tp.id) as total_participations,
                COUNT(CASE WHEN tp.status = 'completed' THEN 1 END) as completed,
                AVG(tp.score) as avg_score
            FROM training_sessions ts
            LEFT JOIN training_participations tp ON ts.id = tp.session_id
            WHERE ts.start_date > datetime('now', '-30 days')
        """).fetchone()
        
        conn.close()
        
        return {
            'trainings': [dict(training) for training in trainings],
            'upcoming_sessions': [dict(session) for session in upcoming_sessions],
            'statistics': dict(stats) if stats else {}
        }
    
    def get_equipment_management_data(self) -> Dict:
        """Récupère les données de gestion des équipements"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Équipements
        equipment = cursor.execute("""
            SELECT 
                e.*,
                COUNT(ei.id) as inspection_count,
                MAX(ei.inspection_date) as last_inspection
            FROM equipment e
            LEFT JOIN equipment_inspections ei ON e.id = ei.equipment_id
            GROUP BY e.id
            ORDER BY e.name
        """).fetchall()
        
        # Inspections à venir
        upcoming_inspections = cursor.execute("""
            SELECT 
                e.name as equipment_name,
                e.next_inspection,
                e.category
            FROM equipment e
            WHERE e.next_inspection <= datetime('now', '+30 days')
            ORDER BY e.next_inspection ASC
        """).fetchall()
        
        # Statistiques par catégorie
        category_stats = cursor.execute("""
            SELECT 
                category,
                COUNT(*) as count,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active,
                COUNT(CASE WHEN next_inspection <= datetime('now') THEN 1 END) as overdue
            FROM equipment
            GROUP BY category
        """).fetchall()
        
        conn.close()
        
        return {
            'equipment': [dict(eq) for eq in equipment],
            'upcoming_inspections': [dict(insp) for insp in upcoming_inspections],
            'category_stats': [dict(stat) for stat in category_stats]
        }
    
    def get_notifications_config(self) -> Dict:
        """Récupère la configuration des notifications"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Canaux de notification par utilisateur
        notification_channels = cursor.execute("""
            SELECT 
                nc.*,
                u.username,
                u.role
            FROM notification_channels nc
            JOIN users u ON nc.user_id = u.id
            ORDER BY u.username
        """).fetchall()
        
        # Statistiques des notifications
        notification_stats = cursor.execute("""
            SELECT 
                notification_type,
                priority,
                COUNT(*) as count,
                COUNT(CASE WHEN status = 'read' THEN 1 END) as read_count
            FROM notifications
            WHERE created_at > datetime('now', '-30 days')
            GROUP BY notification_type, priority
        """).fetchall()
        
        conn.close()
        
        return {
            'channels': [dict(channel) for channel in notification_channels],
            'statistics': [dict(stat) for stat in notification_stats]
        }
    
    def update_notification_config(self, user_id: int, channel_type: str, 
                                 channel_value: str, enabled: bool) -> bool:
        """Met à jour la configuration des notifications d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Vérifier si le canal existe
            existing = cursor.execute("""
                SELECT id FROM notification_channels 
                WHERE user_id = ? AND channel_type = ?
            """, (user_id, channel_type)).fetchone()
            
            if existing:
                # Mettre à jour
                cursor.execute("""
                    UPDATE notification_channels 
                    SET channel_value = ?, enabled = ?, created_at = ?
                    WHERE user_id = ? AND channel_type = ?
                """, (channel_value, enabled, datetime.now(), user_id, channel_type))
            else:
                # Créer
                cursor.execute("""
                    INSERT INTO notification_channels 
                    (user_id, channel_type, channel_value, enabled)
                    VALUES (?, ?, ?, ?)
                """, (user_id, channel_type, channel_value, enabled))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Erreur configuration notifications: {e}")
            return False
        finally:
            conn.close()
    
    def get_system_logs(self, limit: int = 100) -> List[Dict]:
        """Récupère les logs du système (simulation)"""
        # Dans un vrai système, on aurait une table de logs
        logs = []
        for i in range(limit):
            logs.append({
                'id': i + 1,
                'timestamp': (datetime.now() - timedelta(minutes=i*5)).isoformat(),
                'level': ['INFO', 'WARNING', 'ERROR'][i % 3],
                'module': ['auth', 'api', 'ml', 'database'][i % 4],
                'message': f'Log message {i + 1}',
                'user_id': (i % 10) + 1 if i % 3 == 0 else None
            })
        
        return logs
    
    def get_admin_dashboard_data(self) -> Dict:
        """Récupère toutes les données pour le tableau de bord admin"""
        return {
            'system_overview': self.get_system_overview(),
            'user_management': self.get_user_management_data(),
            'ml_models': self.get_ml_models_status(),
            'compliance': self.get_compliance_status(),
            'training': self.get_training_management_data(),
            'equipment': self.get_equipment_management_data(),
            'notifications': self.get_notifications_config(),
            'system_logs': self.get_system_logs(20),
            'generated_at': datetime.now().isoformat()
        }
