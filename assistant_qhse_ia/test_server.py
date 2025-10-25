#!/usr/bin/env python3
"""
Script de test du serveur QHSE IA
"""

import requests
import time
import webbrowser
import subprocess
import sys
import os

def test_server_connection():
    """Teste la connexion au serveur"""
    print("🔍 Test de connexion au serveur...")
    
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:5000", timeout=5)
            if response.status_code == 200:
                print("✅ Serveur accessible!")
                return True
        except requests.exceptions.ConnectionError:
            print(f"⏳ Tentative {attempt + 1}/{max_attempts} - Serveur non accessible, attente...")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    print("❌ Impossible de se connecter au serveur")
    return False

def test_api_endpoints():
    """Teste les endpoints API"""
    print("\n🔍 Test des endpoints API...")
    
    endpoints = [
        ("/api/statistics", "GET"),
        ("/api/dashboard/advanced-stats", "GET"),
        ("/api/incidents", "GET")
    ]
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
            else:
                response = requests.post(f"http://localhost:5000{endpoint}", timeout=5)
            
            if response.status_code in [200, 201]:
                print(f"✅ {method} {endpoint} - OK")
            else:
                print(f"⚠️  {method} {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"❌ {method} {endpoint} - Erreur: {e}")

def open_browser_pages():
    """Ouvre les pages dans le navigateur"""
    print("\n🌐 Ouverture des pages dans le navigateur...")
    
    pages = [
        ("Dashboard Principal", "http://localhost:5000/dashboard"),
        ("Dashboard Animé", "http://localhost:5000/dashboard_animated"),
        ("Connexion Animée", "http://localhost:5000/login_animated"),
        ("Formulaire Animé", "http://localhost:5000/form_animated"),
        ("Chatbot", "http://localhost:5000/chatbot"),
        ("Formulaire", "http://localhost:5000/form")
    ]
    
    for name, url in pages:
        try:
            print(f"Ouverture: {name}")
            webbrowser.open(url)
            time.sleep(1)  # Délai entre les ouvertures
        except Exception as e:
            print(f"❌ Erreur ouverture {name}: {e}")

def start_server():
    """Démarre le serveur"""
    print("🚀 Démarrage du serveur QHSE IA...")
    
    try:
        # Démarrer le serveur en arrière-plan
        process = subprocess.Popen([
            "python3", "app_simple.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ Attente du démarrage du serveur...")
        time.sleep(5)
        
        return process
    except Exception as e:
        print(f"❌ Erreur démarrage serveur: {e}")
        return None

def main():
    """Fonction principale"""
    print("="*60)
    print("🧪 TEST DU SERVEUR QHSE IA")
    print("="*60)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists("app_simple.py"):
        print("❌ Fichier app_simple.py non trouvé!")
        print("💡 Assurez-vous d'être dans le répertoire assistant_qhse_ia")
        return False
    
    # Démarrer le serveur
    server_process = start_server()
    if not server_process:
        return False
    
    try:
        # Tester la connexion
        if not test_server_connection():
            print("❌ Serveur non accessible")
            return False
        
        # Tester les APIs
        test_api_endpoints()
        
        # Ouvrir les pages
        open_browser_pages()
        
        print("\n✅ Tests terminés avec succès!")
        print("🌐 Le serveur est accessible sur http://localhost:5000")
        print("💡 Appuyez sur Ctrl+C pour arrêter le serveur")
        
        # Attendre que l'utilisateur arrête
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du serveur...")
            server_process.terminate()
            print("✅ Serveur arrêté")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        if server_process:
            server_process.terminate()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
