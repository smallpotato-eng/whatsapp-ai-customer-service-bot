from flask import Flask, request, jsonify
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from quotation_gen import generate_quote

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "db" / "cs_ai.db"
SCHEMA_PATH = BASE_DIR / "db" / "schema.sql"

def get_db():
    db_path = Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with open(Path(SCHEMA_PATH), encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

# --- Session ---
@app.route("/session/<phone>", methods=["GET"])
def get_session(phone):
    conn = get_db()
    row = conn.execute("SELECT * FROM sessions WHERE phone_number=?", (phone,)).fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({}), 404

@app.route("/session", methods=["POST"])
def upsert_session():
    data = request.json or request.form.to_dict()
    conn = get_db()
    conn.execute("""
        INSERT INTO sessions (phone_number, business_type, last_active, status, follow_up_count)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(phone_number) DO UPDATE SET
          business_type=excluded.business_type,
          last_active=excluded.last_active,
          status=excluded.status,
          follow_up_count=excluded.follow_up_count
    """, (
        data["phone_number"],
        data.get("business_type"),
        datetime.now().isoformat(),
        data.get("status", "active"),
        data.get("follow_up_count", 0)
    ))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/session/<phone>", methods=["DELETE"])
def delete_session(phone):
    conn = get_db()
    conn.execute("DELETE FROM sessions WHERE phone_number=?", (phone,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# --- Conversations ---
@app.route("/conversations/<phone>", methods=["GET"])
def get_conversations(phone):
    limit = request.args.get("limit", 20, type=int)
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM conversations WHERE phone_number=?
        ORDER BY id DESC LIMIT ?
    """, (phone, limit)).fetchall()
    conn.close()
    history = [dict(r) for r in reversed(rows)]
    return jsonify({"history": history, "count": len(history)})

@app.route("/conversations", methods=["POST"])
def add_conversation():
    data = request.json
    conn = get_db()
    conn.execute("""
        INSERT INTO conversations (phone_number, role, content, timestamp)
        VALUES (?, ?, ?, ?)
    """, (data["phone_number"], data["role"], data["content"], datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# --- Appointments ---
@app.route("/appointments", methods=["POST"])
def create_appointment():
    data = request.json
    conn = get_db()
    conn.execute("""
        INSERT INTO appointments (phone_number, business_type, datetime, service)
        VALUES (?, ?, ?, ?)
    """, (data["phone_number"], data["business_type"], data["datetime"], data["service"]))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/appointments/tomorrow", methods=["GET"])
def appointments_tomorrow():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM appointments
        WHERE datetime LIKE ? AND status='confirmed' AND reminded=0
    """, (f"{tomorrow}%",)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/appointments/<int:appt_id>/reminded", methods=["POST"])
def mark_reminded(appt_id):
    conn = get_db()
    conn.execute("UPDATE appointments SET reminded=1 WHERE id=?", (appt_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# --- Follow-up ---
@app.route("/sessions/stale", methods=["GET"])
def stale_sessions():
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM sessions
        WHERE status='active'
        AND follow_up_count < 2
        AND datetime(last_active) < datetime('now', '-24 hours')
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# --- Orders ---
@app.route("/orders", methods=["POST"])
def create_order():
    data = request.json
    conn = get_db()
    conn.execute("""
        INSERT INTO orders (phone_number, items, total, status, created_at)
        VALUES (?, ?, ?, 'pending', ?)
    """, (data["phone_number"], json.dumps(data["items"]), data["total"], datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/orders/<phone>", methods=["GET"])
def get_orders(phone):
    conn = get_db()
    rows = conn.execute("SELECT * FROM orders WHERE phone_number=? ORDER BY id DESC", (phone,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/orders/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    data = request.json
    conn = get_db()
    conn.execute("UPDATE orders SET status=? WHERE id=?", (data["status"], order_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/quotation", methods=["POST"])
def quotation():
    data = request.json or request.form.to_dict()
    business_type = data.get("business_type")
    phone = data.get("phone", "unknown")
    quote_data = data.get("quote_data", {})
    lang = data.get("lang", "zh-hk")

    if isinstance(quote_data, str):
        try:
            quote_data = json.loads(quote_data)
        except Exception:
            quote_data = {}

    result = generate_quote(business_type, phone, quote_data, lang)
    if not result:
        return jsonify({"ok": False, "error": "Unsupported business type"}), 400

    return jsonify({
        "ok": True,
        "filename": result["filename"],
        "base64": result["base64"]
    })

# --- SOP Reader ---
@app.route("/sop", methods=["GET"])
def read_sop():
    path = request.args.get("path", "")
    if not path:
        return jsonify({"ok": False, "error": "No path provided"}), 400
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    sop = {}
    marker = raw.find("[SOP]")
    header = raw[:marker] if marker != -1 else raw

    for line in header.splitlines():
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip().lower().replace(" ", "_")
        value = value.strip()
        if key and value:
            sop[key] = value

    if marker != -1:
        sop["sop_content"] = raw[marker + 5:].strip()

    return jsonify({"ok": True, "sop": sop})

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized")
    print("✅ Flask API running on http://localhost:5050")
    app.run(port=5050, debug=False)
