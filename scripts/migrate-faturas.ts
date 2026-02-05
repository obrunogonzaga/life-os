/**
 * Migration script to import existing faturas data into SQLite
 * Run with: npx tsx scripts/migrate-faturas.ts
 */

import Database from 'better-sqlite3';
import path from 'path';

const DB_PATH = path.join(process.cwd(), 'brain', 'faturas.db');
const db = new Database(DB_PATH);

// Initialize schema
db.exec(`
  CREATE TABLE IF NOT EXISTS months (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    label TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month)
  );

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

  CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
  );

  CREATE INDEX IF NOT EXISTS idx_transactions_month ON transactions(month_id);
`);

// Settings
db.prepare('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)').run('wife_name', 'Alzi');
db.prepare('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)').run('split_percent', '50');

// === MARÇO 2026 ===
const mar2026 = db.prepare('INSERT OR IGNORE INTO months (year, month, label) VALUES (?, ?, ?)').run(2026, 3, 'Março 2026');
const marId = mar2026.lastInsertRowid || db.prepare('SELECT id FROM months WHERE year = 2026 AND month = 3').get()?.id;

const marchTransactions = [
  // ITAÚ BLACK (cartão 1721)
  { date: "2026-01-30", dateLabel: "30/01", name: "OliveirasMarket", cat: "supermercado · Curitiba", amount: 9.99, bank: "itau" },
  { date: "2026-01-29", dateLabel: "29/01", name: "Livraria da Vila", cat: "livraria · Curitiba", amount: 75.85, bank: "itau", installment: "01/02" },
  { date: "2026-01-28", dateLabel: "28/01", name: "Tendadoespetinhosa", cat: "restaurante · Curitiba", amount: 32.00, bank: "itau" },
  { date: "2026-01-28", dateLabel: "28/01", name: "Salty Produção de Vídeo", cat: "serviços · Curitiba", amount: 62.00, bank: "itau" },
  { date: "2026-01-28", dateLabel: "28/01", name: "Zig*Estádio Major Antônio", cat: "lazer · Curitiba", amount: 70.00, bank: "itau" },
  { date: "2026-01-28", dateLabel: "28/01", name: "Salty Produção de Vídeo", cat: "serviços · Curitiba", amount: 20.00, bank: "itau" },
  { date: "2025-09-05", dateLabel: "05/09", name: "PP *G40Treinamento", cat: "educação · São Paulo", amount: 166.49, bank: "itau", installment: "06/12" },
  { date: "2025-08-03", dateLabel: "03/08", name: "HTM*Luide de Matos", cat: "lazer · Salto do Itararé", amount: 28.90, bank: "itau", installment: "07/12" },
  { date: "2025-07-28", dateLabel: "28/07", name: "FabianaAssis", cat: "serviços · Curitiba", amount: 181.05, bank: "itau", installment: "07/10" },

  // PICPAY (cartão 8032)
  { date: "2026-02-03", dateLabel: "03/02", name: "Mp *AliExpress", cat: "compras · online", amount: 189.83, bank: "picpay", installment: "01/02" },
  { date: "2025-12-30", dateLabel: "30/12", name: "CFC*Pagamento1", cat: "serviços", amount: 188.91, bank: "picpay", installment: "02/12" },

  // BRADESCO 8429
  { date: "2026-02-02", dateLabel: "02/02", name: "Atacadão 859", cat: "supermercado · Curitiba", amount: 64.55, bank: "bradesco-8429" },
  { date: "2026-02-02", dateLabel: "02/02", name: "IOF Diário Rotativo/Atraso", cat: "encargos", amount: 0.78, bank: "bradesco-8429" },
  { date: "2026-02-02", dateLabel: "02/02", name: "IOF Adic Rotativo/Atraso", cat: "encargos", amount: 6.04, bank: "bradesco-8429" },
  { date: "2026-01-28", dateLabel: "28/01", name: "Uber", cat: "transporte", amount: 27.97, bank: "bradesco-8429" },
  { date: "2026-01-28", dateLabel: "28/01", name: "Uber", cat: "transporte", amount: 33.98, bank: "bradesco-8429" },
  { date: "2026-01-28", dateLabel: "28/01", name: "Uber", cat: "transporte", amount: 29.98, bank: "bradesco-8429" },
  { date: "2026-01-27", dateLabel: "27/01", name: "Mercado Zamprogna", cat: "supermercado · Curitiba", amount: 27.92, bank: "bradesco-8429" },
  { date: "2026-01-27", dateLabel: "27/01", name: "Uber", cat: "transporte", amount: 11.99, bank: "bradesco-8429" },
  { date: "2026-01-26", dateLabel: "26/01", name: "Condor Água Verde LJ29", cat: "supermercado · Curitiba", amount: 99.72, bank: "bradesco-8429" },
  { date: "2026-01-25", dateLabel: "25/01", name: "Amazon BR", cat: "compras · online", amount: 23.16, bank: "bradesco-8429" },
  { date: "2026-01-23", dateLabel: "23/01", name: "Aupetmia 06 Água Verde", cat: "pet · Curitiba", amount: 94.62, bank: "bradesco-8429" },
  { date: "2026-01-22", dateLabel: "22/01", name: "Uber", cat: "transporte", amount: 11.98, bank: "bradesco-8429" },
  { date: "2026-01-21", dateLabel: "21/01", name: "Alto da XV Mercearia", cat: "supermercado · Curitiba", amount: 16.00, bank: "bradesco-8429" },
  { date: "2026-01-21", dateLabel: "21/01", name: "Uber", cat: "transporte", amount: 11.99, bank: "bradesco-8429" },
  { date: "2026-01-21", dateLabel: "21/01", name: "Custo Trans. Exterior-IOF", cat: "encargos", amount: 20.93, bank: "bradesco-8429" },
  { date: "2026-01-20", dateLabel: "20/01", name: "Geandra Apoliana dos S", cat: "serviços", amount: 102.30, bank: "bradesco-8429" },
  { date: "2026-01-20", dateLabel: "20/01", name: "Super Festival", cat: "supermercado · Curitiba", amount: 19.29, bank: "bradesco-8429" },
  { date: "2026-01-20", dateLabel: "20/01", name: "Uber", cat: "transporte", amount: 11.98, bank: "bradesco-8429" },
  { date: "2026-01-19", dateLabel: "19/01", name: "Amazon Marketplace", cat: "compras · online", amount: 241.22, bank: "bradesco-8429", installment: "01/04" },
  { date: "2026-01-19", dateLabel: "19/01", name: "Balaroti Portão", cat: "casa · Curitiba", amount: 53.80, bank: "bradesco-8429" },
  { date: "2026-01-16", dateLabel: "16/01", name: "Uber", cat: "transporte", amount: 16.99, bank: "bradesco-8429" },
  { date: "2025-12-22", dateLabel: "22/12", name: "Havaianas Barigui", cat: "compras · Curitiba", amount: 139.96, bank: "bradesco-8429", installment: "02/02" },
  { date: "2025-10-22", dateLabel: "22/10", name: "EC ImagemReal", cat: "serviços · Osasco", amount: 69.00, bank: "bradesco-8429", installment: "04/10" },

  // BRADESCO 5969
  { date: "2026-01-30", dateLabel: "30/01", name: "Conquer Água MCRYPay", cat: "educação", amount: 390.00, bank: "bradesco-5969" },
  { date: "2026-01-27", dateLabel: "27/01", name: "Apple.com/bill", cat: "digital · São Paulo", amount: 29.90, bank: "bradesco-5969" },
  { date: "2026-01-26", dateLabel: "26/01", name: "Apple.com/bill", cat: "digital · São Paulo", amount: 11.90, bank: "bradesco-5969" },
  { date: "2026-01-23", dateLabel: "23/01", name: "Apple.com/bill", cat: "digital · São Paulo", amount: 99.90, bank: "bradesco-5969" },
  { date: "2026-01-21", dateLabel: "21/01", name: "Claude.ai Subscription", cat: "digital · US$", amount: 598.14, bank: "bradesco-5969" },

  // NUBANK
  { date: "2026-02-01", dateLabel: "01/02", name: "Amazonmktplc*Uzindustr", cat: "compras · online", amount: 58.25, bank: "nubank", installment: "05/12" },
  { date: "2026-02-01", dateLabel: "01/02", name: "Amazon", cat: "compras · online", amount: 453.61, bank: "nubank", installment: "08/12" },
  { date: "2026-02-01", dateLabel: "01/02", name: "Mercadolivre*Mercadol", cat: "compras · online", amount: 113.59, bank: "nubank", installment: "04/12" },
];

const insertTx = db.prepare(`
  INSERT INTO transactions (month_id, date, date_label, name, category, amount, bank, installment, is_wife)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
`);

console.log(`Inserting ${marchTransactions.length} transactions for March 2026...`);
for (const tx of marchTransactions) {
  insertTx.run(marId, tx.date, tx.dateLabel, tx.name, tx.cat, tx.amount, tx.bank, tx.installment || null);
}

// Verify
const count = db.prepare('SELECT COUNT(*) as c FROM transactions WHERE month_id = ?').get(marId) as { c: number };
console.log(`✅ Inserted ${count.c} transactions for March 2026`);

const total = db.prepare('SELECT SUM(amount) as t FROM transactions WHERE month_id = ?').get(marId) as { t: number };
console.log(`💰 Total: R$ ${total.t.toFixed(2)}`);

db.close();
console.log('✅ Migration complete!');
