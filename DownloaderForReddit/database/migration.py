import os
import logging
from alembic.config import Config
from alembic import command
from sqlalchemy import desc

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
        self.migration_dir = os.path.join(system_util.get_data_directory(), 'migrations')

    def check_migration(self):
        with self.db.get_scoped_session() as session:
            cache_version = session.query(Version).order_by(desc(Version.id)).limit(1).first()
            if cache_version is not None:
                if version.is_updated(version.__version__, cache_version.version):
                    self.migrate()
                    session.add(Version(version=version.__version__))
                    session.commit()
                    self.logger.info(
                        'New version detected.  Migration has been performed',
                         extra={
                             'cached_version': cache_version.version,
                             'cache_date': cache_version.date_added,
                             'new_version': version.__version__
                         }
                    )
            else:
                self.logger.info('No cache version found in database.  Migration not performed')

    def migrate(self):
        config = Config()
        alembic_path = os.path.abspath('alembic')
        config.set_main_option('script_location', alembic_path)
        config.set_main_option('sqlalchemy.url', self.db.database_url)
        with self.db.engine.begin() as connection:
            config.attributes['connection'] = connection
            command.upgrade(config, 'head')
