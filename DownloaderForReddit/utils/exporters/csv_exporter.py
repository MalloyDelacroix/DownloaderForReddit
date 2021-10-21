import logging
import csv
import sqlite3

from DownloaderForReddit.database.models import RedditObject, RedditObjectList
from DownloaderForReddit.utils import injector


logger = logging.getLogger(f'DownloaderForReddit.{__name__}')


def export_csv(object_list, model, file_path):
    database_path = injector.get_database_handler().database_path
    table = model.__tablename__
    if model != RedditObject:
        model_type = model.__name__
    else:
        model_type = object_list[0].object_type.title()
    id_list = get_id_list(object_list)
    con = sqlite3.connect(database_path)
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        file.write(model_type + '\n')
        writer = csv.writer(file)
        cursor = con.cursor()
        cursor.execute(f'SELECT * FROM {table} WHERE {table}.id in ({",".join(["?"] * len(id_list))})', id_list)

        writer.writerow(x[0] for x in cursor.description)
        writer.writerows(cursor.fetchall())
    logger.info('Exported items to csv file',
                extra={'export_model_type': model.__name__, 'items_exported': len(id_list)})


def get_id_list(object_list):
    if isinstance(object_list, RedditObjectList):
        return [x.id for x in object_list.reddit_objects]
    else:
        return [x.id for x in object_list]
