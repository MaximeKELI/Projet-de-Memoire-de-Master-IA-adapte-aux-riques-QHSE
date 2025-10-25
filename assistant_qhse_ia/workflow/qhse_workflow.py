"""
Système de workflow et approbations QHSE
Gestion des processus d'approbation et d'escalade
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import json

class WorkflowStatus(Enum):
    """Statuts des workflows QHSE"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class WorkflowPriority(Enum):
    """Priorités des workflows QHSE"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class QHSEWorkflowSystem:
    """Système de workflow spécialisé QHSE"""
    
    def __init__(self, db_path: str = 'assistant_qhse_ia/database/qhse.db'):
        self.db_path = db_path
        self.workflow_templates = self.load_workflow_templates()
        self.escalation_rules = self.load_escalation_rules()
    
    def load_workflow_templates(self) -> Dict:
        """Charge les templates de workflow QHSE"""
        return {
            'incident_investigation': {
                'name': 'Investigation d\'Incident',
                'description': 'Processus d\'investigation et de résolution d\'incident',
                'steps': [
                    {'name': 'Signalement', 'role': 'employee', 'duration_hours': 1},
                    {'name': 'Validation', 'role': 'supervisor', 'duration_hours': 4},
                    {'name': 'Investigation', 'role': 'qhse_manager', 'duration_hours': 24},
                    {'name': 'Analyse', 'role': 'qhse_manager', 'duration_hours': 48},
                    {'name': 'Plan d\'action', 'role': 'qhse_manager', 'duration_hours': 72},
                    {'name': 'Approbation', 'role': 'site_manager', 'duration_hours': 24},
                    {'name': 'Mise en œuvre', 'role': 'responsible', 'duration_hours': 168},
                    {'name': 'Vérification', 'role': 'qhse_manager', 'duration_hours': 24}
                ],
                'escalation_triggers': ['overdue', 'rejection', 'critical_severity']
            },
            'corrective_action': {
                'name': 'Action Corrective',
                'description': 'Processus de mise en œuvre d\'action corrective',
                'steps': [
                    {'name': 'Identification', 'role': 'qhse_manager', 'duration_hours': 2},
                    {'name': 'Planification', 'role': 'qhse_manager', 'duration_hours': 24},
                    {'name': 'Approbation', 'role': 'site_manager', 'duration_hours': 48},
                    {'name': 'Exécution', 'role': 'responsible', 'duration_hours': 168},
                    {'name': 'Vérification', 'role': 'qhse_manager', 'duration_hours': 24},
                    {'name': 'Clôture', 'role': 'qhse_manager', 'duration_hours': 2}
                ],
                'escalation_triggers': ['overdue', 'rejection']
            },
            'training_request': {
                'name': 'Demande de Formation',
                'description': 'Processus d\'approbation de demande de formation',
                'steps': [
                    {'name': 'Demande', 'role': 'employee', 'duration_hours': 1},
                    {'name': 'Validation', 'role': 'supervisor', 'duration_hours': 24},
                    {'name': 'Approbation', 'role': 'hr_manager', 'duration_hours': 48},
                    {'name': 'Planification', 'role': 'training_manager', 'duration_hours': 72},
                    {'name': 'Exécution', 'role': 'instructor', 'duration_hours': 8},
                    {'name': 'Validation', 'role': 'instructor', 'duration_hours': 1}
                ],
                'escalation_triggers': ['overdue']
            },
            'equipment_inspection': {
                'name': 'Inspection d\'Équipement',
                'description': 'Processus d\'inspection et de maintenance préventive',
                'steps': [
                    {'name': 'Planification', 'role': 'maintenance_manager', 'duration_hours': 24},
                    {'name': 'Préparation', 'role': 'maintenance_team', 'duration_hours': 4},
                    {'name': 'Inspection', 'role': 'inspector', 'duration_hours': 8},
                    {'name': 'Rapport', 'role': 'inspector', 'duration_hours': 4},
                    {'name': 'Validation', 'role': 'maintenance_manager', 'duration_hours': 24},
                    {'name': 'Actions', 'role': 'maintenance_team', 'duration_hours': 48}
                ],
                'escalation_triggers': ['overdue', 'critical_finding']
            },
            'regulatory_compliance': {
                'name': 'Conformité Réglementaire',
                'description': 'Processus de mise en conformité réglementaire',
                'steps': [
                    {'name': 'Audit', 'role': 'compliance_auditor', 'duration_hours': 40},
                    {'name': 'Analyse', 'role': 'compliance_manager', 'duration_hours': 24},
                    {'name': 'Plan d\'action', 'role': 'compliance_manager', 'duration_hours': 48},
                    {'name': 'Approbation', 'role': 'legal_manager', 'duration_hours': 72},
                    {'name': 'Mise en œuvre', 'role': 'responsible', 'duration_hours': 720},
                    {'name': 'Vérification', 'role': 'compliance_auditor', 'duration_hours': 24},
                    {'name': 'Validation', 'role': 'compliance_manager', 'duration_hours': 24}
                ],
                'escalation_triggers': ['overdue', 'regulatory_deadline']
            }
        }
    
    def load_escalation_rules(self) -> Dict:
        """Charge les règles d'escalade QHSE"""
        return {
            'overdue': {
                'escalation_levels': [
                    {'delay_hours': 24, 'escalate_to': 'supervisor'},
                    {'delay_hours': 72, 'escalate_to': 'manager'},
                    {'delay_hours': 168, 'escalate_to': 'director'}
                ]
            },
            'critical_severity': {
                'immediate_escalation': True,
                'escalate_to': 'emergency_team',
                'notification_channels': ['email', 'sms', 'slack']
            },
            'rejection': {
                'escalate_to': 'next_level_manager',
                'require_justification': True
            },
            'regulatory_deadline': {
                'escalate_to': 'legal_manager',
                'notification_channels': ['email', 'slack']
            }
        }
    
    def create_workflow(self, template_id: str, incident_id: int, priority: str = 'medium') -> int:
        """Crée un nouveau workflow QHSE"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        template = self.workflow_templates[template_id]
        
        # Créer le workflow
        workflow_id = cursor.execute("""
            INSERT INTO qhse_workflows 
            (template_id, incident_id, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (template_id, incident_id, priority, WorkflowStatus.PENDING.value, 
              datetime.now(), datetime.now())).lastrowid
        
        # Créer les étapes du workflow
        for step_order, step in enumerate(template['steps']):
            due_date = datetime.now() + timedelta(hours=step['duration_hours'])
            
            cursor.execute("""
                INSERT INTO workflow_steps 
                (workflow_id, step_order, step_name, assigned_role, status, 
                 due_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (workflow_id, step_order, step['name'], step['role'], 
                  WorkflowStatus.PENDING.value, due_date, datetime.now()))
        
        conn.commit()
        conn.close()
        
        return workflow_id
    
    def get_workflow_status(self, workflow_id: int) -> Dict:
        """Récupère le statut d'un workflow"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Informations du workflow
        workflow = cursor.execute("""
            SELECT w.*, i.title as incident_title, i.severity_level
            FROM qhse_workflows w
            JOIN incident_reports i ON w.incident_id = i.id
            WHERE w.id = ?
        """, (workflow_id,)).fetchone()
        
        # Étapes du workflow
        steps = cursor.execute("""
            SELECT * FROM workflow_steps 
            WHERE workflow_id = ? 
            ORDER BY step_order
        """, (workflow_id,)).fetchall()
        
        # Actions récentes
        actions = cursor.execute("""
            SELECT wa.*, u.username as actor_name
            FROM workflow_actions wa
            JOIN users u ON wa.actor_id = u.id
            WHERE wa.workflow_id = ?
            ORDER BY wa.created_at DESC
            LIMIT 10
        """, (workflow_id,)).fetchall()
        
        conn.close()
        
        return {
            'workflow': dict(workflow) if workflow else None,
            'steps': [dict(step) for step in steps],
            'actions': [dict(action) for action in actions]
        }
    
    def execute_workflow_step(self, workflow_id: int, step_id: int, action: str, 
                            actor_id: int, comment: str = None) -> bool:
        """Exécute une action sur une étape du workflow"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Vérifier que l'étape est en attente
            step = cursor.execute("""
                SELECT * FROM workflow_steps 
                WHERE id = ? AND workflow_id = ? AND status = 'pending'
            """, (step_id, workflow_id)).fetchone()
            
            if not step:
                return False
            
            # Mettre à jour l'étape
            new_status = WorkflowStatus.IN_PROGRESS.value if action == 'start' else action
            cursor.execute("""
                UPDATE workflow_steps 
                SET status = ?, completed_at = ?, updated_at = ?
                WHERE id = ?
            """, (new_status, datetime.now() if action in ['approve', 'reject', 'complete'] else None, 
                  datetime.now(), step_id))
            
            # Enregistrer l'action
            cursor.execute("""
                INSERT INTO workflow_actions 
                (workflow_id, step_id, action, actor_id, comment, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (workflow_id, step_id, action, actor_id, comment, datetime.now()))
            
            # Vérifier si le workflow est terminé
            if action in ['approve', 'complete']:
                self.check_workflow_completion(workflow_id, cursor)
            
            # Vérifier les escalades
            self.check_escalation_rules(workflow_id, cursor)
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Erreur lors de l'exécution de l'étape: {e}")
            return False
        finally:
            conn.close()
    
    def check_workflow_completion(self, workflow_id: int, cursor):
        """Vérifie si un workflow est terminé"""
        # Compter les étapes terminées
        completed_steps = cursor.execute("""
            SELECT COUNT(*) FROM workflow_steps 
            WHERE workflow_id = ? AND status IN ('approved', 'completed')
        """, (workflow_id,)).fetchone()[0]
        
        total_steps = cursor.execute("""
            SELECT COUNT(*) FROM workflow_steps 
            WHERE workflow_id = ?
        """, (workflow_id,)).fetchone()[0]
        
        if completed_steps == total_steps:
            # Marquer le workflow comme terminé
            cursor.execute("""
                UPDATE qhse_workflows 
                SET status = ?, completed_at = ?, updated_at = ?
                WHERE id = ?
            """, (WorkflowStatus.COMPLETED.value, datetime.now(), datetime.now(), workflow_id))
    
    def check_escalation_rules(self, workflow_id: int, cursor):
        """Vérifie les règles d'escalade"""
        # Récupérer les étapes en retard
        overdue_steps = cursor.execute("""
            SELECT ws.*, w.priority, w.template_id
            FROM workflow_steps ws
            JOIN qhse_workflows w ON ws.workflow_id = w.id
            WHERE ws.workflow_id = ? AND ws.status = 'pending' 
            AND ws.due_date < datetime('now')
        """, (workflow_id,)).fetchall()
        
        for step in overdue_steps:
            # Appliquer les règles d'escalade
            self.apply_escalation_rules(workflow_id, dict(step), cursor)
    
    def apply_escalation_rules(self, workflow_id: int, step: Dict, cursor):
        """Applique les règles d'escalade"""
        template_id = step['template_id']
        priority = step['priority']
        
        # Calculer le retard en heures
        delay_hours = (datetime.now() - datetime.fromisoformat(step['due_date'])).total_seconds() / 3600
        
        # Règles d'escalade par retard
        escalation_rules = self.escalation_rules['overdue']['escalation_levels']
        
        for rule in escalation_rules:
            if delay_hours >= rule['delay_hours']:
                # Escalader vers le niveau supérieur
                self.escalate_workflow(workflow_id, rule['escalate_to'], cursor)
                break
    
    def escalate_workflow(self, workflow_id: int, escalate_to: str, cursor):
        """Escalade un workflow vers un niveau supérieur"""
        # Enregistrer l'escalade
        cursor.execute("""
            INSERT INTO workflow_escalations 
            (workflow_id, escalated_to, escalated_at, reason)
            VALUES (?, ?, ?, ?)
        """, (workflow_id, escalate_to, datetime.now(), 'overdue'))
        
        # Mettre à jour le statut du workflow
        cursor.execute("""
            UPDATE qhse_workflows 
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (WorkflowStatus.ESCALATED.value, datetime.now(), workflow_id))
        
        # Notifier les responsables
        self.notify_escalation(workflow_id, escalate_to)
    
    def notify_escalation(self, workflow_id: int, escalate_to: str):
        """Notifie les responsables de l'escalade"""
        print(f"🚨 ESCALADE QHSE - Workflow {workflow_id} escaladé vers {escalate_to}")
        # Ici vous intégreriez le système de notifications
    
    def get_user_workflows(self, user_id: int, role: str) -> List[Dict]:
        """Récupère les workflows d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Workflows assignés à l'utilisateur
        workflows = cursor.execute("""
            SELECT DISTINCT w.*, i.title as incident_title, i.severity_level
            FROM qhse_workflows w
            JOIN incident_reports i ON w.incident_id = i.id
            JOIN workflow_steps ws ON w.id = ws.workflow_id
            WHERE ws.assigned_role = ? AND ws.status = 'pending'
            ORDER BY w.priority DESC, w.created_at ASC
        """, (role,)).fetchall()
        
        conn.close()
        
        return [dict(workflow) for workflow in workflows]
    
    def get_workflow_metrics(self, start_date: str, end_date: str) -> Dict:
        """Récupère les métriques des workflows"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Métriques générales
        total_workflows = cursor.execute("""
            SELECT COUNT(*) FROM qhse_workflows 
            WHERE created_at BETWEEN ? AND ?
        """, (start_date, end_date)).fetchone()[0]
        
        completed_workflows = cursor.execute("""
            SELECT COUNT(*) FROM qhse_workflows 
            WHERE created_at BETWEEN ? AND ? AND status = 'completed'
        """, (start_date, end_date)).fetchone()[0]
        
        overdue_workflows = cursor.execute("""
            SELECT COUNT(DISTINCT w.id) FROM qhse_workflows w
            JOIN workflow_steps ws ON w.id = ws.workflow_id
            WHERE w.created_at BETWEEN ? AND ? 
            AND ws.status = 'pending' AND ws.due_date < datetime('now')
        """, (start_date, end_date)).fetchone()[0]
        
        # Temps moyen de traitement
        avg_processing_time = cursor.execute("""
            SELECT AVG(julianday(completed_at) - julianday(created_at)) * 24
            FROM qhse_workflows 
            WHERE created_at BETWEEN ? AND ? AND status = 'completed'
        """, (start_date, end_date)).fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_workflows': total_workflows,
            'completed_workflows': completed_workflows,
            'overdue_workflows': overdue_workflows,
            'completion_rate': (completed_workflows / total_workflows * 100) if total_workflows > 0 else 0,
            'average_processing_time_hours': round(avg_processing_time, 2)
        }
