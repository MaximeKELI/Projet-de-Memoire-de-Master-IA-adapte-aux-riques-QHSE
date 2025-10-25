-- Schéma de base de données pour l'Assistant QHSE IA
-- Création des tables principales

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user', -- admin, manager, user
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des secteurs d'activité
CREATE TABLE IF NOT EXISTS sectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    risk_level VARCHAR(20) DEFAULT 'medium', -- low, medium, high
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des types d'incidents
CREATE TABLE IF NOT EXISTS incident_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL, -- physical, chemical, biological, ergonomic, psychosocial
    severity_weight INTEGER DEFAULT 1, -- 1-5 pour calculer le niveau de risque
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des rapports d'incidents
CREATE TABLE IF NOT EXISTS incident_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    sector_id INTEGER NOT NULL,
    incident_type_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(200),
    date_incident DATE NOT NULL,
    time_incident TIME NOT NULL,
    severity_level VARCHAR(20) NOT NULL, -- low, medium, high, critical
    probability_score REAL NOT NULL, -- 0.0 à 1.0
    risk_score REAL NOT NULL, -- Calculé automatiquement
    status VARCHAR(20) DEFAULT 'open', -- open, in_progress, resolved, closed
    ai_recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (sector_id) REFERENCES sectors(id),
    FOREIGN KEY (incident_type_id) REFERENCES incident_types(id)
);

-- Table des actions correctives
CREATE TABLE IF NOT EXISTS corrective_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL, -- low, medium, high, urgent
    assigned_to INTEGER, -- user_id
    due_date DATE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, in_progress, completed, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incident_reports(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id)
);

-- Table des modèles d'IA
CREATE TABLE IF NOT EXISTS ml_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- classification, regression, clustering
    file_path VARCHAR(255) NOT NULL,
    accuracy_score REAL,
    training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE,
    parameters TEXT -- JSON des paramètres du modèle
);

-- Table des prédictions
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    input_data TEXT NOT NULL, -- JSON des données d'entrée
    prediction_result TEXT NOT NULL, -- JSON du résultat
    confidence_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES ml_models(id)
);

-- Table des statistiques
CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name VARCHAR(100) NOT NULL,
    metric_value REAL NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- count, percentage, average, etc.
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_incident_reports_date ON incident_reports(date_incident);
CREATE INDEX IF NOT EXISTS idx_incident_reports_sector ON incident_reports(sector_id);
CREATE INDEX IF NOT EXISTS idx_incident_reports_severity ON incident_reports(severity_level);
CREATE INDEX IF NOT EXISTS idx_incident_reports_status ON incident_reports(status);
CREATE INDEX IF NOT EXISTS idx_corrective_actions_incident ON corrective_actions(incident_id);
CREATE INDEX IF NOT EXISTS idx_corrective_actions_status ON corrective_actions(status);
CREATE INDEX IF NOT EXISTS idx_predictions_model ON predictions(model_id);
CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(created_at);

-- ==================== TABLES WORKFLOW QHSE ====================

-- Table des workflows QHSE
CREATE TABLE IF NOT EXISTS qhse_workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id VARCHAR(50) NOT NULL,
    incident_id INTEGER,
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incident_reports(id)
);

-- Table des étapes de workflow
CREATE TABLE IF NOT EXISTS workflow_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    assigned_role VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    due_date TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES qhse_workflows(id)
);

-- Table des actions de workflow
CREATE TABLE IF NOT EXISTS workflow_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id INTEGER NOT NULL,
    step_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    actor_id INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES qhse_workflows(id),
    FOREIGN KEY (step_id) REFERENCES workflow_steps(id),
    FOREIGN KEY (actor_id) REFERENCES users(id)
);

-- Table des escalades
CREATE TABLE IF NOT EXISTS workflow_escalations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id INTEGER NOT NULL,
    escalated_to VARCHAR(50) NOT NULL,
    escalated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(100),
    FOREIGN KEY (workflow_id) REFERENCES qhse_workflows(id)
);

-- ==================== TABLES FORMATION QHSE ====================

-- Table des formations
CREATE TABLE IF NOT EXISTS trainings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    duration_hours INTEGER NOT NULL,
    mandatory BOOLEAN DEFAULT FALSE,
    validity_months INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des sessions de formation
CREATE TABLE IF NOT EXISTS training_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    training_id INTEGER NOT NULL,
    instructor_id INTEGER NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    location VARCHAR(200),
    max_participants INTEGER,
    status VARCHAR(20) DEFAULT 'planned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (training_id) REFERENCES trainings(id),
    FOREIGN KEY (instructor_id) REFERENCES users(id)
);

-- Table des participations aux formations
CREATE TABLE IF NOT EXISTS training_participations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'enrolled',
    completion_date TIMESTAMP,
    score REAL,
    certificate_number VARCHAR(50),
    expiry_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES training_sessions(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ==================== TABLES CONFORMITÉ RÉGLEMENTAIRE ====================

-- Table des réglementations
CREATE TABLE IF NOT EXISTS regulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    applicable_sectors TEXT,
    last_update TIMESTAMP,
    next_review TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des exigences réglementaires
CREATE TABLE IF NOT EXISTS regulatory_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regulation_id INTEGER NOT NULL,
    requirement_text TEXT NOT NULL,
    compliance_criteria TEXT,
    evidence_required TEXT,
    deadline TIMESTAMP,
    responsible_role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (regulation_id) REFERENCES regulations(id)
);

-- Table des audits de conformité
CREATE TABLE IF NOT EXISTS compliance_audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regulation_id INTEGER NOT NULL,
    audit_date TIMESTAMP NOT NULL,
    auditor_id INTEGER NOT NULL,
    audit_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'planned',
    findings TEXT,
    recommendations TEXT,
    score REAL,
    next_audit_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (regulation_id) REFERENCES regulations(id),
    FOREIGN KEY (auditor_id) REFERENCES users(id)
);

-- ==================== TABLES ÉQUIPEMENTS ET INSPECTIONS ====================

-- Table des équipements
CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    location VARCHAR(200),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    purchase_date DATE,
    last_inspection TIMESTAMP,
    next_inspection TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des inspections d'équipement
CREATE TABLE IF NOT EXISTS equipment_inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL,
    inspector_id INTEGER NOT NULL,
    inspection_date TIMESTAMP NOT NULL,
    inspection_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'planned',
    findings TEXT,
    recommendations TEXT,
    next_inspection TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id),
    FOREIGN KEY (inspector_id) REFERENCES users(id)
);

-- ==================== TABLES NOTIFICATIONS ====================

-- Table des notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'unread',
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des canaux de notification
CREATE TABLE IF NOT EXISTS notification_channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    channel_type VARCHAR(20) NOT NULL,
    channel_value VARCHAR(200) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ==================== INDEX SUPPLÉMENTAIRES ====================

-- Index pour les workflows
CREATE INDEX IF NOT EXISTS idx_workflows_status ON qhse_workflows(status);
CREATE INDEX IF NOT EXISTS idx_workflows_priority ON qhse_workflows(priority);
CREATE INDEX IF NOT EXISTS idx_workflow_steps_due ON workflow_steps(due_date);
CREATE INDEX IF NOT EXISTS idx_workflow_steps_status ON workflow_steps(status);

-- Index pour les formations
CREATE INDEX IF NOT EXISTS idx_training_sessions_date ON training_sessions(start_date);
CREATE INDEX IF NOT EXISTS idx_training_participations_user ON training_participations(user_id);
CREATE INDEX IF NOT EXISTS idx_training_participations_expiry ON training_participations(expiry_date);

-- Index pour la conformité
CREATE INDEX IF NOT EXISTS idx_compliance_audits_date ON compliance_audits(audit_date);
CREATE INDEX IF NOT EXISTS idx_compliance_audits_status ON compliance_audits(status);

-- Index pour les équipements
CREATE INDEX IF NOT EXISTS idx_equipment_next_inspection ON equipment(next_inspection);
CREATE INDEX IF NOT EXISTS idx_equipment_inspections_date ON equipment_inspections(inspection_date);

-- Index pour les notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(notification_type);
