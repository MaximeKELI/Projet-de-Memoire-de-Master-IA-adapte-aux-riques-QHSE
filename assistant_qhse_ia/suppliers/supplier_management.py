"""
Système de Gestion des Fournisseurs QHSE
Évaluation, audit et suivi des risques externes
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid
import requests
from urllib.parse import urljoin

class SupplierStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

@dataclass
class Supplier:
    supplier_id: str
    name: str
    contact_person: str
    email: str
    phone: str
    address: str
    country: str
    business_type: str
    registration_number: str
    status: SupplierStatus
    risk_level: RiskLevel
    qhse_score: float
    last_audit_date: Optional[datetime]
    next_audit_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

@dataclass
class SupplierAudit:
    audit_id: str
    supplier_id: str
    auditor_id: int
    audit_type: str
    scheduled_date: datetime
    completed_date: Optional[datetime]
    status: AuditStatus
    score: Optional[float]
    findings: List[Dict]
    recommendations: List[str]
    compliance_percentage: float
    risk_areas: List[str]

@dataclass
class SupplierIncident:
    incident_id: str
    supplier_id: str
    incident_type: str
    description: str
    severity_level: int
    occurred_date: datetime
    reported_date: datetime
    impact_assessment: str
    corrective_actions: List[str]
    status: str

class SupplierManagementSystem:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.suppliers = {}
        self.audits = {}
        self.incidents = {}
        
        self._init_database()
        self._load_data()
    
    def _init_database(self):
        """Initialise la base de données des fournisseurs"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Table des fournisseurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                contact_person TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL,
                business_type TEXT NOT NULL,
                registration_number TEXT,
                status TEXT DEFAULT 'pending',
                risk_level TEXT DEFAULT 'medium',
                qhse_score REAL DEFAULT 0.0,
                last_audit_date TIMESTAMP,
                next_audit_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des audits fournisseurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplier_audits (
                audit_id TEXT PRIMARY KEY,
                supplier_id TEXT NOT NULL,
                auditor_id INTEGER NOT NULL,
                audit_type TEXT NOT NULL,
                scheduled_date TIMESTAMP NOT NULL,
                completed_date TIMESTAMP,
                status TEXT DEFAULT 'scheduled',
                score REAL,
                findings TEXT DEFAULT '[]',
                recommendations TEXT DEFAULT '[]',
                compliance_percentage REAL DEFAULT 0.0,
                risk_areas TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
                FOREIGN KEY (auditor_id) REFERENCES users(id)
            )
        ''')
        
        # Table des incidents fournisseurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplier_incidents (
                incident_id TEXT PRIMARY KEY,
                supplier_id TEXT NOT NULL,
                incident_type TEXT NOT NULL,
                description TEXT NOT NULL,
                severity_level INTEGER NOT NULL,
                occurred_date TIMESTAMP NOT NULL,
                reported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                impact_assessment TEXT,
                corrective_actions TEXT DEFAULT '[]',
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
            )
        ''')
        
        # Table des évaluations QHSE
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplier_evaluations (
                evaluation_id TEXT PRIMARY KEY,
                supplier_id TEXT NOT NULL,
                evaluator_id INTEGER NOT NULL,
                evaluation_date TIMESTAMP NOT NULL,
                criteria TEXT NOT NULL,
                score REAL NOT NULL,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
                FOREIGN KEY (evaluator_id) REFERENCES users(id)
            )
        ''')
        
        # Table des documents fournisseurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplier_documents (
                document_id TEXT PRIMARY KEY,
                supplier_id TEXT NOT NULL,
                document_type TEXT NOT NULL,
                document_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
            )
        ''')
        
        # Table des contrats
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplier_contracts (
                contract_id TEXT PRIMARY KEY,
                supplier_id TEXT NOT NULL,
                contract_type TEXT NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP,
                value REAL,
                qhse_requirements TEXT DEFAULT '[]',
                compliance_requirements TEXT DEFAULT '[]',
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_data(self):
        """Charge les données depuis la base"""
        self._load_suppliers()
        self._load_audits()
        self._load_incidents()
    
    def _load_suppliers(self):
        """Charge les fournisseurs"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM suppliers')
        rows = cursor.fetchall()
        
        for row in rows:
            self.suppliers[row[0]] = Supplier(
                supplier_id=row[0],
                name=row[1],
                contact_person=row[2],
                email=row[3],
                phone=row[4],
                address=row[5],
                country=row[6],
                business_type=row[7],
                registration_number=row[8],
                status=SupplierStatus(row[9]),
                risk_level=RiskLevel(row[10]),
                qhse_score=row[11],
                last_audit_date=datetime.fromisoformat(row[12]) if row[12] else None,
                next_audit_date=datetime.fromisoformat(row[13]) if row[13] else None,
                created_at=datetime.fromisoformat(row[14]),
                updated_at=datetime.fromisoformat(row[15])
            )
        
        conn.close()
    
    def _load_audits(self):
        """Charge les audits"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM supplier_audits')
        rows = cursor.fetchall()
        
        for row in rows:
            self.audits[row[0]] = SupplierAudit(
                audit_id=row[0],
                supplier_id=row[1],
                auditor_id=row[2],
                audit_type=row[3],
                scheduled_date=datetime.fromisoformat(row[4]),
                completed_date=datetime.fromisoformat(row[5]) if row[5] else None,
                status=AuditStatus(row[6]),
                score=row[7],
                findings=json.loads(row[8]),
                recommendations=json.loads(row[9]),
                compliance_percentage=row[10],
                risk_areas=json.loads(row[11])
            )
        
        conn.close()
    
    def _load_incidents(self):
        """Charge les incidents"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM supplier_incidents')
        rows = cursor.fetchall()
        
        for row in rows:
            self.incidents[row[0]] = SupplierIncident(
                incident_id=row[0],
                supplier_id=row[1],
                incident_type=row[2],
                description=row[3],
                severity_level=row[4],
                occurred_date=datetime.fromisoformat(row[5]),
                reported_date=datetime.fromisoformat(row[6]),
                impact_assessment=row[7],
                corrective_actions=json.loads(row[8]),
                status=row[9]
            )
        
        conn.close()
    
    def add_supplier(self, name: str, contact_person: str, email: str, phone: str,
                    address: str, country: str, business_type: str,
                    registration_number: str = None) -> str:
        """Ajoute un nouveau fournisseur"""
        supplier_id = str(uuid.uuid4())
        
        supplier = Supplier(
            supplier_id=supplier_id,
            name=name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            address=address,
            country=country,
            business_type=business_type,
            registration_number=registration_number or "",
            status=SupplierStatus.PENDING,
            risk_level=RiskLevel.MEDIUM,
            qhse_score=0.0,
            last_audit_date=None,
            next_audit_date=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO suppliers
                (supplier_id, name, contact_person, email, phone, address, country, 
                 business_type, registration_number, status, risk_level, qhse_score, 
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                supplier_id, name, contact_person, email, phone, address, country,
                business_type, registration_number or "", SupplierStatus.PENDING.value,
                RiskLevel.MEDIUM.value, 0.0, supplier.created_at, supplier.updated_at
            ))
            
            conn.commit()
            conn.close()
            
            self.suppliers[supplier_id] = supplier
            return supplier_id
            
        except Exception as e:
            print(f"Erreur ajout fournisseur: {e}")
            return None
    
    def update_supplier_status(self, supplier_id: str, status: SupplierStatus) -> bool:
        """Met à jour le statut d'un fournisseur"""
        if supplier_id not in self.suppliers:
            return False
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE suppliers 
                SET status = ?, updated_at = ?
                WHERE supplier_id = ?
            ''', (status.value, datetime.now(), supplier_id))
            
            conn.commit()
            conn.close()
            
            self.suppliers[supplier_id].status = status
            self.suppliers[supplier_id].updated_at = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"Erreur mise à jour statut fournisseur: {e}")
            return False
    
    def schedule_audit(self, supplier_id: str, auditor_id: int, audit_type: str,
                      scheduled_date: datetime) -> str:
        """Planifie un audit fournisseur"""
        if supplier_id not in self.suppliers:
            return None
        
        audit_id = str(uuid.uuid4())
        
        audit = SupplierAudit(
            audit_id=audit_id,
            supplier_id=supplier_id,
            auditor_id=auditor_id,
            audit_type=audit_type,
            scheduled_date=scheduled_date,
            completed_date=None,
            status=AuditStatus.SCHEDULED,
            score=None,
            findings=[],
            recommendations=[],
            compliance_percentage=0.0,
            risk_areas=[]
        )
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO supplier_audits
                (audit_id, supplier_id, auditor_id, audit_type, scheduled_date, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (audit_id, supplier_id, auditor_id, audit_type, scheduled_date, AuditStatus.SCHEDULED.value))
            
            conn.commit()
            conn.close()
            
            self.audits[audit_id] = audit
            return audit_id
            
        except Exception as e:
            print(f"Erreur planification audit: {e}")
            return None
    
    def complete_audit(self, audit_id: str, score: float, findings: List[Dict],
                      recommendations: List[str], compliance_percentage: float,
                      risk_areas: List[str]) -> bool:
        """Finalise un audit fournisseur"""
        if audit_id not in self.audits:
            return False
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE supplier_audits
                SET completed_date = ?, status = ?, score = ?, findings = ?,
                    recommendations = ?, compliance_percentage = ?, risk_areas = ?
                WHERE audit_id = ?
            ''', (
                datetime.now(), AuditStatus.COMPLETED.value, score,
                json.dumps(findings), json.dumps(recommendations),
                compliance_percentage, json.dumps(risk_areas), audit_id
            ))
            
            # Mise à jour du score QHSE du fournisseur
            audit = self.audits[audit_id]
            supplier_id = audit.supplier_id
            
            cursor.execute('''
                UPDATE suppliers
                SET qhse_score = ?, last_audit_date = ?, updated_at = ?
                WHERE supplier_id = ?
            ''', (score, datetime.now(), datetime.now(), supplier_id))
            
            conn.commit()
            conn.close()
            
            # Mise à jour du cache
            self.audits[audit_id].completed_date = datetime.now()
            self.audits[audit_id].status = AuditStatus.COMPLETED
            self.audits[audit_id].score = score
            self.audits[audit_id].findings = findings
            self.audits[audit_id].recommendations = recommendations
            self.audits[audit_id].compliance_percentage = compliance_percentage
            self.audits[audit_id].risk_areas = risk_areas
            
            self.suppliers[supplier_id].qhse_score = score
            self.suppliers[supplier_id].last_audit_date = datetime.now()
            self.suppliers[supplier_id].updated_at = datetime.now()
            
            # Mise à jour du niveau de risque
            self._update_supplier_risk_level(supplier_id)
            
            return True
            
        except Exception as e:
            print(f"Erreur finalisation audit: {e}")
            return False
    
    def _update_supplier_risk_level(self, supplier_id: str):
        """Met à jour le niveau de risque d'un fournisseur"""
        if supplier_id not in self.suppliers:
            return
        
        supplier = self.suppliers[supplier_id]
        score = supplier.qhse_score
        
        # Logique de classification des risques
        if score >= 90:
            new_risk_level = RiskLevel.LOW
        elif score >= 70:
            new_risk_level = RiskLevel.MEDIUM
        elif score >= 50:
            new_risk_level = RiskLevel.HIGH
        else:
            new_risk_level = RiskLevel.CRITICAL
        
        if new_risk_level != supplier.risk_level:
            try:
                conn = sqlite3.connect(self.database_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE suppliers
                    SET risk_level = ?, updated_at = ?
                    WHERE supplier_id = ?
                ''', (new_risk_level.value, datetime.now(), supplier_id))
                
                conn.commit()
                conn.close()
                
                self.suppliers[supplier_id].risk_level = new_risk_level
                self.suppliers[supplier_id].updated_at = datetime.now()
                
            except Exception as e:
                print(f"Erreur mise à jour niveau de risque: {e}")
    
    def report_incident(self, supplier_id: str, incident_type: str, description: str,
                       severity_level: int, occurred_date: datetime,
                       impact_assessment: str = None) -> str:
        """Signale un incident lié à un fournisseur"""
        if supplier_id not in self.suppliers:
            return None
        
        incident_id = str(uuid.uuid4())
        
        incident = SupplierIncident(
            incident_id=incident_id,
            supplier_id=supplier_id,
            incident_type=incident_type,
            description=description,
            severity_level=severity_level,
            occurred_date=occurred_date,
            reported_date=datetime.now(),
            impact_assessment=impact_assessment or "",
            corrective_actions=[],
            status="open"
        )
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO supplier_incidents
                (incident_id, supplier_id, incident_type, description, severity_level,
                 occurred_date, reported_date, impact_assessment, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                incident_id, supplier_id, incident_type, description, severity_level,
                occurred_date, incident.reported_date, impact_assessment or "", "open"
            ))
            
            conn.commit()
            conn.close()
            
            self.incidents[incident_id] = incident
            
            # Impact sur le score QHSE
            self._update_score_from_incident(supplier_id, severity_level)
            
            return incident_id
            
        except Exception as e:
            print(f"Erreur signalement incident: {e}")
            return None
    
    def _update_score_from_incident(self, supplier_id: str, severity_level: int):
        """Met à jour le score QHSE basé sur un incident"""
        if supplier_id not in self.suppliers:
            return
        
        # Pénalités basées sur la gravité
        penalties = {1: 2, 2: 5, 3: 10, 4: 20, 5: 30}
        penalty = penalties.get(severity_level, 5)
        
        current_score = self.suppliers[supplier_id].qhse_score
        new_score = max(0, current_score - penalty)
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE suppliers
                SET qhse_score = ?, updated_at = ?
                WHERE supplier_id = ?
            ''', (new_score, datetime.now(), supplier_id))
            
            conn.commit()
            conn.close()
            
            self.suppliers[supplier_id].qhse_score = new_score
            self.suppliers[supplier_id].updated_at = datetime.now()
            
            # Mise à jour du niveau de risque
            self._update_supplier_risk_level(supplier_id)
            
        except Exception as e:
            print(f"Erreur mise à jour score incident: {e}")
    
    def get_supplier_risk_assessment(self, supplier_id: str) -> Dict:
        """Évalue les risques d'un fournisseur"""
        if supplier_id not in self.suppliers:
            return {}
        
        supplier = self.suppliers[supplier_id]
        
        # Récupération des incidents récents
        recent_incidents = [
            incident for incident in self.incidents.values()
            if incident.supplier_id == supplier_id and
            incident.occurred_date >= datetime.now() - timedelta(days=365)
        ]
        
        # Récupération des audits récents
        recent_audits = [
            audit for audit in self.audits.values()
            if audit.supplier_id == supplier_id and
            audit.completed_date and
            audit.completed_date >= datetime.now() - timedelta(days=365)
        ]
        
        # Calcul du score de risque
        risk_factors = {
            "qhse_score": supplier.qhse_score,
            "incident_count": len(recent_incidents),
            "severe_incidents": len([i for i in recent_incidents if i.severity_level >= 4]),
            "audit_compliance": sum(audit.compliance_percentage for audit in recent_audits) / max(1, len(recent_audits)),
            "risk_level": supplier.risk_level.value
        }
        
        # Score de risque global (0-100, plus élevé = plus risqué)
        risk_score = (
            (100 - risk_factors["qhse_score"]) * 0.4 +
            risk_factors["incident_count"] * 5 +
            risk_factors["severe_incidents"] * 15 +
            (100 - risk_factors["audit_compliance"]) * 0.3
        )
        
        return {
            "supplier_id": supplier_id,
            "supplier_name": supplier.name,
            "risk_score": min(100, max(0, risk_score)),
            "risk_level": supplier.risk_level.value,
            "risk_factors": risk_factors,
            "recommendations": self._generate_risk_recommendations(risk_factors),
            "last_updated": supplier.updated_at.isoformat()
        }
    
    def _generate_risk_recommendations(self, risk_factors: Dict) -> List[str]:
        """Génère des recommandations basées sur les facteurs de risque"""
        recommendations = []
        
        if risk_factors["qhse_score"] < 70:
            recommendations.append("Améliorer le score QHSE par des formations et audits")
        
        if risk_factors["incident_count"] > 3:
            recommendations.append("Réduire le nombre d'incidents par des mesures préventives")
        
        if risk_factors["severe_incidents"] > 0:
            recommendations.append("Mettre en place un plan d'action pour les incidents graves")
        
        if risk_factors["audit_compliance"] < 80:
            recommendations.append("Améliorer la conformité aux exigences QHSE")
        
        if risk_factors["risk_level"] in ["high", "critical"]:
            recommendations.append("Surveillance renforcée et audits plus fréquents")
        
        return recommendations
    
    def get_suppliers_by_risk_level(self, risk_level: RiskLevel) -> List[Dict]:
        """Récupère les fournisseurs par niveau de risque"""
        suppliers = []
        
        for supplier in self.suppliers.values():
            if supplier.risk_level == risk_level:
                suppliers.append({
                    "supplier_id": supplier.supplier_id,
                    "name": supplier.name,
                    "qhse_score": supplier.qhse_score,
                    "status": supplier.status.value,
                    "last_audit_date": supplier.last_audit_date.isoformat() if supplier.last_audit_date else None,
                    "next_audit_date": supplier.next_audit_date.isoformat() if supplier.next_audit_date else None
                })
        
        return suppliers
    
    def get_overdue_audits(self) -> List[Dict]:
        """Récupère les audits en retard"""
        overdue_audits = []
        today = datetime.now()
        
        for audit in self.audits.values():
            if (audit.status == AuditStatus.SCHEDULED and 
                audit.scheduled_date < today):
                overdue_audits.append({
                    "audit_id": audit.audit_id,
                    "supplier_id": audit.supplier_id,
                    "supplier_name": self.suppliers.get(audit.supplier_id, {}).name,
                    "scheduled_date": audit.scheduled_date.isoformat(),
                    "days_overdue": (today - audit.scheduled_date).days,
                    "audit_type": audit.audit_type
                })
        
        return sorted(overdue_audits, key=lambda x: x["days_overdue"], reverse=True)
    
    def get_supplier_statistics(self) -> Dict:
        """Récupère les statistiques des fournisseurs"""
        total_suppliers = len(self.suppliers)
        
        # Répartition par statut
        status_distribution = {}
        for supplier in self.suppliers.values():
            status = supplier.status.value
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # Répartition par niveau de risque
        risk_distribution = {}
        for supplier in self.suppliers.values():
            risk = supplier.risk_level.value
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
        
        # Score QHSE moyen
        avg_qhse_score = sum(s.qhse_score for s in self.suppliers.values()) / max(1, total_suppliers)
        
        # Incidents récents (30 derniers jours)
        recent_incidents = len([
            i for i in self.incidents.values()
            if i.occurred_date >= datetime.now() - timedelta(days=30)
        ])
        
        # Audits en retard
        overdue_audits = len(self.get_overdue_audits())
        
        return {
            "total_suppliers": total_suppliers,
            "status_distribution": status_distribution,
            "risk_distribution": risk_distribution,
            "average_qhse_score": round(avg_qhse_score, 2),
            "recent_incidents": recent_incidents,
            "overdue_audits": overdue_audits,
            "high_risk_suppliers": len(self.get_suppliers_by_risk_level(RiskLevel.HIGH)) +
                                 len(self.get_suppliers_by_risk_level(RiskLevel.CRITICAL))
        }

# Instance globale
supplier_management = SupplierManagementSystem('assistant_qhse_ia/database/qhse.db')
