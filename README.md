# Asetate

A local-first DJ library manager for vinyl collectors. Sync your Discogs collection, add DJ-specific metadata (BPM, key, energy, crates), and export to CSV for label printing.

## Features

- **Discogs Sync** - Pull your collection from Discogs with automatic rate limiting and resume support
- **DJ Metadata** - Add BPM, musical key (Camelot), energy level, and custom tags to tracks
- **Crates** - Organize releases and individual tracks into nested crates
- **Smart Export** - Filter by crate, BPM range, key, energy, and more - then export to CSV for label printing
- **Local-First** - All data stored locally in SQLite. Your library, your data.

## Quick Start

### Prerequisites

- Python 3.10+
- A Discogs account with a personal access token

### Installation

```bash
# Clone the repository
git clone https://github.com/asetate/asetate.git
cd asetate

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# For development
pip install -e ".[dev]"
```

### Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your Discogs credentials
# Get your token at: https://www.discogs.com/settings/developers
```

### Database Setup

```bash
# Initialize the database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Running

```bash
# Development server
flask run

# Or with debug mode
FLASK_DEBUG=1 flask run
```

Visit `http://localhost:5000` in your browser.

## Project Structure

```
asetate/
├── asetate/              # Main application package
│   ├── models/           # Database models
│   ├── routes/           # Flask blueprints
│   ├── templates/        # Jinja2 templates
│   └── static/           # CSS, JS, images
├── migrations/           # Database migrations
├── tests/                # Test suite
├── .env.example          # Environment template
└── pyproject.toml        # Project configuration
```

## Data Model

- **Releases** - Vinyl records from your Discogs collection
- **Tracks** - Individual tracks with DJ metadata (BPM, key, energy, playable)
- **Crates** - Hierarchical folders for organizing releases and tracks
- **Tags** - Custom labels for categorizing tracks

## Discogs API

Asetate uses the Discogs API to sync your collection. You'll need a personal access token:

1. Go to [Discogs Developer Settings](https://www.discogs.com/settings/developers)
2. Click "Generate new token"
3. Copy the token to your `.env` file

Note: Discogs limits API requests to 60/minute. Large collections sync automatically with rate limiting and can be paused/resumed.

## Contributing

Contributions welcome! Please keep dependencies minimal and document any setup changes.

## License

MIT License - see LICENSE for details.
