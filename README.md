# Linkcovery

**Linkcovery** is a modern link discovery and management tool designed for developers and individuals who love Python. It allows you to organize links, tag them, and associate them with authors, all while leveraging SQLite for storage.

---

## 🚀 Features

- **User Management**: Create and manage users with validated inputs.
- **Link Management**: Add, update, delete, and search links with advanced filters.
- **Metadata**: Store descriptions, tags, and timestamps for each link.
- **Relationships**: Associate links with their authors using foreign keys.
- **Search**: Advanced filtering by domain, tags, and descriptions.
- **Pagination**: Retrieve large datasets with pagination support.
- **Terminal Output**: Enhanced and readable terminal outputs using `rich`.

---

## 🛠️ Installation

### Prerequisites

- Python **3.13** or higher.
- `uv` (Python package manager).

### Clone the Repository

```bash
git clone git@github.com:arian24b/linkcovery.git
cd linkcovery
```

### Install Dependencies

```bash
uv sync
```

---

## 📄 Usage

### Initialize the Database

Run the `main.py` file to create the database schema and seed the database with sample data.

```bash
uv run src/main.py
```

### Basic Operations

- **Create a User**: Add a user with a unique email address.
- **Add a Link**: Add a link with metadata (tags, descriptions, etc.) and associate it with a user.
- **Retrieve Links**: Fetch all links with their authors or perform advanced searches.

---

## 🔧 Configuration

- **Database Name**: Modify the database name in `src/settings.py`.

```python
DATABASE_NAME = "app.db"
```

- **Environment Variables**: Use `.env.example` as a template to create a `.env` file for environment-specific settings.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 💡 Contributing

Contributions are welcome! Feel free to submit issues or pull requests for improvements.

### Steps to Contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

---

## 🛠️ Tech Stack

- **Python 3.13**
- **UV**
- **SQLite**
- **Rich** for terminal output
- **Pydantic** for schema validation

---

## 📄 Roadmap

- [ ] Add API or CLI support.
- [ ] Implement unit and integration tests.
- [ ] Add a web or desktop UI.
- [ ] Enhance search functionality with FTS (Full-Text Search).

---

## 🤝 Acknowledgements

- **SQLite**: For its simplicity and performance.
- **Pydantic**: For making schema validation easy.
- **Rich**: For beautiful terminal output.

---

## 📧 Contact

For questions or feedback, reach out to **Arian Omrani** via [arian24b@gmail.com](mailto:arian24b@gmail.com).

---

Happy coding! 😊
