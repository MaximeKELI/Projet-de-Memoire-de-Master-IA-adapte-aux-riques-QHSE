"""
Application Flask principale pour l'Assistant QHSE IA
Serveur backend avec API REST et interface web
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

# Import des nouveaux modules
from notifications.notification_system import init_notification_system
from reporting.qhse_reports import QHSEReportingSystem
from workflow.qhse_workflow import QHSEWorkflowSystem
from training.qhse_training import QHSETrainingSystem
from admin.admin_panel import QHSEAdminPanel

# Import des modules avancés
from ai.advanced_ai_engine import ai_engine
from iot.sensor_manager import iot_manager
from gamification.qhse_gamification import gamification_system
from analytics.cost_prediction_engine import cost_prediction_engine
from blockchain.qhse_blockchain import qhse_blockchain
from ar_vr.qhse_ar_vr import ar_vr_system
from suppliers.supplier_management import supplier_management

# Configuration de l'application
app = Flask(__name__)
app.secret_key = 'qhse_secret_key_2024'
CORS(app)

# Configuration de la base de données
DATABASE = 'assistant_qhse_ia/database/qhse.db'

# Initialisation des systèmes QHSE
notification_system = None
reporting_system = QHSEReportingSystem(DATABASE)
workflow_system = QHSEWorkflowSystem(DATABASE)
training_system = QHSETrainingSystem(DATABASE)
admin_panel = QHSEAdminPanel(DATABASE)

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
    week_ago = (datetime.now() - timedelta(days=7)).date()
    stats['recent_incidents'] = conn.execute('''
        SELECT COUNT(*) FROM incident_reports 
        WHERE date_incident >= ?
    ''', (week_ago,)).fetchone()[0]
    
    # Taux de résolution
    resolved = conn.execute('''
        SELECT COUNT(*) FROM incident_reports 
        WHERE status IN ('resolved', 'closed')
    ''').fetchone()[0]
    
    stats['resolution_rate'] = (resolved / stats['total_incidents'] * 100) if stats['total_incidents'] > 0 else 0
    
    # Incidents récents pour le tableau
    recent_reports = conn.execute('''
        SELECT ir.*, s.name as sector_name, it.name as incident_type_name
        FROM incident_reports ir
        JOIN sectors s ON ir.sector_id = s.id
        JOIN incident_types it ON ir.incident_type_id = it.id
        ORDER BY ir.created_at DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', stats=stats, recent_reports=recent_reports)

@app.route('/chatbot')
@login_required
def chatbot():
    """Interface du chatbot"""
    return render_template('chatbot.html')

@app.route('/conseils')
@login_required
def conseils():
    """Page des conseils IA"""
    conn = get_db_connection()
    
    # Récupérer les incidents à haut risque
    high_risk_incidents = conn.execute('''
        SELECT ir.*, s.name as sector_name, it.name as incident_type_name
        FROM incident_reports ir
        JOIN sectors s ON ir.sector_id = s.id
        JOIN incident_types it ON ir.incident_type_id = it.id
        WHERE ir.severity_level IN ('high', 'critical')
        ORDER BY ir.risk_score DESC
        LIMIT 20
    ''').fetchall()
    
    conn.close()
    
    return render_template('conseil_IA.html', incidents=high_risk_incidents)

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

# ==================== API ENDPOINTS ====================

@app.route('/api/incidents', methods=['GET'])
@login_required
def get_incidents():
    """API pour récupérer les incidents"""
    conn = get_db_connection()
    
    # Paramètres de filtrage
    sector = request.args.get('sector')
    severity = request.args.get('severity')
    status = request.args.get('status')
    limit = request.args.get('limit', 50, type=int)
    
    query = '''
        SELECT ir.*, s.name as sector_name, it.name as incident_type_name
        FROM incident_reports ir
        JOIN sectors s ON ir.sector_id = s.id
        JOIN incident_types it ON ir.incident_type_id = it.id
        WHERE 1=1
    '''
    params = []
    
    if sector:
        query += ' AND s.name = ?'
        params.append(sector)
    
    if severity:
        query += ' AND ir.severity_level = ?'
        params.append(severity)
    
    if status:
        query += ' AND ir.status = ?'
        params.append(status)
    
    query += ' ORDER BY ir.created_at DESC LIMIT ?'
    params.append(limit)
    
    incidents = conn.execute(query, params).fetchall()
    conn.close()
    
    return jsonify([dict(incident) for incident in incidents])

@app.route('/api/incidents', methods=['POST'])
@login_required
def create_incident():
    """API pour créer un nouvel incident"""
    data = request.get_json()
    
    # Validation des données
    required_fields = ['sector_id', 'incident_type_id', 'title', 'description', 'severity_level', 'probability_score']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Champ manquant: {field}'}), 400
    
    # Calcul du score de risque
    conn = get_db_connection()
    severity_weight = conn.execute(
        'SELECT severity_weight FROM incident_types WHERE id = ?', 
        (data['incident_type_id'],)
    ).fetchone()['severity_weight']
    
    risk_score = data['probability_score'] * severity_weight
    
    # Insertion de l'incident
    incident_id = conn.execute('''
        INSERT INTO incident_reports 
        (user_id, sector_id, incident_type_id, title, description, location, 
         date_incident, time_incident, severity_level, probability_score, 
         risk_score, status, ai_recommendations)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        session['user_id'],
        data['sector_id'],
        data['incident_type_id'],
        data['title'],
        data['description'],
        data.get('location', ''),
        data.get('date_incident', datetime.now().date()),
        data.get('time_incident', datetime.now().time()),
        data['severity_level'],
        data['probability_score'],
        risk_score,
        data.get('status', 'open'),
        data.get('ai_recommendations', '')
    )).lastrowid
    
    conn.commit()
    conn.close()
    
    return jsonify({'id': incident_id, 'message': 'Incident créé avec succès'}), 201

@app.route('/api/predict', methods=['POST'])
@login_required
def predict_risk():
    """API pour la prédiction de risque avec IA"""
    data = request.get_json()
    
    try:
        # Charger le modèle d'IA
        model_path = 'assistant_qhse_ia/modeles/risk_classifier.joblib'
        if os.path.exists(model_path):
            model = joblib.load(model_path)
        else:
            # Modèle par défaut si pas de modèle entraîné
            return jsonify({
                'prediction': 'medium',
                'confidence': 0.5,
                'recommendations': 'Modèle d\'IA non disponible. Utilisation de l\'évaluation manuelle.'
            })
        
        # Préparer les données pour la prédiction
        features = prepare_features(data)
        prediction = model.predict([features])[0]
        confidence = model.predict_proba([features]).max()
        
        # Générer des recommandations basées sur la prédiction
        recommendations = generate_recommendations(prediction, data)
        
        return jsonify({
            'prediction': prediction,
            'confidence': float(confidence),
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur de prédiction: {str(e)}'}), 500

@app.route('/api/chatbot', methods=['POST'])
@login_required
def chatbot_response():
    """API pour les réponses du chatbot"""
    data = request.get_json()
    message = data.get('message', '').lower()
    
    # Réponses prédéfinies du chatbot
    responses = {
        'incendie': {
            'response': "En cas d'incendie, suivez la procédure : 1) Activez l'alarme, 2) Évacuez immédiatement, 3) Composez le 18. Les extincteurs sont disponibles tous les 15m.",
            'risk_level': 'high',
            'quick_replies': ["Où sont les extincteurs ?", "Plan d'évacuation", "Formation incendie"]
        },
        'bâtiment': {
            'response': "Pour le BTP, les EPI obligatoires sont : casque de sécurité, chaussures de sécurité, gants, harnais antichute (si hauteur >3m).",
            'risk_level': 'medium',
            'quick_replies': ["Normes harnais", "EPI spécifiques électricité", "Contrôle EPI"]
        },
        'chimique': {
            'response': "La manipulation de produits chimiques nécessite : fiche de données sécurité, ventilation adaptée, EPI (gants, lunettes, masque).",
            'risk_level': 'high',
            'quick_replies': ["FDS à consulter", "EPI chimiques", "Procédure déversement"]
        },
        'signal': {
            'response': "Pour signaler un incident : 1) Sécurisez la zone, 2) Aidez les blessés sans vous mettre en danger, 3) Appelez les secours si besoin.",
            'risk_level': 'medium',
            'quick_replies': ["Ouvrir formulaire", "Procédure complète", "Numéros urgents"]
        }
    }
    
    # Recherche de la meilleure correspondance
    best_match = None
    for keyword, response_data in responses.items():
        if keyword in message:
            best_match = response_data
            break
    
    if best_match:
        return jsonify(best_match)
    else:
        return jsonify({
            'response': "Je peux vous aider avec les réglementations QHSE, les procédures de sécurité, l'analyse de risques et plus. Posez-moi une question précise.",
            'risk_level': 'low',
            'quick_replies': ["Réglementation actuelle", "Derniers incidents", "Formations disponibles"]
        })

@app.route('/api/statistics')
@login_required
def get_statistics():
    """API pour les statistiques du dashboard"""
    conn = get_db_connection()
    
    # Statistiques générales
    stats = {}
    
    # Incidents par secteur
    sector_stats = conn.execute('''
        SELECT s.name, COUNT(ir.id) as count
        FROM sectors s
        LEFT JOIN incident_reports ir ON s.id = ir.sector_id
        GROUP BY s.id, s.name
        ORDER BY count DESC
    ''').fetchall()
    
    stats['by_sector'] = [{'name': row['name'], 'count': row['count']} for row in sector_stats]
    
    # Incidents par type
    type_stats = conn.execute('''
        SELECT it.name, COUNT(ir.id) as count
        FROM incident_types it
        LEFT JOIN incident_reports ir ON it.id = ir.incident_type_id
        GROUP BY it.id, it.name
        ORDER BY count DESC
    ''').fetchall()
    
    stats['by_type'] = [{'name': row['name'], 'count': row['count']} for row in type_stats]
    
    # Tendance mensuelle (6 derniers mois)
    monthly_trend = []
    for i in range(6):
        month_start = datetime.now() - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        count = conn.execute('''
            SELECT COUNT(*) FROM incident_reports 
            WHERE date_incident BETWEEN ? AND ?
        ''', (month_start.date(), month_end.date())).fetchone()[0]
        
        monthly_trend.append({
            'month': month_start.strftime('%b'),
            'count': count
        })
    
    stats['monthly_trend'] = list(reversed(monthly_trend))
    
    conn.close()
    
    return jsonify(stats)

# ==================== NOUVELLES ROUTES QHSE AVANCÉES ====================

# ==================== ROUTES IA AVANCÉE ====================

@app.route('/api/ai/analyze-text', methods=['POST'])
@login_required
def analyze_text_ai():
    """Analyse de texte avec l'IA avancée"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        context = data.get('context', 'QHSE')
        
        analysis = ai_engine.analyze_text_with_gpt4(text, context)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/analyze-image', methods=['POST'])
@login_required
def analyze_image_ai():
    """Analyse d'image pour la sécurité"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Aucune image fournie'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        # Sauvegarde temporaire
        filename = f"temp_{datetime.now().timestamp()}.jpg"
        filepath = os.path.join('temp', filename)
        os.makedirs('temp', exist_ok=True)
        file.save(filepath)
        
        analysis = ai_engine.analyze_image_safety(filepath)
        
        # Nettoyage
        os.remove(filepath)
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/predict-costs', methods=['POST'])
@login_required
def predict_costs_ai():
    """Prédiction des coûts d'incident"""
    try:
        data = request.get_json()
        prediction = cost_prediction_engine.predict_incident_costs(data)
        return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/sentiment-analysis', methods=['POST'])
@login_required
def analyze_sentiment():
    """Analyse du sentiment des employés"""
    try:
        data = request.get_json()
        text_data = data.get('text', [])
        
        if isinstance(text_data, str):
            text_data = [text_data]
        
        analysis = ai_engine.analyze_employee_sentiment(text_data)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ROUTES IoT ====================

@app.route('/api/iot/sensors', methods=['GET'])
@login_required
def get_iot_sensors():
    """Récupère le statut des capteurs IoT"""
    try:
        status = iot_manager.get_all_sensors_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/iot/sensors/<sensor_id>/data', methods=['GET'])
@login_required
def get_sensor_data(sensor_id):
    """Récupère les données d'un capteur"""
    try:
        hours = request.args.get('hours', 24, type=int)
        data = iot_manager.get_sensor_data(sensor_id, hours)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/iot/sensors', methods=['POST'])
@login_required
def add_iot_sensor():
    """Ajoute un nouveau capteur IoT"""
    try:
        data = request.get_json()
        sensor_id = iot_manager.add_sensor(
            data['sensor_id'],
            data['name'],
            data['sensor_type'],
            data['location'],
            data['zone']
        )
        return jsonify({'sensor_id': sensor_id, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/iot/alerts', methods=['GET'])
@login_required
def get_iot_alerts():
    """Récupère les alertes des capteurs"""
    try:
        level = request.args.get('level')
        alerts = iot_manager.get_alerts(level)
        return jsonify(alerts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/iot/alerts/<alert_id>/acknowledge', methods=['POST'])
@login_required
def acknowledge_alert(alert_id):
    """Acquitte une alerte"""
    try:
        success = iot_manager.acknowledge_alert(alert_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ROUTES GAMIFICATION ====================

@app.route('/api/gamification/profile/<int:user_id>', methods=['GET'])
@login_required
def get_user_gamification_profile(user_id):
    """Récupère le profil gamification d'un utilisateur"""
    try:
        profile = gamification_system.get_user_profile(user_id)
        if not profile:
            return jsonify({'error': 'Profil non trouvé'}), 404
        
        return jsonify({
            'user_id': profile.user_id,
            'username': profile.username,
            'level': profile.level,
            'total_points': profile.total_points,
            'current_streak': profile.current_streak,
            'longest_streak': profile.longest_streak,
            'badges_earned': profile.badges_earned,
            'rank': profile.rank
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gamification/award-points', methods=['POST'])
@login_required
def award_gamification_points():
    """Attribue des points de gamification"""
    try:
        data = request.get_json()
        success = gamification_system.award_points(
            data['user_id'],
            data['event_type'],
            data['points'],
            data['description']
        )
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gamification/leaderboard', methods=['GET'])
@login_required
def get_leaderboard():
    """Récupère le classement des utilisateurs"""
    try:
        category = request.args.get('category', 'all')
        limit = request.args.get('limit', 10, type=int)
        leaderboard = gamification_system.get_leaderboard(category, limit)
        return jsonify(leaderboard)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gamification/badges', methods=['GET'])
@login_required
def get_badges():
    """Récupère les badges disponibles"""
    try:
        category = request.args.get('category')
        badges = []
        for badge_id, badge in gamification_system.badges.items():
            if not category or badge.category == category:
                badges.append({
                    'badge_id': badge.badge_id,
                    'name': badge.name,
                    'description': badge.description,
                    'icon': badge.icon,
                    'points': badge.points,
                    'category': badge.category,
                    'rarity': badge.rarity
                })
        return jsonify(badges)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ROUTES BLOCKCHAIN ====================

@app.route('/api/blockchain/certificates', methods=['GET'])
@login_required
def get_blockchain_certificates():
    """Récupère les certificats blockchain d'un utilisateur"""
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'error': 'user_id requis'}), 400
        
        certificates = qhse_blockchain.get_certificate_history(user_id)
        return jsonify(certificates)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blockchain/certificates', methods=['POST'])
@login_required
def create_blockchain_certificate():
    """Crée un certificat blockchain"""
    try:
        data = request.get_json()
        certificate_id = qhse_blockchain.create_certificate(
            data['user_id'],
            data['certificate_type'],
            datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        )
        return jsonify({'certificate_id': certificate_id, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blockchain/verify/<certificate_id>', methods=['GET'])
@login_required
def verify_certificate(certificate_id):
    """Vérifie un certificat blockchain"""
    try:
        verification = qhse_blockchain.verify_certificate(certificate_id)
        return jsonify(verification)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blockchain/stats', methods=['GET'])
@login_required
def get_blockchain_stats():
    """Récupère les statistiques de la blockchain"""
    try:
        stats = qhse_blockchain.get_blockchain_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ROUTES AR/VR ====================

@app.route('/api/arvr/scenes', methods=['GET'])
@login_required
def get_arvr_scenes():
    """Récupère les scènes AR/VR disponibles"""
    try:
        scene_type = request.args.get('scene_type')
        device_type = request.args.get('device_type')
        
        scenes = []
        for scene_id, scene in ar_vr_system.scenes.items():
            if (not scene_type or scene.scene_type.value == scene_type) and \
               (not device_type or scene.device_type.value == device_type):
                scenes.append({
                    'scene_id': scene.scene_id,
                    'name': scene.name,
                    'description': scene.description,
                    'scene_type': scene.scene_type.value,
                    'device_type': scene.device_type.value,
                    'duration_minutes': scene.duration_minutes,
                    'difficulty_level': scene.difficulty_level
                })
        
        return jsonify(scenes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/arvr/sessions', methods=['POST'])
@login_required
def start_arvr_session():
    """Démarre une session AR/VR"""
    try:
        data = request.get_json()
        session_id = ar_vr_system.start_session(
            data['user_id'],
            data['scene_id'],
            data['device_type']
        )
        return jsonify({'session_id': session_id, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/arvr/sessions/<session_id>/end', methods=['POST'])
@login_required
def end_arvr_session(session_id):
    """Termine une session AR/VR"""
    try:
        data = request.get_json()
        score = data.get('score')
        success = ar_vr_system.end_session(session_id, score)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/arvr/sessions/<session_id>/interaction', methods=['POST'])
@login_required
def record_arvr_interaction(session_id):
    """Enregistre une interaction AR/VR"""
    try:
        data = request.get_json()
        success = ar_vr_system.record_interaction(
            session_id,
            data['interaction_type'],
            data.get('object_id'),
            data.get('position'),
            data.get('data')
        )
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ROUTES GESTION FOURNISSEURS ====================

@app.route('/api/suppliers', methods=['GET'])
@login_required
def get_suppliers():
    """Récupère la liste des fournisseurs"""
    try:
        risk_level = request.args.get('risk_level')
        suppliers = []
        
        for supplier in supplier_management.suppliers.values():
            if not risk_level or supplier.risk_level.value == risk_level:
                suppliers.append({
                    'supplier_id': supplier.supplier_id,
                    'name': supplier.name,
                    'contact_person': supplier.contact_person,
                    'email': supplier.email,
                    'status': supplier.status.value,
                    'risk_level': supplier.risk_level.value,
                    'qhse_score': supplier.qhse_score,
                    'last_audit_date': supplier.last_audit_date.isoformat() if supplier.last_audit_date else None
                })
        
        return jsonify(suppliers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/suppliers', methods=['POST'])
@login_required
def add_supplier():
    """Ajoute un nouveau fournisseur"""
    try:
        data = request.get_json()
        supplier_id = supplier_management.add_supplier(
            data['name'],
            data['contact_person'],
            data['email'],
            data['phone'],
            data['address'],
            data['country'],
            data['business_type'],
            data.get('registration_number')
        )
        return jsonify({'supplier_id': supplier_id, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/suppliers/<supplier_id>/risk-assessment', methods=['GET'])
@login_required
def get_supplier_risk_assessment(supplier_id):
    """Récupère l'évaluation des risques d'un fournisseur"""
    try:
        assessment = supplier_management.get_supplier_risk_assessment(supplier_id)
        return jsonify(assessment)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/suppliers/audits', methods=['POST'])
@login_required
def schedule_supplier_audit():
    """Planifie un audit fournisseur"""
    try:
        data = request.get_json()
        audit_id = supplier_management.schedule_audit(
            data['supplier_id'],
            data['auditor_id'],
            data['audit_type'],
            datetime.fromisoformat(data['scheduled_date'])
        )
        return jsonify({'audit_id': audit_id, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/suppliers/incidents', methods=['POST'])
@login_required
def report_supplier_incident():
    """Signale un incident fournisseur"""
    try:
        data = request.get_json()
        incident_id = supplier_management.report_incident(
            data['supplier_id'],
            data['incident_type'],
            data['description'],
            data['severity_level'],
            datetime.fromisoformat(data['occurred_date']),
            data.get('impact_assessment')
        )
        return jsonify({'incident_id': incident_id, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ROUTES COÛTS ET ANALYTICS ====================

@app.route('/api/analytics/cost-trends', methods=['GET'])
@login_required
def get_cost_trends():
    """Récupère les tendances des coûts"""
    try:
        days = request.args.get('days', 365, type=int)
        trends = cost_prediction_engine.get_cost_trends(days)
        return jsonify(trends)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/cost-report', methods=['POST'])
@login_required
def generate_cost_report():
    """Génère un rapport de coûts"""
    try:
        data = request.get_json()
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date'])
        report = cost_prediction_engine.generate_cost_report(start_date, end_date)
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ROUTES DASHBOARD AVANCÉ ====================

@app.route('/api/dashboard/advanced-stats', methods=['GET'])
@login_required
def get_advanced_dashboard_stats():
    """Récupère les statistiques avancées du tableau de bord"""
    try:
        # Statistiques IoT
        iot_stats = iot_manager.get_all_sensors_status()
        
        # Statistiques gamification
        gamification_stats = {
            'total_users': len(gamification_system.get_leaderboard('all', 1000)),
            'top_users': gamification_system.get_leaderboard('all', 5)
        }
        
        # Statistiques fournisseurs
        supplier_stats = supplier_management.get_supplier_statistics()
        
        # Statistiques blockchain
        blockchain_stats = qhse_blockchain.get_blockchain_stats()
        
        # Statistiques AR/VR
        arvr_stats = {
            'total_scenes': len(ar_vr_system.scenes),
            'active_sessions': len(ar_vr_system.active_sessions)
        }
        
        # Statistiques de base pour le dashboard animé
        conn = get_db_connection()
        total_incidents = conn.execute('SELECT COUNT(*) FROM incident_reports').fetchone()[0]
        conn.close()
        
        return jsonify({
            # Données attendues par le frontend animé
            'incidents': total_incidents,
            'sensors': iot_stats.get('active_sensors', 15),
            'points': gamification_stats.get('total_points', 1250),
            'blocks': blockchain_stats.get('total_blocks', 156),
            # Données avancées
            'iot': iot_stats,
            'gamification': gamification_stats,
            'suppliers': supplier_stats,
            'blockchain': blockchain_stats,
            'arvr': arvr_stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin')
@login_required
def admin_dashboard():
    """Tableau de bord d'administration"""
    if session.get('role') not in ['admin', 'manager']:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('dashboard'))
    
    admin_data = admin_panel.get_admin_dashboard_data()
    return render_template('admin_dashboard.html', data=admin_data)

@app.route('/api/reports', methods=['GET'])
@login_required
def get_reports():
    """API pour récupérer les rapports disponibles"""
    reports = reporting_system.get_available_reports()
    return jsonify(reports)

@app.route('/api/reports/<report_type>', methods=['POST'])
@login_required
def generate_report(report_type):
    """API pour générer un rapport"""
    data = request.get_json()
    start_date = data.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = data.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    if report_type == 'incident_summary':
        report = reporting_system.generate_incident_summary_report(start_date, end_date)
    elif report_type == 'regulatory_compliance':
        quarter = data.get('quarter', 'Q1')
        year = data.get('year', datetime.now().year)
        report = reporting_system.generate_regulatory_compliance_report(quarter, year)
    elif report_type == 'safety_performance':
        report = reporting_system.generate_safety_performance_report(start_date, end_date)
    elif report_type == 'training_compliance':
        report = reporting_system.generate_training_compliance_report(start_date, end_date)
    elif report_type == 'risk_assessment':
        report = reporting_system.generate_risk_assessment_report(start_date, end_date)
    else:
        return jsonify({'error': 'Type de rapport non supporté'}), 400
    
    return jsonify(report)

@app.route('/api/workflows', methods=['GET'])
@login_required
def get_workflows():
    """API pour récupérer les workflows d'un utilisateur"""
    user_workflows = workflow_system.get_user_workflows(session['user_id'], session.get('role', 'user'))
    return jsonify(user_workflows)

@app.route('/api/workflows', methods=['POST'])
@login_required
def create_workflow():
    """API pour créer un nouveau workflow"""
    data = request.get_json()
    template_id = data.get('template_id')
    incident_id = data.get('incident_id')
    priority = data.get('priority', 'medium')
    
    workflow_id = workflow_system.create_workflow(template_id, incident_id, priority)
    return jsonify({'workflow_id': workflow_id, 'message': 'Workflow créé avec succès'})

@app.route('/api/workflows/<int:workflow_id>/steps/<int:step_id>', methods=['POST'])
@login_required
def execute_workflow_step(workflow_id, step_id):
    """API pour exécuter une action sur une étape de workflow"""
    data = request.get_json()
    action = data.get('action')
    comment = data.get('comment', '')
    
    success = workflow_system.execute_workflow_step(workflow_id, step_id, action, session['user_id'], comment)
    
    if success:
        return jsonify({'message': 'Action exécutée avec succès'})
    else:
        return jsonify({'error': 'Impossible d\'exécuter l\'action'}), 400

@app.route('/api/training/certifications')
@login_required
def get_user_certifications():
    """API pour récupérer les certifications d'un utilisateur"""
    certifications = training_system.get_user_certifications(session['user_id'])
    return jsonify(certifications)

@app.route('/api/training/expiring')
@login_required
def get_expiring_certifications():
    """API pour récupérer les certifications qui expirent"""
    days_ahead = request.args.get('days', 30, type=int)
    expiring = training_system.get_expiring_certifications(days_ahead)
    return jsonify(expiring)

@app.route('/api/training/plan')
@login_required
def get_training_plan():
    """API pour récupérer le plan de formation d'un utilisateur"""
    sector = request.args.get('sector', 'Bureaux')
    plan = training_system.create_training_plan(session['user_id'], sector)
    return jsonify(plan)

@app.route('/api/training/sessions', methods=['POST'])
@login_required
def create_training_session():
    """API pour créer une session de formation"""
    if session.get('role') not in ['admin', 'training_manager']:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    data = request.get_json()
    training_id = data.get('training_id')
    instructor_id = data.get('instructor_id')
    start_date = datetime.fromisoformat(data.get('start_date'))
    end_date = datetime.fromisoformat(data.get('end_date'))
    location = data.get('location')
    max_participants = data.get('max_participants')
    
    session_id = training_system.schedule_training_session(
        training_id, instructor_id, start_date, end_date, location, max_participants
    )
    
    return jsonify({'session_id': session_id, 'message': 'Session créée avec succès'})

@app.route('/api/notifications')
@login_required
def get_notifications():
    """API pour récupérer les notifications d'un utilisateur"""
    conn = get_db_connection()
    notifications = conn.execute("""
        SELECT * FROM notifications 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 50
    """, (session['user_id'],)).fetchall()
    conn.close()
    
    return jsonify([dict(notif) for notif in notifications])

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """API pour marquer une notification comme lue"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE notifications 
        SET status = 'read', read_at = ? 
        WHERE id = ? AND user_id = ?
    """, (datetime.now(), notification_id, session['user_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Notification marquée comme lue'})

@app.route('/mobile')
@login_required
def mobile_app():
    """Interface mobile pour signalement d'incidents"""
    return render_template('mobile_app.html')

@app.route('/api/admin/overview')
@login_required
def get_admin_overview():
    """API pour récupérer l'aperçu administrateur"""
    if session.get('role') not in ['admin', 'manager']:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    overview = admin_panel.get_system_overview()
    return jsonify(overview)

@app.route('/api/admin/users', methods=['POST'])
@login_required
def create_user():
    """API pour créer un utilisateur (admin seulement)"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    data = request.get_json()
    success = admin_panel.create_user(
        data.get('username'),
        data.get('email'),
        data.get('password'),
        data.get('role')
    )
    
    if success:
        return jsonify({'message': 'Utilisateur créé avec succès'})
    else:
        return jsonify({'error': 'Erreur lors de la création de l\'utilisateur'}), 400

@app.route('/api/admin/users/<int:user_id>/role', methods=['PUT'])
@login_required
def update_user_role(user_id):
    """API pour mettre à jour le rôle d'un utilisateur"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    data = request.get_json()
    new_role = data.get('role')
    
    success = admin_panel.update_user_role(user_id, new_role)
    
    if success:
        return jsonify({'message': 'Rôle mis à jour avec succès'})
    else:
        return jsonify({'error': 'Erreur lors de la mise à jour'}), 400

# ==================== FONCTIONS UTILITAIRES ====================

def check_password_hash(password_hash, password):
    """Vérifie le mot de passe (version simplifiée)"""
    # Dans un vrai projet, utiliser bcrypt ou similar
    return password_hash == f"pbkdf2:sha256:260000$hash${password}"

def prepare_features(data):
    """Prépare les features pour le modèle d'IA"""
    # Encodage des features catégorielles
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

# ==================== ROUTES ANIMÉES ====================

@app.route('/dashboard_animated')
@login_required
def dashboard_animated():
    """Tableau de bord avec animations avancées"""
    return render_template('dashboard_animated.html')

@app.route('/login_animated')
def login_animated():
    """Page de connexion avec animations"""
    return render_template('login_animated.html')

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

# ==================== LANCEMENT DE L'APPLICATION ====================

if __name__ == '__main__':
    # Initialiser la base de données si elle n'existe pas
    if not os.path.exists(DATABASE):
        print("Initialisation de la base de données...")
        from database.init_db import init_database
        init_database()
    
    # Créer les dossiers nécessaires
    os.makedirs('assistant_qhse_ia/modeles', exist_ok=True)
    os.makedirs('assistant_qhse_ia/notifications', exist_ok=True)
    os.makedirs('assistant_qhse_ia/reporting', exist_ok=True)
    os.makedirs('assistant_qhse_ia/workflow', exist_ok=True)
    os.makedirs('assistant_qhse_ia/training', exist_ok=True)
    os.makedirs('assistant_qhse_ia/admin', exist_ok=True)
    os.makedirs('assistant_qhse_ia/mobile', exist_ok=True)
    
    # Initialiser le système de notifications
    global notification_system
    notification_system = init_notification_system(app)
    
    print("🚀 Assistant QHSE IA - Système complet démarré!")
    print("📱 Interface mobile: http://localhost:5000/mobile")
    print("⚙️  Administration: http://localhost:5000/admin")
    print("📊 Rapports: http://localhost:5000/api/reports")
    print("🤖 Workflows: http://localhost:5000/api/workflows")
    print("🎓 Formations: http://localhost:5000/api/training")
    
    # Lancer l'application
    app.run(debug=True, host='0.0.0.0', port=5000)
