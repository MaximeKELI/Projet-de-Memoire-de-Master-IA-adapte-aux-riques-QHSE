#!/usr/bin/env python3
"""
Application Flask minimale pour tester le système QHSE IA
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

# Configuration de l'application
app = Flask(__name__)
app.secret_key = 'qhse_secret_key_2024'
CORS(app)

# Configuration de la base de données
DATABASE = 'qhse_minimal.db'

def get_db_connection():
    """Crée une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialise la base de données"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Table des utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Table des secteurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    
    # Table des types d'incidents
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incident_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    
    # Table des rapports d'incidents
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incident_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            severity_level TEXT,
            sector_id INTEGER,
            incident_type_id INTEGER,
            probability_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insérer des données de base
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, role) VALUES 
        ('admin', 'admin', 'admin'),
        ('user', 'user', 'user')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO sectors (name) VALUES 
        ('Production'), ('Maintenance'), ('Logistique'), ('Administration'),
        ('R&D'), ('Qualité'), ('Sécurité'), ('Autres')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO incident_types (name) VALUES 
        ('Chute'), ('Coupure'), ('Brûlure'), ('Intoxication'),
        ('Électrocution'), ('Écrasement'), ('Exposition'), ('Autres')
    ''')
    
    # Insérer quelques incidents de démonstration
    cursor.execute('''
        INSERT OR IGNORE INTO incident_reports 
        (title, description, severity_level, sector_id, incident_type_id, probability_score) VALUES 
        ('Chute sur chantier', 'Chute d''un échafaudage', 'high', 2, 1, 0.8),
        ('Coupure en atelier', 'Coupure avec un cutter', 'medium', 1, 2, 0.6),
        ('Brûlure chimique', 'Projection d''acide', 'critical', 5, 3, 0.9)
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée!")

# ==================== ROUTES ====================

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
            'SELECT * FROM users WHERE username = ? AND password_hash = ?', 
            (username, password)
        ).fetchone()
        conn.close()
        
        if user:
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
def dashboard():
    """Tableau de bord principal"""
    conn = get_db_connection()
    
    # Statistiques générales
    stats = {}
    stats['total_incidents'] = conn.execute('SELECT COUNT(*) FROM incident_reports').fetchone()[0]
    
    # Incidents par sévérité
    severity_counts = conn.execute('''
        SELECT severity_level, COUNT(*) as count 
        FROM incident_reports 
        GROUP BY severity_level
    ''').fetchall()
    
    stats['severity_breakdown'] = {row['severity_level']: row['count'] for row in severity_counts}
    
    conn.close()
    
    return render_template('dashboard.html', stats=stats)

@app.route('/dashboard_animated')
def dashboard_animated():
    """Tableau de bord avec animations avancées"""
    return render_template('dashboard_animated.html')

@app.route('/login_animated')
def login_animated():
    """Page de connexion avec animations"""
    return render_template('login_animated.html')

@app.route('/form')
def form():
    """Formulaire d'analyse de risque"""
    conn = get_db_connection()
    sectors = conn.execute('SELECT * FROM sectors ORDER BY name').fetchall()
    incident_types = conn.execute('SELECT * FROM incident_types ORDER BY name').fetchall()
    conn.close()
    
    return render_template('form.html', sectors=sectors, incident_types=incident_types)

@app.route('/form_animated')
def form_animated():
    """Formulaire d'analyse avec animations"""
    conn = get_db_connection()
    sectors = conn.execute('SELECT id, name FROM sectors ORDER BY name').fetchall()
    incident_types = conn.execute('SELECT id, name FROM incident_types ORDER BY name').fetchall()
    conn.close()
    
    return render_template('form_animated.html', 
                         sectors=sectors, 
                         incident_types=incident_types)

@app.route('/chatbot')
def chatbot():
    """Interface chatbot"""
    return render_template('chatbot.html')

# ==================== API ENDPOINTS ====================

@app.route('/api/incidents', methods=['GET'])
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
def create_incident():
    """Crée un nouvel incident"""
    data = request.get_json()
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO incident_reports 
        (title, description, severity_level, sector_id, incident_type_id, probability_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get('title'),
        data.get('description'),
        data.get('severity_level'),
        data.get('sector_id'),
        data.get('incident_type_id'),
        data.get('probability_score')
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Incident créé avec succès'})

@app.route('/api/predict', methods=['POST'])
def predict_risk():
    """Prédiction de risque avec IA"""
    data = request.get_json()
    
    # Simulation simple de prédiction
    risk_score = 0.3 + (data.get('probability_score', 0.5) * 0.4)
    
    if risk_score < 0.4:
        prediction = 'low'
    elif risk_score < 0.7:
        prediction = 'medium'
    else:
        prediction = 'high'
    
    recommendations = [
        "Formation préventive recommandée",
        "Vérification de l'équipement",
        "Sensibilisation des employés"
    ]
    
    return jsonify({
        'prediction': prediction,
        'risk_score': risk_score,
        'recommendations': recommendations
    })

@app.route('/api/chatbot', methods=['POST'])
def chatbot_response():
    """Réponse du chatbot"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    responses = {
        'incendie': "En cas d'incendie, suivez la procédure : 1) Activez l'alarme, 2) Évacuez immédiatement, 3) Composez le 18.",
        'chute': "Pour éviter les chutes, portez des chaussures antidérapantes et vérifiez les surfaces de travail.",
        'coupure': "En cas de coupure, arrêtez le saignement et consultez un médecin si nécessaire.",
        'sécurité': "La sécurité est notre priorité. Respectez toujours les procédures et portez les EPI."
    }
    
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
    
    conn.close()
    
    return jsonify({
        'by_sector': [dict(row) for row in by_sector],
        'by_type': [dict(row) for row in by_type],
        'monthly_trend': [
            {'month': '2024-01', 'count': 5},
            {'month': '2024-02', 'count': 8},
            {'month': '2024-03', 'count': 3}
        ]
    })

@app.route('/api/dashboard/advanced-stats', methods=['GET'])
def get_advanced_dashboard_stats():
    """Récupère les statistiques avancées du tableau de bord"""
    conn = get_db_connection()
    total_incidents = conn.execute('SELECT COUNT(*) FROM incident_reports').fetchone()[0]
    conn.close()
    
    return jsonify({
        'incidents': total_incidents,
        'sensors': 15,
        'points': 1250,
        'blocks': 156,
        'timestamp': datetime.now().isoformat()
    })

# ==================== LANCEMENT DE L'APPLICATION ====================

if __name__ == '__main__':
    print("🚀 Assistant QHSE IA - Version Minimale")
    print("="*50)
    
    # Initialiser la base de données
    init_database()
    
    print("🌐 Application accessible sur: http://localhost:5001")
    print("📊 Dashboard: http://localhost:5001/dashboard")
    print("🎨 Dashboard Animé: http://localhost:5001/dashboard_animated")
    print("🔐 Connexion Animée: http://localhost:5001/login_animated")
    print("📋 Formulaire Animé: http://localhost:5001/form_animated")
    print("🤖 Chatbot: http://localhost:5001/chatbot")
    print("📋 Formulaire: http://localhost:5001/form")
    print("="*50)
    print("💡 Appuyez sur Ctrl+C pour arrêter l'application")
    print("="*50)
    
    # Lancer l'application
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
