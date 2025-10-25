"""
Application Flask simplifiée pour l'Assistant QHSE IA
Version de démonstration sans modules avancés
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime, timedelta
import hashlib
import secrets
from functools import wraps
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pandas as pd

# Configuration de l'application
app = Flask(__name__)
app.secret_key = 'qhse_secret_key_2024'
CORS(app)

# Configuration de la base de données
DATABASE = 'assistant_qhse_ia/database/qhse.db'

def get_db_connection():
    """Crée une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    """Décorateur pour les routes nécessitant une authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES PRINCIPALES ====================

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Connexion réussie!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord principal"""
    conn = get_db_connection()
    
    # Statistiques générales
    stats = {}
    
    # Nombre total d'incidents
    stats['total_incidents'] = conn.execute('SELECT COUNT(*) FROM incident_reports').fetchone()[0]
    
    # Incidents par sévérité
    severity_counts = conn.execute('''
        SELECT severity_level, COUNT(*) as count 
        FROM incident_reports 
        GROUP BY severity_level
    ''').fetchall()
    
    stats['severity_breakdown'] = {row['severity_level']: row['count'] for row in severity_counts}
    
    # Incidents récents (7 derniers jours)
    recent_incidents = conn.execute('''
        SELECT COUNT(*) FROM incident_reports 
        WHERE created_at >= datetime('now', '-7 days')
    ''').fetchone()[0]
    stats['recent_incidents'] = recent_incidents
    
    conn.close()
    
    return render_template('dashboard.html', stats=stats)

@app.route('/dashboard_animated')
@login_required
def dashboard_animated():
    """Tableau de bord avec animations avancées"""
    return render_template('dashboard_animated.html')

@app.route('/login_animated')
def login_animated():
    """Page de connexion avec animations"""
    return render_template('login_animated.html')

@app.route('/form')
@login_required
def form():
    """Formulaire d'analyse de risque"""
    conn = get_db_connection()
    
    # Récupérer les secteurs et types d'incidents
    sectors = conn.execute('SELECT * FROM sectors ORDER BY name').fetchall()
    incident_types = conn.execute('SELECT * FROM incident_types ORDER BY name').fetchall()
    
    conn.close()
    
    return render_template('form.html', sectors=sectors, incident_types=incident_types)

@app.route('/form_animated')
@login_required
def form_animated():
    """Formulaire d'analyse avec animations"""
    # Récupérer les données pour les dropdowns
    conn = get_db_connection()
    sectors = conn.execute('SELECT id, name FROM sectors ORDER BY name').fetchall()
    incident_types = conn.execute('SELECT id, name FROM incident_types ORDER BY name').fetchall()
    conn.close()
    
    return render_template('form_animated.html', 
                         sectors=sectors, 
                         incident_types=incident_types)

@app.route('/chatbot')
@login_required
def chatbot():
    """Interface chatbot"""
    return render_template('chatbot.html')

@app.route('/conseils')
@login_required
def conseils():
    """Page de conseils IA"""
    conn = get_db_connection()
    
    # Récupérer les incidents à haut risque
    high_risk_incidents = conn.execute('''
        SELECT * FROM incident_reports 
        WHERE severity_level IN ('high', 'critical')
        ORDER BY created_at DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('conseil_IA.html', incidents=high_risk_incidents)

# ==================== API ENDPOINTS ====================

@app.route('/api/incidents', methods=['GET'])
@login_required
def get_incidents():
    """Récupère la liste des incidents"""
    conn = get_db_connection()
    
    incidents = conn.execute('''
        SELECT ir.*, s.name as sector_name, it.name as incident_type_name
        FROM incident_reports ir
        LEFT JOIN sectors s ON ir.sector_id = s.id
        LEFT JOIN incident_types it ON ir.incident_type_id = it.id
        ORDER BY ir.created_at DESC
    ''').fetchall()
    
    conn.close()
    
    return jsonify([dict(incident) for incident in incidents])

@app.route('/api/incidents', methods=['POST'])
@login_required
def create_incident():
    """Crée un nouvel incident"""
    data = request.get_json()
    
    conn = get_db_connection()
    
    conn.execute('''
        INSERT INTO incident_reports 
        (title, description, location, severity_level, sector_id, incident_type_id, 
         probability_score, time_incident, ai_recommendations, user_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('title'),
        data.get('description'),
        data.get('location'),
        data.get('severity_level'),
        data.get('sector_id'),
        data.get('incident_type_id'),
        data.get('probability_score'),
        data.get('time_incident'),
        data.get('ai_recommendations'),
        session['user_id'],
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Incident créé avec succès'})

@app.route('/api/predict', methods=['POST'])
@login_required
def predict_risk():
    """Prédiction de risque avec IA"""
    data = request.get_json()
    
    # Simulation simple de prédiction
    features = prepare_features(data)
    
    # Calculer un score de risque basique
    risk_score = calculate_risk_score(features)
    
    # Déterminer le niveau de risque
    if risk_score < 0.3:
        prediction = 'low'
    elif risk_score < 0.6:
        prediction = 'medium'
    elif risk_score < 0.8:
        prediction = 'high'
    else:
        prediction = 'critical'
    
    # Générer des recommandations
    recommendations = generate_recommendations(prediction, data)
    
    return jsonify({
        'prediction': prediction,
        'risk_score': risk_score,
        'recommendations': recommendations
    })

@app.route('/api/chatbot', methods=['POST'])
@login_required
def chatbot_response():
    """Réponse du chatbot"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    # Réponses prédéfinies simples
    responses = {
        'incendie': "En cas d'incendie, suivez la procédure : 1) Activez l'alarme, 2) Évacuez immédiatement, 3) Composez le 18.",
        'chute': "Pour éviter les chutes, portez des chaussures antidérapantes et vérifiez les surfaces de travail.",
        'coupure': "En cas de coupure, arrêtez le saignement et consultez un médecin si nécessaire.",
        'sécurité': "La sécurité est notre priorité. Respectez toujours les procédures et portez les EPI."
    }
    
    # Recherche de mots-clés
    response_text = "Je suis là pour vous aider avec vos questions de sécurité. Pouvez-vous être plus spécifique ?"
    
    for keyword, response in responses.items():
        if keyword.lower() in user_message.lower():
            response_text = response
            break
    
    return jsonify({
        'response': response_text,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/statistics')
@login_required
def get_statistics():
    """Récupère les statistiques pour le dashboard"""
    conn = get_db_connection()
    
    # Statistiques par secteur
    by_sector = conn.execute('''
        SELECT s.name, COUNT(ir.id) as count
        FROM sectors s
        LEFT JOIN incident_reports ir ON s.id = ir.sector_id
        GROUP BY s.id, s.name
        ORDER BY count DESC
    ''').fetchall()
    
    # Statistiques par type d'incident
    by_type = conn.execute('''
        SELECT it.name, COUNT(ir.id) as count
        FROM incident_types it
        LEFT JOIN incident_reports ir ON it.id = ir.incident_type_id
        GROUP BY it.id, it.name
        ORDER BY count DESC
    ''').fetchall()
    
    # Tendances mensuelles
    monthly_trend = conn.execute('''
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
        FROM incident_reports
        WHERE created_at >= datetime('now', '-12 months')
        GROUP BY strftime('%Y-%m', created_at)
        ORDER BY month
    ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'by_sector': [dict(row) for row in by_sector],
        'by_type': [dict(row) for row in by_type],
        'monthly_trend': [dict(row) for row in monthly_trend]
    })

@app.route('/api/dashboard/advanced-stats', methods=['GET'])
@login_required
def get_advanced_dashboard_stats():
    """Récupère les statistiques avancées du tableau de bord"""
    try:
        conn = get_db_connection()
        total_incidents = conn.execute('SELECT COUNT(*) FROM incident_reports').fetchone()[0]
        conn.close()
        
        return jsonify({
            # Données attendues par le frontend animé
            'incidents': total_incidents,
            'sensors': 15,  # Simulation
            'points': 1250,  # Simulation
            'blocks': 156,  # Simulation
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== FONCTIONS UTILITAIRES ====================

def check_password_hash(password_hash, password):
    """Vérifie le mot de passe (version simplifiée)"""
    # Dans un vrai projet, utiliser bcrypt ou similar
    return password_hash == f"pbkdf2:sha256:260000$hash${password}"

def prepare_features(data):
    """Prépare les features pour le modèle d'IA"""
    features = []
    
    # Sector encoding
    sector_mapping = {'Industrie': 1, 'BTP': 2, 'Agroalimentaire': 3, 'Transport': 4, 'Santé': 5, 'Commerce': 6, 'Bureaux': 7}
    features.append(sector_mapping.get(data.get('sector', 'Bureaux'), 7))
    
    # Incident type encoding
    incident_mapping = {'Chute': 1, 'Incendie': 2, 'Électrocution': 3, 'Coupure': 4, 'TMS': 5, 'Inhalation': 6, 'Autre': 7}
    features.append(incident_mapping.get(data.get('incident_type', 'Autre'), 7))
    
    # Probability score
    features.append(data.get('probability_score', 0.5))
    
    # Time of day (extract hour from time)
    time_str = data.get('time_incident', '12:00')
    hour = int(time_str.split(':')[0])
    features.append(hour)
    
    return features

def calculate_risk_score(features):
    """Calcule un score de risque basique"""
    # Score basé sur les features
    base_score = 0.3
    
    # Ajustements selon les features
    if features[0] in [1, 2]:  # Industrie, BTP
        base_score += 0.2
    if features[1] in [2, 3]:  # Incendie, Électrocution
        base_score += 0.3
    if features[2] > 0.7:  # Probabilité élevée
        base_score += 0.2
    if features[3] in [22, 23, 0, 1, 2]:  # Heures de nuit
        base_score += 0.1
    
    return min(base_score, 1.0)

def generate_recommendations(prediction, data):
    """Génère des recommandations basées sur la prédiction"""
    recommendations = []
    
    if prediction == 'high' or prediction == 'critical':
        recommendations.extend([
            "Formation urgente requise pour l'équipe",
            "Inspection immédiate de l'équipement",
            "Mise en place d'EPI supplémentaires",
            "Révision des procédures de sécurité"
        ])
    elif prediction == 'medium':
        recommendations.extend([
            "Formation préventive recommandée",
            "Vérification périodique de l'équipement",
            "Sensibilisation des employés"
        ])
    else:  # low
        recommendations.extend([
            "Maintien des procédures actuelles",
            "Surveillance continue recommandée"
        ])
    
    return recommendations

def create_simple_database():
    """Crée une base de données simple"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Table des utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des secteurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    # Table des types d'incidents
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incident_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    # Table des rapports d'incidents
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incident_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            location TEXT,
            severity_level TEXT,
            sector_id INTEGER,
            incident_type_id INTEGER,
            probability_score REAL,
            time_incident TEXT,
            ai_recommendations TEXT,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sector_id) REFERENCES sectors (id),
            FOREIGN KEY (incident_type_id) REFERENCES incident_types (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insérer des données de base
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, role) VALUES 
        ('admin', 'pbkdf2:sha256:260000$hash$admin', 'admin'),
        ('user', 'pbkdf2:sha256:260000$hash$user', 'user')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO sectors (name, description) VALUES 
        ('Production', 'Secteur de production industrielle'),
        ('Maintenance', 'Secteur de maintenance'),
        ('Logistique', 'Secteur logistique'),
        ('Administration', 'Secteur administratif'),
        ('R&D', 'Recherche et développement'),
        ('Qualité', 'Contrôle qualité'),
        ('Sécurité', 'Sécurité au travail'),
        ('Autres', 'Autres secteurs')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO incident_types (name, description) VALUES 
        ('Chute', 'Chute de hauteur ou de plain-pied'),
        ('Coupure', 'Coupure avec un outil ou objet'),
        ('Brûlure', 'Brûlure thermique ou chimique'),
        ('Intoxication', 'Intoxication par inhalation'),
        ('Électrocution', 'Choc électrique'),
        ('Écrasement', 'Écrasement par un objet'),
        ('Exposition', 'Exposition à des substances'),
        ('Autres', 'Autres types d\'incidents')
    ''')
    
    # Insérer quelques incidents de démonstration
    cursor.execute('''
        INSERT OR IGNORE INTO incident_reports 
        (title, description, location, severity_level, sector_id, incident_type_id, 
         probability_score, time_incident, ai_recommendations, user_id) VALUES 
        ('Chute sur chantier', 'Chute d\'un échafaudage', 'Chantier A', 'high', 2, 1, 0.8, '14:30', 'Vérifier les fixations', 1),
        ('Coupure en atelier', 'Coupure avec un cutter', 'Atelier B', 'medium', 1, 2, 0.6, '10:15', 'Formation aux outils', 1),
        ('Brûlure chimique', 'Projection d\'acide', 'Laboratoire', 'critical', 5, 3, 0.9, '16:45', 'EPI obligatoires', 1)
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de données créée avec succès!")

# ==================== LANCEMENT DE L'APPLICATION ====================

if __name__ == '__main__':
    # Initialiser la base de données si elle n'existe pas
    if not os.path.exists(DATABASE):
        print("Initialisation de la base de données...")
        try:
            from database.init_db import init_database
            init_database()
        except Exception as e:
            print(f"Erreur initialisation DB: {e}")
            print("Création de la base de données manuellement...")
            create_simple_database()
    
    # Créer les dossiers nécessaires
    os.makedirs('assistant_qhse_ia/database', exist_ok=True)
    os.makedirs('assistant_qhse_ia/models', exist_ok=True)
    os.makedirs('assistant_qhse_ia/temp', exist_ok=True)
    os.makedirs('assistant_qhse_ia/logs', exist_ok=True)
    os.makedirs('assistant_qhse_ia/uploads', exist_ok=True)
    os.makedirs('assistant_qhse_ia/exports', exist_ok=True)
    os.makedirs('assistant_qhse_ia/backups', exist_ok=True)
    
    print("🚀 Assistant QHSE IA - Version Simplifiée démarrée!")
    print("🌐 Application accessible sur: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000/dashboard")
    print("🎨 Dashboard Animé: http://localhost:5000/dashboard_animated")
    print("🔐 Connexion Animée: http://localhost:5000/login_animated")
    print("📋 Formulaire Animé: http://localhost:5000/form_animated")
    print("🤖 Chatbot: http://localhost:5000/chatbot")
    print("📋 Formulaire: http://localhost:5000/form")
    print("="*60)
    print("💡 Appuyez sur Ctrl+C pour arrêter l'application")
    print("="*60)
    
    # Lancer l'application
    app.run(debug=True, host='0.0.0.0', port=5000)
