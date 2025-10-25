"""
Moteur de Prédiction des Coûts QHSE Avancé
Analyse financière et optimisation des investissements sécurité
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import warnings
warnings.filterwarnings('ignore')

class CostPredictionEngine:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_importance = {}
        
        # Initialisation des modèles
        self._init_models()
    
    def _init_models(self):
        """Initialise les modèles de prédiction"""
        self.models = {
            'medical_costs': RandomForestRegressor(n_estimators=100, random_state=42),
            'equipment_damage': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'regulatory_fines': LinearRegression(),
            'insurance_impact': RandomForestRegressor(n_estimators=50, random_state=42),
            'productivity_loss': GradientBoostingRegressor(n_estimators=50, random_state=42),
            'total_cost': RandomForestRegressor(n_estimators=200, random_state=42)
        }
        
        # Initialisation des scalers et encoders
        for model_name in self.models.keys():
            self.scalers[model_name] = StandardScaler()
            self.encoders[model_name] = LabelEncoder()
    
    def prepare_training_data(self) -> pd.DataFrame:
        """Prépare les données d'entraînement"""
        # Génération de données synthétiques réalistes
        np.random.seed(42)
        n_samples = 5000
        
        # Données de base
        data = {
            'severity_level': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.4, 0.3, 0.15, 0.1, 0.05]),
            'incident_type_id': np.random.choice(range(1, 11), n_samples),
            'sector_id': np.random.choice(range(1, 9), n_samples),
            'employee_count': np.random.randint(10, 2000, n_samples),
            'days_lost': np.random.poisson(5, n_samples),
            'age_employee': np.random.randint(18, 65, n_samples),
            'experience_years': np.random.randint(0, 40, n_samples),
            'safety_training_hours': np.random.randint(0, 100, n_samples),
            'previous_incidents': np.random.poisson(2, n_samples),
            'equipment_age': np.random.randint(0, 20, n_samples),
            'safety_investment': np.random.uniform(1000, 100000, n_samples),
            'compliance_score': np.random.uniform(60, 100, n_samples),
            'weather_conditions': np.random.choice(['good', 'moderate', 'poor'], n_samples, p=[0.6, 0.3, 0.1]),
            'time_of_day': np.random.choice(['morning', 'afternoon', 'evening', 'night'], n_samples),
            'day_of_week': np.random.choice(['weekday', 'weekend'], n_samples, p=[0.8, 0.2])
        }
        
        df = pd.DataFrame(data)
        
        # Calcul des coûts basés sur des formules réalistes
        df['medical_costs'] = self._calculate_medical_costs(df)
        df['equipment_damage'] = self._calculate_equipment_damage(df)
        df['regulatory_fines'] = self._calculate_regulatory_fines(df)
        df['insurance_impact'] = self._calculate_insurance_impact(df)
        df['productivity_loss'] = df['days_lost'] * 200 + np.random.normal(0, 50, n_samples)
        
        # Coût total
        df['total_cost'] = (
            df['medical_costs'] + 
            df['equipment_damage'] + 
            df['regulatory_fines'] + 
            df['insurance_impact'] + 
            df['productivity_loss']
        )
        
        return df
    
    def _calculate_medical_costs(self, df: pd.DataFrame) -> np.ndarray:
        """Calcule les coûts médicaux"""
        base_costs = {
            1: 500,   # Mineur
            2: 2000,  # Modéré
            3: 10000, # Sérieux
            4: 50000, # Majeur
            5: 200000 # Critique
        }
        
        costs = []
        for _, row in df.iterrows():
            base = base_costs[row['severity_level']]
            
            # Facteurs d'ajustement
            age_factor = 1 + (row['age_employee'] - 30) * 0.01
            experience_factor = 1 - (row['experience_years'] * 0.005)
            training_factor = 1 - (row['safety_training_hours'] * 0.001)
            
            # Variation aléatoire
            random_factor = np.random.uniform(0.5, 1.5)
            
            cost = base * age_factor * experience_factor * training_factor * random_factor
            costs.append(max(0, cost))
        
        return np.array(costs)
    
    def _calculate_equipment_damage(self, df: pd.DataFrame) -> np.ndarray:
        """Calcule les dommages matériels"""
        base_costs = {
            1: 1000,
            2: 5000,
            3: 25000,
            4: 100000,
            5: 500000
        }
        
        costs = []
        for _, row in df.iterrows():
            base = base_costs[row['severity_level']]
            
            # Facteurs d'ajustement
            equipment_age_factor = 1 + (row['equipment_age'] * 0.1)
            investment_factor = 1 - (row['safety_investment'] / 100000) * 0.3
            
            # Variation aléatoire
            random_factor = np.random.uniform(0.3, 2.0)
            
            cost = base * equipment_age_factor * investment_factor * random_factor
            costs.append(max(0, cost))
        
        return np.array(costs)
    
    def _calculate_regulatory_fines(self, df: pd.DataFrame) -> np.ndarray:
        """Calcule les amendes réglementaires"""
        base_fines = {
            1: 0,
            2: 1000,
            3: 10000,
            4: 50000,
            5: 200000
        }
        
        costs = []
        for _, row in df.iterrows():
            if row['severity_level'] < 2:
                costs.append(0)
                continue
            
            base = base_fines[row['severity_level']]
            
            # Facteurs d'ajustement
            compliance_factor = 1 - (row['compliance_score'] - 60) / 40
            previous_incidents_factor = 1 + (row['previous_incidents'] * 0.2)
            
            # Variation aléatoire
            random_factor = np.random.uniform(0.5, 1.5)
            
            cost = base * compliance_factor * previous_incidents_factor * random_factor
            costs.append(max(0, cost))
        
        return np.array(costs)
    
    def _calculate_insurance_impact(self, df: pd.DataFrame) -> np.ndarray:
        """Calcule l'impact sur l'assurance"""
        base_impacts = {
            1: 500,
            2: 2000,
            3: 10000,
            4: 50000,
            5: 200000
        }
        
        costs = []
        for _, row in df.iterrows():
            base = base_impacts[row['severity_level']]
            
            # Facteurs d'ajustement
            employee_count_factor = 1 + (row['employee_count'] / 1000) * 0.1
            previous_incidents_factor = 1 + (row['previous_incidents'] * 0.3)
            
            # Variation aléatoire
            random_factor = np.random.uniform(0.7, 1.3)
            
            cost = base * employee_count_factor * previous_incidents_factor * random_factor
            costs.append(max(0, cost))
        
        return np.array(costs)
    
    def train_models(self) -> Dict[str, float]:
        """Entraîne tous les modèles"""
        print("Préparation des données d'entraînement...")
        df = self.prepare_training_data()
        
        # Préparation des features
        feature_columns = [
            'severity_level', 'incident_type_id', 'sector_id', 'employee_count',
            'days_lost', 'age_employee', 'experience_years', 'safety_training_hours',
            'previous_incidents', 'equipment_age', 'safety_investment', 'compliance_score'
        ]
        
        # Encodage des variables catégorielles
        df['weather_encoded'] = self.encoders['total_cost'].fit_transform(df['weather_conditions'])
        df['time_encoded'] = self.encoders['total_cost'].fit_transform(df['time_of_day'])
        df['day_encoded'] = self.encoders['total_cost'].fit_transform(df['day_of_week'])
        
        feature_columns.extend(['weather_encoded', 'time_encoded', 'day_encoded'])
        X = df[feature_columns]
        
        results = {}
        
        # Entraînement de chaque modèle
        for cost_type in self.models.keys():
            print(f"Entraînement du modèle pour {cost_type}...")
            
            y = df[cost_type]
            
            # Division train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Normalisation
            X_train_scaled = self.scalers[cost_type].fit_transform(X_train)
            X_test_scaled = self.scalers[cost_type].transform(X_test)
            
            # Entraînement
            self.models[cost_type].fit(X_train_scaled, y_train)
            
            # Prédiction et évaluation
            y_pred = self.models[cost_type].predict(X_test_scaled)
            
            # Métriques
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            results[cost_type] = {
                'mae': mae,
                'mse': mse,
                'r2': r2,
                'rmse': np.sqrt(mse)
            }
            
            # Importance des features
            if hasattr(self.models[cost_type], 'feature_importances_'):
                self.feature_importance[cost_type] = dict(zip(
                    feature_columns, 
                    self.models[cost_type].feature_importances_
                ))
        
        # Sauvegarde des modèles
        self._save_models()
        
        return results
    
    def _save_models(self):
        """Sauvegarde les modèles entraînés"""
        import os
        os.makedirs('models/cost_prediction', exist_ok=True)
        
        for model_name, model in self.models.items():
            joblib.dump(model, f'models/cost_prediction/{model_name}_model.pkl')
            joblib.dump(self.scalers[model_name], f'models/cost_prediction/{model_name}_scaler.pkl')
        
        # Sauvegarde des encoders
        joblib.dump(self.encoders, 'models/cost_prediction/encoders.pkl')
        joblib.dump(self.feature_importance, 'models/cost_prediction/feature_importance.pkl')
    
    def load_models(self):
        """Charge les modèles pré-entraînés"""
        try:
            for model_name in self.models.keys():
                self.models[model_name] = joblib.load(f'models/cost_prediction/{model_name}_model.pkl')
                self.scalers[model_name] = joblib.load(f'models/cost_prediction/{model_name}_scaler.pkl')
            
            self.encoders = joblib.load('models/cost_prediction/encoders.pkl')
            self.feature_importance = joblib.load('models/cost_prediction/feature_importance.pkl')
            
            print("Modèles de prédiction des coûts chargés avec succès")
            return True
            
        except Exception as e:
            print(f"Erreur lors du chargement des modèles: {e}")
            return False
    
    def predict_incident_costs(self, incident_data: Dict) -> Dict:
        """Prédit les coûts d'un incident"""
        try:
            # Préparation des données
            features = self._prepare_prediction_features(incident_data)
            
            predictions = {}
            confidence_scores = {}
            
            # Prédiction pour chaque type de coût
            for cost_type in self.models.keys():
                if cost_type == 'total_cost':
                    continue
                
                # Normalisation
                features_scaled = self.scalers[cost_type].transform([features])
                
                # Prédiction
                prediction = self.models[cost_type].predict(features_scaled)[0]
                predictions[cost_type] = max(0, prediction)
                
                # Score de confiance (basé sur la variance des prédictions)
                confidence_scores[cost_type] = 0.85  # À améliorer avec des méthodes plus sophistiquées
            
            # Prédiction du coût total
            features_scaled = self.scalers['total_cost'].transform([features])
            total_cost = self.models['total_cost'].predict(features_scaled)[0]
            
            # Analyse de sensibilité
            sensitivity = self._analyze_sensitivity(incident_data, features)
            
            # Recommandations d'optimisation
            recommendations = self._generate_cost_optimization_recommendations(
                incident_data, predictions, total_cost
            )
            
            # ROI des investissements préventifs
            roi_analysis = self._calculate_preventive_roi(incident_data, total_cost)
            
            return {
                'predictions': predictions,
                'total_cost': max(0, total_cost),
                'confidence_scores': confidence_scores,
                'sensitivity_analysis': sensitivity,
                'optimization_recommendations': recommendations,
                'roi_analysis': roi_analysis,
                'breakdown': {
                    'medical_costs': predictions.get('medical_costs', 0),
                    'equipment_damage': predictions.get('equipment_damage', 0),
                    'regulatory_fines': predictions.get('regulatory_fines', 0),
                    'insurance_impact': predictions.get('insurance_impact', 0),
                    'productivity_loss': predictions.get('productivity_loss', 0)
                }
            }
            
        except Exception as e:
            return {'error': f'Erreur prédiction coûts: {str(e)}'}
    
    def _prepare_prediction_features(self, incident_data: Dict) -> List[float]:
        """Prépare les features pour la prédiction"""
        # Valeurs par défaut
        defaults = {
            'severity_level': 3,
            'incident_type_id': 1,
            'sector_id': 1,
            'employee_count': 100,
            'days_lost': 5,
            'age_employee': 35,
            'experience_years': 5,
            'safety_training_hours': 20,
            'previous_incidents': 1,
            'equipment_age': 5,
            'safety_investment': 10000,
            'compliance_score': 80,
            'weather_conditions': 'good',
            'time_of_day': 'morning',
            'day_of_week': 'weekday'
        }
        
        # Récupération des valeurs
        features = []
        for key in [
            'severity_level', 'incident_type_id', 'sector_id', 'employee_count',
            'days_lost', 'age_employee', 'experience_years', 'safety_training_hours',
            'previous_incidents', 'equipment_age', 'safety_investment', 'compliance_score'
        ]:
            features.append(incident_data.get(key, defaults[key]))
        
        # Encodage des variables catégorielles
        weather = incident_data.get('weather_conditions', defaults['weather_conditions'])
        time_of_day = incident_data.get('time_of_day', defaults['time_of_day'])
        day_of_week = incident_data.get('day_of_week', defaults['day_of_week'])
        
        features.extend([
            self.encoders['total_cost'].transform([weather])[0],
            self.encoders['total_cost'].transform([time_of_day])[0],
            self.encoders['total_cost'].transform([day_of_week])[0]
        ])
        
        return features
    
    def _analyze_sensitivity(self, incident_data: Dict, features: List[float]) -> Dict:
        """Analyse la sensibilité des coûts aux différents paramètres"""
        sensitivity = {}
        
        # Paramètres à tester
        test_params = {
            'severity_level': [1, 2, 3, 4, 5],
            'days_lost': [0, 5, 10, 20, 30],
            'employee_count': [50, 100, 200, 500, 1000],
            'compliance_score': [60, 70, 80, 90, 100]
        }
        
        base_prediction = self.predict_incident_costs(incident_data)
        base_cost = base_prediction['total_cost']
        
        for param, values in test_params.items():
            if param not in incident_data:
                continue
            
            param_sensitivity = []
            for value in values:
                test_data = incident_data.copy()
                test_data[param] = value
                
                test_features = self._prepare_prediction_features(test_data)
                test_features_scaled = self.scalers['total_cost'].transform([test_features])
                test_cost = self.models['total_cost'].predict(test_features_scaled)[0]
                
                impact = ((test_cost - base_cost) / base_cost) * 100
                param_sensitivity.append({
                    'value': value,
                    'cost': test_cost,
                    'impact_percent': impact
                })
            
            sensitivity[param] = param_sensitivity
        
        return sensitivity
    
    def _generate_cost_optimization_recommendations(self, incident_data: Dict, 
                                                  predictions: Dict, total_cost: float) -> List[str]:
        """Génère des recommandations d'optimisation des coûts"""
        recommendations = []
        
        # Recommandations basées sur les coûts prédits
        if predictions.get('medical_costs', 0) > 50000:
            recommendations.append("Coûts médicaux élevés - Renforcer la formation aux premiers secours")
            recommendations.append("Investir dans des équipements de protection individuelle de qualité")
        
        if predictions.get('equipment_damage', 0) > 100000:
            recommendations.append("Dommages matériels importants - Programme de maintenance préventive")
            recommendations.append("Mise à jour des équipements obsolètes")
        
        if predictions.get('regulatory_fines', 0) > 20000:
            recommendations.append("Risque d'amendes élevé - Audit de conformité immédiat")
            recommendations.append("Formation réglementaire renforcée")
        
        if predictions.get('insurance_impact', 0) > 50000:
            recommendations.append("Impact assurance important - Négociation des primes")
            recommendations.append("Mise en place d'un programme de prévention des risques")
        
        # Recommandations générales
        if total_cost > 200000:
            recommendations.append("Incident majeur - Plan de gestion de crise")
            recommendations.append("Audit complet du système QHSE")
        elif total_cost > 100000:
            recommendations.append("Incident significatif - Renforcement des contrôles")
            recommendations.append("Formation ciblée sur les risques identifiés")
        
        return recommendations
    
    def _calculate_preventive_roi(self, incident_data: Dict, predicted_cost: float) -> Dict:
        """Calcule le ROI des investissements préventifs"""
        # Coûts préventifs suggérés
        preventive_investments = {
            'formation_securite': 5000,
            'equipements_protection': 10000,
            'maintenance_preventive': 15000,
            'audit_conformite': 8000,
            'systeme_alerte': 12000
        }
        
        # Réduction estimée des coûts (en %)
        cost_reduction = {
            'formation_securite': 0.15,
            'equipements_protection': 0.25,
            'maintenance_preventive': 0.20,
            'audit_conformite': 0.10,
            'systeme_alerte': 0.30
        }
        
        roi_analysis = {}
        
        for investment, cost in preventive_investments.items():
            reduction = cost_reduction[investment]
            savings = predicted_cost * reduction
            roi = (savings - cost) / cost * 100
            payback_period = cost / (savings / 12) if savings > 0 else float('inf')
            
            roi_analysis[investment] = {
                'investment_cost': cost,
                'estimated_savings': savings,
                'roi_percent': roi,
                'payback_period_months': payback_period,
                'recommended': roi > 50 and payback_period < 24
            }
        
        return roi_analysis
    
    def get_cost_trends(self, days: int = 365) -> Dict:
        """Analyse les tendances des coûts"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        # Récupération des incidents
        cursor.execute('''
            SELECT created_at, severity_level, incident_type_id, sector_id
            FROM incident_reports
            WHERE created_at >= ?
            ORDER BY created_at
        ''', (since_date,))
        
        incidents = cursor.fetchall()
        conn.close()
        
        if not incidents:
            return {'error': 'Aucune donnée disponible'}
        
        # Analyse des tendances
        df = pd.DataFrame(incidents, columns=['date', 'severity_level', 'incident_type_id', 'sector_id'])
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        
        # Coûts estimés par mois
        monthly_costs = []
        for month in df['month'].unique():
            month_incidents = df[df['month'] == month]
            total_cost = 0
            
            for _, incident in month_incidents.iterrows():
                incident_data = {
                    'severity_level': incident['severity_level'],
                    'incident_type_id': incident['incident_type_id'],
                    'sector_id': incident['sector_id']
                }
                prediction = self.predict_incident_costs(incident_data)
                total_cost += prediction.get('total_cost', 0)
            
            monthly_costs.append({
                'month': str(month),
                'incident_count': len(month_incidents),
                'estimated_cost': total_cost
            })
        
        return {
            'monthly_trends': monthly_costs,
            'total_estimated_cost': sum(mc['estimated_cost'] for mc in monthly_costs),
            'average_monthly_cost': np.mean([mc['estimated_cost'] for mc in monthly_costs]),
            'trend_direction': 'increasing' if len(monthly_costs) > 1 and 
                             monthly_costs[-1]['estimated_cost'] > monthly_costs[0]['estimated_cost'] else 'stable'
        }
    
    def generate_cost_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Génère un rapport détaillé des coûts"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM incident_reports
            WHERE created_at >= ? AND created_at <= ?
            ORDER BY created_at
        ''', (start_date, end_date))
        
        incidents = cursor.fetchall()
        conn.close()
        
        if not incidents:
            return {'error': 'Aucun incident dans la période'}
        
        # Analyse des coûts
        total_costs = {
            'medical_costs': 0,
            'equipment_damage': 0,
            'regulatory_fines': 0,
            'insurance_impact': 0,
            'productivity_loss': 0,
            'total': 0
        }
        
        cost_breakdown = []
        
        for incident in incidents:
            incident_data = {
                'severity_level': incident[4],  # Ajuster selon votre schéma
                'incident_type_id': incident[2],
                'sector_id': incident[3]
            }
            
            prediction = self.predict_incident_costs(incident_data)
            
            if 'predictions' in prediction:
                for cost_type, cost in prediction['predictions'].items():
                    total_costs[cost_type] += cost
                
                total_costs['total'] += prediction.get('total_cost', 0)
                
                cost_breakdown.append({
                    'incident_id': incident[0],
                    'date': incident[1],
                    'severity': incident[4],
                    'predicted_cost': prediction.get('total_cost', 0),
                    'breakdown': prediction.get('predictions', {})
                })
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days
            },
            'summary': {
                'total_incidents': len(incidents),
                'total_estimated_cost': total_costs['total'],
                'average_cost_per_incident': total_costs['total'] / len(incidents) if incidents else 0,
                'cost_breakdown': total_costs
            },
            'detailed_breakdown': cost_breakdown,
            'recommendations': self._generate_cost_optimization_recommendations(
                {}, total_costs, total_costs['total']
            )
        }

# Instance globale
cost_prediction_engine = CostPredictionEngine('assistant_qhse_ia/database/qhse.db')
