"""
AEETE Configuration Management
Centralized configuration with validation and environment variables
"""
import os
import logging
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class FirebaseConfig:
    """Firebase configuration with validation"""
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    client_x509_cert_url: str
    
    @classmethod
    def from_env(cls) -> 'FirebaseConfig':
        """Initialize from environment variables with validation"""
        required_vars = [
            'FIREBASE_PROJECT_ID',
            'FIREBASE_PRIVATE_KEY_ID', 
            'FIREBASE_PRIVATE_KEY',
            'FIREBASE_CLIENT_EMAIL',
            'FIREBASE_CLIENT_ID',
            'FIREBASE_CLIENT_X509_CERT_URL'
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing Firebase environment variables: {missing}")
        
        # Handle private key formatting
        private_key = os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
        
        return cls(
            project_id=os.getenv('FIREBASE_PROJECT_ID', ''),
            private_key_id=os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
            private_key=private_key,
            client_email=os.getenv('FIREBASE_CLIENT_EMAIL', ''),
            client_id=os.getenv('FIREBASE_CLIENT_ID', ''),
            client_x509_cert_url=os.getenv('FIREBASE_CLIENT_X509_CERT_URL', '')
        )

@dataclass
class TradingConfig:
    """Trading configuration parameters"""
    exchange_api_key: str
    exchange_secret: str
    exchange_passphrase: Optional[str]
    default_exchange: str
    default_symbol: str
    max_position_size: float
    max_daily_loss: float
    stop_loss_pct: float
    take_profit_pct: float
    
    @classmethod
    def from_env(cls) -> 'TradingConfig':
        """Initialize from environment variables"""
        return cls(
            exchange_api_key=os.getenv('EXCHANGE_API_KEY', ''),
            exchange_secret=os.getenv('EXCHANGE_SECRET', ''),
            exchange_passphrase=os.getenv('EXCHANGE_PASSPHRASE'),
            default_exchange=os.getenv('DEFAULT_EXCHANGE', 'binance'),
            default_symbol=os.getenv('DEFAULT_SYMBOL', 'BTC/USDT'),
            max_position_size=float(os.getenv('MAX_POSITION_SIZE', 0.1)),
            max_daily_loss=float(os.getenv('MAX_DAILY_LOSS', 0.05)),
            stop_loss_pct=float(os.getenv('STOP_LOSS_PCT', 0.02)),
            take_profit_pct=float(os.getenv('TAKE_PROFIT_PCT', 0.04))
        )

class Config:
    """Main configuration singleton"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize configuration from environment"""
        self.firebase: FirebaseConfig = FirebaseConfig.from_env()
        self.trading: TradingConfig = TradingConfig.from_env()
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO')
        
        # Validate critical configurations
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration values"""
        if not self.trading.exchange_api_key:
            logging.warning("Exchange API key not configured - simulation mode only")
        
        if self.trading.max_position_size <= 0 or self.trading.max_position_size > 1:
            raise ValueError("MAX_POSITION_SIZE must be between 0 and 1")
        
        if self.trading.stop_loss_pct <= 0:
            raise ValueError("STOP_LOSS_PCT must be positive")