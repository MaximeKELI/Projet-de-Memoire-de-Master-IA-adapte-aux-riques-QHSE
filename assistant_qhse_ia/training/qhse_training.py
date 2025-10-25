"""
Module de formation et certification QHSE
Gestion des formations, certifications et compétences
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

class QHSETrainingSystem:
    """Système de formation spécialisé QHSE"""
    
    def __init__(self, db_path: str = 'assistant_qhse_ia/database/qhse.db'):
        self.db_path = db_path
        self.training_categories = self.load_training_categories()
        self.certification_rules = self.load_certification_rules()
    
    def load_training_categories(self) -> Dict:
        """Charge les catégories de formation QHSE"""
        return {
            'safety_general': {
                'name': 'Sécurité Générale',
                'description': 'Formations de base en sécurité au travail',
                'mandatory': True,
                'validity_months': 24,
                'sectors': ['all']
            },
            'epi': {
                'name': 'Équipements de Protection Individuelle',
                'description': 'Formation sur l\'utilisation des EPI',
                'mandatory': True,
                'validity_months': 12,
                'sectors': ['Industrie', 'BTP', 'Agroalimentaire']
            },
            'fire_safety': {
                'name': 'Sécurité Incendie',
                'description': 'Formation à la prévention et lutte contre l\'incendie',
                'mandatory': True,
                'validity_months': 12,
                'sectors': ['all']
            },
            'chemical_safety': {
                'name': 'Sécurité Chimique',
                'description': 'Formation à la manipulation des produits chimiques',
                'mandatory': False,
                'validity_months': 24,
                'sectors': ['Industrie', 'Agroalimentaire', 'Santé']
            },
            'height_work': {
                'name': 'Travail en Hauteur',
                'description': 'Formation aux travaux en hauteur et antichute',
                'mandatory': False,
                'validity_months': 36,
                'sectors': ['BTP', 'Industrie']
            },
            'electrical_safety': {
                'name': 'Sécurité Électrique',
                'description': 'Formation aux risques électriques',
                'mandatory': False,
                'validity_months': 24,
                'sectors': ['Industrie', 'BTP']
            },
            'ergonomics': {
                'name': 'Ergonomie',
                'description': 'Formation à la prévention des TMS',
                'mandatory': False,
                'validity_months': 24,
                'sectors': ['all']
            },
            'environmental': {
                'name': 'Environnement',
                'description': 'Formation à la protection de l\'environnement',
                'mandatory': False,
                'validity_months': 36,
                'sectors': ['Industrie', 'Agroalimentaire']
            }
        }
    
    def load_certification_rules(self) -> Dict:
        """Charge les règles de certification QHSE"""
        return {
            'passing_score': 70,  # Score minimum pour valider
            'retry_attempts': 3,  # Nombre de tentatives autorisées
            'certificate_validity': {
                'safety_general': 24,  # mois
                'epi': 12,
                'fire_safety': 12,
                'chemical_safety': 24,
                'height_work': 36,
                'electrical_safety': 24,
                'ergonomics': 24,
                'environmental': 36
            },
            'renewal_requirements': {
                'refresher_training': True,
                'practical_assessment': True,
                'knowledge_test': True
            }
        }
    
    def create_training(self, name: str, description: str, category: str, 
                       duration_hours: int, mandatory: bool = False, 
                       validity_months: int = None) -> int:
        """Crée une nouvelle formation QHSE"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Utiliser la validité par défaut de la catégorie si non spécifiée
        if validity_months is None:
            validity_months = self.training_categories.get(category, {}).get('validity_months', 24)
        
        training_id = cursor.execute("""
            INSERT INTO trainings 
            (name, description, category, duration_hours, mandatory, validity_months)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, description, category, duration_hours, mandatory, validity_months)).lastrowid
        
        conn.commit()
        conn.close()
        
        return training_id
    
    def schedule_training_session(self, training_id: int, instructor_id: int, 
                                start_date: datetime, end_date: datetime, 
                                location: str = None, max_participants: int = None) -> int:
        """Planifie une session de formation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        session_id = cursor.execute("""
            INSERT INTO training_sessions 
            (training_id, instructor_id, start_date, end_date, location, max_participants)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (training_id, instructor_id, start_date, end_date, location, max_participants)).lastrowid
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def enroll_participant(self, session_id: int, user_id: int) -> bool:
        """Inscrit un participant à une session de formation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Vérifier les places disponibles
            session = cursor.execute("""
                SELECT max_participants, COUNT(*) as current_participants
                FROM training_sessions ts
                LEFT JOIN training_participations tp ON ts.id = tp.session_id
                WHERE ts.id = ?
                GROUP BY ts.id
            """, (session_id,)).fetchone()
            
            if session and session['max_participants'] and session['current_participants'] >= session['max_participants']:
                return False  # Plus de places disponibles
            
            # Inscrire le participant
            cursor.execute("""
                INSERT INTO training_participations 
                (session_id, user_id, status)
                VALUES (?, ?, 'enrolled')
            """, (session_id, user_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Erreur lors de l'inscription: {e}")
            return False
        finally:
            conn.close()
    
    def complete_training(self, participation_id: int, score: float, 
                         certificate_number: str = None) -> bool:
        """Marque une formation comme terminée"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Récupérer les informations de la formation
            participation = cursor.execute("""
                SELECT tp.*, t.validity_months, ts.end_date
                FROM training_participations tp
                JOIN training_sessions ts ON tp.session_id = ts.id
                JOIN trainings t ON ts.training_id = t.id
                WHERE tp.id = ?
            """, (participation_id,)).fetchone()
            
            if not participation:
                return False
            
            # Calculer la date d'expiration
            validity_months = participation['validity_months'] or 24
            expiry_date = datetime.now() + timedelta(days=validity_months * 30)
            
            # Générer un numéro de certificat si non fourni
            if not certificate_number:
                certificate_number = f"CERT-{participation_id:06d}-{datetime.now().strftime('%Y%m%d')}"
            
            # Mettre à jour la participation
            cursor.execute("""
                UPDATE training_participations 
                SET status = 'completed', completion_date = ?, score = ?, 
                    certificate_number = ?, expiry_date = ?
                WHERE id = ?
            """, (datetime.now(), score, certificate_number, expiry_date, participation_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Erreur lors de la finalisation: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_certifications(self, user_id: int) -> List[Dict]:
        """Récupère les certifications d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        certifications = cursor.execute("""
            SELECT 
                tp.*,
                t.name as training_name,
                t.category,
                t.validity_months,
                ts.start_date,
                ts.end_date,
                u.username as instructor_name
            FROM training_participations tp
            JOIN training_sessions ts ON tp.session_id = ts.id
            JOIN trainings t ON ts.training_id = t.id
            JOIN users u ON ts.instructor_id = u.id
            WHERE tp.user_id = ? AND tp.status = 'completed'
            ORDER BY tp.completion_date DESC
        """, (user_id,)).fetchall()
        
        conn.close()
        
        return [dict(cert) for cert in certifications]
    
    def get_expiring_certifications(self, days_ahead: int = 30) -> List[Dict]:
        """Récupère les certifications qui expirent bientôt"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        expiry_threshold = datetime.now() + timedelta(days=days_ahead)
        
        expiring = cursor.execute("""
            SELECT 
                tp.*,
                t.name as training_name,
                t.category,
                u.username as employee_name,
                u.email as employee_email
            FROM training_participations tp
            JOIN training_sessions ts ON tp.session_id = ts.id
            JOIN trainings t ON ts.training_id = t.id
            JOIN users u ON tp.user_id = u.id
            WHERE tp.status = 'completed' 
            AND tp.expiry_date <= ?
            AND tp.expiry_date > datetime('now')
            ORDER BY tp.expiry_date ASC
        """, (expiry_threshold,)).fetchall()
        
        conn.close()
        
        return [dict(cert) for cert in expiring]
    
    def get_mandatory_training_status(self, user_id: int, sector: str) -> Dict:
        """Vérifie le statut des formations obligatoires pour un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Récupérer les formations obligatoires pour le secteur
        mandatory_trainings = []
        for category, config in self.training_categories.items():
            if config['mandatory'] and (sector in config['sectors'] or 'all' in config['sectors']):
                mandatory_trainings.append(category)
        
        # Vérifier le statut de chaque formation obligatoire
        status = {}
        for category in mandatory_trainings:
            # Récupérer la dernière formation de cette catégorie
            latest_training = cursor.execute("""
                SELECT tp.*, t.validity_months
                FROM training_participations tp
                JOIN training_sessions ts ON tp.session_id = ts.id
                JOIN trainings t ON ts.training_id = t.id
                WHERE tp.user_id = ? AND t.category = ? AND tp.status = 'completed'
                ORDER BY tp.completion_date DESC
                LIMIT 1
            """, (user_id, category)).fetchone()
            
            if latest_training:
                # Vérifier si la certification est encore valide
                validity_months = latest_training['validity_months'] or 24
                expiry_date = datetime.fromisoformat(latest_training['completion_date']) + timedelta(days=validity_months * 30)
                
                status[category] = {
                    'completed': True,
                    'completion_date': latest_training['completion_date'],
                    'expiry_date': expiry_date.isoformat(),
                    'valid': expiry_date > datetime.now(),
                    'days_until_expiry': (expiry_date - datetime.now()).days if expiry_date > datetime.now() else 0
                }
            else:
                status[category] = {
                    'completed': False,
                    'valid': False,
                    'required': True
                }
        
        conn.close()
        
        return status
    
    def get_training_statistics(self, start_date: str, end_date: str) -> Dict:
        """Récupère les statistiques de formation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Statistiques générales
        total_sessions = cursor.execute("""
            SELECT COUNT(*) FROM training_sessions 
            WHERE start_date BETWEEN ? AND ?
        """, (start_date, end_date)).fetchone()[0]
        
        total_participants = cursor.execute("""
            SELECT COUNT(*) FROM training_participations tp
            JOIN training_sessions ts ON tp.session_id = ts.id
            WHERE ts.start_date BETWEEN ? AND ?
        """, (start_date, end_date)).fetchone()[0]
        
        completed_trainings = cursor.execute("""
            SELECT COUNT(*) FROM training_participations tp
            JOIN training_sessions ts ON tp.session_id = ts.id
            WHERE ts.start_date BETWEEN ? AND ? AND tp.status = 'completed'
        """, (start_date, end_date)).fetchone()[0]
        
        # Répartition par catégorie
        category_stats = cursor.execute("""
            SELECT t.category, COUNT(*) as count
            FROM training_participations tp
            JOIN training_sessions ts ON tp.session_id = ts.id
            JOIN trainings t ON ts.training_id = t.id
            WHERE ts.start_date BETWEEN ? AND ?
            GROUP BY t.category
        """, (start_date, end_date)).fetchall()
        
        # Taux de réussite par catégorie
        success_rates = cursor.execute("""
            SELECT 
                t.category,
                COUNT(*) as total,
                COUNT(CASE WHEN tp.status = 'completed' THEN 1 END) as completed,
                AVG(tp.score) as avg_score
            FROM training_participations tp
            JOIN training_sessions ts ON tp.session_id = ts.id
            JOIN trainings t ON ts.training_id = t.id
            WHERE ts.start_date BETWEEN ? AND ?
            GROUP BY t.category
        """, (start_date, end_date)).fetchall()
        
        conn.close()
        
        return {
            'total_sessions': total_sessions,
            'total_participants': total_participants,
            'completed_trainings': completed_trainings,
            'completion_rate': (completed_trainings / total_participants * 100) if total_participants > 0 else 0,
            'category_breakdown': {row[0]: row[1] for row in category_stats},
            'success_rates': {
                row[0]: {
                    'total': row[1],
                    'completed': row[2],
                    'success_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0,
                    'avg_score': round(row[3], 2) if row[3] else 0
                }
                for row in success_rates
            }
        }
    
    def generate_training_report(self, start_date: str, end_date: str) -> Dict:
        """Génère un rapport de formation complet"""
        stats = self.get_training_statistics(start_date, end_date)
        expiring_certs = self.get_expiring_certifications(30)
        
        # Recommandations basées sur les statistiques
        recommendations = []
        
        if stats['completion_rate'] < 80:
            recommendations.append("Le taux de complétion des formations est faible. Renforcer le suivi des participants.")
        
        if len(expiring_certs) > 10:
            recommendations.append(f"{len(expiring_certs)} certifications expirent dans les 30 jours. Planifier les recyclages.")
        
        # Identifier les catégories avec un faible taux de réussite
        for category, data in stats['success_rates'].items():
            if data['success_rate'] < 70:
                recommendations.append(f"Taux de réussite faible pour {category} ({data['success_rate']:.1f}%). Réviser le contenu de formation.")
        
        return {
            'report_type': 'training_report',
            'generated_at': datetime.now().isoformat(),
            'period': {'start': start_date, 'end': end_date},
            'statistics': stats,
            'expiring_certifications': expiring_certs,
            'recommendations': recommendations
        }
    
    def create_training_plan(self, user_id: int, sector: str) -> Dict:
        """Crée un plan de formation personnalisé pour un utilisateur"""
        mandatory_status = self.get_mandatory_training_status(user_id, sector)
        user_certifications = self.get_user_certifications(user_id)
        
        # Identifier les formations manquantes ou expirées
        missing_trainings = []
        for category, status in mandatory_status.items():
            if not status['completed'] or not status['valid']:
                training_config = self.training_categories[category]
                missing_trainings.append({
                    'category': category,
                    'name': training_config['name'],
                    'description': training_config['description'],
                    'priority': 'high' if status['required'] else 'medium',
                    'validity_months': training_config['validity_months']
                })
        
        # Recommandations de formations optionnelles
        optional_recommendations = []
        for category, config in self.training_categories.items():
            if not config['mandatory'] and sector in config['sectors']:
                # Vérifier si l'utilisateur a déjà cette formation
                has_training = any(cert['category'] == category for cert in user_certifications)
                if not has_training:
                    optional_recommendations.append({
                        'category': category,
                        'name': config['name'],
                        'description': config['description'],
                        'priority': 'low',
                        'validity_months': config['validity_months']
                    })
        
        return {
            'user_id': user_id,
            'sector': sector,
            'mandatory_trainings': missing_trainings,
            'optional_recommendations': optional_recommendations,
            'current_certifications': user_certifications,
            'generated_at': datetime.now().isoformat()
        }
