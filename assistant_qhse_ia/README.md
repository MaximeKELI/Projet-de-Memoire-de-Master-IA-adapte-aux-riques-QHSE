# Assistant QHSE IA 🤖

Un système d'intelligence artificielle complet pour la gestion des risques en Qualité, Hygiène, Sécurité et Environnement (QHSE).

## 🚀 Fonctionnalités Complètes

### 🎯 **Analyse Prédictive des Risques**
- Modèles d'IA entraînés pour prédire les niveaux de risque
- Classification automatique des incidents (faible, moyen, élevé, critique)
- Recommandations personnalisées basées sur l'analyse
- Prédiction des coûts d'accidents et ROI des mesures préventives

### 💬 **Chatbot Expert QHSE**
- Interface de chat interactive avec IA avancée
- Réponses contextuelles aux questions de sécurité
- Quick replies pour les questions fréquentes
- Intégration avec la base de données des incidents
- Support multilingue et apprentissage continu

### 📊 **Tableaux de Bord Interactifs**
- Visualisations en temps réel des statistiques
- Graphiques par secteur, type d'incident, gravité
- Tendance mensuelle des incidents
- Métriques de performance QHSE
- Tableaux de bord personnalisables par rôle

### 📝 **Gestion des Incidents**
- Formulaire d'analyse de risque intelligent
- Sauvegarde automatique des rapports
- Suivi des actions correctives
- Historique complet des incidents
- Signalement mobile avec géolocalisation et photos

### 🔍 **Recommandations IA**
- Suggestions personnalisées par niveau de risque
- Actions correctives prioritaires
- Formations recommandées
- Mise à jour des procédures
- Analyse prédictive des tendances

### 🚨 **Système de Notifications Avancé**
- Alertes en temps réel pour incidents critiques
- Notifications par email, SMS, et Slack
- Escalade automatique selon la gravité
- Rappels de formations et inspections
- Configuration personnalisée par utilisateur

### 📋 **Workflow et Approbations**
- Processus d'approbation automatisés
- Escalade intelligente des dossiers
- Suivi des délais et KPIs
- Assignation des tâches aux responsables
- Templates de workflow personnalisables

### 🎓 **Gestion des Formations**
- Catalogue complet de formations QHSE
- Planification et suivi des sessions
- Gestion des certifications et validités
- Plans de formation personnalisés
- Rapports de conformité formation

### ⚖️ **Conformité Réglementaire**
- Base de données des réglementations QHSE
- Suivi des audits et échéances
- Checklist de conformité automatique
- Alertes de changements réglementaires
- Génération de preuves d'audit

### 🔧 **Gestion des Équipements**
- Inventaire complet des équipements
- Planification des inspections
- Suivi des maintenances préventives
- Alertes d'échéances d'inspection
- Historique des interventions

### 📱 **Application Mobile**
- Interface mobile responsive
- Signalement d'incidents avec photos
- Géolocalisation automatique
- Mode hors ligne avec synchronisation
- Notifications push

### ⚙️ **Panel d'Administration**
- Gestion complète des utilisateurs
- Configuration des modèles IA
- Monitoring système en temps réel
- Gestion des permissions et rôles
- Logs et métriques détaillées

### 📊 **Reporting Avancé**
- Rapports réglementaires automatiques
- Export PDF/Excel personnalisables
- Tableaux de bord par direction
- Rapports de performance QHSE
- Analytics prédictifs

## 🛠️ **Technologies Utilisées**

### Backend
- **Flask** - Framework web Python
- **SQLite** - Base de données relationnelle
- **Scikit-learn** - Machine Learning
- **Pandas** - Manipulation des données

### Frontend
- **HTML5/CSS3/JavaScript** - Interface utilisateur
- **Bootstrap 5** - Framework CSS
- **Chart.js** - Visualisations
- **AOS** - Animations

### IA/ML
- **Random Forest** - Classification des risques
- **Label Encoding** - Préprocessing des données
- **Cross-validation** - Validation des modèles

## 📦 **Installation**

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation rapide
```bash
# Cloner le projet
git clone <repository-url>
cd assistant_qhse_ia

# Lancer le script d'installation
python run.py
```

### Installation manuelle
```bash
# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
python database/init_db.py

# Entraîner les modèles d'IA
python scripts/train_model.py

# Lancer l'application
python app.py
```

## 🚀 **Utilisation**

### Démarrage
```bash
python run.py
```

L'application sera disponible sur `http://localhost:5000`

### Comptes de démonstration
- **Admin**: `admin` / `admin`
- **Manager**: `manager` / `manager`
- **User**: `user` / `user`

### Navigation
1. **Connexion** - Page d'authentification
2. **Dashboard** - Vue d'ensemble des statistiques
3. **Analyse** - Formulaire d'évaluation des risques
4. **Chatbot** - Assistant IA interactif
5. **Conseils** - Recommandations personnalisées

## 📊 **Structure du Projet**

```
assistant_qhse_ia/
├── app.py                 # Application Flask principale
├── run.py                 # Script de démarrage
├── requirements.txt       # Dépendances Python
├── database/              # Base de données
│   ├── schema.sql         # Schéma SQLite
│   └── init_db.py         # Initialisation DB
├── scripts/               # Scripts Python
│   └── train_model.py     # Entraînement IA
├── interface/             # Interface web
│   └── templates/         # Templates HTML
├── modeles/               # Modèles ML sauvegardés
└── visualisation/         # Tableaux de bord
```

## 🔧 **Configuration**

### Variables d'environnement
```bash
export FLASK_ENV=development  # Mode développement
export FLASK_DEBUG=True       # Debug activé
```

### Base de données
La base de données SQLite est créée automatiquement avec :
- Tables des utilisateurs, secteurs, incidents
- Données de démonstration réalistes
- Index pour optimiser les performances

### Modèles d'IA
Les modèles sont entraînés automatiquement avec :
- Données synthétiques réalistes
- Validation croisée
- Métriques de performance
- Sauvegarde automatique

## 📈 **API Endpoints**

### Incidents
- `GET /api/incidents` - Liste des incidents
- `POST /api/incidents` - Créer un incident

### Prédictions
- `POST /api/predict` - Prédiction de risque IA

### Chatbot
- `POST /api/chatbot` - Réponse du chatbot

### Statistiques
- `GET /api/statistics` - Données du dashboard

## 🎯 **Fonctionnalités Avancées**

### Analyse Prédictive
- Prédiction du niveau de risque basée sur :
  - Secteur d'activité
  - Type d'incident
  - Heure de l'incident
  - Probabilité estimée

### Recommandations Intelligentes
- Actions correctives par niveau de risque
- Formations suggérées
- Mise à jour des procédures
- Surveillance renforcée

### Visualisations Dynamiques
- Graphiques en temps réel
- Filtres interactifs
- Export des données
- Rapports automatiques

## 🔒 **Sécurité**

- Authentification utilisateur
- Sessions sécurisées
- Validation des données
- Protection CSRF
- Chiffrement des mots de passe

## 🚀 **Déploiement**

### Production
```bash
# Installer gunicorn
pip install gunicorn

# Lancer en production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (optionnel)
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🤝 **Contribution**

1. Fork le projet
2. Créer une branche feature
3. Commiter les changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📄 **Licence**

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 **Support**

Pour toute question ou problème :
- Créer une issue sur GitHub
- Contacter l'équipe de développement
- Consulter la documentation

---

**Développé avec ❤️ pour la sécurité au travail**
