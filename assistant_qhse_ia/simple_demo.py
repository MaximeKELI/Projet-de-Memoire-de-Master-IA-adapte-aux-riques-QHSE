#!/usr/bin/env python3
"""
Démonstration simple du système QHSE IA
Version sans templates pour tester les APIs
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

# Configuration de l'application
app = Flask(__name__)
CORS(app)

# Configuration de la base de données
DATABASE = 'qhse_demo.db'

def get_db_connection():
    """Crée une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialise la base de données"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
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
    """Page d'accueil avec informations"""
    return jsonify({
        "message": "🎯 Système QHSE IA - Démonstration",
        "version": "1.0.0",
        "status": "actif",
        "endpoints": {
            "incidents": "/api/incidents",
            "statistics": "/api/statistics",
            "predict": "/api/predict",
            "chatbot": "/api/chatbot",
            "advanced_stats": "/api/dashboard/advanced-stats"
        },
        "timestamp": datetime.now().isoformat()
    })

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

@app.route('/api/sectors')
def get_sectors():
    """Récupère la liste des secteurs"""
    conn = get_db_connection()
    sectors = conn.execute('SELECT * FROM sectors ORDER BY name').fetchall()
    conn.close()
    
    return jsonify([dict(sector) for sector in sectors])

@app.route('/api/incident-types')
def get_incident_types():
    """Récupère la liste des types d'incidents"""
    conn = get_db_connection()
    incident_types = conn.execute('SELECT * FROM incident_types ORDER BY name').fetchall()
    conn.close()
    
    return jsonify([dict(incident_type) for incident_type in incident_types])

# ==================== LANCEMENT DE L'APPLICATION ====================

if __name__ == '__main__':
    print("🚀 Assistant QHSE IA - Démonstration API")
    print("="*50)
    
    # Initialiser la base de données
    init_database()
    
    print("🌐 API accessible sur: http://localhost:5001")
    print("📊 Statistiques: http://localhost:5001/api/statistics")
    print("📋 Incidents: http://localhost:5001/api/incidents")
    print("🤖 Prédiction: http://localhost:5001/api/predict")
    print("💬 Chatbot: http://localhost:5001/api/chatbot")
    print("🏢 Secteurs: http://localhost:5001/api/sectors")
    print("⚠️  Types d'incidents: http://localhost:5001/api/incident-types")
    print("="*50)
    print("💡 Testez les APIs avec curl ou Postman")
    print("="*50)
    
    # Lancer l'application
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
