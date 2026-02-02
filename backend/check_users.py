import asyncio
import asyncpg

async def check_users():
    conn = await asyncpg.connect('postgresql://fincoach:fincoach_dev_password@localhost:5432/fincoach')
    rows = await conn.fetch('SELECT id, first_name, last_name, email, created_at, is_active FROM users ORDER BY created_at DESC LIMIT 5')
    
    print('\nRecent User Accounts:')
    print('-' * 80)
    for row in rows:
        print(f'ID: {row["id"]}')
        print(f'Name: {row["first_name"]} {row["last_name"]}')
        print(f'Email: {row["email"]}')
        print(f'Created: {row["created_at"]}')
        print(f'Active: {row["is_active"]}')
        print('-' * 80)
    
    await conn.close()

asyncio.run(check_users())
