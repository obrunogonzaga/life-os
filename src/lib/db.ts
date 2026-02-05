import Database from 'better-sqlite3';
import path from 'path';

const DB_PATH = path.join(process.cwd(), 'brain', 'faturas.db');

let db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!db) {
    db = new Database(DB_PATH);
    db.pragma('journal_mode = WAL');
    initSchema();
  }
  return db;
}

function initSchema() {
  const database = db!;
  
  database.exec(`
    -- Meses/Faturas
    CREATE TABLE IF NOT EXISTS months (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      year INTEGER NOT NULL,
      month INTEGER NOT NULL,
      label TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(year, month)
    );

    -- Transações
    CREATE TABLE IF NOT EXISTS transactions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      month_id INTEGER NOT NULL,
      date TEXT NOT NULL,
      date_label TEXT NOT NULL,
      name TEXT NOT NULL,
      category TEXT,
      amount REAL NOT NULL,
      bank TEXT NOT NULL,
      installment TEXT,
      is_wife INTEGER DEFAULT 0,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (month_id) REFERENCES months(id) ON DELETE CASCADE
    );

    -- Configurações
    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      value TEXT
    );

    -- Índices
    CREATE INDEX IF NOT EXISTS idx_transactions_month ON transactions(month_id);
    CREATE INDEX IF NOT EXISTS idx_transactions_bank ON transactions(bank);
  `);

  // Default settings
  const insertSetting = database.prepare(
    'INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)'
  );
  insertSetting.run('wife_name', 'Alzi');
  insertSetting.run('split_percent', '50');
}

// === MONTHS ===
export function getAllMonths() {
  const db = getDb();
  return db.prepare(`
    SELECT m.*, 
      (SELECT SUM(amount) FROM transactions WHERE month_id = m.id) as total,
      (SELECT SUM(amount) FROM transactions WHERE month_id = m.id AND is_wife = 1) as wife_total,
      (SELECT COUNT(*) FROM transactions WHERE month_id = m.id) as tx_count,
      (SELECT GROUP_CONCAT(DISTINCT bank) FROM transactions WHERE month_id = m.id) as banks
    FROM months m
    ORDER BY year DESC, month DESC
  `).all();
}

export function getMonth(year: number, month: number) {
  const db = getDb();
  return db.prepare('SELECT * FROM months WHERE year = ? AND month = ?').get(year, month);
}

export function getMonthById(id: number) {
  const db = getDb();
  return db.prepare('SELECT * FROM months WHERE id = ?').get(id);
}

export function createMonth(year: number, month: number, label: string) {
  const db = getDb();
  const result = db.prepare(
    'INSERT INTO months (year, month, label) VALUES (?, ?, ?)'
  ).run(year, month, label);
  return result.lastInsertRowid;
}

// === TRANSACTIONS ===
export function getTransactionsByMonth(monthId: number) {
  const db = getDb();
  return db.prepare(
    'SELECT * FROM transactions WHERE month_id = ? ORDER BY date DESC, id'
  ).all(monthId);
}

export function createTransaction(tx: {
  month_id: number;
  date: string;
  date_label: string;
  name: string;
  category?: string;
  amount: number;
  bank: string;
  installment?: string;
  is_wife?: number;
}) {
  const db = getDb();
  const result = db.prepare(`
    INSERT INTO transactions (month_id, date, date_label, name, category, amount, bank, installment, is_wife)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    tx.month_id,
    tx.date,
    tx.date_label,
    tx.name,
    tx.category || null,
    tx.amount,
    tx.bank,
    tx.installment || null,
    tx.is_wife || 0
  );
  return result.lastInsertRowid;
}

export function updateTransactionWife(id: number, isWife: boolean) {
  const db = getDb();
  return db.prepare('UPDATE transactions SET is_wife = ? WHERE id = ?').run(isWife ? 1 : 0, id);
}

export function bulkUpdateWife(ids: number[], isWife: boolean) {
  const db = getDb();
  const placeholders = ids.map(() => '?').join(',');
  return db.prepare(
    `UPDATE transactions SET is_wife = ? WHERE id IN (${placeholders})`
  ).run(isWife ? 1 : 0, ...ids);
}

export function deleteTransaction(id: number) {
  const db = getDb();
  return db.prepare('DELETE FROM transactions WHERE id = ?').run(id);
}

// === SETTINGS ===
export function getSetting(key: string): string | null {
  const db = getDb();
  const row = db.prepare('SELECT value FROM settings WHERE key = ?').get(key) as { value: string } | undefined;
  return row?.value || null;
}

export function setSetting(key: string, value: string) {
  const db = getDb();
  return db.prepare(
    'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)'
  ).run(key, value);
}

// === STATS ===
export function getMonthStats(monthId: number) {
  const db = getDb();
  const stats = db.prepare(`
    SELECT 
      SUM(amount) as total,
      SUM(CASE WHEN is_wife = 1 THEN amount ELSE 0 END) as wife_total,
      COUNT(*) as tx_count,
      COUNT(CASE WHEN is_wife = 1 THEN 1 END) as wife_count
    FROM transactions 
    WHERE month_id = ?
  `).get(monthId) as { total: number; wife_total: number; tx_count: number; wife_count: number };
  
  const splitPercent = parseInt(getSetting('split_percent') || '50');
  const wifeHalf = (stats.wife_total || 0) * (splitPercent / 100);
  const brunoPays = (stats.total || 0) - wifeHalf;
  
  return {
    ...stats,
    wife_half: wifeHalf,
    bruno_pays: brunoPays,
    split_percent: splitPercent,
  };
}

export function getBankStats(monthId: number) {
  const db = getDb();
  return db.prepare(`
    SELECT bank, SUM(amount) as total, COUNT(*) as count
    FROM transactions 
    WHERE month_id = ?
    GROUP BY bank
    ORDER BY total DESC
  `).all(monthId);
}
