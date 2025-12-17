
import bcrypt

hashes = {
    'admin': b'$2b$12$6sFl90cYxRMwoIBKsSXDw.8.R41uV9n.yjZLAMxL/Br/hpwONOaWW',
    'analyst': b'$2b$12$sIxiLvgvnsaiHcU8YBtMcOfuEOJXwV5SVqkmWyDu2gC6c6BZaoPlm'
}

candidates = ['admin', '123', 'password', 'analyst', 'ecommerce']

print("Checking passwords...")
for user, hash_val in hashes.items():
    for cand in candidates:
        if bcrypt.checkpw(cand.encode('utf-8'), hash_val):
            print(f"MATCH FOUND: User '{user}' has password '{cand}'")
