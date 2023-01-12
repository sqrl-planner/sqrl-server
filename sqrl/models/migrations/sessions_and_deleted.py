def migrate():
    from sqrl.models.timetable import Timetable
    from sqrl.app import create_app
    import time

    app = create_app()
    with app.app_context():
        assert Timetable.objects(deleted__exists=True).count() == 0
        assert Timetable.objects(session__exists=True).count() == 0

        print('Migrating timetables...')
        start_time = time.time()
        Timetable.objects().update(deleted=False, session="202209", schema_version=2)
        end_time = time.time()
        timetables = list(Timetable.objects.all())
        print(
            f'Migrated {len(timetables)} timetables in {end_time - start_time} seconds.')
        return timetables 
    
if __name__ == "__main__":
    migrate()
