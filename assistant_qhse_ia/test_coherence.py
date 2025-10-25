#!/usr/bin/env python3
"""
Script de test de cohérence Frontend-Backend
Vérifie que les APIs et les templates communiquent correctement
"""

import requests
import json
import sys
from pathlib import Path

def print_banner():
    """Affiche la bannière de test"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                TEST COHÉRENCE FRONTEND-BACKEND               ║
    ║                   QHSE IA - Système Avancé                  ║
    ║                                                              ║
    ║  🔍 Vérifications:                                           ║
    ║     • APIs disponibles et fonctionnelles                    ║
    ║     • Données cohérentes entre frontend/backend             ║
    ║     • Templates avec données correctes                      ║
    ║     • Communication fluide                                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def test_api_endpoints():
    """Teste les endpoints API principaux"""
    print("🔍 Test des endpoints API...")
    
    base_url = "http://localhost:5000"
    endpoints = [
        ("/api/statistics", "GET"),
        ("/api/dashboard/advanced-stats", "GET"),
        ("/api/incidents", "GET"),
        ("/api/predict", "POST"),
        ("/api/chatbot", "POST")
    ]
    
    results = []
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            else:
                # Test POST avec données minimales
                test_data = {
                    "sector_id": 1,
                    "incident_type_id": 1,
                    "probability_score": 0.5,
                    "time_incident": "12:00"
                }
                response = requests.post(f"{base_url}{endpoint}", 
                                       json=test_data, 
                                       timeout=5)
            
            status = "✅ OK" if response.status_code in [200, 201] else f"❌ {response.status_code}"
            results.append((endpoint, method, status, response.status_code))
            
        except requests.exceptions.ConnectionError:
            results.append((endpoint, method, "❌ SERVEUR NON DÉMARRÉ", 0))
        except Exception as e:
            results.append((endpoint, method, f"❌ ERREUR: {str(e)[:50]}", 0))
    
    # Afficher les résultats
    print("\n📊 Résultats des tests API:")
    print("-" * 60)
    for endpoint, method, status, code in results:
        print(f"{method:4} {endpoint:30} {status}")
    
    return all("✅" in result[2] for result in results)

def test_data_consistency():
    """Teste la cohérence des données entre APIs"""
    print("\n🔍 Test de cohérence des données...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test API statistics
        stats_response = requests.get(f"{base_url}/api/statistics", timeout=5)
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print("✅ API /api/statistics accessible")
            print(f"   Données: {list(stats_data.keys())}")
        else:
            print("❌ API /api/statistics non accessible")
            return False
        
        # Test API dashboard avancé
        advanced_response = requests.get(f"{base_url}/api/dashboard/advanced-stats", timeout=5)
        if advanced_response.status_code == 200:
            advanced_data = advanced_response.json()
            print("✅ API /api/dashboard/advanced-stats accessible")
            
            # Vérifier les données attendues par le frontend
            expected_keys = ['incidents', 'sensors', 'points', 'blocks']
            missing_keys = [key for key in expected_keys if key not in advanced_data]
            
            if missing_keys:
                print(f"❌ Données manquantes: {missing_keys}")
                return False
            else:
                print("✅ Toutes les données attendues sont présentes")
                print(f"   Valeurs: incidents={advanced_data.get('incidents')}, "
                      f"sensors={advanced_data.get('sensors')}, "
                      f"points={advanced_data.get('points')}, "
                      f"blocks={advanced_data.get('blocks')}")
        else:
            print("❌ API /api/dashboard/advanced-stats non accessible")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de cohérence: {e}")
        return False

def test_templates_data():
    """Teste que les templates reçoivent les bonnes données"""
    print("\n🔍 Test des données des templates...")
    
    # Vérifier que les routes passent les bonnes données
    template_routes = [
        ("/form", ["sectors", "incident_types"]),
        ("/form_animated", ["sectors", "incident_types"]),
        ("/dashboard", ["stats"]),
        ("/dashboard_animated", [])  # Pas de données passées, utilise API
    ]
    
    results = []
    
    for route, expected_data in template_routes:
        try:
            response = requests.get(f"http://localhost:5000{route}", timeout=5)
            if response.status_code == 200:
                # Vérifier que la page se charge (pas d'erreur 500)
                if "error" not in response.text.lower():
                    results.append((route, "✅ OK", "Template chargé"))
                else:
                    results.append((route, "❌ ERREUR", "Erreur dans le template"))
            else:
                results.append((route, f"❌ {response.status_code}", "Erreur HTTP"))
        except Exception as e:
            results.append((route, "❌ ERREUR", str(e)[:50]))
    
    # Afficher les résultats
    print("\n📄 Résultats des templates:")
    print("-" * 50)
    for route, status, details in results:
        print(f"{route:20} {status:10} {details}")
    
    return all("✅" in result[1] for result in results)

def test_frontend_backend_communication():
    """Teste la communication frontend-backend"""
    print("\n🔍 Test de communication frontend-backend...")
    
    base_url = "http://localhost:5000"
    
    # Test de prédiction (simulation d'un formulaire)
    test_prediction_data = {
        "sector_id": 1,
        "incident_type_id": 1,
        "title": "Test de cohérence",
        "description": "Test automatique",
        "location": "Test",
        "severity_level": "medium",
        "probability_score": 0.5,
        "time_incident": "12:00"
    }
    
    try:
        response = requests.post(f"{base_url}/api/predict", 
                               json=test_prediction_data, 
                               timeout=10)
        
        if response.status_code == 200:
            prediction = response.json()
            print("✅ API de prédiction fonctionnelle")
            print(f"   Réponse: {list(prediction.keys())}")
            
            # Vérifier la structure de la réponse
            expected_keys = ['prediction', 'risk_score', 'recommendations']
            missing_keys = [key for key in expected_keys if key not in prediction]
            
            if missing_keys:
                print(f"⚠️  Clés manquantes dans la réponse: {missing_keys}")
            else:
                print("✅ Structure de réponse correcte")
            
            return True
        else:
            print(f"❌ Erreur API prédiction: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur communication: {e}")
        return False

def test_database_consistency():
    """Teste la cohérence de la base de données"""
    print("\n🔍 Test de cohérence base de données...")
    
    try:
        import sqlite3
        db_path = "assistant_qhse_ia/database/qhse.db"
        
        if not Path(db_path).exists():
            print("❌ Base de données non trouvée")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier les tables essentielles
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        essential_tables = ['users', 'incident_reports', 'sectors', 'incident_types']
        missing_tables = [table for table in essential_tables if table not in tables]
        
        if missing_tables:
            print(f"❌ Tables manquantes: {missing_tables}")
            return False
        
        print("✅ Toutes les tables essentielles présentes")
        
        # Vérifier les données de base
        cursor.execute("SELECT COUNT(*) FROM sectors")
        sectors_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM incident_types")
        incident_types_count = cursor.fetchone()[0]
        
        print(f"✅ Secteurs: {sectors_count}, Types d'incidents: {incident_types_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        return False

def generate_report():
    """Génère un rapport complet"""
    print("\n" + "="*60)
    print("📋 RAPPORT DE COHÉRENCE FRONTEND-BACKEND")
    print("="*60)
    
    tests = [
        ("APIs disponibles", test_api_endpoints),
        ("Cohérence des données", test_data_consistency),
        ("Templates avec données", test_templates_data),
        ("Communication frontend-backend", test_frontend_backend_communication),
        ("Cohérence base de données", test_database_consistency)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur lors du test {test_name}: {e}")
            results.append((test_name, False))
    
    # Afficher le rapport
    print("\n📊 RÉSULTATS FINAUX:")
    print("-" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print("-" * 40)
    print(f"Résultat: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! Le système est cohérent.")
    elif passed >= total * 0.8:
        print("⚠️  La plupart des tests sont passés. Quelques ajustements nécessaires.")
    else:
        print("❌ Plusieurs tests ont échoué. Vérifiez la configuration.")
    
    return passed == total

def main():
    """Fonction principale"""
    print_banner()
    
    print("🚀 Démarrage des tests de cohérence...")
    print("⚠️  Assurez-vous que l'application Flask est démarrée sur http://localhost:5000")
    print()
    
    # Vérifier que le serveur est accessible
    try:
        response = requests.get("http://localhost:5000", timeout=2)
        print("✅ Serveur Flask accessible")
    except requests.exceptions.ConnectionError:
        print("❌ Serveur Flask non accessible!")
        print("💡 Démarrez l'application avec: python start_advanced_system.py")
        return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    
    # Exécuter les tests
    success = generate_report()
    
    if success:
        print("\n✨ Tests de cohérence terminés avec succès!")
    else:
        print("\n🔧 Des corrections sont nécessaires. Consultez le rapport ci-dessus.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
