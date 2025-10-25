"""
Module de reporting QHSE avancé
Génération de rapports réglementaires et tableaux de bord
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from jinja2 import Template
import io
import base64

class QHSEReportingSystem:
    """Système de reporting spécialisé QHSE"""
    
    def __init__(self, db_path: str = 'assistant_qhse_ia/database/qhse.db'):
        self.db_path = db_path
        self.report_templates = self.load_report_templates()
    
    def load_report_templates(self) -> Dict:
        """Charge les templates de rapports QHSE"""
        return {
            'incident_summary': {
                'title': 'Rapport de Synthèse des Incidents QHSE',
                'description': 'Vue d\'ensemble des incidents et tendances',
                'frequency': 'monthly',
                'regulatory': False
            },
            'regulatory_compliance': {
                'title': 'Rapport de Conformité Réglementaire',
                'description': 'État de conformité aux réglementations QHSE',
                'frequency': 'quarterly',
                'regulatory': True
            },
            'safety_performance': {
                'title': 'Rapport de Performance Sécurité',
                'description': 'Indicateurs de performance et KPIs',
                'frequency': 'monthly',
                'regulatory': False
            },
            'training_compliance': {
                'title': 'Rapport de Conformité Formation',
                'description': 'État des formations et certifications',
                'frequency': 'monthly',
                'regulatory': True
            },
            'risk_assessment': {
                'title': 'Rapport d\'Évaluation des Risques',
                'description': 'Analyse des risques et recommandations',
                'frequency': 'quarterly',
                'regulatory': False
            },
            'audit_report': {
                'title': 'Rapport d\'Audit QHSE',
                'description': 'Résultats des audits internes et externes',
                'frequency': 'annual',
                'regulatory': True
            }
        }
    
    def generate_incident_summary_report(self, start_date: str, end_date: str) -> Dict:
        """Génère un rapport de synthèse des incidents"""
        conn = sqlite3.connect(self.db_path)
        
        # Données principales
        query = """
            SELECT 
                ir.*,
                s.name as sector_name,
                it.name as incident_type_name,
                it.category,
                u.username as reported_by
            FROM incident_reports ir
            JOIN sectors s ON ir.sector_id = s.id
            JOIN incident_types it ON ir.incident_type_id = it.id
            JOIN users u ON ir.user_id = u.id
            WHERE ir.date_incident BETWEEN ? AND ?
            ORDER BY ir.date_incident DESC
        """
        
        df = pd.read_sql_query(query, conn, params=[start_date, end_date])
        
        # Statistiques générales
        stats = {
            'total_incidents': len(df),
            'critical_incidents': len(df[df['severity_level'] == 'critical']),
            'high_risk_incidents': len(df[df['severity_level'] == 'high']),
            'resolved_incidents': len(df[df['status'].isin(['resolved', 'closed'])]),
            'average_risk_score': df['risk_score'].mean(),
            'period': f"{start_date} à {end_date}"
        }
        
        # Répartition par secteur
        sector_breakdown = df.groupby('sector_name').size().to_dict()
        
        # Répartition par type d'incident
        type_breakdown = df.groupby('incident_type_name').size().to_dict()
        
        # Répartition par gravité
        severity_breakdown = df.groupby('severity_level').size().to_dict()
        
        # Tendance mensuelle
        df['month'] = pd.to_datetime(df['date_incident']).dt.to_period('M')
        monthly_trend = df.groupby('month').size().to_dict()
        
        # Top 5 des secteurs à risque
        sector_risk = df.groupby('sector_name')['risk_score'].mean().sort_values(ascending=False).head(5).to_dict()
        
        # Recommandations IA les plus fréquentes
        recommendations = df['ai_recommendations'].dropna().str.split('\n').explode().value_counts().head(10).to_dict()
        
        conn.close()
        
        return {
            'report_type': 'incident_summary',
            'generated_at': datetime.now().isoformat(),
            'period': {'start': start_date, 'end': end_date},
            'statistics': stats,
            'sector_breakdown': sector_breakdown,
            'type_breakdown': type_breakdown,
            'severity_breakdown': severity_breakdown,
            'monthly_trend': monthly_trend,
            'top_risk_sectors': sector_risk,
            'top_recommendations': recommendations,
            'data': df.to_dict('records')
        }
    
    def generate_regulatory_compliance_report(self, quarter: str, year: int) -> Dict:
        """Génère un rapport de conformité réglementaire"""
        # Simulation de données réglementaires QHSE
        regulations = {
            'ISO_45001': {
                'name': 'ISO 45001 - Système de management SST',
                'status': 'conforme',
                'last_audit': '2024-01-15',
                'next_audit': '2024-07-15',
                'score': 92
            },
            'RGPD': {
                'name': 'RGPD - Protection des données personnelles',
                'status': 'conforme',
                'last_audit': '2024-02-01',
                'next_audit': '2024-08-01',
                'score': 88
            },
            'Code_Travail': {
                'name': 'Code du Travail - Santé et Sécurité',
                'status': 'conforme',
                'last_audit': '2024-01-30',
                'next_audit': '2024-07-30',
                'score': 95
            },
            'REACH': {
                'name': 'REACH - Substances chimiques',
                'status': 'non_conforme',
                'last_audit': '2024-01-10',
                'next_audit': '2024-04-10',
                'score': 75,
                'non_conformities': [
                    'Fiches de données sécurité manquantes',
                    'Formation insuffisante sur les produits chimiques'
                ]
            }
        }
        
        # Calcul des métriques de conformité
        total_regulations = len(regulations)
        conforming_regulations = len([r for r in regulations.values() if r['status'] == 'conforme'])
        compliance_rate = (conforming_regulations / total_regulations) * 100
        
        # Actions correctives en cours
        corrective_actions = [
            {
                'regulation': 'REACH',
                'action': 'Mise à jour des FDS',
                'deadline': '2024-04-01',
                'responsible': 'Responsable QHSE',
                'status': 'en_cours'
            },
            {
                'regulation': 'REACH',
                'action': 'Formation équipes chimie',
                'deadline': '2024-03-15',
                'responsible': 'Formateur QHSE',
                'status': 'planifiée'
            }
        ]
        
        return {
            'report_type': 'regulatory_compliance',
            'generated_at': datetime.now().isoformat(),
            'period': {'quarter': quarter, 'year': year},
            'compliance_rate': compliance_rate,
            'total_regulations': total_regulations,
            'conforming_regulations': conforming_regulations,
            'regulations': regulations,
            'corrective_actions': corrective_actions,
            'recommendations': [
                'Prioriser la mise en conformité REACH',
                'Planifier les audits de suivi',
                'Renforcer la formation des équipes'
            ]
        }
    
    def generate_safety_performance_report(self, start_date: str, end_date: str) -> Dict:
        """Génère un rapport de performance sécurité"""
        conn = sqlite3.connect(self.db_path)
        
        # KPIs QHSE
        query = """
            SELECT 
                COUNT(*) as total_incidents,
                AVG(risk_score) as avg_risk_score,
                COUNT(CASE WHEN severity_level = 'critical' THEN 1 END) as critical_incidents,
                COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_incidents,
                COUNT(CASE WHEN status = 'open' THEN 1 END) as open_incidents
            FROM incident_reports 
            WHERE date_incident BETWEEN ? AND ?
        """
        
        cursor = conn.cursor()
        cursor.execute(query, [start_date, end_date])
        kpis = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
        
        # Calcul des indicateurs de performance
        total_incidents = kpis['total_incidents']
        resolution_rate = (kpis['resolved_incidents'] / total_incidents * 100) if total_incidents > 0 else 0
        critical_rate = (kpis['critical_incidents'] / total_incidents * 100) if total_incidents > 0 else 0
        
        # Comparaison avec la période précédente
        prev_start = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d')
        prev_end = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        
        cursor.execute(query, [prev_start, prev_end])
        prev_kpis = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
        
        # Évolution des indicateurs
        incident_trend = ((total_incidents - prev_kpis['total_incidents']) / prev_kpis['total_incidents'] * 100) if prev_kpis['total_incidents'] > 0 else 0
        risk_trend = kpis['avg_risk_score'] - prev_kpis['avg_risk_score']
        
        # Objectifs QHSE (simulation)
        objectives = {
            'target_incidents': 10,  # Objectif mensuel
            'target_resolution_rate': 90,  # 90% de résolution
            'target_critical_rate': 5,  # Moins de 5% d'incidents critiques
            'target_risk_score': 2.0  # Score de risque moyen < 2.0
        }
        
        # Performance vs objectifs
        performance = {
            'incidents_vs_target': (total_incidents / objectives['target_incidents'] * 100) if objectives['target_incidents'] > 0 else 0,
            'resolution_vs_target': resolution_rate / objectives['target_resolution_rate'] * 100,
            'critical_vs_target': critical_rate / objectives['target_critical_rate'] * 100,
            'risk_vs_target': (kpis['avg_risk_score'] / objectives['target_risk_score'] * 100) if objectives['target_risk_score'] > 0 else 0
        }
        
        conn.close()
        
        return {
            'report_type': 'safety_performance',
            'generated_at': datetime.now().isoformat(),
            'period': {'start': start_date, 'end': end_date},
            'kpis': kpis,
            'performance_indicators': {
                'resolution_rate': resolution_rate,
                'critical_rate': critical_rate,
                'incident_trend': incident_trend,
                'risk_trend': risk_trend
            },
            'objectives': objectives,
            'performance_vs_targets': performance,
            'recommendations': self.generate_performance_recommendations(performance, kpis)
        }
    
    def generate_training_compliance_report(self, start_date: str, end_date: str) -> Dict:
        """Génère un rapport de conformité formation"""
        # Simulation de données de formation QHSE
        training_data = {
            'total_employees': 150,
            'trained_employees': 142,
            'training_rate': 94.7,
            'expired_certifications': 8,
            'expiring_soon': 12,
            'mandatory_trainings': {
                'Sécurité générale': {'completed': 145, 'required': 150, 'rate': 96.7},
                'EPI': {'completed': 140, 'required': 150, 'rate': 93.3},
                'Incendie': {'completed': 135, 'required': 150, 'rate': 90.0},
                'Chimie': {'completed': 120, 'required': 130, 'rate': 92.3},
                'Hauteur': {'completed': 85, 'required': 90, 'rate': 94.4}
            },
            'training_sessions': [
                {'name': 'Formation Sécurité Générale', 'date': '2024-03-01', 'participants': 25, 'instructor': 'J. Dupont'},
                {'name': 'Formation EPI', 'date': '2024-03-05', 'participants': 20, 'instructor': 'M. Martin'},
                {'name': 'Formation Incendie', 'date': '2024-03-10', 'participants': 30, 'instructor': 'L. Bernard'},
                {'name': 'Formation Chimie', 'date': '2024-03-15', 'participants': 15, 'instructor': 'P. Durand'}
            ],
            'expiring_certifications': [
                {'employee': 'A. Martin', 'training': 'Sécurité Générale', 'expiry': '2024-04-15'},
                {'employee': 'B. Durand', 'training': 'EPI', 'expiry': '2024-04-20'},
                {'employee': 'C. Bernard', 'training': 'Incendie', 'expiry': '2024-04-25'}
            ]
        }
        
        return {
            'report_type': 'training_compliance',
            'generated_at': datetime.now().isoformat(),
            'period': {'start': start_date, 'end': end_date},
            'data': training_data,
            'recommendations': [
                'Planifier les formations de recyclage pour les certifications expirées',
                'Organiser une session de rattrapage pour les formations manquantes',
                'Mettre en place un système d\'alerte automatique pour les échéances'
            ]
        }
    
    def generate_risk_assessment_report(self, start_date: str, end_date: str) -> Dict:
        """Génère un rapport d'évaluation des risques"""
        conn = sqlite3.connect(self.db_path)
        
        # Analyse des risques par secteur
        query = """
            SELECT 
                s.name as sector,
                COUNT(*) as incident_count,
                AVG(ir.risk_score) as avg_risk_score,
                MAX(ir.risk_score) as max_risk_score,
                COUNT(CASE WHEN ir.severity_level = 'critical' THEN 1 END) as critical_count
            FROM incident_reports ir
            JOIN sectors s ON ir.sector_id = s.id
            WHERE ir.date_incident BETWEEN ? AND ?
            GROUP BY s.id, s.name
            ORDER BY avg_risk_score DESC
        """
        
        df = pd.read_sql_query(query, conn, params=[start_date, end_date])
        
        # Classification des risques
        risk_levels = {
            'low': df[df['avg_risk_score'] < 2.0],
            'medium': df[(df['avg_risk_score'] >= 2.0) & (df['avg_risk_score'] < 3.0)],
            'high': df[(df['avg_risk_score'] >= 3.0) & (df['avg_risk_score'] < 4.0)],
            'critical': df[df['avg_risk_score'] >= 4.0]
        }
        
        # Recommandations par niveau de risque
        recommendations = {
            'critical': [
                'Arrêt immédiat des activités à risque',
                'Formation d\'urgence de l\'équipe',
                'Révision complète des procédures',
                'Audit approfondi du secteur'
            ],
            'high': [
                'Formation renforcée des équipes',
                'Vérification des EPI',
                'Mise à jour des procédures',
                'Surveillance accrue'
            ],
            'medium': [
                'Formation préventive',
                'Contrôles périodiques',
                'Sensibilisation des équipes'
            ],
            'low': [
                'Maintien des procédures',
                'Surveillance de routine'
            ]
        }
        
        conn.close()
        
        return {
            'report_type': 'risk_assessment',
            'generated_at': datetime.now().isoformat(),
            'period': {'start': start_date, 'end': end_date},
            'risk_analysis': df.to_dict('records'),
            'risk_classification': {level: data.to_dict('records') for level, data in risk_levels.items()},
            'recommendations': recommendations,
            'summary': {
                'total_sectors': len(df),
                'high_risk_sectors': len(risk_levels['high']) + len(risk_levels['critical']),
                'average_risk_score': df['avg_risk_score'].mean(),
                'highest_risk_sector': df.loc[df['avg_risk_score'].idxmax(), 'sector'] if len(df) > 0 else None
            }
        }
    
    def generate_performance_recommendations(self, performance: Dict, kpis: Dict) -> List[str]:
        """Génère des recommandations basées sur la performance"""
        recommendations = []
        
        if performance['incidents_vs_target'] > 120:
            recommendations.append("🚨 Le nombre d'incidents dépasse l'objectif de 20%. Renforcer les mesures préventives.")
        
        if performance['resolution_vs_target'] < 80:
            recommendations.append("⏰ Le taux de résolution est insuffisant. Accélérer le traitement des incidents.")
        
        if performance['critical_vs_target'] > 200:
            recommendations.append("🚨 Trop d'incidents critiques. Mise en place d'actions d'urgence.")
        
        if performance['risk_vs_target'] > 150:
            recommendations.append("⚠️ Score de risque trop élevé. Révision des procédures de sécurité.")
        
        if not recommendations:
            recommendations.append("✅ Performance conforme aux objectifs. Maintenir les efforts.")
        
        return recommendations
    
    def export_report_to_html(self, report_data: Dict) -> str:
        """Exporte un rapport en HTML"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ report_type|title }} - QHSE Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
                .content { margin: 20px 0; }
                .metric { background: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .critical { background: #e74c3c; color: white; }
                .high { background: #f39c12; color: white; }
                .medium { background: #f1c40f; }
                .low { background: #27ae60; color: white; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background: #34495e; color: white; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ report_type|title }} - Rapport QHSE</h1>
                <p>Généré le {{ generated_at }}</p>
            </div>
            <div class="content">
                <!-- Contenu du rapport -->
                {% if report_type == 'incident_summary' %}
                    <h2>Statistiques Générales</h2>
                    <div class="metric">
                        <strong>Total Incidents:</strong> {{ statistics.total_incidents }}
                    </div>
                    <div class="metric critical">
                        <strong>Incidents Critiques:</strong> {{ statistics.critical_incidents }}
                    </div>
                    <div class="metric">
                        <strong>Taux de Résolution:</strong> {{ (statistics.resolved_incidents / statistics.total_incidents * 100)|round(1) }}%
                    </div>
                {% endif %}
            </div>
        </body>
        </html>
        """
        
        jinja_template = Template(template)
        return jinja_template.render(**report_data)
    
    def get_available_reports(self) -> List[Dict]:
        """Retourne la liste des rapports disponibles"""
        return [
            {
                'id': report_id,
                'name': template['title'],
                'description': template['description'],
                'frequency': template['frequency'],
                'regulatory': template['regulatory']
            }
            for report_id, template in self.report_templates.items()
        ]
