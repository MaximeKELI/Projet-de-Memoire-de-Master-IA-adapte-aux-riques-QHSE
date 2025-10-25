"""
API GraphQL pour le système QHSE
Architecture microservices avec requêtes flexibles
"""

from flask import Flask, request, jsonify
from flask_graphql import GraphQLView
import graphene
from graphene import ObjectType, String, Int, Float, Boolean, List, Field, ID
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import sqlite3

# Import des modules existants
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.advanced_ai_engine import ai_engine
from iot.sensor_manager import iot_manager
from gamification.qhse_gamification import gamification_system
from analytics.cost_prediction_engine import cost_prediction_engine
from blockchain.qhse_blockchain import qhse_blockchain
from ar_vr.qhse_ar_vr import ar_vr_system

# Types GraphQL pour les entités QHSE
class IncidentType(graphene.ObjectType):
    id = ID()
    title = String()
    description = String()
    severity_level = Int()
    status = String()
    created_at = String()
    reported_by = Int()
    sector_id = Int()
    incident_type_id = Int()
    ai_recommendations = String()
    predicted_cost = Float()

class UserType(graphene.ObjectType):
    id = ID()
    username = String()
    email = String()
    role = String()
    level = Int()
    total_points = Int()
    rank = String()

class SensorDataType(graphene.ObjectType):
    sensor_id = String()
    sensor_type = String()
    value = Float()
    unit = String()
    timestamp = String()
    location = String()
    zone = String()

class BadgeType(graphene.ObjectType):
    badge_id = String()
    name = String()
    description = String()
    icon = String()
    points = Int()
    category = String()
    rarity = String()

class ARVRSceneType(graphene.ObjectType):
    scene_id = String()
    name = String()
    description = String()
    scene_type = String()
    device_type = String()
    duration_minutes = Int()
    difficulty_level = Int()

class CostPredictionType(graphene.ObjectType):
    total_cost = Float()
    medical_costs = Float()
    equipment_damage = Float()
    regulatory_fines = Float()
    insurance_impact = Float()
    productivity_loss = Float()
    confidence_score = Float()

class BlockchainCertificateType(graphene.ObjectType):
    certificate_id = String()
    user_id = Int()
    certificate_type = String()
    issued_at = String()
    expires_at = String()
    verified = Boolean()
    block_hash = String()

# Queries GraphQL
class Query(graphene.ObjectType):
    # Incidents
    incidents = List(IncidentType, limit=Int(), offset=Int(), severity=Int())
    incident = Field(IncidentType, id=ID(required=True))
    
    # Utilisateurs
    users = List(UserType, limit=Int(), offset=Int())
    user = Field(UserType, id=ID(required=True))
    user_profile = Field(UserType, id=ID(required=True))
    
    # Capteurs IoT
    sensors = List(SensorDataType, limit=Int(), hours=Int())
    sensor_data = List(SensorDataType, sensor_id=String(required=True), hours=Int())
    sensor_alerts = List(String, level=String())
    
    # Gamification
    badges = List(BadgeType, category=String())
    user_badges = List(BadgeType, user_id=ID(required=True))
    leaderboard = List(UserType, category=String(), limit=Int())
    user_stats = Field(UserType, user_id=ID(required=True))
    
    # AR/VR
    arvr_scenes = List(ARVRSceneType, scene_type=String(), device_type=String())
    user_sessions = List(String, user_id=ID(required=True), limit=Int())
    
    # Prédictions de coûts
    predict_costs = Field(CostPredictionType, incident_data=String(required=True))
    cost_trends = Field(String, days=Int())
    
    # Blockchain
    certificates = List(BlockchainCertificateType, user_id=ID(required=True))
    verify_certificate = Field(BlockchainCertificateType, certificate_id=String(required=True))
    blockchain_stats = Field(String)
    
    # Statistiques générales
    dashboard_stats = Field(String)
    ai_analysis = Field(String, text=String(required=True))
    
    def resolve_incidents(self, info, limit=10, offset=0, severity=None):
        """Récupère la liste des incidents"""
        conn = sqlite3.connect('assistant_qhse_ia/database/qhse.db')
        cursor = conn.cursor()
        
        query = "SELECT * FROM incident_reports WHERE 1=1"
        params = []
        
        if severity:
            query += " AND severity_level = ?"
            params.append(severity)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        incidents = []
        for row in rows:
            incidents.append(IncidentType(
                id=str(row[0]),
                title=row[1],
                description=row[2],
                severity_level=row[4],
                status=row[5],
                created_at=row[6],
                reported_by=row[7],
                sector_id=row[3],
                incident_type_id=row[2],
                ai_recommendations=row[8] if len(row) > 8 else None
            ))
        
        return incidents
    
    def resolve_incident(self, info, id):
        """Récupère un incident spécifique"""
        conn = sqlite3.connect('assistant_qhse_ia/database/qhse.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM incident_reports WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return IncidentType(
            id=str(row[0]),
            title=row[1],
            description=row[2],
            severity_level=row[4],
            status=row[5],
            created_at=row[6],
            reported_by=row[7],
            sector_id=row[3],
            incident_type_id=row[2],
            ai_recommendations=row[8] if len(row) > 8 else None
        )
    
    def resolve_users(self, info, limit=10, offset=0):
        """Récupère la liste des utilisateurs"""
        conn = sqlite3.connect('assistant_qhse_ia/database/qhse.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.role, 
                   g.level, g.total_points, g.rank
            FROM users u
            LEFT JOIN user_gamification_profiles g ON u.id = g.user_id
            ORDER BY u.id
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append(UserType(
                id=str(row[0]),
                username=row[1],
                email=row[2],
                role=row[3],
                level=row[4] or 1,
                total_points=row[5] or 0,
                rank=row[6] or "Rookie"
            ))
        
        return users
    
    def resolve_user(self, info, id):
        """Récupère un utilisateur spécifique"""
        conn = sqlite3.connect('assistant_qhse_ia/database/qhse.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.role, 
                   g.level, g.total_points, g.rank
            FROM users u
            LEFT JOIN user_gamification_profiles g ON u.id = g.user_id
            WHERE u.id = ?
        """, (id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return UserType(
            id=str(row[0]),
            username=row[1],
            email=row[2],
            role=row[3],
            level=row[4] or 1,
            total_points=row[5] or 0,
            rank=row[6] or "Rookie"
        )
    
    def resolve_sensors(self, info, limit=10, hours=24):
        """Récupère les données des capteurs"""
        try:
            status = iot_manager.get_all_sensors_status()
            sensors = []
            
            for sensor in status.get('sensors', [])[:limit]:
                # Récupération des dernières données
                sensor_data = iot_manager.get_sensor_data(sensor['id'], hours)
                if sensor_data:
                    latest_data = sensor_data[0]
                    sensors.append(SensorDataType(
                        sensor_id=sensor['id'],
                        sensor_type=sensor['type'],
                        value=latest_data['value'],
                        unit=latest_data['unit'],
                        timestamp=latest_data['timestamp'],
                        location=sensor['location'],
                        zone=sensor['zone']
                    ))
            
            return sensors
        except Exception as e:
            return []
    
    def resolve_sensor_data(self, info, sensor_id, hours=24):
        """Récupère les données d'un capteur spécifique"""
        try:
            data = iot_manager.get_sensor_data(sensor_id, hours)
            sensor_data = []
            
            for point in data:
                sensor_data.append(SensorDataType(
                    sensor_id=sensor_id,
                    sensor_type="unknown",  # À récupérer depuis la base
                    value=point['value'],
                    unit=point['unit'],
                    timestamp=point['timestamp'],
                    location="unknown",
                    zone="unknown"
                ))
            
            return sensor_data
        except Exception as e:
            return []
    
    def resolve_sensor_alerts(self, info, level=None):
        """Récupère les alertes des capteurs"""
        try:
            alerts = iot_manager.get_alerts()
            alert_messages = []
            
            for alert in alerts:
                if not level or alert['level'] == level:
                    alert_messages.append(f"{alert['message']} - {alert['location']}")
            
            return alert_messages
        except Exception as e:
            return []
    
    def resolve_badges(self, info, category=None):
        """Récupère les badges disponibles"""
        try:
            badges = []
            for badge_id, badge in gamification_system.badges.items():
                if not category or badge.category == category:
                    badges.append(BadgeType(
                        badge_id=badge.badge_id,
                        name=badge.name,
                        description=badge.description,
                        icon=badge.icon,
                        points=badge.points,
                        category=badge.category,
                        rarity=badge.rarity
                    ))
            
            return badges
        except Exception as e:
            return []
    
    def resolve_user_badges(self, info, user_id):
        """Récupère les badges d'un utilisateur"""
        try:
            profile = gamification_system.get_user_profile(int(user_id))
            if not profile:
                return []
            
            badges = []
            for badge_id in profile.badges_earned:
                if badge_id in gamification_system.badges:
                    badge = gamification_system.badges[badge_id]
                    badges.append(BadgeType(
                        badge_id=badge.badge_id,
                        name=badge.name,
                        description=badge.description,
                        icon=badge.icon,
                        points=badge.points,
                        category=badge.category,
                        rarity=badge.rarity
                    ))
            
            return badges
        except Exception as e:
            return []
    
    def resolve_leaderboard(self, info, category="all", limit=10):
        """Récupère le classement des utilisateurs"""
        try:
            leaderboard = gamification_system.get_leaderboard(category, limit)
            users = []
            
            for entry in leaderboard:
                users.append(UserType(
                    id=str(entry['user_id']),
                    username=entry['username'],
                    email="",  # Non inclus pour la sécurité
                    role="",
                    level=entry.get('level', 1),
                    total_points=entry['points'],
                    rank=entry.get('rank_name', 'Rookie')
                ))
            
            return users
        except Exception as e:
            return []
    
    def resolve_user_stats(self, info, user_id):
        """Récupère les statistiques d'un utilisateur"""
        try:
            stats = gamification_system.get_user_stats(int(user_id))
            profile = stats.get('profile', {})
            
            return UserType(
                id=str(profile.get('user_id', user_id)),
                username=profile.get('username', ''),
                email="",
                role="",
                level=profile.get('level', 1),
                total_points=profile.get('total_points', 0),
                rank=profile.get('rank', 'Rookie')
            )
        except Exception as e:
            return None
    
    def resolve_arvr_scenes(self, info, scene_type=None, device_type=None):
        """Récupère les scènes AR/VR"""
        try:
            scenes = []
            for scene_id, scene in ar_vr_system.scenes.items():
                if (not scene_type or scene.scene_type.value == scene_type) and \
                   (not device_type or scene.device_type.value == device_type):
                    scenes.append(ARVRSceneType(
                        scene_id=scene.scene_id,
                        name=scene.name,
                        description=scene.description,
                        scene_type=scene.scene_type.value,
                        device_type=scene.device_type.value,
                        duration_minutes=scene.duration_minutes,
                        difficulty_level=scene.difficulty_level
                    ))
            
            return scenes
        except Exception as e:
            return []
    
    def resolve_user_sessions(self, info, user_id, limit=10):
        """Récupère les sessions AR/VR d'un utilisateur"""
        try:
            sessions = ar_vr_system.get_user_sessions(int(user_id), limit)
            return [json.dumps(session) for session in sessions]
        except Exception as e:
            return []
    
    def resolve_predict_costs(self, info, incident_data):
        """Prédit les coûts d'un incident"""
        try:
            data = json.loads(incident_data)
            prediction = cost_prediction_engine.predict_incident_costs(data)
            
            return CostPredictionType(
                total_cost=prediction.get('total_cost', 0),
                medical_costs=prediction.get('breakdown', {}).get('medical_costs', 0),
                equipment_damage=prediction.get('breakdown', {}).get('equipment_damage', 0),
                regulatory_fines=prediction.get('breakdown', {}).get('regulatory_fines', 0),
                insurance_impact=prediction.get('breakdown', {}).get('insurance_impact', 0),
                productivity_loss=prediction.get('breakdown', {}).get('productivity_loss', 0),
                confidence_score=prediction.get('confidence_scores', {}).get('total_cost', 0.85)
            )
        except Exception as e:
            return CostPredictionType(
                total_cost=0, medical_costs=0, equipment_damage=0,
                regulatory_fines=0, insurance_impact=0, productivity_loss=0,
                confidence_score=0
            )
    
    def resolve_cost_trends(self, info, days=365):
        """Récupère les tendances des coûts"""
        try:
            trends = cost_prediction_engine.get_cost_trends(days)
            return json.dumps(trends)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def resolve_certificates(self, info, user_id):
        """Récupère les certificats blockchain d'un utilisateur"""
        try:
            certificates = qhse_blockchain.get_certificate_history(int(user_id))
            cert_objects = []
            
            for cert in certificates:
                cert_objects.append(BlockchainCertificateType(
                    certificate_id=cert['certificate_id'],
                    user_id=int(user_id),
                    certificate_type=cert['certificate_type'],
                    issued_at=cert['issued_at'],
                    expires_at=cert['expires_at'],
                    verified=cert['verified'],
                    block_hash=cert['block_hash']
                ))
            
            return cert_objects
        except Exception as e:
            return []
    
    def resolve_verify_certificate(self, info, certificate_id):
        """Vérifie un certificat blockchain"""
        try:
            verification = qhse_blockchain.verify_certificate(certificate_id)
            
            if verification.get('valid'):
                return BlockchainCertificateType(
                    certificate_id=certificate_id,
                    user_id=verification.get('user_id', 0),
                    certificate_type=verification.get('certificate_type', ''),
                    issued_at=verification.get('issued_at', ''),
                    expires_at=verification.get('expires_at', ''),
                    verified=verification.get('blockchain_verified', False),
                    block_hash=verification.get('block_hash', '')
                )
            
            return None
        except Exception as e:
            return None
    
    def resolve_blockchain_stats(self, info):
        """Récupère les statistiques de la blockchain"""
        try:
            stats = qhse_blockchain.get_blockchain_stats()
            return json.dumps(stats)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def resolve_dashboard_stats(self, info):
        """Récupère les statistiques du tableau de bord"""
        try:
            # Statistiques générales
            conn = sqlite3.connect('assistant_qhse_ia/database/qhse.db')
            cursor = conn.cursor()
            
            # Nombre d'incidents
            cursor.execute("SELECT COUNT(*) FROM incident_reports")
            total_incidents = cursor.fetchone()[0]
            
            # Incidents par gravité
            cursor.execute("""
                SELECT severity_level, COUNT(*) 
                FROM incident_reports 
                GROUP BY severity_level
            """)
            severity_stats = dict(cursor.fetchall())
            
            # Capteurs actifs
            sensor_status = iot_manager.get_all_sensors_status()
            
            conn.close()
            
            stats = {
                "total_incidents": total_incidents,
                "severity_breakdown": severity_stats,
                "active_sensors": sensor_status.get('active_sensors', 0),
                "total_sensors": sensor_status.get('total_sensors', 0),
                "active_alerts": sensor_status.get('active_alerts', 0)
            }
            
            return json.dumps(stats)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def resolve_ai_analysis(self, info, text):
        """Analyse de texte avec l'IA"""
        try:
            analysis = ai_engine.analyze_text_with_gpt4(text)
            return json.dumps(analysis)
        except Exception as e:
            return json.dumps({"error": str(e)})

# Mutations GraphQL
class CreateIncident(graphene.Mutation):
    class Arguments:
        title = String(required=True)
        description = String(required=True)
        severity_level = Int(required=True)
        sector_id = Int(required=True)
        incident_type_id = Int(required=True)
        reported_by = Int(required=True)
    
    incident = Field(IncidentType)
    success = Boolean()
    message = String()
    
    def mutate(self, info, title, description, severity_level, sector_id, incident_type_id, reported_by):
        try:
            conn = sqlite3.connect('assistant_qhse_ia/database/qhse.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO incident_reports 
                (title, description, sector_id, incident_type_id, severity_level, reported_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, description, sector_id, incident_type_id, severity_level, reported_by, datetime.now()))
            
            incident_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Attribution de points gamification
            gamification_system.award_points(
                reported_by, 
                "incident_report", 
                10, 
                f"Signalement d'incident: {title}"
            )
            
            return CreateIncident(
                incident=IncidentType(
                    id=str(incident_id),
                    title=title,
                    description=description,
                    severity_level=severity_level,
                    status="open",
                    created_at=datetime.now().isoformat(),
                    reported_by=reported_by,
                    sector_id=sector_id,
                    incident_type_id=incident_type_id
                ),
                success=True,
                message="Incident créé avec succès"
            )
            
        except Exception as e:
            return CreateIncident(
                incident=None,
                success=False,
                message=f"Erreur: {str(e)}"
            )

class AwardPoints(graphene.Mutation):
    class Arguments:
        user_id = ID(required=True)
        event_type = String(required=True)
        points = Int(required=True)
        description = String(required=True)
    
    success = Boolean()
    message = String()
    
    def mutate(self, info, user_id, event_type, points, description):
        try:
            success = gamification_system.award_points(
                int(user_id), event_type, points, description
            )
            
            return AwardPoints(
                success=success,
                message="Points attribués avec succès" if success else "Erreur attribution points"
            )
            
        except Exception as e:
            return AwardPoints(
                success=False,
                message=f"Erreur: {str(e)}"
            )

class StartARVRSession(graphene.Mutation):
    class Arguments:
        user_id = ID(required=True)
        scene_id = String(required=True)
        device_type = String(required=True)
    
    session_id = String()
    success = Boolean()
    message = String()
    
    def mutate(self, info, user_id, scene_id, device_type):
        try:
            from ar_vr.qhse_ar_vr import DeviceType
            
            device_enum = DeviceType(device_type)
            session_id = ar_vr_system.start_session(int(user_id), scene_id, device_enum)
            
            return StartARVRSession(
                session_id=session_id,
                success=True,
                message="Session AR/VR démarrée"
            )
            
        except Exception as e:
            return StartARVRSession(
                session_id=None,
                success=False,
                message=f"Erreur: {str(e)}"
            )

class Mutations(graphene.ObjectType):
    create_incident = CreateIncident.Field()
    award_points = AwardPoints.Field()
    start_arvr_session = StartARVRSession.Field()

# Schéma GraphQL
schema = graphene.Schema(query=Query, mutation=Mutations)

# Configuration Flask
app = Flask(__name__)

# Route GraphQL
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Interface GraphiQL pour les tests
    )
)

# Route de santé pour les microservices
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "ai_engine": "active",
            "iot_manager": "active",
            "gamification": "active",
            "cost_prediction": "active",
            "blockchain": "active",
            "ar_vr": "active"
        }
    })

# Route de métriques
@app.route('/metrics')
def metrics():
    try:
        # Métriques des capteurs
        sensor_status = iot_manager.get_all_sensors_status()
        
        # Métriques de gamification
        leaderboard = gamification_system.get_leaderboard("all", 5)
        
        # Métriques blockchain
        blockchain_stats = qhse_blockchain.get_blockchain_stats()
        
        return jsonify({
            "sensors": {
                "total": sensor_status.get('total_sensors', 0),
                "active": sensor_status.get('active_sensors', 0),
                "alerts": sensor_status.get('active_alerts', 0)
            },
            "gamification": {
                "top_users": len(leaderboard),
                "total_points": sum(user.get('points', 0) for user in leaderboard)
            },
            "blockchain": {
                "blocks": blockchain_stats.get('total_blocks', 0),
                "transactions": blockchain_stats.get('total_transactions', 0),
                "valid": blockchain_stats.get('chain_valid', False)
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
