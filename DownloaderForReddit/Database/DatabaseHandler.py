import os
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from ..Utils import SystemUtil


class DatabaseHandler:

    base = declarative_base()

    def __init__(self):
        database_path = os.path.join(SystemUtil.get_data_directory(), 'dfr.db')
        self.engine = sqlalchemy.create_engine(f'sqlite:///{database_path}')
        self.base.metadata.create_all(self.engine)

        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """Returns a new instance of a database session."""
        return self.Session()

    def commit_and_close(self, session):
        """Commit all uncommitted changes to the database."""
        session.commit()
        session.close()

    def add(self, *args):
        """
        Adds the items supplied in args to the database and commits the transaction.
        :param args: Database items that are to be added to the database.
        """
        session = self.get_session()
        if len(args) > 0:
            session.add_all(args)
        else:
            session.add(args[0])
        session.commit()
        session.close()
