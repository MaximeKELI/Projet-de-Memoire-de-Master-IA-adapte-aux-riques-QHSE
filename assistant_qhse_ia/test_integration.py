#!/usr/bin/env python3
"""
Script de test d'intégration pour l'Assistant QHSE IA
Vérifie que tous les composants fonctionnent correctement
"""

import os
import sys
import sqlite3
import requests
import time
import subprocess
from pathlib import Path

def test_database():
    """Test de la base de données"""
    print("🗄️  Test de la base de données...")
    
    try:
        conn = sqlite3.connect('assistant_qhse_ia/database/qhse.db')
        cursor = conn.cursor()
        
        # Vérifier les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['users', 'sectors', 'incident_types', 'incident_reports', 'corrective_actions']
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            print(f"❌ Tables manquantes: {missing_tables}")
            return False
        
        # Vérifier les données
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sectors")
        sector_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM incident_reports")
        incident_count = cursor.fetchone()[0]
        
        print(f"✅ Tables créées: {len(tables)}")
        print(f"✅ Utilisateurs: {user_count}")
        print(f"✅ Secteurs: {sector_count}")
        print(f"✅ Incidents: {incident_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        return False

def test_ml_models():
    """Test des modèles d'IA"""
    print("🤖 Test des modèles d'IA...")
    
    try:
        import joblib
        
        # Vérifier les fichiers de modèles
        model_files = [
            'assistant_qhse_ia/modeles/risk_classifier.joblib',
            'assistant_qhse_ia/modeles/le_sector.joblib',
            'assistant_qhse_ia/modeles/le_incident.joblib',
            'assistant_qhse_ia/modeles/recommendations.joblib'
        ]
        
        missing_files = []
        for file_path in model_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Fichiers de modèles manquants: {missing_files}")
            return False
        
        # Tester le chargement du modèle principal
        model = joblib.load('assistant_qhse_ia/modeles/risk_classifier.joblib')
        print(f"✅ Modèle chargé: {type(model).__name__}")
        
        # Tester une prédiction
        test_features = [1, 2, 0.5, 10, 1]  # Exemple de features
        prediction = model.predict([test_features])
        print(f"✅ Prédiction test: {prediction[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur modèles IA: {e}")
        return False

def test_flask_app():
    """Test de l'application Flask"""
    print("🌐 Test de l'application Flask...")
    
    try:
        # Importer l'app Flask
        sys.path.append('.')
        from app import app
        
        # Tester en mode test
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Test des routes principales
        routes_to_test = [
            ('/', 'GET'),
            ('/login', 'GET'),
            ('/dashboard', 'GET'),
            ('/api/statistics', 'GET')
        ]
        
        for route, method in routes_to_test:
            if method == 'GET':
                response = client.get(route)
            else:
                response = client.post(route)
            
            if response.status_code not in [200, 302]:  # 302 pour les redirections
                print(f"❌ Route {route} retourne {response.status_code}")
                return False
        
        print("✅ Routes Flask fonctionnelles")
        return True
        
    except Exception as e:
        print(f"❌ Erreur Flask: {e}")
        return False

def test_api_endpoints():
    """Test des endpoints API"""
    print("🔌 Test des endpoints API...")
    
    try:
        # Démarrer le serveur en arrière-plan
        process = subprocess.Popen([sys.executable, 'app.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Attendre que le serveur démarre
        time.sleep(5)
        
        base_url = 'http://localhost:5000'
        
        # Test des endpoints
        endpoints = [
            '/api/statistics',
            '/api/incidents'
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code not in [200, 401]:  # 401 pour auth required
                    print(f"❌ Endpoint {endpoint} retourne {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"❌ Erreur requête {endpoint}: {e}")
                return False
        
        print("✅ Endpoints API fonctionnels")
        
        # Arrêter le serveur
        process.terminate()
        return True
        
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False

def test_frontend_files():
    """Test des fichiers frontend"""
    print("🎨 Test des fichiers frontend...")
    
    try:
        frontend_files = [
            'assistant_qhse_ia/interface/templates/dashboard.html',
            'assistant_qhse_ia/interface/templates/chatbot.html',
            'assistant_qhse_ia/interface/templates/form.html',
            'assistant_qhse_ia/interface/templates/login.html',
            'assistant_qhse_ia/interface/templates/conseil_IA.html'
        ]
        
        missing_files = []
        for file_path in frontend_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Fichiers frontend manquants: {missing_files}")
            return False
        
        # Vérifier le contenu des fichiers
        for file_path in frontend_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) < 100:  # Fichier trop petit
                    print(f"❌ Fichier {file_path} semble vide ou corrompu")
                    return False
        
        print("✅ Fichiers frontend présents et valides")
        return True
        
    except Exception as e:
        print(f"❌ Erreur frontend: {e}")
        return False

def run_integration_tests():
    """Lance tous les tests d'intégration"""
    print("🧪 Tests d'intégration - Assistant QHSE IA")
    print("=" * 50)
    
    tests = [
        ("Base de données", test_database),
        ("Modèles IA", test_ml_models),
        ("Application Flask", test_flask_app),
        ("Fichiers Frontend", test_frontend_files),
        ("Endpoints API", test_api_endpoints)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSÉ")
            else:
                print(f"❌ {test_name}: ÉCHEC")
        except Exception as e:
            print(f"❌ {test_name}: ERREUR - {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHEC"
        print(f"{test_name:<20} {status}")
    
    print(f"\nRésultat global: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! L'application est prête.")
        return True
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
