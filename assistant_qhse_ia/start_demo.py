#!/usr/bin/env python3
"""
Script de démonstration du système QHSE IA
Lance le serveur et ouvre les pages dans le navigateur
"""

import subprocess
import time
import webbrowser
import sys
import os
import signal

def start_server():
    """Démarre le serveur Flask"""
    print("🚀 Démarrage du serveur QHSE IA...")
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists("minimal_app.py"):
        print("❌ Fichier minimal_app.py non trouvé!")
        return None
    
    try:
        # Démarrer le serveur
        process = subprocess.Popen([
            "python3", "minimal_app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ Attente du démarrage du serveur...")
        time.sleep(3)
        
        # Vérifier que le processus fonctionne
        if process.poll() is None:
            print("✅ Serveur démarré avec succès!")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Erreur démarrage serveur:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_server():
    """Teste si le serveur répond"""
    print("🔍 Test de connexion au serveur...")
    
    try:
        import requests
        response = requests.get("http://localhost:5001", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur accessible!")
            return True
        else:
            print(f"⚠️  Serveur répond avec le code: {response.status_code}")
            return False
    except ImportError:
        print("⚠️  Module requests non disponible, test avec curl...")
        try:
            result = subprocess.run(["curl", "-s", "-I", "http://localhost:5001"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Serveur accessible via curl!")
                return True
            else:
                print("❌ Serveur non accessible")
                return False
        except Exception as e:
            print(f"❌ Erreur test curl: {e}")
            return False
    except Exception as e:
        print(f"❌ Erreur test serveur: {e}")
        return False

def open_pages():
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
            print(f"  📄 Ouverture: {name}")
            webbrowser.open(url)
            time.sleep(1)  # Délai entre les ouvertures
        except Exception as e:
            print(f"  ❌ Erreur ouverture {name}: {e}")

def signal_handler(sig, frame):
    """Gestionnaire de signal pour arrêter proprement"""
    print("\n🛑 Arrêt du serveur...")
    sys.exit(0)

def main():
    """Fonction principale"""
    print("="*60)
    print("🎯 DÉMONSTRATION SYSTÈME QHSE IA")
    print("="*60)
    
    # Gestionnaire de signal
    signal.signal(signal.SIGINT, signal_handler)
    
    # Démarrer le serveur
    server_process = start_server()
    if not server_process:
        print("❌ Impossible de démarrer le serveur")
        return False
    
    try:
        # Tester le serveur
        if not test_server():
            print("❌ Serveur non accessible")
            return False
        
        # Ouvrir les pages
        open_pages()
        
        print("\n" + "="*60)
        print("✅ DÉMONSTRATION PRÊTE!")
        print("="*60)
        print("🌐 Le serveur est accessible sur: http://localhost:5000")
        print("📊 Dashboard: http://localhost:5000/dashboard")
        print("🎨 Dashboard Animé: http://localhost:5000/dashboard_animated")
        print("🔐 Connexion Animée: http://localhost:5000/login_animated")
        print("📋 Formulaire Animé: http://localhost:5000/form_animated")
        print("🤖 Chatbot: http://localhost:5000/chatbot")
        print("📋 Formulaire: http://localhost:5000/form")
        print("="*60)
        print("💡 Appuyez sur Ctrl+C pour arrêter le serveur")
        print("="*60)
        
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
        print(f"❌ Erreur: {e}")
        if server_process:
            server_process.terminate()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
