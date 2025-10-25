"""
Script d'initialisation de la base de données SQLite
Créé les tables et insère les données de base
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random
import json

def init_database():
    """Initialise la base de données avec le schéma et les données de base"""
    
    # Créer le dossier database s'il n'existe pas
    os.makedirs('assistant_qhse_ia/database', exist_ok=True)
    
    # Connexion à la base de données
    conn = sqlite3.connect('assistant_qhse_ia/database/qhse.db')
    cursor = conn.cursor()
    
    # Lire et exécuter le schéma
    with open('assistant_qhse_ia/database/schema.sql', 'r', encoding='utf-8') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    # Insérer les données de base
    insert_base_data(cursor)
    
    # Générer des données de démonstration
    generate_demo_data(cursor)
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée avec succès!")

def insert_base_data(cursor):
    """Insère les données de base nécessaires au fonctionnement"""
    
    # Secteurs d'activité
    sectors = [
        ('Industrie', 'Secteur industriel avec risques mécaniques et chimiques', 'high'),
        ('BTP', 'Bâtiment et Travaux Publics - risques de chute et TMS', 'high'),
        ('Agroalimentaire', 'Production alimentaire - risques biologiques et chimiques', 'medium'),
        ('Transport', 'Transport et logistique - risques routiers et manutention', 'medium'),
        ('Santé', 'Santé et services sociaux - risques biologiques et ergonomiques', 'medium'),
        ('Commerce', 'Commerce et distribution - risques de manutention', 'low'),
        ('Bureaux', 'Travail de bureau - risques ergonomiques', 'low')
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO sectors (name, description, risk_level) VALUES (?, ?, ?)",
        sectors
    )
    
    # Types d'incidents
    incident_types = [
        ('Chute de plain-pied', 'physical', 3, 'Chute sur le même niveau'),
        ('Chute de hauteur', 'physical', 5, 'Chute depuis une hauteur > 1m'),
        ('Incendie', 'physical', 5, 'Départ de feu ou explosion'),
        ('Électrocution', 'physical', 4, 'Contact avec courant électrique'),
        ('Coupure', 'physical', 2, 'Blessure par outil tranchant'),
        ('TMS', 'ergonomic', 3, 'Trouble musculo-squelettique'),
        ('Inhalation', 'chemical', 4, 'Inhalation de substances toxiques'),
        ('Contact chimique', 'chemical', 3, 'Contact cutané avec produits chimiques'),
        ('Stress', 'psychosocial', 2, 'Stress au travail'),
        ('Harcèlement', 'psychosocial', 4, 'Harcèlement moral ou sexuel'),
        ('Accident de trajet', 'physical', 3, 'Accident sur le trajet domicile-travail'),
        ('Autre', 'other', 1, 'Autre type d\'incident')
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO incident_types (name, category, severity_weight, description) VALUES (?, ?, ?, ?)",
        incident_types
    )
    
    # Utilisateur admin par défaut
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ('admin', 'admin@qhse.com', 'pbkdf2:sha256:260000$hash$admin', 'admin')
    )
    
    # Modèle d'IA par défaut
    cursor.execute(
        "INSERT OR IGNORE INTO ml_models (name, version, model_type, file_path, accuracy_score, is_active) VALUES (?, ?, ?, ?, ?, ?)",
        ('risk_classifier', '1.0', 'classification', 'assistant_qhse_ia/modeles/risk_classifier.joblib', 0.85, True)
    )

def generate_demo_data(cursor):
    """Génère des données de démonstration réalistes"""
    
    # Récupérer les IDs des secteurs et types d'incidents
    cursor.execute("SELECT id FROM sectors")
    sector_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM incident_types")
    incident_type_ids = [row[0] for row in cursor.fetchall()]
    
    # Générer des rapports d'incidents sur les 6 derniers mois
    start_date = datetime.now() - timedelta(days=180)
    
    for i in range(50):  # 50 incidents de démonstration
        # Date aléatoire dans les 6 derniers mois
        days_ago = random.randint(0, 180)
        incident_date = start_date + timedelta(days=days_ago)
        
        # Heure aléatoire de travail (6h-18h)
        incident_time = f"{random.randint(6, 18):02d}:{random.randint(0, 59):02d}"
        
        # Sélection aléatoire
        sector_id = random.choice(sector_ids)
        incident_type_id = random.choice(incident_type_ids)
        
        # Niveaux de sévérité avec distribution réaliste
        severity_weights = ['low'] * 20 + ['medium'] * 15 + ['high'] * 10 + ['critical'] * 5
        severity = random.choice(severity_weights)
        
        # Score de probabilité basé sur la sévérité
        if severity == 'low':
            probability = random.uniform(0.1, 0.3)
        elif severity == 'medium':
            probability = random.uniform(0.3, 0.6)
        elif severity == 'high':
            probability = random.uniform(0.6, 0.8)
        else:  # critical
            probability = random.uniform(0.8, 1.0)
        
        # Calcul du score de risque (probabilité * poids de sévérité)
        cursor.execute("SELECT severity_weight FROM incident_types WHERE id = ?", (incident_type_id,))
        severity_weight = cursor.fetchone()[0]
        risk_score = probability * severity_weight
        
        # Titre et description
        titles = [
            f"Incident {severity} dans le secteur {sector_id}",
            f"Rapport d'urgence - {severity}",
            f"Signalement {severity} - Action requise",
            f"Incident {severity} - Investigation en cours"
        ]
        
        descriptions = [
            "Incident signalé par un employé. Investigation en cours.",
            "Situation nécessitant une intervention immédiate.",
            "Risque identifié nécessitant des mesures correctives.",
            "Incident mineur mais nécessitant un suivi.",
            "Situation critique nécessitant une action urgente."
        ]
        
        locations = [
            "Atelier principal", "Bureau 1er étage", "Chantier A", "Laboratoire",
            "Entrepôt", "Zone de production", "Parking", "Salle de réunion",
            "Cuisine", "Couloir principal", "Escalier", "Ascenseur"
        ]
        
        # Statuts avec distribution réaliste
        status_weights = ['open'] * 10 + ['in_progress'] * 15 + ['resolved'] * 20 + ['closed'] * 5
        status = random.choice(status_weights)
        
        # Recommandations IA simulées
        ai_recommendations = [
            "Formation supplémentaire recommandée pour l'équipe concernée.",
            "Mise en place d'EPI supplémentaires nécessaire.",
            "Révision des procédures de sécurité requise.",
            "Inspection approfondie de l'équipement recommandée.",
            "Sensibilisation des employés à ce type de risque nécessaire."
        ]
        
        cursor.execute("""
            INSERT INTO incident_reports 
            (user_id, sector_id, incident_type_id, title, description, location, 
             date_incident, time_incident, severity_level, probability_score, 
             risk_score, status, ai_recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1,  # admin user
            sector_id,
            incident_type_id,
            random.choice(titles),
            random.choice(descriptions),
            random.choice(locations),
            incident_date.date(),
            incident_time,
            severity,
            probability,
            risk_score,
            status,
            random.choice(ai_recommendations)
        ))
    
    # Générer des actions correctives pour certains incidents
    cursor.execute("SELECT id FROM incident_reports WHERE severity_level IN ('high', 'critical')")
    high_risk_incidents = [row[0] for row in cursor.fetchall()]
    
    for incident_id in high_risk_incidents[:10]:  # Actions pour 10 incidents à haut risque
        actions = [
            ("Formation sécurité", "Organiser une session de formation pour l'équipe concernée", "high", "pending"),
            ("Inspection équipement", "Vérifier et réparer l'équipement défaillant", "urgent", "in_progress"),
            ("Mise à jour procédures", "Réviser les procédures de sécurité existantes", "medium", "pending"),
            ("Installation EPI", "Installer de nouveaux équipements de protection", "high", "pending"),
            ("Sensibilisation", "Lancer une campagne de sensibilisation", "low", "completed")
        ]
        
        action = random.choice(actions)
        due_date = datetime.now() + timedelta(days=random.randint(1, 30))
        
        cursor.execute("""
            INSERT INTO corrective_actions 
            (incident_id, title, description, priority, assigned_to, due_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            incident_id,
            action[0],
            action[1],
            action[2],
            1,  # admin user
            due_date.date(),
            action[3]
        ))
    
    # Générer des statistiques
    generate_statistics(cursor)

def generate_statistics(cursor):
    """Génère des statistiques de démonstration"""
    
    # Statistiques des 6 derniers mois
    for month in range(6):
        month_date = datetime.now() - timedelta(days=30 * month)
        period_start = month_date.replace(day=1)
        period_end = month_date.replace(day=28)
        
        # Nombre total d'incidents
        cursor.execute("""
            SELECT COUNT(*) FROM incident_reports 
            WHERE date_incident BETWEEN ? AND ?
        """, (period_start.date(), period_end.date()))
        total_incidents = cursor.fetchone()[0]
        
        # Incidents par sévérité
        for severity in ['low', 'medium', 'high', 'critical']:
            cursor.execute("""
                SELECT COUNT(*) FROM incident_reports 
                WHERE date_incident BETWEEN ? AND ? AND severity_level = ?
            """, (period_start.date(), period_end.date(), severity))
            count = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO statistics (metric_name, metric_value, metric_type, period_start, period_end)
                VALUES (?, ?, ?, ?, ?)
            """, (f'incidents_{severity}', count, 'count', period_start.date(), period_end.date()))
        
        # Taux de résolution
        cursor.execute("""
            SELECT COUNT(*) FROM incident_reports 
            WHERE date_incident BETWEEN ? AND ? AND status IN ('resolved', 'closed')
        """, (period_start.date(), period_end.date()))
        resolved = cursor.fetchone()[0]
        
        resolution_rate = (resolved / total_incidents * 100) if total_incidents > 0 else 0
        
        cursor.execute("""
            INSERT INTO statistics (metric_name, metric_value, metric_type, period_start, period_end)
            VALUES (?, ?, ?, ?, ?)
        """, ('resolution_rate', resolution_rate, 'percentage', period_start.date(), period_end.date()))

if __name__ == "__main__":
    init_database()
