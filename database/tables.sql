-- SQLite için Foreign Key desteğini açar
PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- ==========================================
-- 1. ADIM: BAĞIMSIZ (LOOKUP) TABLOLAR
-- ==========================================

CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS units (
    unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_code TEXT NOT NULL UNIQUE,
    unit_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS currencies (
    currency_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    symbol TEXT,
    name TEXT
);

-- STATUS TABLOLARI (AYRIŞTIRILMIŞ)
CREATE TABLE IF NOT EXISTS request_statuses (
    status_id INTEGER PRIMARY KEY AUTOINCREMENT,
    status_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS order_statuses (
    status_id INTEGER PRIMARY KEY AUTOINCREMENT,
    status_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS supplier_statuses (
    status_id INTEGER PRIMARY KEY AUTOINCREMENT,
    status_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS offer_statuses (
    status_id INTEGER PRIMARY KEY AUTOINCREMENT,
    status_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS invoice_statuses (
    status_id INTEGER PRIMARY KEY AUTOINCREMENT,
    status_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS payment_methods (
    method_id INTEGER PRIMARY KEY AUTOINCREMENT,
    method_name TEXT NOT NULL UNIQUE
);

-- ==========================================
-- 2. ADIM: ANA VARLIK TABLOLARI
-- ==========================================

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT,
    email TEXT UNIQUE,
    password_hash TEXT,
    role_id INTEGER,
    department_id INTEGER,
    is_active INTEGER DEFAULT 1, -- 1: Aktif, 0: Pasif
    FOREIGN KEY (role_id) REFERENCES roles (role_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (department_id) REFERENCES departments (department_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL UNIQUE,
    contact_name TEXT,
    email TEXT,
    iban TEXT UNIQUE,
    black_list INTEGER DEFAULT 0, -- Ekstra güvenlik olarak kalsın, status ile de yönetilebilir
    status_id INTEGER,
    FOREIGN KEY (status_id) REFERENCES supplier_statuses (status_id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    unit_id INTEGER,
    item_name TEXT NOT NULL UNIQUE,
    description TEXT,
    FOREIGN KEY (category_id) REFERENCES categories (category_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (unit_id) REFERENCES units (unit_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ==========================================
-- 3. ADIM: İŞLEM VE HAREKET TABLOLARI
-- ==========================================



CREATE TABLE IF NOT EXISTS purchase_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    status_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requester_user_id) REFERENCES users (user_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (item_id) REFERENCES items (item_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (status_id) REFERENCES request_statuses (status_id) ON UPDATE CASCADE
);

-- ==========================================
-- 4. ADIM: TEKLİF VE SİPARİŞ
-- ==========================================

CREATE TABLE IF NOT EXISTS offers (
    offer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    currency_id INTEGER NOT NULL,
    price REAL NOT NULL,
    status_id INTEGER DEFAULT 1, -- 1: Bekliyor
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES purchase_requests (request_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (currency_id) REFERENCES currencies (currency_id) ON UPDATE CASCADE,
    FOREIGN KEY (status_id) REFERENCES offer_statuses (status_id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    offer_id INTEGER NOT NULL,
    status_id INTEGER,
    delivery_date TEXT,
    exchange_rate REAL DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (offer_id) REFERENCES offers (offer_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (status_id) REFERENCES order_statuses (status_id) ON UPDATE CASCADE
);

-- ==========================================
-- 5. ADIM: FİNANS VE BÜTÇE
-- ==========================================

CREATE TABLE IF NOT EXISTS budgets (
    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER DEFAULT 0, -- 0: Yıllık Genel, 1-12: Ay Bazlı
    amount REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments (department_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no TEXT,
    supplier_id INTEGER NOT NULL,
    invoice_date TEXT,
    due_date TEXT,
    total_amount REAL DEFAULT 0,
    tax_amount REAL DEFAULT 0,
    status_id INTEGER DEFAULT 2, -- 2: Bekliyor
    exchange_rate REAL DEFAULT 1.0,
    order_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (status_id) REFERENCES invoice_statuses (status_id) ON UPDATE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    payment_date TEXT,
    amount REAL NOT NULL,
    payment_method TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id) ON UPDATE CASCADE ON DELETE CASCADE
);


COMMIT;