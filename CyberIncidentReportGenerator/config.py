"""
config.py
---------
Central configuration for the Cybersecurity Incident Report Generator.
Keeping paths and settings here means every other file just imports
from config instead of hardcoding strings everywhere.
"""

import os

# Base directory of the project (folder this file lives in)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder paths
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
DATABASE_DIR = os.path.join(BASE_DIR, "database")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# File paths
DATASET_CSV = os.path.join(DATASET_DIR, "incidents.csv")
DATABASE_PATH = os.path.join(DATABASE_DIR, "incidents.db")

# Hugging Face model name (pretrained, not trained from scratch)
MODEL_NAME = "google/flan-t5-base"

# Flask settings
SECRET_KEY = "dev-secret-key-change-this-in-production"
DEBUG = True

# Make sure required folders exist even on a fresh checkout
for folder in [DATASET_DIR, DATABASE_DIR, REPORTS_DIR, STATIC_DIR, TEMPLATES_DIR]:
    os.makedirs(folder, exist_ok=True)
