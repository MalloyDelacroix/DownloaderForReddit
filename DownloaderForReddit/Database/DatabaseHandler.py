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

        Session = sessionmaker(bind=self.engine)
        self.session = Session()
