import logging
import csv
import sqlite3

from DownloaderForReddit.database.models import RedditObjectList, RedditObject, User, Subreddit, Post, Content, Comment
from DownloaderForReddit.utils import injector


model_map = {model.__name__: model for model in [RedditObjectList, RedditObject, User, Subreddit, Post, Content,
                                                 Comment]}


logger = logging.getLogger(f'DownloaderForReddit.{__name__}')


def import_csv(file_path):
    database_path = injector.get_database_handler().database_path
    object_type, columns, data = read_file(file_path)
    sub_type = None
    if object_type == 'User' or object_type == 'Subreddit':
        model = RedditObject
        sub_type = object_type
    else:
        model = model_map[object_type]
    table = model.__tablename__
    con = sqlite3.connect(database_path)
    cursor = con.cursor()
    cursor.execute('BEGIN TRANSACTION;')
    sql = f'INSERT INTO {table} ({",".join(columns)}) VALUES({",".join(["?"] * len(columns))});'
    for row in data:
        for x in row:
            if x == '':
                row[row.index(x)] = None
        cursor.execute(sql, row)
    cursor.execute('COMMIT;')

    index = columns.index('id')
    if sub_type == 'User':
        handle_user_import([row[index] for row in data], cursor)
    elif sub_type == 'Subreddit':
        handle_subreddit_import([row[index] for row in data], cursor)
    logger.info('Imported data from csv file', extra={'file_path': file_path, 'import_model_type': object_type,
                                                      'import_count': len(data)})


def handle_user_import(user_id_list, cursor):
    cursor.execute('BEGIN TRANSACTION;')
    sql = f'INSERT INTO {User.__tablename__} (id) VALUES (?);'
    print(sql)
    for user_id in user_id_list:
        cursor.execute(sql, [user_id])
    cursor.execute('COMMIT;')


def handle_subreddit_import(sub_id_list, cursor):
    cursor.execute('BEGIN TRANSACTION;')
    sql = f'INSERT INTO {User.__tablename__} (id) VALUES (?));'
    for sub_id in sub_id_list:
        cursor.execute(sql, [sub_id])
    cursor.execute('COMMIT;')


def read_file(file_path):
    object_type = None
    data = []
    columns = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        count = 0
        for row in reader:
            if count == 0:
                object_type = row[0]
                count += 1
            elif count == 1:
                columns = row
                count += 1
            else:
                data.append(row)
    return object_type, columns, data
