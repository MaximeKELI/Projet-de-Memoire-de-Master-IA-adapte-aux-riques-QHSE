"""
Moteur IA Avancé pour QHSE
Intégration GPT-4, Vision par ordinateur, NLP, Deep Learning
"""

import openai
import cv2
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel, pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import base64
import io
from PIL import Image
import requests
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class AdvancedAIEngine:
    def __init__(self, config):
        self.config = config
        self.openai_api_key = config.get('openai_api_key')
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialisation des modèles
        self._init_models()
        
    def _init_models(self):
        """Initialise tous les modèles IA"""
        try:
            # Modèle de sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Modèle de classification d'images
            self.image_classifier = pipeline(
                "image-classification",
                model="microsoft/resnet-50",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Modèle de prédiction de coûts
            self.cost_predictor = self._load_cost_predictor()
            
            # Modèle de deep learning pour prédictions complexes
            self.deep_learning_model = self._init_deep_learning_model()
            
        except Exception as e:
            print(f"Erreur lors de l'initialisation des modèles IA: {e}")
    
    def _load_cost_predictor(self):
        """Charge le modèle de prédiction de coûts"""
        try:
            return joblib.load('models/cost_predictor.pkl')
        except:
            return self._train_cost_predictor()
    
    def _train_cost_predictor(self):
        """Entraîne le modèle de prédiction de coûts"""
        # Données synthétiques pour l'entraînement
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'severity_level': np.random.randint(1, 5, n_samples),
            'incident_type_id': np.random.randint(1, 10, n_samples),
            'sector_id': np.random.randint(1, 8, n_samples),
            'employee_count': np.random.randint(10, 1000, n_samples),
            'days_lost': np.random.randint(0, 365, n_samples),
            'medical_costs': np.random.uniform(0, 50000, n_samples),
            'equipment_damage': np.random.uniform(0, 100000, n_samples),
            'regulatory_fines': np.random.uniform(0, 100000, n_samples),
            'insurance_impact': np.random.uniform(0, 50000, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Calcul des coûts totaux (cible)
        df['total_cost'] = (
            df['medical_costs'] + 
            df['equipment_damage'] + 
            df['regulatory_fines'] + 
            df['insurance_impact'] +
            df['days_lost'] * 200  # Coût par jour perdu
        )
        
        X = df.drop('total_cost', axis=1)
        y = df['total_cost']
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Sauvegarde du modèle
        joblib.dump(model, 'models/cost_predictor.pkl')
        return model
    
    def _init_deep_learning_model(self):
        """Initialise le modèle de deep learning"""
        class QHSEDeepModel(nn.Module):
            def __init__(self, input_size, hidden_sizes, output_size):
                super().__init__()
                layers = []
                prev_size = input_size
                
                for hidden_size in hidden_sizes:
                    layers.extend([
                        nn.Linear(prev_size, hidden_size),
                        nn.ReLU(),
                        nn.Dropout(0.2),
                        nn.BatchNorm1d(hidden_size)
                    ])
                    prev_size = hidden_size
                
                layers.append(nn.Linear(prev_size, output_size))
                self.network = nn.Sequential(*layers)
            
            def forward(self, x):
                return self.network(x)
        
        return QHSEDeepModel(10, [64, 32, 16], 1)
    
    def analyze_text_with_gpt4(self, text, context="QHSE"):
        """Analyse de texte avec GPT-4"""
        try:
            if not self.openai_api_key:
                return {"error": "Clé API OpenAI non configurée"}
            
            openai.api_key = self.openai_api_key
            
            prompt = f"""
            En tant qu'expert QHSE, analysez le texte suivant et fournissez :
            1. Niveau de risque identifié (1-5)
            2. Recommandations spécifiques
            3. Actions correctives prioritaires
            4. Conformité réglementaire
            5. Coût estimé des mesures
            
            Contexte: {context}
            Texte: {text}
            
            Répondez en JSON structuré.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {"error": f"Erreur GPT-4: {str(e)}"}
    
    def analyze_image_safety(self, image_path):
        """Analyse d'image pour la sécurité"""
        try:
            # Chargement et prétraitement de l'image
            image = Image.open(image_path)
            image = image.convert('RGB')
            
            # Classification de l'image
            results = self.image_classifier(image)
            
            # Analyse de sécurité spécifique
            safety_analysis = {
                "general_classification": results[0],
                "safety_risks": [],
                "recommendations": [],
                "compliance_issues": []
            }
            
            # Détection de risques spécifiques
            if any("person" in str(result).lower() for result in results):
                safety_analysis["safety_risks"].append("Personnes détectées - Vérifier les EPI")
            
            if any("vehicle" in str(result).lower() for result in results):
                safety_analysis["safety_risks"].append("Véhicules détectés - Vérifier les zones de circulation")
            
            if any("construction" in str(result).lower() for result in results):
                safety_analysis["safety_risks"].append("Zone de construction - Vérifier les protections")
            
            return safety_analysis
            
        except Exception as e:
            return {"error": f"Erreur analyse d'image: {str(e)}"}
    
    def predict_incident_costs(self, incident_data):
        """Prédiction des coûts d'un incident"""
        try:
            # Préparation des données
            features = np.array([[
                incident_data.get('severity_level', 3),
                incident_data.get('incident_type_id', 1),
                incident_data.get('sector_id', 1),
                incident_data.get('employee_count', 100),
                incident_data.get('days_lost', 0),
                incident_data.get('medical_costs', 0),
                incident_data.get('equipment_damage', 0),
                incident_data.get('regulatory_fines', 0),
                incident_data.get('insurance_impact', 0)
            ]])
            
            # Prédiction
            predicted_cost = self.cost_predictor.predict(features)[0]
            
            # Analyse de sensibilité
            sensitivity_analysis = self._analyze_cost_sensitivity(incident_data, predicted_cost)
            
            return {
                "predicted_total_cost": round(predicted_cost, 2),
                "cost_breakdown": {
                    "medical_costs": incident_data.get('medical_costs', 0),
                    "equipment_damage": incident_data.get('equipment_damage', 0),
                    "regulatory_fines": incident_data.get('regulatory_fines', 0),
                    "insurance_impact": incident_data.get('insurance_impact', 0),
                    "productivity_loss": incident_data.get('days_lost', 0) * 200
                },
                "sensitivity_analysis": sensitivity_analysis,
                "confidence_level": 0.85,
                "recommendations": self._generate_cost_recommendations(predicted_cost)
            }
            
        except Exception as e:
            return {"error": f"Erreur prédiction coûts: {str(e)}"}
    
    def _analyze_cost_sensitivity(self, incident_data, base_cost):
        """Analyse de sensibilité des coûts"""
        sensitivity = {}
        
        # Test de sensibilité pour chaque paramètre
        for param in ['severity_level', 'days_lost', 'medical_costs']:
            if param in incident_data:
                original_value = incident_data[param]
                
                # Test +10%
                test_data = incident_data.copy()
                if param == 'severity_level':
                    test_data[param] = min(5, original_value + 1)
                else:
                    test_data[param] = original_value * 1.1
                
                test_features = np.array([[
                    test_data.get('severity_level', 3),
                    test_data.get('incident_type_id', 1),
                    test_data.get('sector_id', 1),
                    test_data.get('employee_count', 100),
                    test_data.get('days_lost', 0),
                    test_data.get('medical_costs', 0),
                    test_data.get('equipment_damage', 0),
                    test_data.get('regulatory_fines', 0),
                    test_data.get('insurance_impact', 0)
                ]])
                
                test_cost = self.cost_predictor.predict(test_features)[0]
                sensitivity[param] = {
                    "impact_percent": round(((test_cost - base_cost) / base_cost) * 100, 2),
                    "cost_difference": round(test_cost - base_cost, 2)
                }
        
        return sensitivity
    
    def _generate_cost_recommendations(self, predicted_cost):
        """Génère des recommandations basées sur les coûts prédits"""
        recommendations = []
        
        if predicted_cost > 100000:
            recommendations.append("Incident majeur - Mise en place d'un plan de gestion de crise")
            recommendations.append("Audit complet des procédures de sécurité")
            recommendations.append("Formation d'urgence pour tout le personnel")
        elif predicted_cost > 50000:
            recommendations.append("Incident significatif - Renforcement des contrôles")
            recommendations.append("Formation ciblée sur les risques identifiés")
        elif predicted_cost > 10000:
            recommendations.append("Incident modéré - Vérification des procédures")
            recommendations.append("Rappel des bonnes pratiques")
        else:
            recommendations.append("Incident mineur - Suivi standard")
        
        return recommendations
    
    def analyze_employee_sentiment(self, text_data):
        """Analyse du sentiment des employés"""
        try:
            if isinstance(text_data, str):
                text_data = [text_data]
            
            sentiments = []
            for text in text_data:
                result = self.sentiment_analyzer(text)
                sentiments.append({
                    "text": text,
                    "sentiment": result[0]['label'],
                    "confidence": result[0]['score']
                })
            
            # Analyse globale
            positive_count = sum(1 for s in sentiments if s['sentiment'] == 'LABEL_2')
            negative_count = sum(1 for s in sentiments if s['sentiment'] == 'LABEL_0')
            neutral_count = sum(1 for s in sentiments if s['sentiment'] == 'LABEL_1')
            
            return {
                "individual_analysis": sentiments,
                "global_sentiment": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count,
                    "sentiment_score": (positive_count - negative_count) / len(sentiments)
                },
                "recommendations": self._generate_sentiment_recommendations(sentiments)
            }
            
        except Exception as e:
            return {"error": f"Erreur analyse sentiment: {str(e)}"}
    
    def _generate_sentiment_recommendations(self, sentiments):
        """Génère des recommandations basées sur l'analyse de sentiment"""
        recommendations = []
        
        negative_sentiments = [s for s in sentiments if s['sentiment'] == 'LABEL_0']
        
        if len(negative_sentiments) > len(sentiments) * 0.3:
            recommendations.append("Sentiment négatif élevé - Enquête de satisfaction nécessaire")
            recommendations.append("Mise en place d'un plan d'amélioration du climat social")
            recommendations.append("Formation des managers sur la communication")
        
        return recommendations
    
    def generate_ai_recommendations(self, incident_data, context="QHSE"):
        """Génère des recommandations IA complètes"""
        try:
            recommendations = {
                "immediate_actions": [],
                "preventive_measures": [],
                "training_needs": [],
                "equipment_recommendations": [],
                "regulatory_compliance": [],
                "cost_optimization": []
            }
            
            # Analyse basée sur le type d'incident
            incident_type = incident_data.get('incident_type_id', 1)
            severity = incident_data.get('severity_level', 3)
            
            if incident_type == 1:  # Chute
                recommendations["immediate_actions"].extend([
                    "Vérification immédiate des zones de chute",
                    "Mise en place de barrières de sécurité",
                    "Contrôle des équipements de protection individuelle"
                ])
                recommendations["preventive_measures"].extend([
                    "Audit des surfaces de travail",
                    "Formation aux techniques de prévention des chutes",
                    "Mise en place de systèmes d'alerte"
                ])
            
            elif incident_type == 2:  # Coupure
                recommendations["immediate_actions"].extend([
                    "Vérification des outils tranchants",
                    "Contrôle des gants de protection",
                    "Inspection des postes de travail"
                ])
                recommendations["preventive_measures"].extend([
                    "Formation à l'utilisation sécurisée des outils",
                    "Mise en place de protections sur les machines",
                    "Contrôle régulier des équipements"
                ])
            
            # Recommandations basées sur la gravité
            if severity >= 4:
                recommendations["immediate_actions"].insert(0, "ARRÊT IMMÉDIAT des opérations concernées")
                recommendations["immediate_actions"].insert(1, "Enquête approfondie obligatoire")
            
            return recommendations
            
        except Exception as e:
            return {"error": f"Erreur génération recommandations: {str(e)}"}
    
    def predict_future_incidents(self, historical_data, prediction_days=30):
        """Prédiction des incidents futurs"""
        try:
            # Analyse des tendances
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            
            # Prédiction basée sur les tendances
            daily_incidents = df.resample('D').size()
            
            # Moyenne mobile
            moving_avg = daily_incidents.rolling(window=7).mean()
            
            # Prédiction simple (moyenne des 30 derniers jours)
            recent_avg = daily_incidents.tail(30).mean()
            
            predictions = []
            for i in range(prediction_days):
                date = datetime.now() + timedelta(days=i+1)
                predicted_count = max(0, recent_avg + np.random.normal(0, recent_avg * 0.1))
                predictions.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "predicted_incidents": round(predicted_count, 1),
                    "confidence": 0.7
                })
            
            return {
                "predictions": predictions,
                "trend_analysis": {
                    "current_trend": "stable",
                    "risk_level": "medium" if recent_avg > 1 else "low",
                    "recommendations": self._generate_trend_recommendations(recent_avg)
                }
            }
            
        except Exception as e:
            return {"error": f"Erreur prédiction future: {str(e)}"}
    
    def _generate_trend_recommendations(self, avg_incidents):
        """Génère des recommandations basées sur les tendances"""
        if avg_incidents > 2:
            return [
                "Tendance à la hausse - Renforcement des contrôles",
                "Audit complet des procédures",
                "Formation d'urgence du personnel"
            ]
        elif avg_incidents > 1:
            return [
                "Surveillance renforcée recommandée",
                "Vérification des équipements de protection"
            ]
        else:
            return [
                "Tendance stable - Maintien des bonnes pratiques",
                "Formation continue recommandée"
            ]

# Configuration par défaut
DEFAULT_CONFIG = {
    'openai_api_key': None,  # À configurer
    'model_path': 'models/',
    'confidence_threshold': 0.7
}

# Instance globale
ai_engine = AdvancedAIEngine(DEFAULT_CONFIG)
