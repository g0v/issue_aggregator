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
    else:
        conn.commit()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    print('tables dropped\n')


def create_repos_table(db, user, json_fpath):
    print('creating repos table')

    with open(json_fpath, 'r') as f:
        repos = json.load(f)

    try:
        conn = psycopg2.connect(database=db, user=user)
        cur = conn.cursor()

        # create table
        sql_create_table = ('CREATE TABLE repos (id integer PRIMARY KEY, name varchar, '
                            'description text, url varchar, html_url varchar, language varchar, '
                            'languages_url varchar, open_issues_count integer, created_at date, '
                            'updated_at date, pushed_at date);')
        cur.execute(sql_create_table)

        # insert rows
        col_names = ['id',
                     'name',
                     'description',
                     'url',
                     'html_url',
                     'language',
                     'languages_url',
                     'open_issues_count',
                     'created_at',
                     'updated_at',
                     'pushed_at']
        for r in repos:
            col_values = [r[k] for k in col_names]
            sql_insert = 'INSERT INTO repos (%s) VALUES (%s);' % (', '.join(col_names), ', '.join(['%s'] * len(col_values)))
            cur.execute(sql_insert, col_values)
    except psycopg2.DatabaseError as e:
        print(e)
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

        # create table
        sql_create_table = ('CREATE TABLE issues (id integer PRIMARY KEY, '
                            'repo_id integer REFERENCES repos(id), title varchar, body text, '
                            'state varchar, url varchar, html_url varchar, labels varchar[], '
                            'labels_url varchar, pull_request jsonb, created_at date, '
                            'updated_at date);')
        cur.execute(sql_create_table)

        # insert rows
        col_names = ['id',
                     'repo_id',
                     'title',
                     'body',
                     'state',
                     'url',
                     'html_url',
                     'labels',
                     'labels_url',
                     'pull_request',
                     'created_at',
                     'updated_at']
        pr_idx = col_names.index('pull_request')
        lbs_idx = col_names.index('labels')
        for i in issues:
            col_values = [(i[k] if k in i else None) for k in col_names]
            col_values[pr_idx] = json.dumps(col_values[pr_idx])
            col_values[lbs_idx] = [l['name'] for l in col_values[lbs_idx]]
            col_values_holder = ['%s'] * len(col_values)
            # col_values[lbs_idx] = [json.dumps(j) for j in col_values[lbs_idx]]
            # col_values_holder[lbs_idx] = '%s::jsonb[]'

            sql_insert = 'INSERT INTO issues (%s) VALUES (%s);' % (', '.join(col_names), ', '.join(col_values_holder))
            cur.execute(sql_insert, col_values)
    except psycopg2.DatabaseError as e:
        print(e)
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

        # create table
        sql_create_table = 'CREATE TABLE labels (id serial PRIMARY KEY, name varchar);'
        cur.execute(sql_create_table)

        # insert rows
        for l in labels:
            sql_insert = 'INSERT INTO labels (name) VALUES (%s)'
            cur.execute(sql_insert, (l,))
    except psycopg2.DatabaseError as e:
        print(e)
    else:
        conn.commit()
    finally:
        cur.close()
        conn.close()

    print('labels table created')


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

    print('===== DB Creation Complete =====\n\n')
