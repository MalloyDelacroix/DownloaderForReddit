import os
import logging
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import desc
from sqlalchemy.exc import OperationalError, IntegrityError

from .models import Version
from ..utils import injector, system_util
from .. import version


class Migrator:
    """
    A class responsible for checking the current database version against the application version, and migrating any
    database changes if necessary.
    """

    def __init__(self):
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.db = injector.get_database_handler()
        self.session = self.db.get_session()
        self.migration_dir = os.path.join(system_util.get_data_directory(), 'migrations')

    def check_migration(self):
        try:
            cache_version = self.session.query(Version).order_by(desc(Version.id)).limit(1).first()
            self.write_current_version(cache_version)
            if cache_version is not None:
                if version.is_updated(version.__version__, cache_version.version):
                    self.migrate()
                    self.session.add(Version(version=version.__version__))
                    self.session.commit()
                    self.logger.info(
                        'New version detected.  Migration has been performed',
                        extra={
                            'cached_version': cache_version.version,
                            'cache_date': cache_version.date_added,
                            'new_version': version.__version__
                        }
                    )
            else:
                self.session.add(Version(version=version.__version__))
                self.session.commit()
                self.logger.info(f'Migration not performed: no version information found in database.  Database entry'
                                 f'for version {version.__version__} has been created.')
        finally:
            self.session.close()

    def get_config(self):
        config = Config()
        alembic_path = os.path.abspath('alembic')
        config.set_main_option('script_location', alembic_path)
        config.set_main_option('sqlalchemy.url', self.db.database_url)
        return config

    def migrate(self):
        config = self.get_config()
        with self.db.engine.begin() as connection:
            config.attributes['connection'] = connection
            command.upgrade(config, 'head')

    def write_current_version(self, cache_version):
        """
        Writes the current alembic revision to the database if there is not already a version stored there.  This is
        done because if a user first uses the application after v3.3.0, their database is created with database columns
        as a default.  But after this version database tables have been altered to add these columns in existing
        databases.  If this version is not stored when created, the application will not be able to migrate future
        versions of the database in the event that it is updated again.
        """
        if cache_version is None or version.is_updated(cache_version.version, 'v3.2.1'):
            if not self.check_version_three_three_zero():
                cached_revision = self.get_cached_revision()
                if cached_revision is None:
                    current_version = self.get_current_version()
                    self.write_version_to_db(current_version)

    def get_cached_revision(self):
        """
        Retrieves the "version_num" from the database as is stored by alembic when a migration is performed.
        """
        try:
            with self.db.engine.connect() as con:
                result_set = con.execute('SELECT version_num FROM alembic_version')
                for row in result_set:
                    stored_version = row[0]
                    if stored_version != '':
                        return stored_version
        except OperationalError:
            self.create_alembic_table()
            return None

    def create_alembic_table(self):
        statement = """CREATE TABLE alembic_version (
                        version_num VARCHAR(32) NOT NULL, 
                        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                    )"""
        with self.db.engine.connect() as con:
            con.execute(statement)

    def get_current_version(self):
        """
        Returns the most recent revision script id as located by alembic.
        :return: The most recent revision id.
        """
        sd = ScriptDirectory.from_config(self.get_config())
        return sd.get_current_head()

    def write_version_to_db(self, version_num):
        """
        Writes the supplied version_num to the database in the alembic version table.

        Yes, I know; I know.  This is not a safe way to craft an sql statement.  But this is a desktop app, and if an
        end user wants to go through the trouble to figure out how to inject this and sabotage their own database, then
        far be it from me to stand in their way.
        """
        try:
            with self.db.engine.connect() as con:
                statement = f'INSERT INTO alembic_version(version_num) VALUES("{version_num}")'
                con.execute(statement)
        except IntegrityError:
            pass

    def check_version_three_three_zero(self):
        """
        A method that only fixes a problem that only occurs if the user is using version 3.3.0-beta.  A bug was
        introduced by that version of this class not handling migrations right if it was the first version that the user
        had used.
        :return: True if the version was v3.3.0-beta and the issue was handled, False if this was a different version.
        """
        cache_version = self.session.query(Version).order_by(desc(Version.id)).limit(1).first()
        self.get_cached_revision()
        if cache_version is not None and cache_version.version == 'v3.3.0-beta':
            self.write_version_to_db('70d9de393850')
            return True
        return False
