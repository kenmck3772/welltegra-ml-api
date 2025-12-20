"""
Configuration management for WellTegra ML API

Handles environment-specific settings for local development,
testing, and production deployment.
"""

import os
from typing import Dict, Any


class Config:
    """Base configuration"""

    # Google Cloud
    GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'portfolio-project-481815')
    BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', 'welltegra_historical')
    GCP_REGION = os.getenv('GCP_REGION', 'us-central1')

    # API Settings
    API_VERSION = 'v1'
    API_TITLE = 'WellTegra ML API'
    API_DESCRIPTION = 'Cloud-native API for physics-informed industrial ML'

    # CORS Settings
    CORS_ORIGINS = [
        'https://welltegra.network',
        'https://*.welltegra.network'
    ]

    # Rate Limiting (for future implementation)
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'false').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # BigQuery Settings
    BIGQUERY_TIMEOUT_SECONDS = int(os.getenv('BIGQUERY_TIMEOUT_SECONDS', 30))
    BIGQUERY_MAX_RESULTS = int(os.getenv('BIGQUERY_MAX_RESULTS', 1000))


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    TESTING = False

    # Add localhost for local development
    CORS_ORIGINS = Config.CORS_ORIGINS + [
        'http://localhost:3000',
        'http://localhost:8000',
        'http://localhost:8080'
    ]


class TestingConfig(Config):
    """Testing configuration"""

    DEBUG = False
    TESTING = True

    # Use test dataset
    BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', 'welltegra_historical_test')


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    TESTING = False

    # Stricter settings for production
    RATE_LIMIT_ENABLED = True
    BIGQUERY_TIMEOUT_SECONDS = 10


# Configuration dictionary
config: Dict[str, Any] = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env: str = None) -> Config:
    """
    Get configuration for specified environment

    Args:
        env: Environment name (development, testing, production)

    Returns:
        Configuration object
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')

    return config.get(env, config['default'])
