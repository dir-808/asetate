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

# Edit .env and set a SECRET_KEY
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

## Authentication Modes

Asetate supports two authentication modes:

### Self-Hosted Mode (Default)

Best for single-user deployments. No OAuth app registration required.

1. Run the app with default `.env` (no Discogs OAuth credentials)
2. Click "Get Started" when you visit the app
3. Go to [Discogs Developer Settings](https://www.discogs.com/settings/developers)
4. Click "Generate new token" to create a Personal Access Token
5. Enter your Discogs username and token in the Settings page

### Hosted Mode (Multi-user)

Best for hosting Asetate as a service for multiple users.

1. Go to [Discogs Developer Settings](https://www.discogs.com/settings/developers)
2. Click "Add New Application"
3. Set the callback URL to `http://yourdomain.com/auth/callback`
4. Add `DISCOGS_CONSUMER_KEY` and `DISCOGS_CONSUMER_SECRET` to your `.env`
5. Users sign in with "Sign in with Discogs" button

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

## Rate Limiting

Discogs limits API requests to 60/minute. Large collections sync automatically with rate limiting and can be paused/resumed.

## Contributing

Contributions welcome! Please keep dependencies minimal and document any setup changes.

## License

MIT License - see LICENSE for details.
