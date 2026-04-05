import sqlite3
from datetime import datetime
from pathlib import Path

conn = sqlite3.connect(Path(__file__).resolve().parent / 'data' / 'fms-D.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all users
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()

print('=' * 70)
print('FINANCE MANAGEMENT SYSTEM - USER ACCOUNT DATABASE')
print('=' * 70)
print(f'\n📊 TOTAL ACCOUNTS IN SYSTEM: {len(users)}')
print(f'\n📅 TODAY\'S DATE: April 3, 2026')
print('\n' + '-' * 70)
print(f'{"ID":<5} {"USERNAME":<40} {"RISK LEVEL":<15}')
print('-' * 70)

for user in users:
    risk_level = user['risk_level'] if user['risk_level'] else 'Not Set'
    print(f'{user["id"]:<5} {user["username"]:<40} {risk_level:<15}')

print('-' * 70)
print(f'\n✅ Total Accounts: {len(users)}')

conn.close()
