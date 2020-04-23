import os
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

from ..Utils import SystemUtil


class DatabaseHandler:

    base = declarative_base()

    def __init__(self):
        database_path = os.path.join(SystemUtil.get_data_directory(), 'dfr.db')
        self.engine = sqlalchemy.create_engine(f'sqlite:///{database_path}')
        self.base.metadata.create_all(self.engine)

        # session_factory = sessionmaker(bind=self.engine)
        # self.Session = scoped_session(session_factory)

        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """Returns a new instance of a database session."""
        return self.Session()

    @contextmanager
    def get_scoped_session(self):
        session = self.Session()
        try:
            yield session
        except:
            raise
        finally:
            session.close()

    @contextmanager
    def get_scoped_update_session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

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

    def get_object_session(self, obj):
        return self.Session.object_session(obj)

    def commit_object(self, obj):
        self.get_object_session(obj).commit()

    def get_or_create(self, model, session=None, defaults=None, **kwargs):
        """
        Queries the supplied model by the supplied kwargs and returns the model instance if one is found.  If a matching
        model instance is not found, one is created in the database and then returned.  Returns a tuple, the second part
        of which is a bool indicating if the instance was created or not.
        :param model: The model that is to be queried or created.
        :param session: An optional session instance.  If not supplied, a default scoped session is used.
        :param defaults: A dict of default values to be used in a new model instances creation.
        :param kwargs: Model attributes with matching values that are to be queried and if not found, used to create a
                       new model instance.
        :return: A tuple containing the instance that is found or created and a bool indicating if the instance was
                 created or not respectively.
        :rtype: tuple
        """
        if session is None:
            with self.get_scoped_update_session() as session:
                return self.get_or_create(model, session=session, defaults=defaults, **kwargs)
        instance = session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance, False
        else:
            params = {}
            if defaults is not None:
                params.update(defaults)
            params.update(kwargs)
            instance = model(**params)
            session.add(instance)
            session.commit()
            return instance, True
