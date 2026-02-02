#!/usr/bin/env bash
# Render build script - runs during deployment
# https://render.com/docs/deploy-flask

set -o errexit  # Exit on error

echo "==> Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

echo "==> Running database migrations..."
flask db upgrade

echo "==> Seeding demo data (if database is empty)..."
python scripts/seed_demo_data.py

echo "==> Build complete!"
