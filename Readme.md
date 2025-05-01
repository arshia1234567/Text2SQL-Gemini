# 🧠 Text2SQL + CRUD Streamlit App using Gemini and SQLite

This project is an interactive **Natural Language to SQL (Text2SQL)** application powered by **Gemini (Google Generative AI)** and **SQLite**. Users can interact with the database using natural language queries, and also perform full **CRUD operations** (Create, Read, Update, Delete) through a user-friendly Streamlit interface.

---

## 🚀 Features

- 🔍 **Natural Language to SQL Translation** using Gemini Pro API
- 🗄️ **Query Execution** on a local SQLite database
- 📊 **Dynamic Table Display** for `SELECT` queries
- ➕ **Insert Records** into any selected table
- 📝 **Update Records** in any table by choosing it from a dropdown
- ❌ **Delete Records** dynamically based on table selection
- 🧱 **Create New Tables** interactively by specifying column names and data types
- ✅ Integrated with `.env` for API key security

---

## 📦 Requirements

- Python 3.8+
- Streamlit
- Python-dotenv
- Google Generative AI SDK (`google-generativeai`)
- SQLite (built-in with Python)
- Pandas

---

## 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/arshia1234567/Text2SQL-Gemini.git
   cd Text2SQL-Gemini
   ```
