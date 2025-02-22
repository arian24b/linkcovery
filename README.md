# Linkcovery

![Linkcovery Logo](https://via.placeholder.com/150)

**Linkcovery** is a powerful bookmark and link discovery tool built with Python, designed to help users efficiently manage and explore their collection of links. It provides an intuitive command-line interface (CLI) that enables developers, researchers, and avid internet users to seamlessly add, search, and organize links.

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

- **User Management**: Easily create, update, delete, and list users.
- **Link Management**: Add, list, search, update, and delete links with full metadata (URL, description, domain, tags).
- **Search Capabilities**: Advanced search functionality to filter links by domain, tags, description, read status, and more.
- **Link Import**: Import links from `.txt`, `.csv`, and `.json` files, associating them with a specific user.
- **Atomic Operations**: Ensures data integrity during user and link creation with atomic transactions.
- **Rich CLI Interface**: A user-friendly, interactive CLI with prompts and colored output for enhanced usability.
- **SQLite Database**: Stores data efficiently in an SQLite database, supporting connection pooling for optimized performance.

## Installation

### Prerequisites

- **Python 3.13+**: Ensure Python 3.13 or higher is installed on your system.
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

   Copy the example environment file and configure it:

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file to set your preferred configurations.

4. **Run the Application**

   Before running the app, initialize the SQLite database:

   ```bash
   uv run linkcovery --help
   ```

## Configuration

Linkcovery uses environment variables for configuration. The `.env` file can be configured with the following settings:

1. **Environment Variables**

   Create a `.env` file in the root directory based on `.env.example`:

   ```bash
   cp .env.example .env
   ```

2. **Configure `.env`**

   Example configuration:

   ```env
   DATABASE_NAME=app.db
   DEBUG=True
   ALLOW_EXTENTIONS=csv,txt,json
   ```

   - `DATABASE_NAME`: Name of the SQLite database file.
   - `DEBUG`: Enable or disable debug mode.
   - `ALLOW_EXTENSIONS`: Allowed file extensions for importing links.

## Usage

Linkcovery provides a CLI built using [Typer](https://typer.tiangolo.com/) to manage users and links.

### Running the CLI

Activate the virtual environment and run the CLI:

```bash
uv run
```

Alternatively, you can use Poetry to run commands without activating the shell:

```bash
uv run linkcovery [COMMAND]
```

### User Commands

#### Add a New User

```bash
linkcovery user create --name "Alice" --email "alice@example.com"
```

#### List All Users

```bash
linkcovery user list
```

### Link Commands

#### Add a New Link

```bash
linkcovery link create --url "https://example.com" --domain "example.com" --author-email "alice@example.com" --description "An example website" --tag "example" "test"
```

#### Search for Links

```bash
linkcovery link search --domain "example" --tag "test" --description "example" --sort-by "created_at" --sort-order "DESC" --limit 5 --offset 0
```

#### Delete a Link

```bash
linkcovery link delete --link-id 1
```

#### Update a Link

```bash
linkcovery link update --link-id 1 --description "Updated description" --is-read True
```

### Import Commands

#### Import Links from a File

Import links from `.txt`, `.csv`, or `.json` files.

```bash
linkcovery db import --file-path links.txt --author-id 1
```

## License

[MIT License](LICENSE)

## Contact

For inquiries or support, please contact:

- **Email**: [arian24b@gmail.com](mailto:arian24b@gmail.com)
- **GitHub**: [@arian24b](https://github.com/arian24b)

---

_Made with ❤️ and Python 🐍_
