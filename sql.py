from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# Configure GenAI with API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt for Gemini
prompt = [
    """
    You are an expert in converting English questions to SQL queries using SQLite syntax!

    The SQL database may have one or more tables.
    
    Notes:
    - This is SQLite. Avoid MySQL commands like `SHOW TABLES`.
    - To list tables: SELECT name FROM sqlite_master WHERE type='table';
    - To get column info: PRAGMA table_info(table_name);

    Examples:
    Q: How many entries of records are present in STUDENT?
    A: SELECT COUNT(*) FROM STUDENT;

    Q: List all students in Data Science class?
    A: SELECT * FROM STUDENT WHERE CLASS='Data Science';

    Do NOT include ``` or the word 'sql' in the output.
    """
]

# Utility Functions
def get_tables():
    conn = sqlite3.connect("student.db")
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]
    conn.close()
    return tables

def get_columns(table):
    conn = sqlite3.connect("student.db")
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    cols = [(row[1], row[2]) for row in cur.fetchall()]
    conn.close()
    return cols

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
    response = model.generate_content([prompt[0], question])
    return response.text

def run_sql_query(query):
    try:
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        return rows
    except Exception as e:
        return str(e)

def execute_sql_command(query):
    try:
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return str(e)

# Streamlit UI
st.set_page_config(page_title="Text2SQL + CRUD")
st.title("🧠 Gemini SQL Assistant + CRUD")

mode = st.sidebar.radio("Choose Mode", [
    "Ask in Natural Language",
    "Insert Record",
    "Update Record",
    "Delete Record",
    "Create New Table"
])

# 1. Natural Language to SQL
if mode == "Ask in Natural Language":
    question = st.text_input("Enter your question:")
    if st.button("Get SQL & Execute"):
        sql_query = get_gemini_response(question, prompt)
        st.code(sql_query, language='sql')
        result = run_sql_query(sql_query)
        if isinstance(result, str):
            st.error(result)
        else:
            st.success("✅ Query executed!")
            for row in result:
                st.write(row)

# 2. Insert Record
elif mode == "Insert Record":
    st.subheader("📥 Insert Record")
    table = st.selectbox("Choose a table", get_tables())
    columns = get_columns(table)

    values = {}
    for col_name, col_type in columns:
        if col_type.upper() in ['INT', 'INTEGER']:
            values[col_name] = st.number_input(f"{col_name} ({col_type})", key=col_name)
        else:
            values[col_name] = st.text_input(f"{col_name} ({col_type})", key=col_name)

    if st.button("Insert"):
        cols_str = ", ".join(values.keys())
        vals_str = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in values.values()])
        query = f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str})"
        result = execute_sql_command(query)
        if result == True:
            st.success("✅ Record inserted!")
        else:
            st.error(result)

# 3. Update Record
elif mode == "Update Record":
    st.subheader("✏️ Update Record")
    table = st.selectbox("Choose a table", get_tables())
    columns = get_columns(table)

    update_col = st.selectbox("Column to update", [col[0] for col in columns])
    new_value = st.text_input(f"New value for {update_col}")

    condition_col = st.selectbox("Condition column (WHERE)", [col[0] for col in columns])
    condition_val = st.text_input(f"Value to match in {condition_col}")

    if st.button("Update"):
        new_val_formatted = f"'{new_value}'" if not new_value.isnumeric() else new_value
        cond_val_formatted = f"'{condition_val}'" if not condition_val.isnumeric() else condition_val
        query = f"UPDATE {table} SET {update_col}={new_val_formatted} WHERE {condition_col}={cond_val_formatted}"
        result = execute_sql_command(query)
        if result == True:
            st.success("✅ Record updated!")
        else:
            st.error(result)

# 4. Delete Record
elif mode == "Delete Record":
    st.subheader("🗑️ Delete Record")
    table = st.selectbox("Choose a table", get_tables())
    columns = get_columns(table)

    cond_col = st.selectbox("Condition column", [col[0] for col in columns])
    cond_val = st.text_input(f"Value to match in {cond_col}")

    if st.button("Delete"):
        cond_val_formatted = f"'{cond_val}'" if not cond_val.isnumeric() else cond_val
        query = f"DELETE FROM {table} WHERE {cond_col}={cond_val_formatted}"
        result = execute_sql_command(query)
        if result == True:
            st.success("✅ Record deleted!")
        else:
            st.error(result)

# 5. Create New Table
elif mode == "Create New Table":
    st.subheader("📦 Create New Table")

    table_name = st.text_input("Enter new table name")
    num_cols = st.number_input("Number of columns", min_value=1, step=1)

    columns = []
    for i in range(int(num_cols)):
        col_name = st.text_input(f"Column {i+1} Name", key=f"col_{i}")
        col_type = st.selectbox(f"Column {i+1} Type", ["TEXT", "INT", "REAL", "BOOLEAN"], key=f"type_{i}")
        columns.append((col_name, col_type))

    if st.button("Create Table"):
        try:
            col_defs = ", ".join([f"{name} {dtype}" for name, dtype in columns if name])
            query = f"CREATE TABLE {table_name} ({col_defs});"
            result = execute_sql_command(query)
            if result == True:
                st.success(f"✅ Table `{table_name}` created successfully!")
            else:
                st.error(result)
        except Exception as e:
            st.error(f"❌ Error: {e}")
