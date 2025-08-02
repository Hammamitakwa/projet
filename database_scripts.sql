-- Script de création de la base de données pour l'application bancaire en ligne
-- Base de données: amen_bank_online

CREATE DATABASE IF NOT EXISTS amen_bank_online;
USE amen_bank_online;

-- Table des utilisateurs
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    date_registered DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table des comptes
CREATE TABLE accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_label VARCHAR(100) NOT NULL,
    currency VARCHAR(5) NOT NULL DEFAULT 'TND',
    current_balance DECIMAL(15, 3) NOT NULL DEFAULT 0.000,
    date_opened DATE NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Table des transactions
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount DECIMAL(15, 3) NOT NULL,
    debit_credit_indicator ENUM('D', 'C') NOT NULL,
    piece_number VARCHAR(50),
    value_date DATE,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

-- Table des bénéficiaires
CREATE TABLE beneficiaries (
    beneficiary_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    bank_name VARCHAR(100),
    account_number VARCHAR(20) NOT NULL,
    rib VARCHAR(30),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Table des virements
CREATE TABLE transfers (
    transfer_id INT AUTO_INCREMENT PRIMARY KEY,
    from_account_id INT NOT NULL,
    to_account_number VARCHAR(20) NOT NULL,
    beneficiary_name VARCHAR(100) NOT NULL,
    amount DECIMAL(15, 3) NOT NULL,
    transfer_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    is_scheduled BOOLEAN DEFAULT FALSE,
    schedule_frequency VARCHAR(50),
    next_execution_date DATE,
    FOREIGN KEY (from_account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

-- Table des demandes de crédit
CREATE TABLE loan_applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    requested_amount DECIMAL(15, 3) NOT NULL,
    loan_term_years INT NOT NULL,
    application_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    monthly_payment_simulation DECIMAL(15, 3),
    justification_docs_path VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_beneficiaries_user_id ON beneficiaries(user_id);
CREATE INDEX idx_transfers_from_account ON transfers(from_account_id);
CREATE INDEX idx_transfers_date ON transfers(transfer_date);
CREATE INDEX idx_loan_applications_user_id ON loan_applications(user_id);

-- Données de test (optionnel)
INSERT INTO users (username, password, email, phone_number, full_name, address) VALUES
('demo_user', 'password123', 'demo@amenbank.com.tn', '+21612345678', 'Utilisateur Demo', '123 Rue de la République, Tunis');

INSERT INTO accounts (user_id, account_number, account_label, current_balance, date_opened, account_type) VALUES
(1, '000110123456', 'Compte DEMO 1', 32501.730, '2015-01-01', 'courant'),
(1, '081150543314', 'Compte DEMO 2', -32124.250, '2015-01-01', 'courant');

INSERT INTO transactions (account_id, description, transaction_type, amount, debit_credit_indicator, piece_number, value_date) VALUES
(1, 'VIREMENT', 'VIREMENT', 7000.000, 'C', NULL, '2015-08-13'),
(1, 'VERSEMENT', 'VERSEMENT', 1000.000, 'C', NULL, '2015-08-13'),
(1, 'ENC 0005 CHQ 13.01', 'ENCAISSEMENT', 739.067, 'C', NULL, '2015-08-12'),
(1, 'CHQ 7457881 FAV RECEVEUR FINANCE ARI', 'CHEQUE', 3450.000, 'D', '7457881', '2015-08-11');

INSERT INTO beneficiaries (user_id, full_name, bank_name, account_number, rib) VALUES
(1, 'Ahmed Ben Salah', 'Amen Bank', '123456789012', 'TN59 08 011 123456789012 34');

