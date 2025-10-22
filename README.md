# DDO Item Catalog Manager

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Overview

This project is a Python-based tool designed for Dungeons & Dragons Online (DDO) players and developers to collect, store, and manage item data. It supports two primary data sources:

- **JSON Payloads**: Ingest item data from the "Dungeon Helper - Trove" plugin, which provides structured JSON outputs.
- **Web Scraping**: Extract item details from [ddowiki.com](https://ddowiki.com), a community-driven wiki for DDO.

The collected data is standardized into a structured format and stored in a lightweight SQLite database. Users can then add items to their personal catalog, enhancing them with custom attributes such as Mythic Bonuses, Augments, or Reaper Bonuses. This allows for easy tracking, querying, and customization of in-game items.

The tool is built with modularity in mind, making it extensible for additional data sources or features. It's ideal for GitHub developers looking to contribute to DDO-related projects or build personal inventory managers.

## Features

- **Data Collection**:
  - Parse JSON payloads from the Dungeon Helper - Trove plugin.
  - Scrape item data from ddowiki.com using ethical web scraping practices (e.g., respecting rate limits and robots.txt).
- **Data Standardization**: Convert raw data into a consistent schema (e.g., item name, type, stats, effects).
- **Database Storage**: Use SQLite for a flat-file database that's portable and requires no server setup.
- **Personal Catalog Management**:
  - Add items to a user-specific catalog.
  - Apply custom attributes like Mythic Bonus (+1 to +3), Augments (e.g., slot-based enhancements), or Reaper Bonus (e.g., +1 to +10 scaling).
  - Query and export catalog data for analysis or sharing.
- **Command-Line Interface (CLI)**: Simple CLI for data ingestion, catalog updates, and queries.
- **Extensibility**: Modular code structure for adding new scrapers, parsers, or database schemas.

## Installation

1. **Clone the Repository**:
   ```
   git clone https://github.com/yourusername/ddo-item-catalog-manager.git
   cd ddo-item-catalog-manager
   ```

2. **Set Up a Virtual Environment** (Recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   The project uses a `requirements.txt` file for dependencies. Install them with:
   ```
   pip install -r requirements.txt
   ```
   Key dependencies include:
   - `requests` and `beautifulsoup4` for web scraping.
   - `sqlite3` (built-in) for database operations.
   - `json` (built-in) for parsing payloads.

4. **Database Initialization**:
   Run the setup script to create the SQLite database:
   ```
   python scripts/init_db.py
   ```

## Usage

### Collecting Data from JSON Payloads
Provide a JSON file from the Dungeon Helper - Trove plugin:
```
python main.py ingest-json --file path/to/item.json
```
This parses the JSON, standardizes the data, and inserts it into the `items.db` database.

### Web Scraping from ddowiki.com
Scrape a specific item page (e.g., for "Celestial Avenger"):
```
python main.py scrape --url https://ddowiki.com/page/Celestial_Avenger
```
**Note**: Always check ddowiki.com's terms of service and robots.txt before scraping. Implement delays to avoid overloading the site.

### Adding to Personal Catalog
Once items are in the database, add them to your catalog with custom attributes:
```
python main.py add-to-catalog --item-id 123 --mythic 2 --augment "Topaz of Power +150" --reaper 5
```
This updates the user's catalog table with the enhanced item.

### Querying the Catalog
View your personal catalog:
```
python main.py query --user your_username
```
Export to CSV:
```
python main.py export --format csv --output catalog.csv
```

For full CLI options, run:
```
python main.py --help
```

## Project Structure

```
ddo-item-catalog-manager/
├── main.py              # Entry point for CLI
├── requirements.txt     # Python dependencies
├── items.db             # SQLite database (generated)
├── src/                 # Core source code
│   ├── __init__.py
│   ├── data_ingest.py   # JSON parsing and standardization
│   ├── scraper.py       # Web scraping logic
│   ├── database.py      # SQLite operations (CRUD)
│   └── catalog.py       # Personal catalog management
├── scripts/             # Utility scripts
│   └── init_db.py       # Database schema setup
├── tests/               # Unit tests
│   └── test_scraper.py
├── docs/                # Additional documentation
└── README.md            # This file
```

## Best Practices Guidelines

To maintain a clean, scalable, and collaborative codebase, follow these guidelines:

### Code Style and Quality
- **PEP 8 Compliance**: Adhere to Python's PEP 8 style guide. Use tools like `black` or `flake8` for auto-formatting and linting.
- **Docstrings**: Document all functions, classes, and modules using Google-style or NumPy-style docstrings. Example:
  ```python
  def ingest_json(file_path: str) -> None:
      """Ingests item data from a JSON file and inserts into the database.

      Args:
          file_path: Path to the JSON file.
      """
  ```
- **Type Hints**: Use type annotations (e.g., from `typing`) for function parameters and returns to improve readability and enable static analysis with `mypy`.
- **Error Handling**: Implement robust try-except blocks, especially for I/O operations, network requests, and database queries. Log errors using the `logging` module instead of `print`.

### Testing
- Write unit tests for all core modules using `pytest`. Aim for at least 80% code coverage.
- Test edge cases, such as invalid JSON, failed scrapes, or duplicate database entries.
- Run tests with:
  ```
  pytest
  ```

### Version Control
- **Commit Messages**: Use conventional commits (e.g., "feat: add JSON ingestion", "fix: handle scraping errors").
- **Branching**: Use feature branches (e.g., `feat/new-scraper`) and pull requests for merges to `main`.
- **Gitignore**: Ensure `.gitignore` excludes virtual environments, databases, and temporary files.

### Security and Ethics
- **Web Scraping Ethics**: Respect website terms—add delays (e.g., via `time.sleep`) and user-agent headers. Do not scrape excessively.
- **Data Privacy**: Avoid storing sensitive user data. The personal catalog is local-only.
- **Dependencies**: Regularly update dependencies with `pip install -r requirements.txt --upgrade` and scan for vulnerabilities using `pip-audit`.

### Performance
- Use efficient queries in SQLite (e.g., indexes on frequently queried fields like item ID).
- For large datasets, batch insertions to avoid performance bottlenecks.

### Contributing
Contributions are welcome! Fork the repo, create a feature branch, and submit a pull request. Include tests and update documentation as needed.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the DDO community and tools like Dungeon Helper - Trove.
- Thanks to ddowiki.com for providing open item data.

If you encounter issues or have suggestions, open an issue on GitHub!
