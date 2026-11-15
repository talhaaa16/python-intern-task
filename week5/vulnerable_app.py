"""
vulnerable_app.py
Vulnerable Customer Account & Portal Authentication System.
Demonstrates 8 high-severity real-world security vulnerabilities:
1. SQL Injection (SQLi) via raw string concatenation in SQL queries.
2. Plaintext Password Storage (lack of cryptographic hashing/salting).
3. Plaintext Sensitive Data Storage (Credit cards and SSNs unencrypted).
4. Path Traversal (Arbitrary file download/read via unvalidated filename input).
5. Command Injection via unsanitized system commands (`os.system` / shell calls).
6. Hardcoded Secrets & Cryptographic API Keys in source code.
7. Information Leakage & Detailed Internal Tracebacks exposed to users.
8. Insecure / Missing Input Sanitization & Authentication Bypass.
"""

import os
import sqlite3
import sys
from typing import Optional, Dict, Any

# VULNERABILITY 6: Hardcoded Secret Keys & API Tokens
JWT_SECRET_KEY = "SUPER_SECRET_INSECURE_HARDCODED_KEY_12345"
PAYMENT_API_KEY = "sk_live_99887766554433221100_insecure_token"


class VulnerableApp:
    def __init__(self, db_path: str = "vulnerable_portal.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS users")
        # VULNERABILITY 2 & 3: Storing password, credit card, and SSN in plaintext!
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                email TEXT,
                role TEXT,
                credit_card TEXT,
                ssn TEXT
            )
        """)
        # Seed vulnerable database with default test users
        cursor.execute("""
            INSERT INTO users (username, password, email, role, credit_card, ssn)
            VALUES ('admin', 'admin123', 'admin@corp.internal', 'admin', '4111-2222-3333-4444', '000-12-3456')
        """)
        cursor.execute("""
            INSERT INTO users (username, password, email, role, credit_card, ssn)
            VALUES ('alice', 'P@ssword1', 'alice@example.com', 'user', '5500-1111-2222-3333', '111-23-4567')
        """)
        conn.commit()
        conn.close()

    # VULNERABILITY 1: SQL Injection via direct string formatting in authentication query
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Direct string concatenation allows ' OR '1'='1 bypass!
        query = f"SELECT id, username, email, role, credit_card, ssn FROM users WHERE username = '{username}' AND password = '{password}'"
        try:
            cursor.execute(query)
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "role": row[3],
                    "credit_card": row[4],
                    "ssn": row[5]
                }
            return None
        except Exception as e:
            # VULNERABILITY 7: Verbose error messages exposing database internals
            raise RuntimeError(f"Database execution error on query [{query}]: {str(e)}")
        finally:
            conn.close()

    # VULNERABILITY 4: Path Traversal (Arbitrary File Read)
    def read_user_document(self, base_folder: str, filename: str) -> str:
        # Directly concatenating paths without validation allows "../" traversal
        filepath = os.path.join(base_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    # VULNERABILITY 5: Command Injection via os.system / shell execution
    def ping_host(self, host: str) -> str:
        # User input directly interpolated into shell command
        cmd = f"ping -n 1 {host}"
        # os.popen executes shell with full command chaining capability (e.g., "127.0.0.1 & dir")
        stream = os.popen(cmd)
        output = stream.read()
        return output

    # VULNERABILITY 8: Register User without input validation or password strength checks
    def register_user(self, username: str, password: str, email: str, credit_card: str, ssn: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Allows empty passwords, sql injection, and stores plain text
        query = f"INSERT INTO users (username, password, email, role, credit_card, ssn) VALUES ('{username}', '{password}', '{email}', 'user', '{credit_card}', '{ssn}')"
        try:
            cursor.execute(query)
            conn.commit()
            return True
        except Exception as e:
            print(f"[DEBUG EXCEPTION] Raw Error: {e}")
            return False
        finally:
            conn.close()

