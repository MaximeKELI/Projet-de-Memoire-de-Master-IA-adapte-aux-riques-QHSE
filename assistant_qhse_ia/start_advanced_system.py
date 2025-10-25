#!/usr/bin/env python3
"""
Script de démarrage du système QHSE IA avancé
Initialise tous les modules et démarre l'application
"""

import os
import sys
import subprocess
import time
import sqlite3
from datetime import datetime

def print_banner():
    """Affiche la bannière de démarrage"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    ASSISTANT QHSE IA                        ║
    ║                   SYSTÈME AVANCÉ v2.0                       ║
    ║                                                              ║
    ║  🚀 Fonctionnalités Avancées:                               ║
    ║     • IA Avancée (GPT-4, Vision, NLP, Deep Learning)        ║
    ║     • IoT et Capteurs Intelligents                          ║
    ║     • Blockchain pour Traçabilité                           ║
    ║     • Gamification QHSE                                     ║
    ║     • AR/VR pour Formation                                  ║
    ║     • Prédiction des Coûts                                  ║
    ║     • Gestion des Fournisseurs                              ║
    ║     • API GraphQL                                           ║
    ║     • Analytics Prédictifs                                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Vérifie la version de Python"""
    if sys.version_info < (3.8, 0):
        print("❌ Python 3.8+ requis. Version actuelle:", sys.version)
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} détecté")

def install_dependencies():
    """Installe les dépendances"""
    print("\n📦 Installation des dépendances...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dépendances installées avec succès")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation dépendances: {e}")
        return False
    return True

def create_directories():
    """Crée les répertoires nécessaires"""
    directories = [
        "models",
        "models/cost_prediction",
        "temp",
        "logs",
        "uploads",
        "exports",
        "backups"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Répertoire créé: {directory}")

def initialize_database():
    """Initialise la base de données"""
    print("\n🗄️ Initialisation de la base de données...")
    try:
        # Exécution du script d'initialisation
        from database.init_db import init_database
        init_database()
        print("✅ Base de données initialisée")
    except Exception as e:
        print(f"❌ Erreur initialisation base de données: {e}")
        return False
    return True

def train_ai_models():
    """Entraîne les modèles IA"""
    print("\n🤖 Entraînement des modèles IA...")
    try:
        # Entraînement du modèle de base
        from scripts.train_model import train_model
        train_model()
        
        # Entraînement du modèle de prédiction des coûts
        from analytics.cost_prediction_engine import cost_prediction_engine
        cost_prediction_engine.train_models()
        
        print("✅ Modèles IA entraînés")
    except Exception as e:
        print(f"⚠️ Avertissement entraînement modèles: {e}")
        print("Les modèles seront entraînés au premier usage")

def initialize_iot_system():
    """Initialise le système IoT"""
    print("\n🌐 Initialisation du système IoT...")
    try:
        from iot.sensor_manager import iot_manager
        
        # Ajout de capteurs de démonstration
        demo_sensors = [
            ("temp_001", "Capteur Température Zone A", "temperature", "Zone A", "Production"),
            ("humidity_001", "Capteur Humidité Zone B", "humidity", "Zone B", "Production"),
            ("noise_001", "Capteur Bruit Zone C", "noise", "Zone C", "Production"),
            ("gas_001", "Détecteur Gaz Zone D", "gas", "Zone D", "Production"),
            ("vibration_001", "Capteur Vibration Machine 1", "vibration", "Machine 1", "Maintenance")
        ]
        
        for sensor_id, name, sensor_type, location, zone in demo_sensors:
            iot_manager.add_sensor(sensor_id, name, sensor_type, location, zone)
        
        # Démarrage du monitoring
        iot_manager.start_monitoring()
        print("✅ Système IoT initialisé avec capteurs de démonstration")
    except Exception as e:
        print(f"⚠️ Avertissement système IoT: {e}")

def initialize_gamification():
    """Initialise le système de gamification"""
    print("\n🎮 Initialisation du système de gamification...")
    try:
        from gamification.qhse_gamification import gamification_system
        
        # Création de profils de démonstration
        demo_users = [
            (1, "admin", "Administrateur"),
            (2, "manager", "Manager QHSE"),
            (3, "employee", "Employé"),
            (4, "auditor", "Auditeur"),
            (5, "trainer", "Formateur")
        ]
        
        for user_id, username, role in demo_users:
            gamification_system.create_user_profile(user_id, username)
        
        print("✅ Système de gamification initialisé")
    except Exception as e:
        print(f"⚠️ Avertissement gamification: {e}")

def initialize_blockchain():
    """Initialise le système blockchain"""
    print("\n⛓️ Initialisation du système blockchain...")
    try:
        from blockchain.qhse_blockchain import qhse_blockchain
        
        # Vérification de la validité de la chaîne
        if qhse_blockchain.is_chain_valid():
            print("✅ Système blockchain initialisé et valide")
        else:
            print("⚠️ Chaîne blockchain invalide, recréation...")
            qhse_blockchain._create_genesis_block()
    except Exception as e:
        print(f"⚠️ Avertissement blockchain: {e}")

def initialize_arvr():
    """Initialise le système AR/VR"""
    print("\n🥽 Initialisation du système AR/VR...")
    try:
        from ar_vr.qhse_ar_vr import ar_vr_system
        print(f"✅ {len(ar_vr_system.scenes)} scènes AR/VR chargées")
    except Exception as e:
        print(f"⚠️ Avertissement AR/VR: {e}")

def initialize_suppliers():
    """Initialise le système de gestion des fournisseurs"""
    print("\n🏢 Initialisation du système fournisseurs...")
    try:
        from suppliers.supplier_management import supplier_management
        
        # Ajout de fournisseurs de démonstration
        demo_suppliers = [
            ("Fournisseur Sécurité Pro", "Jean Dupont", "jean.dupont@securitepro.fr", 
             "01 23 45 67 89", "123 Rue de la Sécurité, Paris", "France", "Équipements de sécurité"),
            ("Protection Plus", "Marie Martin", "marie.martin@protectionplus.com", 
             "01 98 76 54 32", "456 Avenue de la Protection, Lyon", "France", "Vêtements de protection"),
            ("Formation QHSE Expert", "Pierre Durand", "pierre.durand@qhse-expert.fr", 
             "01 11 22 33 44", "789 Boulevard de la Formation, Marseille", "France", "Formation QHSE")
        ]
        
        for name, contact, email, phone, address, country, business_type in demo_suppliers:
            supplier_management.add_supplier(name, contact, email, phone, address, country, business_type)
        
        print("✅ Système fournisseurs initialisé avec données de démonstration")
    except Exception as e:
        print(f"⚠️ Avertissement fournisseurs: {e}")

def start_application():
    """Démarre l'application Flask"""
    print("\n🚀 Démarrage de l'application...")
    print("\n" + "="*60)
    print("🌐 Application accessible sur: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000/dashboard")
    print("🎨 Dashboard Animé: http://localhost:5000/dashboard_animated")
    print("🔐 Connexion Animée: http://localhost:5000/login_animated")
    print("📋 Formulaire Animé: http://localhost:5000/form_animated")
    print("🤖 Chatbot: http://localhost:5000/chatbot")
    print("📋 Formulaire: http://localhost:5000/form")
    print("👨‍💼 Admin: http://localhost:5000/admin")
    print("📱 Mobile: http://localhost:5000/mobile")
    print("🔗 GraphQL: http://localhost:5000/graphql")
    print("="*60)
    print("\n💡 Appuyez sur Ctrl+C pour arrêter l'application")
    print("="*60)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt de l'application...")
    except Exception as e:
        print(f"\n❌ Erreur démarrage application: {e}")

def main():
    """Fonction principale"""
    print_banner()
    
    # Vérifications préliminaires
    check_python_version()
    
    # Installation des dépendances
    if not install_dependencies():
        print("❌ Impossible de continuer sans les dépendances")
        sys.exit(1)
    
    # Création des répertoires
    create_directories()
    
    # Initialisation de la base de données
    if not initialize_database():
        print("❌ Impossible de continuer sans la base de données")
        sys.exit(1)
    
    # Entraînement des modèles IA
    train_ai_models()
    
    # Initialisation des systèmes avancés
    initialize_iot_system()
    initialize_gamification()
    initialize_blockchain()
    initialize_arvr()
    initialize_suppliers()
    
    print("\n✅ Tous les systèmes initialisés avec succès!")
    
    # Démarrage de l'application
    start_application()

if __name__ == "__main__":
    main()
