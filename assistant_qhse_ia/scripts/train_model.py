"""
Script d'entraînement des modèles d'IA pour la prédiction des risques QHSE
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import sqlite3
import os
from datetime import datetime

def load_data_from_db():
    """Charge les données depuis la base de données SQLite"""
    conn = sqlite3.connect('assistant_qhse_ia/database/qhse.db')
    
    query = '''
        SELECT 
            ir.severity_level,
            ir.probability_score,
            ir.risk_score,
            s.name as sector,
            it.name as incident_type,
            it.category,
            it.severity_weight,
            strftime('%H', ir.time_incident) as hour,
            strftime('%w', ir.date_incident) as day_of_week
        FROM incident_reports ir
        JOIN sectors s ON ir.sector_id = s.id
        JOIN incident_types it ON ir.incident_type_id = it.id
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def generate_synthetic_data():
    """Génère des données synthétiques pour l'entraînement si pas assez de données"""
    np.random.seed(42)
    
    # Paramètres pour génération de données réalistes
    n_samples = 1000
    
    # Secteurs avec probabilités de risque
    sectors = ['Industrie', 'BTP', 'Agroalimentaire', 'Transport', 'Santé', 'Commerce', 'Bureaux']
    sector_risk_weights = [0.8, 0.9, 0.6, 0.7, 0.5, 0.3, 0.2]
    
    # Types d'incidents avec sévérité
    incident_types = ['Chute', 'Incendie', 'Électrocution', 'Coupure', 'TMS', 'Inhalation', 'Autre']
    incident_severity_weights = [0.7, 0.9, 0.8, 0.4, 0.6, 0.8, 0.3]
    
    data = []
    
    for i in range(n_samples):
        # Sélection aléatoire pondérée
        sector_idx = np.random.choice(len(sectors), p=np.array(sector_risk_weights)/sum(sector_risk_weights))
        incident_idx = np.random.choice(len(incident_types), p=np.array(incident_severity_weights)/sum(incident_severity_weights))
        
        sector = sectors[sector_idx]
        incident_type = incident_types[incident_idx]
        
        # Calcul du score de probabilité basé sur les poids
        base_prob = (sector_risk_weights[sector_idx] + incident_severity_weights[incident_idx]) / 2
        probability_score = np.random.beta(2, 5) * base_prob  # Distribution bêta pour des valeurs réalistes
        
        # Calcul du score de risque
        severity_weight = incident_severity_weights[incident_idx] * 5  # Échelle 1-5
        risk_score = probability_score * severity_weight
        
        # Détermination du niveau de sévérité basé sur le score de risque
        if risk_score >= 3.5:
            severity_level = 'critical'
        elif risk_score >= 2.5:
            severity_level = 'high'
        elif risk_score >= 1.5:
            severity_level = 'medium'
        else:
            severity_level = 'low'
        
        # Heure de travail (6h-18h avec pic vers 10h-14h)
        hour = np.random.choice(range(6, 19), p=[0.05, 0.05, 0.1, 0.15, 0.2, 0.2, 0.15, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05])
        
        # Jour de la semaine (lundi=0, dimanche=6)
        day_of_week = np.random.choice(range(7))
        
        # Catégorie d'incident
        categories = ['physical', 'chemical', 'biological', 'ergonomic', 'psychosocial', 'other']
        category = categories[incident_idx % len(categories)]
        
        data.append({
            'severity_level': severity_level,
            'probability_score': probability_score,
            'risk_score': risk_score,
            'sector': sector,
            'incident_type': incident_type,
            'category': category,
            'severity_weight': severity_weight,
            'hour': hour,
            'day_of_week': day_of_week
        })
    
    return pd.DataFrame(data)

def prepare_features(df):
    """Prépare les features pour l'entraînement"""
    # Encodage des variables catégorielles
    le_sector = LabelEncoder()
    le_incident = LabelEncoder()
    le_category = LabelEncoder()
    le_severity = LabelEncoder()
    
    df['sector_encoded'] = le_sector.fit_transform(df['sector'])
    df['incident_encoded'] = le_incident.fit_transform(df['incident_type'])
    df['category_encoded'] = le_category.fit_transform(df['category'])
    df['severity_encoded'] = le_severity.fit_transform(df['severity_level'])
    
    # Features numériques
    features = [
        'sector_encoded', 'incident_encoded', 'category_encoded',
        'probability_score', 'severity_weight', 'hour', 'day_of_week'
    ]
    
    X = df[features]
    y = df['severity_encoded']
    
    # Sauvegarder les encodeurs
    joblib.dump(le_sector, 'assistant_qhse_ia/modeles/le_sector.joblib')
    joblib.dump(le_incident, 'assistant_qhse_ia/modeles/le_incident.joblib')
    joblib.dump(le_category, 'assistant_qhse_ia/modeles/le_category.joblib')
    joblib.dump(le_severity, 'assistant_qhse_ia/modeles/le_severity.joblib')
    
    return X, y, le_severity

def train_risk_classifier():
    """Entraîne le classificateur de risque"""
    print("🔄 Chargement des données...")
    
    # Essayer de charger depuis la DB, sinon générer des données synthétiques
    try:
        df = load_data_from_db()
        if len(df) < 50:  # Pas assez de données réelles
            print("⚠️  Pas assez de données réelles, génération de données synthétiques...")
            df = generate_synthetic_data()
    except:
        print("⚠️  Base de données non disponible, génération de données synthétiques...")
        df = generate_synthetic_data()
    
    print(f"📊 {len(df)} échantillons chargés")
    
    # Préparation des features
    X, y, le_severity = prepare_features(df)
    
    # Division train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("🤖 Entraînement du modèle Random Forest...")
    
    # Entraînement du modèle
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Évaluation
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"📈 Score d'entraînement: {train_score:.3f}")
    print(f"📈 Score de test: {test_score:.3f}")
    
    # Validation croisée
    cv_scores = cross_val_score(model, X, y, cv=5)
    print(f"📈 Score de validation croisée: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    # Prédictions sur le test set
    y_pred = model.predict(X_test)
    
    print("\n📋 Rapport de classification:")
    print(classification_report(y_test, y_pred, target_names=le_severity.classes_))
    
    # Sauvegarder le modèle
    model_path = 'assistant_qhse_ia/modeles/risk_classifier.joblib'
    joblib.dump(model, model_path)
    
    # Sauvegarder les métadonnées
    metadata = {
        'model_type': 'RandomForestClassifier',
        'training_date': datetime.now().isoformat(),
        'n_samples': len(df),
        'train_score': float(train_score),
        'test_score': float(test_score),
        'cv_score_mean': float(cv_scores.mean()),
        'cv_score_std': float(cv_scores.std()),
        'features': list(X.columns)
    }
    
    joblib.dump(metadata, 'assistant_qhse_ia/modeles/model_metadata.joblib')
    
    print(f"✅ Modèle sauvegardé: {model_path}")
    print("✅ Entraînement terminé!")
    
    return model, le_severity

def create_recommendation_engine():
    """Crée un moteur de recommandations basé sur les règles"""
    
    recommendations = {
        'critical': [
            "🚨 ARRÊT IMMÉDIAT de l'activité",
            "📞 Alerte des secours si nécessaire",
            "👥 Évacuation de la zone",
            "📋 Rapport d'urgence obligatoire",
            "🔍 Investigation approfondie requise"
        ],
        'high': [
            "⚠️ Formation urgente de l'équipe",
            "🛡️ Vérification des EPI",
            "📋 Révision des procédures",
            "👨‍🔧 Inspection de l'équipement",
            "📊 Suivi renforcé recommandé"
        ],
        'medium': [
            "📚 Formation préventive",
            "🔍 Contrôle périodique",
            "📝 Mise à jour des consignes",
            "👥 Sensibilisation des employés",
            "📈 Surveillance continue"
        ],
        'low': [
            "✅ Maintien des procédures",
            "👀 Surveillance de routine",
            "📋 Documentation standard",
            "🔄 Révision périodique"
        ]
    }
    
    # Sauvegarder les recommandations
    joblib.dump(recommendations, 'assistant_qhse_ia/modeles/recommendations.joblib')
    print("✅ Moteur de recommandations créé")

if __name__ == "__main__":
    print("🚀 Démarrage de l'entraînement des modèles QHSE IA")
    print("=" * 50)
    
    # Créer le dossier des modèles
    os.makedirs('assistant_qhse_ia/modeles', exist_ok=True)
    
    # Entraîner le classificateur
    model, le_severity = train_risk_classifier()
    
    # Créer le moteur de recommandations
    create_recommendation_engine()
    
    print("\n🎉 Entraînement terminé avec succès!")
    print("📁 Modèles sauvegardés dans: assistant_qhse_ia/modeles/")
