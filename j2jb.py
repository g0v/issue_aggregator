#!/usr/bin/env python3

import json
import psycopg2


def drop_tables(db, user):
    print('droping tables')

    sql_drop_repos_table = 'DROP TABLE IF EXISTS repos'
    sql_drop_issues_table = 'DROP TABLE IF EXISTS issues'
    sql_drop_labels_table = 'DROP TABLE IF EXISTS labels'

    try:
        conn = psycopg2.connect(database=db, user=user)
        cur = conn.cursor()
        cur.execute(sql_drop_issues_table)
        cur.execute(sql_drop_repos_table)
        cur.execute(sql_drop_labels_table)
    except psycopg2.DatabaseError as e:
        print(e)
        pass
    else:
        conn.commit()
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

    print('tables dropped\n')


def create_repos_table(db, user, json_fpath):
    print('creating repos table')

    with open(json_fpath, 'r') as f:
        repos = json.load(f)

    try:
        conn = psycopg2.connect(database=db, user=user)
        cur = conn.cursor()
        sql_create_table = ('CREATE TABLE repos (id integer PRIMARY KEY, data jsonb);')
        cur.execute(sql_create_table)
        for r in repos:
            sql_insert = 'INSERT INTO repos (id, data) VALUES (%s, %s::jsonb) ON CONFLICT DO NOTHING;'
            cur.execute(sql_insert, (r['id'], json.dumps(r),))
    except psycopg2.DatabaseError as e:
        print(e)
        pass
    else:
        conn.commit()
    finally:
        cur.close()
        conn.close()

    print('repos table created\n')


def create_issues_table(db, user, json_fpath):
    print('creating issues table')

    with open(json_fpath, 'r') as f:
        issues = json.load(f)

    try:
        conn = psycopg2.connect(database=db, user=user)
        cur = conn.cursor()
        sql_create_table = 'CREATE TABLE issues (id integer PRIMARY KEY, repo_id integer REFERENCES repos(id), data jsonb);'
        cur.execute(sql_create_table)
        for i in issues:
            sql_insert = 'INSERT INTO issues (id, repo_id, data) VALUES (%s, %s, %s::jsonb) ON CONFLICT DO NOTHING;'
            cur.execute(sql_insert, (i['id'], i['repo_id'], json.dumps(i),))
    except psycopg2.DatabaseError as e:
        print(e)
        pass
    else:
        conn.commit()
    finally:
        cur.close()
        conn.close()

    print('issues table created\n')


def create_labels_table(db, user, json_fpath):
    print('creating labels table')

    with open(json_fpath, 'r') as f:
        labels = json.load(f)

    try:
        conn = psycopg2.connect(database=db, user=user)
        cur = conn.cursor()
        sql_create_table = 'CREATE TABLE labels (id serial PRIMARY KEY, name varchar);'
        cur.execute(sql_create_table)
        for l in labels:
            sql_insert = 'INSERT INTO labels (name) VALUES (%s) ON CONFLICT DO NOTHING;'
            cur.execute(sql_insert, (l,))
    except psycopg2.DatabaseError as e:
        print(e)
        pass
    else:
        conn.commit()
    finally:
        cur.close()
        conn.close()

    print('labels table created\n')


if __name__ == '__main__':
    print('===== DB Creation Start =====')

    # conn = psycopg2.connect('dbname=db user=user host=localhost password=xxx')
    with open('./config.json', 'r') as f:
        config = json.load(f)
        db = config['db']
        user = config['user']

    drop_tables(db, user)
    create_repos_table(db, user, './data/repos.json')
    create_issues_table(db, user, './data/issues.json')
    create_labels_table(db, user, './data/labels.json')

    print('===== DB Creation Complete =====')
