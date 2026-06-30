CREATE TABLE IF NOT EXISTS sessions (
  phone_number TEXT PRIMARY KEY,
  business_type TEXT,
  last_active TEXT,
  status TEXT DEFAULT 'active',
  follow_up_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS conversations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  phone_number TEXT,
  role TEXT,
  content TEXT,
  timestamp TEXT
);

CREATE TABLE IF NOT EXISTS appointments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  phone_number TEXT,
  business_type TEXT,
  datetime TEXT,
  service TEXT,
  status TEXT DEFAULT 'confirmed',
  reminded INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  phone_number TEXT,
  items TEXT,
  total REAL,
  status TEXT DEFAULT 'pending',
  created_at TEXT
);
