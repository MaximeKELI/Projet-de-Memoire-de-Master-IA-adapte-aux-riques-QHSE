#!/usr/bin/env python3
"""
Script de démarrage pour l'Assistant QHSE IA
Initialise la base de données et lance le serveur Flask
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Vérifie que Python 3.8+ est utilisé"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou supérieur est requis")
        print(f"Version actuelle: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} détecté")

def install_requirements():
    """Installe les dépendances Python"""
    print("📦 Installation des dépendances...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dépendances installées avec succès")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation des dépendances: {e}")
        sys.exit(1)

def initialize_database():
    """Initialise la base de données"""
    print("🗄️  Initialisation de la base de données...")
    try:
        from database.init_db import init_database
        init_database()
        print("✅ Base de données initialisée")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
        sys.exit(1)

def train_models():
    """Entraîne les modèles d'IA"""
    print("🤖 Entraînement des modèles d'IA...")
    try:
        from scripts.train_model import train_risk_classifier, create_recommendation_engine
        train_risk_classifier()
        create_recommendation_engine()
        print("✅ Modèles d'IA entraînés")
    except Exception as e:
        print(f"⚠️  Erreur lors de l'entraînement des modèles: {e}")
        print("L'application fonctionnera avec des prédictions par défaut")

def start_server():
    """Démarre le serveur Flask"""
    print("🚀 Démarrage du serveur Flask...")
    print("=" * 50)
    print("🌐 Application disponible sur: http://localhost:5000")
    print("👤 Compte de démonstration: admin / admin")
    print("=" * 50)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Arrêt du serveur")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du serveur: {e}")
        sys.exit(1)

def main():
    """Fonction principale"""
    print("🏗️  Assistant QHSE IA - Démarrage")
    print("=" * 50)
    
    # Vérifications préliminaires
    check_python_version()
    
    # Installation des dépendances
    if not os.path.exists("venv") and "--no-install" not in sys.argv:
        install_requirements()
    
    # Initialisation de la base de données
    if not os.path.exists("assistant_qhse_ia/database/qhse.db") or "--force-init" in sys.argv:
        initialize_database()
    else:
        print("✅ Base de données existante trouvée")
    
    # Entraînement des modèles
    if not os.path.exists("assistant_qhse_ia/modeles/risk_classifier.joblib") or "--force-train" in sys.argv:
        train_models()
    else:
        print("✅ Modèles d'IA existants trouvés")
    
    # Démarrage du serveur
    start_server()

if __name__ == "__main__":
    main()
