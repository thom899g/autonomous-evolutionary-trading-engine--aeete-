"""
Firebase State Management
Handles all Firestore operations for strategy persistence and real-time updates
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.exceptions import FirebaseError

from config import Config

class FirebaseManager:
    """Firebase Firestore manager for AEETE state persistence"""
    
    def __init__(self):
        self.config = Config()
        self._initialized = False
        self._db = None
        self.logger = logging.getLogger(__name__)
        self._initialize_firebase()
    
    def _initialize_firebase(self) -> None:
        """Initialize Firebase Admin SDK with error handling"""
        try:
            if not firebase_admin._apps:
                # Create credentials from configuration
                cred_dict = {
                    "type": "service_account",
                    "project_id": self.config.firebase.project_id,
                    "private_key_id": self.config.firebase.private_key_id,
                    "private_key": self.config.firebase.private_key,
                    "client_email": self.config.firebase.client_email,
                    "client_id": self.config.firebase.client_id,
                    "auth_uri": "https://accounts.google.com/o/