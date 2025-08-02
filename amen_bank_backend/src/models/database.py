import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime, date
from decimal import Decimal

def get_db_connection():
    """Fonction utilitaire pour obtenir une connexion à la base de données"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='amen_bank_online',
            user='root',
            password='21329467takwa',  # Mot de passe vide pour le développement local
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except Error as e:
        print(f"Erreur lors de la connexion à MySQL: {e}")
        return None

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        try:
            # Configuration de la base de données MySQL
            # En production, ces valeurs devraient être dans des variables d'environnement
            self.connection = mysql.connector.connect(
                host='localhost',
                database='amen_bank_online',
                user='root',
                password='21329467takwa',  # Mot de passe vide pour le développement local
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print("Connexion à MySQL réussie")
                return True
        except Error as e:
            print(f"Erreur lors de la connexion à MySQL: {e}")
            return False
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("Connexion MySQL fermée")
    
    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return self.cursor.rowcount
        except Error as e:
            print(f"Erreur lors de l'exécution de la requête: {e}")
            self.connection.rollback()
            return None

class User:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def authenticate(self, username, password):
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        result = self.db.execute_query(query, (username, password))
        return result[0] if result else None
    
    def get_by_id(self, user_id):
        query = "SELECT * FROM users WHERE user_id = %s"
        result = self.db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def create(self, username, password, email, phone_number, full_name, address=None):
        query = """
        INSERT INTO users (username, password, email, phone_number, full_name, address)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, (username, password, email, phone_number, full_name, address))

class Account:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_by_user_id(self, user_id):
        query = "SELECT * FROM accounts WHERE user_id = %s"
        return self.db.execute_query(query, (user_id,))
    
    def get_by_account_number(self, account_number):
        query = "SELECT * FROM accounts WHERE account_number = %s"
        result = self.db.execute_query(query, (account_number,))
        return result[0] if result else None
    
    def update_balance(self, account_id, new_balance):
        query = "UPDATE accounts SET current_balance = %s WHERE account_id = %s"
        return self.db.execute_query(query, (new_balance, account_id))

class Transaction:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_by_account_id(self, account_id, limit=50):
        query = """
        SELECT * FROM transactions 
        WHERE account_id = %s 
        ORDER BY transaction_date DESC 
        LIMIT %s
        """
        return self.db.execute_query(query, (account_id, limit))
    
    def create(self, account_id, description, transaction_type, amount, debit_credit_indicator, piece_number=None, value_date=None):
        query = """
        INSERT INTO transactions (account_id, description, transaction_type, amount, debit_credit_indicator, piece_number, value_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, (account_id, description, transaction_type, amount, debit_credit_indicator, piece_number, value_date))

class Beneficiary:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_by_user_id(self, user_id):
        query = "SELECT * FROM beneficiaries WHERE user_id = %s"
        return self.db.execute_query(query, (user_id,))
    
    def create(self, user_id, full_name, bank_name, account_number, rib=None):
        query = """
        INSERT INTO beneficiaries (user_id, full_name, bank_name, account_number, rib)
        VALUES (%s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, (user_id, full_name, bank_name, account_number, rib))

class Transfer:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create(self, from_account_id, to_account_number, beneficiary_name, amount, is_scheduled=False, schedule_frequency=None, next_execution_date=None):
        query = """
        INSERT INTO transfers (from_account_id, to_account_number, beneficiary_name, amount, is_scheduled, schedule_frequency, next_execution_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, (from_account_id, to_account_number, beneficiary_name, amount, is_scheduled, schedule_frequency, next_execution_date))
    
    def get_by_user_id(self, user_id):
        query = """
        SELECT t.*, a.account_number as from_account_number
        FROM transfers t
        JOIN accounts a ON t.from_account_id = a.account_id
        WHERE a.user_id = %s
        ORDER BY t.transfer_date DESC
        """
        return self.db.execute_query(query, (user_id,))
    
    def update_status(self, transfer_id, status):
        query = "UPDATE transfers SET status = %s WHERE transfer_id = %s"
        return self.db.execute_query(query, (status, transfer_id))

class LoanApplication:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create(self, user_id, requested_amount, loan_term_years, monthly_payment_simulation=None):
        query = """
        INSERT INTO loan_applications (user_id, requested_amount, loan_term_years, monthly_payment_simulation)
        VALUES (%s, %s, %s, %s)
        """
        return self.db.execute_query(query, (user_id, requested_amount, loan_term_years, monthly_payment_simulation))
    
    def get_by_user_id(self, user_id):
        query = "SELECT * FROM loan_applications WHERE user_id = %s ORDER BY application_date DESC"
        return self.db.execute_query(query, (user_id,))
    
    def calculate_monthly_payment(self, amount, years, annual_rate=0.07):
        """Calcul de la mensualité d'un crédit"""
        monthly_rate = annual_rate / 12
        num_payments = years * 12
        
        if monthly_rate == 0:
            return amount / num_payments
        
        monthly_payment = amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        return round(monthly_payment, 3)

