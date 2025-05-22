import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import pyodbc

app = Flask(__name__)
CORS(app)

SQL_SERVER   = os.getenv("AZURE_SQL_SERVER")
SQL_DATABASE = os.getenv("AZURE_SQL_DATABASE")
SQL_USER     = os.getenv("AZURE_SQL_USER")
SQL_PASSWORD = os.getenv("AZURE_SQL_PASSWORD")
DRIVER       = os.getenv("AZURE_SQL_DRIVER", "ODBC Driver 17 for SQL Server")

conn_str = (
    f"DRIVER={{ {DRIVER} }};"
    f"SERVER={SQL_SERVER};"
    f"DATABASE={SQL_DATABASE};"
    f"UID={SQL_USER};PWD={SQL_PASSWORD}"
)

@app.route('/mensagem-atual')
def get_ultima_mensagem():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 1 id, mensagem, autor, canal, datahora FROM MensagensTeams ORDER BY datahora DESC")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({}), 204
    return jsonify({
        "id": row.id,
        "mensagem": row.mensagem,
        "autor": row.autor,
        "canal": row.canal,
        "datahora": row.datahora.isoformat()
    })

@app.route('/historico')
def get_historico():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, mensagem, autor, canal, datahora
        FROM MensagensTeams
        WHERE id < (SELECT MAX(id) FROM MensagensTeams)
        ORDER BY datahora DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    historico = [{
        "id": r.id,
        "mensagem": r.mensagem,
        "autor": r.autor,
        "canal": r.canal,
        "datahora": r.datahora.isoformat()
    } for r in rows]
    return jsonify(historico)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
