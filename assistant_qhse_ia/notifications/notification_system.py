"""
Système de notifications QHSE en temps réel
Gestion des alertes, escalades et communications d'urgence
"""

import smtplib
import sqlite3
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask
import json
import requests
from typing import List, Dict, Optional

class QHSENotificationSystem:
    """Système de notifications spécialisé QHSE"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.db_path = 'assistant_qhse_ia/database/qhse.db'
        self.notification_rules = self.load_notification_rules()
        
    def load_notification_rules(self) -> Dict:
        """Charge les règles de notification QHSE"""
        return {
            'critical_incident': {
                'immediate': True,
                'channels': ['email', 'sms', 'slack'],
                'recipients': ['qhse_manager', 'site_manager', 'emergency_team'],
                'template': 'critical_incident_alert'
            },
            'high_risk': {
                'immediate': True,
                'channels': ['email', 'slack'],
                'recipients': ['qhse_manager', 'site_manager'],
                'template': 'high_risk_alert'
            },
            'regulatory_deadline': {
                'immediate': False,
                'channels': ['email'],
                'recipients': ['compliance_team'],
                'template': 'regulatory_deadline_reminder'
            },
            'training_expiry': {
                'immediate': False,
                'channels': ['email'],
                'recipients': ['hr_team', 'employee'],
                'template': 'training_expiry_warning'
            },
            'equipment_inspection': {
                'immediate': False,
                'channels': ['email'],
                'recipients': ['maintenance_team'],
                'template': 'equipment_inspection_due'
            }
        }
    
    def send_critical_incident_alert(self, incident_data: Dict):
        """Envoie une alerte d'incident critique"""
        severity = incident_data.get('severity_level', 'unknown')
        location = incident_data.get('location', 'Non spécifié')
        incident_type = incident_data.get('incident_type_name', 'Inconnu')
        
        # Message d'urgence QHSE
        subject = f"🚨 ALERTE QHSE CRITIQUE - {severity.upper()}"
        message = f"""
        INCIDENT CRITIQUE SIGNALÉ
        
        ⚠️  NIVEAU: {severity.upper()}
        📍 LOCALISATION: {location}
        🔧 TYPE: {incident_type}
        ⏰ HEURE: {datetime.now().strftime('%H:%M')}
        
        ACTIONS IMMÉDIATES REQUISES:
        1. Sécuriser la zone
        2. Évacuer si nécessaire
        3. Alerter les secours
        4. Prévenir la direction
        
        Consultez le système QHSE pour plus de détails.
        """
        
        self.send_notification('critical_incident', subject, message, incident_data)
    
    def send_high_risk_alert(self, incident_data: Dict):
        """Envoie une alerte de risque élevé"""
        risk_score = incident_data.get('risk_score', 0)
        recommendations = incident_data.get('ai_recommendations', '')
        
        subject = f"⚠️ RISQUE ÉLEVÉ DÉTECTÉ - Score: {risk_score:.2f}"
        message = f"""
        RISQUE ÉLEVÉ IDENTIFIÉ
        
        📊 Score de risque: {risk_score:.2f}
        🤖 Recommandations IA:
        {recommendations}
        
        Actions recommandées:
        - Formation immédiate de l'équipe
        - Vérification des EPI
        - Révision des procédures
        - Surveillance renforcée
        """
        
        self.send_notification('high_risk', subject, message, incident_data)
    
    def send_regulatory_deadline_reminder(self, deadline_data: Dict):
        """Rappel de délai réglementaire"""
        regulation = deadline_data.get('regulation_name', 'Réglementation')
        deadline = deadline_data.get('deadline', '')
        days_left = deadline_data.get('days_left', 0)
        
        subject = f"📋 RAPPEL RÉGLEMENTAIRE - {regulation}"
        message = f"""
        DÉLAI RÉGLEMENTAIRE APPROCHANT
        
        📋 Réglementation: {regulation}
        📅 Échéance: {deadline}
        ⏰ Jours restants: {days_left}
        
        Actions requises:
        - Préparer la documentation
        - Planifier l'audit si nécessaire
        - Mettre à jour les procédures
        - Former les équipes
        """
        
        self.send_notification('regulatory_deadline', subject, message, deadline_data)
    
    def send_training_expiry_warning(self, training_data: Dict):
        """Avertissement d'expiration de formation"""
        employee = training_data.get('employee_name', 'Employé')
        training = training_data.get('training_name', 'Formation')
        expiry_date = training_data.get('expiry_date', '')
        
        subject = f"🎓 FORMATION QHSE - Expiration proche"
        message = f"""
        FORMATION QHSE À RENOUVELER
        
        👤 Employé: {employee}
        📚 Formation: {training}
        📅 Expiration: {expiry_date}
        
        Actions requises:
        - Planifier la formation de recyclage
        - Bloquer les accès si nécessaire
        - Mettre à jour les compétences
        """
        
        self.send_notification('training_expiry', subject, message, training_data)
    
    def send_equipment_inspection_due(self, equipment_data: Dict):
        """Rappel d'inspection d'équipement"""
        equipment = equipment_data.get('equipment_name', 'Équipement')
        inspection_type = equipment_data.get('inspection_type', 'Inspection')
        due_date = equipment_data.get('due_date', '')
        
        subject = f"🔧 INSPECTION ÉQUIPEMENT - {equipment}"
        message = f"""
        INSPECTION D'ÉQUIPEMENT REQUISE
        
        🔧 Équipement: {equipment}
        📋 Type: {inspection_type}
        📅 Échéance: {due_date}
        
        Actions requises:
        - Planifier l'inspection
        - Préparer la documentation
        - Former l'inspecteur
        - Mettre à jour les registres
        """
        
        self.send_notification('equipment_inspection', subject, message, equipment_data)
    
    def send_notification(self, notification_type: str, subject: str, message: str, data: Dict):
        """Envoie une notification via les canaux configurés"""
        rules = self.notification_rules.get(notification_type, {})
        
        # Récupérer les destinataires
        recipients = self.get_recipients(rules.get('recipients', []), data)
        
        # Envoyer via les canaux configurés
        for channel in rules.get('channels', ['email']):
            if channel == 'email':
                self.send_email(recipients, subject, message)
            elif channel == 'sms':
                self.send_sms(recipients, message)
            elif channel == 'slack':
                self.send_slack(recipients, subject, message)
    
    def get_recipients(self, recipient_types: List[str], data: Dict) -> List[Dict]:
        """Récupère les destinataires selon leur type"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        recipients = []
        
        for recipient_type in recipient_types:
            if recipient_type == 'qhse_manager':
                cursor.execute("SELECT email, name FROM users WHERE role = 'admin'")
                for row in cursor.fetchall():
                    recipients.append({'email': row['email'], 'name': row['name'], 'type': 'QHSE Manager'})
            
            elif recipient_type == 'site_manager':
                cursor.execute("SELECT email, name FROM users WHERE role = 'manager'")
                for row in cursor.fetchall():
                    recipients.append({'email': row['email'], 'name': row['name'], 'type': 'Site Manager'})
            
            elif recipient_type == 'employee' and 'user_id' in data:
                cursor.execute("SELECT email, name FROM users WHERE id = ?", (data['user_id'],))
                row = cursor.fetchone()
                if row:
                    recipients.append({'email': row['email'], 'name': row['name'], 'type': 'Employee'})
        
        conn.close()
        return recipients
    
    def send_email(self, recipients: List[Dict], subject: str, message: str):
        """Envoie un email (simulation - à configurer avec un vrai SMTP)"""
        print(f"📧 EMAIL ENVOYÉ:")
        print(f"   Sujet: {subject}")
        print(f"   Destinataires: {[r['email'] for r in recipients]}")
        print(f"   Message: {message[:100]}...")
        
        # Ici vous intégreriez un vrai service SMTP
        # smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        # smtp_server.starttls()
        # smtp_server.login('your_email', 'your_password')
        # smtp_server.sendmail('from_email', recipient_emails, message)
    
    def send_sms(self, recipients: List[Dict], message: str):
        """Envoie un SMS (simulation - à intégrer avec un service SMS)"""
        print(f"📱 SMS ENVOYÉ:")
        print(f"   Destinataires: {[r['email'] for r in recipients]}")
        print(f"   Message: {message[:50]}...")
    
    def send_slack(self, recipients: List[Dict], subject: str, message: str):
        """Envoie une notification Slack (simulation)"""
        print(f"💬 SLACK NOTIFICATION:")
        print(f"   Canal: #qhse-alerts")
        print(f"   Sujet: {subject}")
        print(f"   Message: {message[:100]}...")
    
    def check_and_send_notifications(self):
        """Vérifie et envoie les notifications programmées"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Vérifier les incidents critiques récents
        recent_critical = cursor.execute("""
            SELECT ir.*, s.name as sector_name, it.name as incident_type_name
            FROM incident_reports ir
            JOIN sectors s ON ir.sector_id = s.id
            JOIN incident_types it ON ir.incident_type_id = it.id
            WHERE ir.severity_level = 'critical' 
            AND ir.created_at > datetime('now', '-1 hour')
        """).fetchall()
        
        for incident in recent_critical:
            self.send_critical_incident_alert(dict(incident))
        
        # Vérifier les risques élevés
        high_risk = cursor.execute("""
            SELECT ir.*, s.name as sector_name, it.name as incident_type_name
            FROM incident_reports ir
            JOIN sectors s ON ir.sector_id = s.id
            JOIN incident_types it ON ir.incident_type_id = it.id
            WHERE ir.risk_score > 3.0 
            AND ir.created_at > datetime('now', '-2 hours')
        """).fetchall()
        
        for incident in high_risk:
            self.send_high_risk_alert(dict(incident))
        
        conn.close()

# Intégration avec Flask
def init_notification_system(app: Flask):
    """Initialise le système de notifications avec Flask"""
    notification_system = QHSENotificationSystem(app)
    
    @app.before_request
    def check_notifications():
        """Vérifie les notifications avant chaque requête"""
        notification_system.check_and_send_notifications()
    
    return notification_system
