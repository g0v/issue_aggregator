#!/usr/bin/env python3

import datetime
import json
import psycopg2
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from urllib.parse import quote, unquote, urlencode

app = Flask(__name__)
CORS(app)

with open('./config.json', 'r') as f:
    config = json.load(f)
    db = config['db']
    user = config['user']


@app.route('/api/repos', methods=['GET'])
def repos():
    with psycopg2.connect(database=db, user=user) as conn:
        with conn.cursor() as cur:
            sql = "SELECT data FROM repos"
            ids = []
            if 'ids' in request.args:
                ids = [i.strip() for i in request.args.get('ids').split(',')]
                sql += " WHERE id IN (%s)" % ','.join(['%s']*len(ids))
                sql += " ORDER BY data->>'updated_at' DESC;"
            cur.execute(sql, ids)
            rs = cur.fetchall()
            j = {'result': [r[0] for r in rs]}
            return jsonify(**j)
    abort(500)


@app.route('/api/issues', methods=['GET'])
def issues():
    with psycopg2.connect(database=db, user=user) as conn:
        with conn.cursor() as cur:
            sql = "SELECT a.data from "
            if 'labels' in request.args:
                labels = [l.strip() for l in request.args.get('labels').split(',')]
                sql += "(SELECT * FROM issues, jsonb_array_elements(data->'labels') l WHERE l->>'name' = Any ('{%s}')) AS a" % ','.join(labels)
            else:
                sql += "(SELECT * FROM issues) AS a"
            if 'language' in request.args:
                language = request.args.get('language').lower()
                sql += " INNER JOIN (SELECT r.id FROM repos r WHERE lower(r.data->>'language') = '%s') AS b ON a.repo_id = b.id" % language
            sql += " ORDER BY a.data->>'updated_at' DESC;"
            cur.execute(sql)
            rs = cur.fetchall()
            j = {'result': [r[0] for r in rs]}
            return jsonify(**j)
    abort(500)


@app.route('/api/labels', methods=['GET'])
def labels():
    with psycopg2.connect(database=db, user=user) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT name FROM labels ORDER BY name DESC;')
            rs = cur.fetchall()
            j = {'result': [r[0] for r in rs]}
            return jsonify(**j)
    abort(500)


@app.route('/api/gas', methods=['GET'])
def gas():
    gdn = 'https://www.github.com'

    if 'prev_page' in request.args:
        query = unquote(request.args.get('prev_page'))
    elif 'next_page' in request.args:
        query = unquote(request.args.get('next_page'))
    else:
        q = 'state:open updated:<%s' % datetime.datetime.utcnow().isoformat()

        with open('./data/url_list.json', 'r') as f:
            urls = json.load(f)
            q += ''.join([u.replace('https://github.com/', ' repo:') for u in urls])

        if 'language' in request.args:
            q += ' language:%s' % request.args.get('language')

        if 'labels' in request.args:
            labels = [l.strip() for l in request.args.get('labels').split(',')]
            q += ''.join([' label:%s' % l for l in labels])

        params = {'q': q, 'l': '', 'o': 'desc', 'ref': 'advsearch', 's': 'updated', 'type': 'Issues', 'utf8': '✓'}
        query = '/search?%s' % urlencode(params)

    j = {}
    issues = []
    r = requests.get(gdn + query)

    # html parsing
    soup = BeautifulSoup(r.text, 'html.parser')
    items = soup.find_all('div', class_='issue-list-item public')
    for item in items:
        issue = {}
        issue['sn'] = item.span.contents[0].replace('#', '')

        all_p = item.find_all('p')
        issue['html_url'] = gdn + all_p[0].a['href']
        issue['title'] = all_p[0].a['title']
        issue['body'] = all_p[1].contents[0] if all_p[1].contents else ''

        all_li = item.ul.find_all('li')
        issue['issues_html_url'] = gdn + all_li[0].a['href']
        issue['user_html_url'] = gdn + all_li[1].a['href']
        issue['updated_at'] = all_li[1].find('relative-time')['datetime']
        issue['comments'] = int(all_li[2].strong.contents[0]) if len(all_li) >= 3 else 0

        issues.append(issue)

    prev_page = soup.find('a', class_='prev_page')
    if prev_page:
        j['prev_page'] = quote(unquote(prev_page['href']))

    next_page = soup.find('a', class_='next_page')
    if next_page:
        j['next_page'] = quote(unquote(next_page['href']))

    j['result'] = issues

    return jsonify(**j)


if __name__ == '__main__':
    app.run(host='0.0.0.0')

