"""
Gestionnaire de Capteurs IoT pour QHSE
Monitoring en temps réel des conditions de travail
"""

import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import sqlite3
import threading
import websockets
import logging
from dataclasses import dataclass
from enum import Enum

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorType(Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    NOISE = "noise"
    VIBRATION = "vibration"
    GAS = "gas"
    LIGHT = "light"
    PRESSURE = "pressure"
    MOTION = "motion"
    AIR_QUALITY = "air_quality"
    WEATHER = "weather"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class SensorData:
    sensor_id: str
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime
    location: str
    zone: str
    status: str = "active"
    battery_level: float = 100.0
    signal_strength: float = 100.0

@dataclass
class Alert:
    alert_id: str
    sensor_id: str
    alert_type: str
    level: AlertLevel
    message: str
    value: float
    threshold: float
    timestamp: datetime
    location: str
    acknowledged: bool = False
    resolved: bool = False

class IoTManager:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.sensors: Dict[str, Dict] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.callbacks: List[Callable] = []
        self.running = False
        self.websocket_clients = set()
        
        # Seuils de sécurité par type de capteur
        self.safety_thresholds = {
            SensorType.TEMPERATURE: {"min": 15, "max": 35, "critical_min": 5, "critical_max": 45},
            SensorType.HUMIDITY: {"min": 30, "max": 70, "critical_min": 10, "critical_max": 90},
            SensorType.NOISE: {"min": 0, "max": 80, "critical_min": 0, "critical_max": 100},
            SensorType.VIBRATION: {"min": 0, "max": 2, "critical_min": 0, "critical_max": 5},
            SensorType.GAS: {"min": 0, "max": 10, "critical_min": 0, "critical_max": 50},
            SensorType.LIGHT: {"min": 200, "max": 1000, "critical_min": 50, "critical_max": 2000},
            SensorType.PRESSURE: {"min": 95, "max": 105, "critical_min": 90, "critical_max": 110},
            SensorType.AIR_QUALITY: {"min": 0, "max": 50, "critical_min": 0, "critical_max": 100}
        }
        
        self._init_database()
        self._load_sensors()
    
    def _init_database(self):
        """Initialise la base de données pour les capteurs"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Table des capteurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iot_sensors (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                location TEXT NOT NULL,
                zone TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                battery_level REAL DEFAULT 100.0,
                signal_strength REAL DEFAULT 100.0,
                last_update TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des données de capteurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sensor_id) REFERENCES iot_sensors(id)
            )
        ''')
        
        # Table des alertes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_alerts (
                id TEXT PRIMARY KEY,
                sensor_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                value REAL NOT NULL,
                threshold REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                location TEXT NOT NULL,
                acknowledged BOOLEAN DEFAULT FALSE,
                resolved BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (sensor_id) REFERENCES iot_sensors(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_sensors(self):
        """Charge les capteurs depuis la base de données"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM iot_sensors')
        rows = cursor.fetchall()
        
        for row in rows:
            self.sensors[row[0]] = {
                'id': row[0],
                'name': row[1],
                'type': SensorType(row[2]),
                'location': row[3],
                'zone': row[4],
                'status': row[5],
                'battery_level': row[6],
                'signal_strength': row[7],
                'last_update': row[8]
            }
        
        conn.close()
    
    def add_sensor(self, sensor_id: str, name: str, sensor_type: SensorType, 
                   location: str, zone: str) -> bool:
        """Ajoute un nouveau capteur"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO iot_sensors (id, name, type, location, zone)
                VALUES (?, ?, ?, ?, ?)
            ''', (sensor_id, name, sensor_type.value, location, zone))
            
            conn.commit()
            conn.close()
            
            self.sensors[sensor_id] = {
                'id': sensor_id,
                'name': name,
                'type': sensor_type,
                'location': location,
                'zone': zone,
                'status': 'active',
                'battery_level': 100.0,
                'signal_strength': 100.0,
                'last_update': None
            }
            
            logger.info(f"Capteur {sensor_id} ajouté avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du capteur {sensor_id}: {e}")
            return False
    
    def remove_sensor(self, sensor_id: str) -> bool:
        """Supprime un capteur"""
        try:
            if sensor_id in self.sensors:
                conn = sqlite3.connect(self.database_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM iot_sensors WHERE id = ?', (sensor_id,))
                cursor.execute('DELETE FROM sensor_data WHERE sensor_id = ?', (sensor_id,))
                cursor.execute('DELETE FROM sensor_alerts WHERE sensor_id = ?', (sensor_id,))
                
                conn.commit()
                conn.close()
                
                del self.sensors[sensor_id]
                logger.info(f"Capteur {sensor_id} supprimé avec succès")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du capteur {sensor_id}: {e}")
            return False
    
    def update_sensor_data(self, sensor_id: str, value: float, unit: str) -> bool:
        """Met à jour les données d'un capteur"""
        try:
            if sensor_id not in self.sensors:
                logger.warning(f"Capteur {sensor_id} non trouvé")
                return False
            
            sensor = self.sensors[sensor_id]
            sensor_type = sensor['type']
            timestamp = datetime.now()
            
            # Création de l'objet SensorData
            sensor_data = SensorData(
                sensor_id=sensor_id,
                sensor_type=sensor_type,
                value=value,
                unit=unit,
                timestamp=timestamp,
                location=sensor['location'],
                zone=sensor['zone']
            )
            
            # Sauvegarde en base
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sensor_data (sensor_id, value, unit, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (sensor_id, value, unit, timestamp))
            
            # Mise à jour du capteur
            cursor.execute('''
                UPDATE iot_sensors 
                SET last_update = ?, battery_level = ?, signal_strength = ?
                WHERE id = ?
            ''', (timestamp, sensor_data.battery_level, sensor_data.signal_strength, sensor_id))
            
            conn.commit()
            conn.close()
            
            # Vérification des seuils et génération d'alertes
            self._check_thresholds(sensor_data)
            
            # Notification des callbacks
            self._notify_callbacks(sensor_data)
            
            # Mise à jour WebSocket
            self._broadcast_to_websockets(sensor_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du capteur {sensor_id}: {e}")
            return False
    
    def _check_thresholds(self, sensor_data: SensorData):
        """Vérifie les seuils de sécurité et génère des alertes"""
        sensor_type = sensor_data.sensor_type
        value = sensor_data.value
        
        if sensor_type not in self.safety_thresholds:
            return
        
        thresholds = self.safety_thresholds[sensor_type]
        
        # Vérification des seuils critiques
        if value <= thresholds["critical_min"] or value >= thresholds["critical_max"]:
            level = AlertLevel.EMERGENCY
            alert_type = "critical_threshold"
            message = f"Valeur critique détectée: {value} {sensor_data.unit}"
        
        # Vérification des seuils d'alerte
        elif value <= thresholds["min"] or value >= thresholds["max"]:
            level = AlertLevel.WARNING
            alert_type = "threshold_exceeded"
            message = f"Seuil dépassé: {value} {sensor_data.unit}"
        
        else:
            return  # Pas d'alerte nécessaire
        
        # Création de l'alerte
        alert_id = f"{sensor_data.sensor_id}_{int(time.time())}"
        alert = Alert(
            alert_id=alert_id,
            sensor_id=sensor_data.sensor_id,
            alert_type=alert_type,
            level=level,
            message=message,
            value=value,
            threshold=thresholds["min"] if value <= thresholds["min"] else thresholds["max"],
            timestamp=sensor_data.timestamp,
            location=sensor_data.location
        )
        
        # Sauvegarde de l'alerte
        self._save_alert(alert)
        
        # Ajout aux alertes actives
        self.active_alerts[alert_id] = alert
        
        logger.warning(f"Alerte générée: {alert.message}")
    
    def _save_alert(self, alert: Alert):
        """Sauvegarde une alerte en base"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_alerts 
            (id, sensor_id, alert_type, level, message, value, threshold, 
             timestamp, location, acknowledged, resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (alert.alert_id, alert.sensor_id, alert.alert_type, alert.level.value,
              alert.message, alert.value, alert.threshold, alert.timestamp,
              alert.location, alert.acknowledged, alert.resolved))
        
        conn.commit()
        conn.close()
    
    def _notify_callbacks(self, sensor_data: SensorData):
        """Notifie tous les callbacks enregistrés"""
        for callback in self.callbacks:
            try:
                callback(sensor_data)
            except Exception as e:
                logger.error(f"Erreur dans le callback: {e}")
    
    def _broadcast_to_websockets(self, sensor_data: SensorData):
        """Diffuse les données via WebSocket"""
        if self.websocket_clients:
            message = {
                "type": "sensor_data",
                "data": {
                    "sensor_id": sensor_data.sensor_id,
                    "sensor_type": sensor_data.sensor_type.value,
                    "value": sensor_data.value,
                    "unit": sensor_data.unit,
                    "timestamp": sensor_data.timestamp.isoformat(),
                    "location": sensor_data.location,
                    "zone": sensor_data.zone
                }
            }
            
            # Envoi à tous les clients connectés
            for client in self.websocket_clients.copy():
                try:
                    asyncio.create_task(client.send(json.dumps(message)))
                except Exception as e:
                    logger.error(f"Erreur envoi WebSocket: {e}")
                    self.websocket_clients.discard(client)
    
    def add_callback(self, callback: Callable):
        """Ajoute un callback pour les notifications"""
        self.callbacks.append(callback)
    
    def get_sensor_data(self, sensor_id: str, hours: int = 24) -> List[Dict]:
        """Récupère les données d'un capteur sur une période"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT value, unit, timestamp
            FROM sensor_data
            WHERE sensor_id = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        ''', (sensor_id, since))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "value": row[0],
                "unit": row[1],
                "timestamp": row[2]
            }
            for row in rows
        ]
    
    def get_all_sensors_status(self) -> Dict:
        """Récupère le statut de tous les capteurs"""
        status = {
            "total_sensors": len(self.sensors),
            "active_sensors": 0,
            "inactive_sensors": 0,
            "low_battery": 0,
            "active_alerts": len(self.active_alerts),
            "sensors": []
        }
        
        for sensor_id, sensor in self.sensors.items():
            sensor_status = {
                "id": sensor_id,
                "name": sensor['name'],
                "type": sensor['type'].value,
                "location": sensor['location'],
                "zone": sensor['zone'],
                "status": sensor['status'],
                "battery_level": sensor['battery_level'],
                "signal_strength": sensor['signal_strength'],
                "last_update": sensor['last_update']
            }
            
            if sensor['status'] == 'active':
                status["active_sensors"] += 1
            else:
                status["inactive_sensors"] += 1
            
            if sensor['battery_level'] < 20:
                status["low_battery"] += 1
            
            status["sensors"].append(sensor_status)
        
        return status
    
    def get_alerts(self, level: Optional[AlertLevel] = None, 
                   acknowledged: Optional[bool] = None) -> List[Dict]:
        """Récupère les alertes avec filtres"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM sensor_alerts WHERE 1=1"
        params = []
        
        if level:
            query += " AND level = ?"
            params.append(level.value)
        
        if acknowledged is not None:
            query += " AND acknowledged = ?"
            params.append(acknowledged)
        
        query += " ORDER BY timestamp DESC LIMIT 100"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "alert_id": row[0],
                "sensor_id": row[1],
                "alert_type": row[2],
                "level": row[3],
                "message": row[4],
                "value": row[5],
                "threshold": row[6],
                "timestamp": row[7],
                "location": row[8],
                "acknowledged": bool(row[9]),
                "resolved": bool(row[10])
            }
            for row in rows
        ]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Marque une alerte comme acquittée"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sensor_alerts 
                SET acknowledged = TRUE 
                WHERE id = ?
            ''', (alert_id,))
            
            conn.commit()
            conn.close()
            
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].acknowledged = True
            
            logger.info(f"Alerte {alert_id} acquittée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'acquittement de l'alerte {alert_id}: {e}")
            return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Marque une alerte comme résolue"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sensor_alerts 
                SET resolved = TRUE 
                WHERE id = ?
            ''', (alert_id,))
            
            conn.commit()
            conn.close()
            
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].resolved = True
                del self.active_alerts[alert_id]
            
            logger.info(f"Alerte {alert_id} résolue")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la résolution de l'alerte {alert_id}: {e}")
            return False
    
    def start_monitoring(self):
        """Démarre le monitoring en continu"""
        self.running = True
        logger.info("Monitoring IoT démarré")
        
        # Simulation de données de capteurs (à remplacer par de vrais capteurs)
        threading.Thread(target=self._simulate_sensor_data, daemon=True).start()
    
    def stop_monitoring(self):
        """Arrête le monitoring"""
        self.running = False
        logger.info("Monitoring IoT arrêté")
    
    def _simulate_sensor_data(self):
        """Simule des données de capteurs (pour les tests)"""
        while self.running:
            for sensor_id, sensor in self.sensors.items():
                if sensor['status'] != 'active':
                    continue
                
                # Simulation de données réalistes
                sensor_type = sensor['type']
                value = self._generate_realistic_value(sensor_type)
                unit = self._get_unit_for_type(sensor_type)
                
                self.update_sensor_data(sensor_id, value, unit)
            
            time.sleep(5)  # Mise à jour toutes les 5 secondes
    
    def _generate_realistic_value(self, sensor_type: SensorType) -> float:
        """Génère une valeur réaliste pour un type de capteur"""
        if sensor_type == SensorType.TEMPERATURE:
            return round(random.uniform(18, 25), 1)
        elif sensor_type == SensorType.HUMIDITY:
            return round(random.uniform(40, 60), 1)
        elif sensor_type == SensorType.NOISE:
            return round(random.uniform(50, 70), 1)
        elif sensor_type == SensorType.VIBRATION:
            return round(random.uniform(0.5, 1.5), 2)
        elif sensor_type == SensorType.GAS:
            return round(random.uniform(0, 5), 2)
        elif sensor_type == SensorType.LIGHT:
            return round(random.uniform(300, 800), 0)
        elif sensor_type == SensorType.PRESSURE:
            return round(random.uniform(98, 102), 1)
        elif sensor_type == SensorType.AIR_QUALITY:
            return round(random.uniform(20, 40), 1)
        else:
            return round(random.uniform(0, 100), 2)
    
    def _get_unit_for_type(self, sensor_type: SensorType) -> str:
        """Retourne l'unité pour un type de capteur"""
        units = {
            SensorType.TEMPERATURE: "°C",
            SensorType.HUMIDITY: "%",
            SensorType.NOISE: "dB",
            SensorType.VIBRATION: "m/s²",
            SensorType.GAS: "ppm",
            SensorType.LIGHT: "lux",
            SensorType.PRESSURE: "kPa",
            SensorType.AIR_QUALITY: "AQI"
        }
        return units.get(sensor_type, "unit")

# Instance globale
iot_manager = IoTManager('assistant_qhse_ia/database/qhse.db')
