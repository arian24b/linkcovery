# Linkcovery

![Linkcovery Logo](https://via.placeholder.com/150) <!-- Replace with actual logo if available -->

**Linkcovery** is a robust link discovery tool built with Python, designed to help you efficiently manage and explore your collection of links. Whether you're a developer, researcher, or avid internet surfer, Linkcovery provides an intuitive CLI to add, search, and organize your links seamlessly.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [User Commands](#user-commands)
  - [Link Commands](#link-commands)
  - [Import Commands](#import-commands)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Add and Manage Users**: Easily add new users and list existing ones.
- **Link Management**: Add, list, search, update, and delete links with comprehensive metadata.
- **Import Functionality**: Import links from TXT and CSV files efficiently.
- **Search Capabilities**: Advanced search with filtering by domain, tags, and description, along with sorting and pagination.
- **Atomic Operations**: Ensures data integrity with atomic transactions when creating users and links.
- **Rich CLI Interface**: User-friendly command-line interface with prompts and colored outputs for better usability.
- **SQLite Database with Connection Pooling**: Efficient database management using SQLite with a connection pool for optimized performance.

## Installation

### Prerequisites

- **Python 3.13+**: Ensure you have Python version 3.13 or higher installed.
- **UV**: Used for dependency management and packaging.

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/linkcovery.git
   cd linkcovery
   ```

2. **Install Dependencies**

   Using UV:

   ```bash
   uv sync
   ```

3. **Set Up Environment Variables**

   Copy the example environment file and configure as needed.

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file to set your desired configurations.

4. **Run cli**

   Before running the application, initialize the SQLite database.

   ```bash
   uv run linkcovery --help
   ```

## Configuration

Linkcovery uses environment variables for configuration. Here's how to set them up:

1. **Environment Variables**

   Create a `.env` file in the root directory based on `.env.example`:

   ```bash
   cp .env.example .env
   ```

2. **Configure `.env`**

   ```env
   DATABASE_NAME=app.db
   DEBUG=True
   ALLOW_EXTENTIONS=csv,txt
   ```

   - `DATABASE_NAME`: Name of the SQLite database file.
   - `DEBUG`: Enable or disable debug mode.
   - `ALLOW_EXTENTIONS`: Allowed file extensions for import functionality.

## Usage

Linkcovery provides a comprehensive CLI built with [Typer](https://typer.tiangolo.com/) for managing users and links. Below are the available commands and their descriptions.

### Running the CLI

Activate the virtual environment and run the CLI:

```bash
uv run
```

Alternatively, use Poetry to run commands without activating the shell:

```bash
uv run linkcovery [COMMAND]
```

### User Commands

#### Add a New User

Add a new user to the database.

```bash
linkcovery user-add
```

You will be prompted to enter the user's name and email.

**Options:**

- `--name, -n`: Name of the user.
- `--email, -e`: Email of the user.

**Example:**

```bash
linkcovery user-add --name "Alice" --email "alice@example.com"
```

#### List All Users

Display a list of all users in the database.

```bash
linkcovery user-list
```

**Example:**

```bash
linkcovery user-list
```

### Link Commands

#### Add a New Link

Add a new link to the database.

```bash
linkcovery link-add
```

You can provide options or use interactive prompts.

**Options:**

- `--url, -u`: URL of the link.
- `--domain, -d`: Domain of the link.
- `--author-email, -a`: Email of the author.
- `--description, -desc`: Description of the link.
- `--tag, -t`: Tags associated with the link.

**Example:**

```bash
linkcovery link-add --url "https://example.com" --domain "example.com" --author-email "alice@example.com" --description "An example website" --tag "example" "test"
```

#### List All Links

Display all links along with their authors.

```bash
linkcovery link-list
```

**Example:**

```bash
linkcovery link-list
```

#### Search for Links

Search for links based on various criteria.

```bash
linkcovery link-search [OPTIONS]
```

**Options:**

- `--domain, -d`: Filter by domain.
- `--tag, -t`: Tags to filter by.
- `--description, -desc`: Filter by description.
- `--sort-by, -s`: Field to sort by (`created_at`, `updated_at`, `domain`).
- `--sort-order, -o`: Sort order (`ASC`, `DESC`).
- `--limit, -l`: Number of results to return.
- `--offset, -of`: Number of results to skip.

**Example:**

```bash
linkcovery link-search --domain "example" --tag "test" --description "example" --sort-by "created_at" --sort-order "DESC" --limit 5 --offset 0
```

#### Delete a Link

Delete a link by its ID.

```bash
linkcovery link-delete --link-id [ID]
```

**Options:**

- `--link-id, -id`: ID of the link to delete.

**Example:**

```bash
linkcovery link-delete --link-id 1
```

#### Update a Link

Update details of a link by its ID.

```bash
linkcovery link-update [OPTIONS]
```

**Options:**

- `--link-id, -id`: ID of the link to update.
- `--url, -u`: New URL.
- `--domain, -d`: New domain.
- `--description, -desc`: New description.
- `--tag, -t`: New tags.
- `--is-read, -r`: Mark as read (`True` or `False`).

**Example:**

```bash
linkcovery link-update --link-id 1 --description "Updated description" --is-read True
```

### Import Commands

#### Import Links from a File

Import links from a TXT or CSV file.

```bash
linkcovery import --file-path [PATH] --author-id [ID]
```

**Options:**

- `--file-path, -f`: Path to the `.txt` or `.csv` file.
- `--author-id, -a`: ID of the author to associate with the imported links.

**Examples:**

- Import from TXT:

  ```bash
  linkcovery import --file-path links.txt --author-id 1
  ```

- Import from CSV:

  ```bash
  linkcovery import --file-path links.csv --author-id 1
  ```

## License

[MIT License](LICENSE)

## Contact

For any inquiries or support, please contact:

- **Email**: [arian24b@gmail.com](mailto:arian24b@gmail.com)
- **GitHub**: [@arian24b](https://github.com/arian24b)

---

_Made with ❤️ and Python 🐍_
