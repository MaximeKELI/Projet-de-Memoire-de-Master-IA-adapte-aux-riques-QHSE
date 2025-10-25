"""
Système Blockchain QHSE pour la Traçabilité
Certificats, audits et conformité immuables
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import sqlite3
import uuid

@dataclass
class Block:
    """Représente un bloc dans la blockchain"""
    index: int
    timestamp: float
    data: Dict[str, Any]
    previous_hash: str
    nonce: int = 0
    hash: str = ""
    
    def calculate_hash(self) -> str:
        """Calcule le hash du bloc"""
        block_string = f"{self.index}{self.timestamp}{json.dumps(self.data, sort_keys=True)}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 4):
        """Mine le bloc avec la difficulté spécifiée"""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

@dataclass
class QHSETransaction:
    """Transaction QHSE dans la blockchain"""
    transaction_id: str
    transaction_type: str  # certificate, audit, incident, compliance
    user_id: int
    data: Dict[str, Any]
    timestamp: float
    signature: str = ""
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire pour le hash"""
        return {
            'transaction_id': self.transaction_id,
            'transaction_type': self.transaction_type,
            'user_id': self.user_id,
            'data': self.data,
            'timestamp': self.timestamp
        }

class QHSEBlockchain:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.chain: List[Block] = []
        self.difficulty = 4
        self.pending_transactions: List[QHSETransaction] = []
        
        # Initialisation
        self._init_database()
        self._create_genesis_block()
        self._load_chain_from_db()
    
    def _init_database(self):
        """Initialise la base de données blockchain"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Table des blocs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blockchain_blocks (
                index INTEGER PRIMARY KEY,
                timestamp REAL NOT NULL,
                data TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                nonce INTEGER NOT NULL,
                hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des transactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blockchain_transactions (
                transaction_id TEXT PRIMARY KEY,
                block_index INTEGER,
                transaction_type TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                timestamp REAL NOT NULL,
                signature TEXT NOT NULL,
                FOREIGN KEY (block_index) REFERENCES blockchain_blocks(index)
            )
        ''')
        
        # Table des certificats blockchain
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blockchain_certificates (
                certificate_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                certificate_type TEXT NOT NULL,
                issued_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP,
                block_hash TEXT NOT NULL,
                verified BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Table des audits blockchain
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blockchain_audits (
                audit_id TEXT PRIMARY KEY,
                auditor_id INTEGER NOT NULL,
                auditee_id INTEGER NOT NULL,
                audit_type TEXT NOT NULL,
                results TEXT NOT NULL,
                block_hash TEXT NOT NULL,
                verified BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (auditor_id) REFERENCES users(id),
                FOREIGN KEY (auditee_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _create_genesis_block(self):
        """Crée le bloc genesis"""
        if not self.chain:
            genesis_data = {
                "message": "Genesis Block - QHSE Blockchain",
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            genesis_block = Block(
                index=0,
                timestamp=time.time(),
                data=genesis_data,
                previous_hash="0"
            )
            
            genesis_block.mine_block(self.difficulty)
            self.chain.append(genesis_block)
            self._save_block_to_db(genesis_block)
    
    def _load_chain_from_db(self):
        """Charge la blockchain depuis la base de données"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT index, timestamp, data, previous_hash, nonce, hash
            FROM blockchain_blocks
            ORDER BY index
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Reconstruire la chaîne
        self.chain = []
        for row in rows:
            block = Block(
                index=row[0],
                timestamp=row[1],
                data=json.loads(row[2]),
                previous_hash=row[3],
                nonce=row[4],
                hash=row[5]
            )
            self.chain.append(block)
    
    def _save_block_to_db(self, block: Block):
        """Sauvegarde un bloc en base de données"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO blockchain_blocks
            (index, timestamp, data, previous_hash, nonce, hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            block.index,
            block.timestamp,
            json.dumps(block.data),
            block.previous_hash,
            block.nonce,
            block.hash
        ))
        
        conn.commit()
        conn.close()
    
    def add_transaction(self, transaction: QHSETransaction) -> bool:
        """Ajoute une transaction à la file d'attente"""
        try:
            # Vérification de la validité de la transaction
            if not self._validate_transaction(transaction):
                return False
            
            # Signature de la transaction
            transaction.signature = self._sign_transaction(transaction)
            
            self.pending_transactions.append(transaction)
            return True
            
        except Exception as e:
            print(f"Erreur ajout transaction: {e}")
            return False
    
    def _validate_transaction(self, transaction: QHSETransaction) -> bool:
        """Valide une transaction"""
        # Vérifications de base
        if not transaction.transaction_id or not transaction.transaction_type:
            return False
        
        if transaction.user_id <= 0:
            return False
        
        # Vérifications spécifiques par type
        if transaction.transaction_type == "certificate":
            return self._validate_certificate_transaction(transaction)
        elif transaction.transaction_type == "audit":
            return self._validate_audit_transaction(transaction)
        elif transaction.transaction_type == "incident":
            return self._validate_incident_transaction(transaction)
        elif transaction.transaction_type == "compliance":
            return self._validate_compliance_transaction(transaction)
        
        return True
    
    def _validate_certificate_transaction(self, transaction: QHSETransaction) -> bool:
        """Valide une transaction de certificat"""
        required_fields = ['certificate_type', 'issued_at', 'expires_at']
        return all(field in transaction.data for field in required_fields)
    
    def _validate_audit_transaction(self, transaction: QHSETransaction) -> bool:
        """Valide une transaction d'audit"""
        required_fields = ['auditor_id', 'auditee_id', 'audit_type', 'results']
        return all(field in transaction.data for field in required_fields)
    
    def _validate_incident_transaction(self, transaction: QHSETransaction) -> bool:
        """Valide une transaction d'incident"""
        required_fields = ['incident_id', 'severity_level', 'description']
        return all(field in transaction.data for field in required_fields)
    
    def _validate_compliance_transaction(self, transaction: QHSETransaction) -> bool:
        """Valide une transaction de conformité"""
        required_fields = ['compliance_type', 'status', 'requirements']
        return all(field in transaction.data for field in required_fields)
    
    def _sign_transaction(self, transaction: QHSETransaction) -> str:
        """Signe une transaction"""
        transaction_string = json.dumps(transaction.to_dict(), sort_keys=True)
        return hashlib.sha256(transaction_string.encode()).hexdigest()
    
    def mine_pending_transactions(self) -> Block:
        """Mine les transactions en attente"""
        if not self.pending_transactions:
            raise ValueError("Aucune transaction en attente")
        
        # Création du nouveau bloc
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data={
                "transactions": [tx.to_dict() for tx in self.pending_transactions],
                "transaction_count": len(self.pending_transactions)
            },
            previous_hash=self.chain[-1].hash if self.chain else "0"
        )
        
        # Mining du bloc
        new_block.mine_block(self.difficulty)
        
        # Ajout à la chaîne
        self.chain.append(new_block)
        self._save_block_to_db(new_block)
        
        # Sauvegarde des transactions
        self._save_transactions_to_db(new_block)
        
        # Nettoyage des transactions en attente
        self.pending_transactions = []
        
        return new_block
    
    def _save_transactions_to_db(self, block: Block):
        """Sauvegarde les transactions d'un bloc"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        transactions = block.data.get("transactions", [])
        for tx_data in transactions:
            cursor.execute('''
                INSERT INTO blockchain_transactions
                (transaction_id, block_index, transaction_type, user_id, data, timestamp, signature)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                tx_data['transaction_id'],
                block.index,
                tx_data['transaction_type'],
                tx_data['user_id'],
                json.dumps(tx_data['data']),
                tx_data['timestamp'],
                tx_data.get('signature', '')
            ))
        
        conn.commit()
        conn.close()
    
    def is_chain_valid(self) -> bool:
        """Vérifie la validité de la chaîne"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Vérification du hash
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Vérification de la liaison
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def create_certificate(self, user_id: int, certificate_type: str, 
                          expires_at: Optional[datetime] = None) -> str:
        """Crée un certificat blockchain"""
        certificate_id = str(uuid.uuid4())
        
        transaction_data = {
            'certificate_id': certificate_id,
            'certificate_type': certificate_type,
            'issued_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat() if expires_at else None,
            'status': 'active'
        }
        
        transaction = QHSETransaction(
            transaction_id=str(uuid.uuid4()),
            transaction_type="certificate",
            user_id=user_id,
            data=transaction_data,
            timestamp=time.time()
        )
        
        if self.add_transaction(transaction):
            # Mining immédiat pour les certificats
            self.mine_pending_transactions()
            
            # Sauvegarde en base
            self._save_certificate_to_db(certificate_id, user_id, certificate_type, expires_at)
            
            return certificate_id
        
        return None
    
    def _save_certificate_to_db(self, certificate_id: str, user_id: int, 
                               certificate_type: str, expires_at: Optional[datetime]):
        """Sauvegarde un certificat en base"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO blockchain_certificates
            (certificate_id, user_id, certificate_type, issued_at, expires_at, block_hash, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            certificate_id,
            user_id,
            certificate_type,
            datetime.now(),
            expires_at,
            self.chain[-1].hash if self.chain else "",
            True
        ))
        
        conn.commit()
        conn.close()
    
    def create_audit_record(self, auditor_id: int, auditee_id: int, 
                           audit_type: str, results: Dict) -> str:
        """Crée un enregistrement d'audit blockchain"""
        audit_id = str(uuid.uuid4())
        
        transaction_data = {
            'audit_id': audit_id,
            'auditor_id': auditor_id,
            'auditee_id': auditee_id,
            'audit_type': audit_type,
            'results': results,
            'audit_date': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        transaction = QHSETransaction(
            transaction_id=str(uuid.uuid4()),
            transaction_type="audit",
            user_id=auditor_id,
            data=transaction_data,
            timestamp=time.time()
        )
        
        if self.add_transaction(transaction):
            # Mining immédiat pour les audits
            self.mine_pending_transactions()
            
            # Sauvegarde en base
            self._save_audit_to_db(audit_id, auditor_id, auditee_id, audit_type, results)
            
            return audit_id
        
        return None
    
    def _save_audit_to_db(self, audit_id: str, auditor_id: int, auditee_id: int,
                         audit_type: str, results: Dict):
        """Sauvegarde un audit en base"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO blockchain_audits
            (audit_id, auditor_id, auditee_id, audit_type, results, block_hash, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            audit_id,
            auditor_id,
            auditee_id,
            audit_type,
            json.dumps(results),
            self.chain[-1].hash if self.chain else "",
            True
        ))
        
        conn.commit()
        conn.close()
    
    def verify_certificate(self, certificate_id: str) -> Dict:
        """Vérifie un certificat blockchain"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM blockchain_certificates WHERE certificate_id = ?
        ''', (certificate_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {'valid': False, 'error': 'Certificat non trouvé'}
        
        # Vérification de la blockchain
        block_hash = row[5]
        is_in_blockchain = self._verify_in_blockchain(block_hash)
        
        # Vérification de l'expiration
        expires_at = row[4]
        is_expired = expires_at and datetime.fromisoformat(expires_at) < datetime.now()
        
        return {
            'valid': is_in_blockchain and not is_expired,
            'certificate_id': certificate_id,
            'user_id': row[1],
            'certificate_type': row[2],
            'issued_at': row[3],
            'expires_at': expires_at,
            'block_hash': block_hash,
            'is_expired': is_expired,
            'blockchain_verified': is_in_blockchain
        }
    
    def _verify_in_blockchain(self, block_hash: str) -> bool:
        """Vérifie qu'un hash est dans la blockchain"""
        for block in self.chain:
            if block.hash == block_hash:
                return True
        return False
    
    def get_certificate_history(self, user_id: int) -> List[Dict]:
        """Récupère l'historique des certificats d'un utilisateur"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM blockchain_certificates 
            WHERE user_id = ? 
            ORDER BY issued_at DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        certificates = []
        for row in rows:
            certificates.append({
                'certificate_id': row[0],
                'certificate_type': row[2],
                'issued_at': row[3],
                'expires_at': row[4],
                'block_hash': row[5],
                'verified': bool(row[6])
            })
        
        return certificates
    
    def get_audit_history(self, user_id: int) -> List[Dict]:
        """Récupère l'historique des audits d'un utilisateur"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM blockchain_audits 
            WHERE auditee_id = ? OR auditor_id = ?
            ORDER BY audit_id DESC
        ''', (user_id, user_id))
        
        rows = cursor.fetchall()
        conn.close()
        
        audits = []
        for row in rows:
            audits.append({
                'audit_id': row[0],
                'auditor_id': row[1],
                'auditee_id': row[2],
                'audit_type': row[3],
                'results': json.loads(row[4]),
                'block_hash': row[5],
                'verified': bool(row[6])
            })
        
        return audits
    
    def get_blockchain_stats(self) -> Dict:
        """Récupère les statistiques de la blockchain"""
        return {
            'total_blocks': len(self.chain),
            'total_transactions': sum(block.data.get('transaction_count', 0) for block in self.chain),
            'pending_transactions': len(self.pending_transactions),
            'difficulty': self.difficulty,
            'chain_valid': self.is_chain_valid(),
            'last_block_hash': self.chain[-1].hash if self.chain else None,
            'last_block_timestamp': self.chain[-1].timestamp if self.chain else None
        }
    
    def export_blockchain_data(self, start_block: int = 0, end_block: Optional[int] = None) -> Dict:
        """Exporte les données de la blockchain"""
        if end_block is None:
            end_block = len(self.chain)
        
        blocks_to_export = self.chain[start_block:end_block]
        
        return {
            'export_info': {
                'start_block': start_block,
                'end_block': end_block,
                'export_timestamp': datetime.now().isoformat(),
                'total_blocks': len(blocks_to_export)
            },
            'blocks': [
                {
                    'index': block.index,
                    'timestamp': block.timestamp,
                    'data': block.data,
                    'previous_hash': block.previous_hash,
                    'nonce': block.nonce,
                    'hash': block.hash
                }
                for block in blocks_to_export
            ]
        }

# Instance globale
qhse_blockchain = QHSEBlockchain('assistant_qhse_ia/database/qhse.db')
