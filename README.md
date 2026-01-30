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
- A Discogs account
- Discogs OAuth application credentials (for self-hosting)

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

# Edit .env with your Discogs OAuth credentials
```

To get Discogs OAuth credentials:
1. Go to [Discogs Developer Settings](https://www.discogs.com/settings/developers)
2. Click "Add New Application"
3. Fill in the application details
4. Set the callback URL to `http://localhost:5000/auth/callback`
5. Copy the Consumer Key and Consumer Secret to your `.env` file

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

## Authentication

Asetate uses Discogs OAuth for authentication. Users sign in with their Discogs account, which also grants access to sync their collection. No separate account creation is required.

Note: Discogs limits API requests to 60/minute. Large collections sync automatically with rate limiting and can be paused/resumed.

## Contributing

Contributions welcome! Please keep dependencies minimal and document any setup changes.

## License

MIT License - see LICENSE for details.
