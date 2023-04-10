from sessions_and_deleted import migrate as migrate_sessions_and_deleted

migrations = [migrate_sessions_and_deleted]

for i, migration in enumerate(migrations):
    try:
        migration()
    except:
        print(f"Migration {i} failed or already done.")