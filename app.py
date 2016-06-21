from flask import Flask, request, jsonify
import json
import psycopg2

app = Flask(__name__)

db, user = None, None
with open('./config.json', 'r') as f:
    config = json.load(f)
    db = config['db']
    user = config['user']

@app.route('/api/repos', methods=['GET'])
def repos():
    with psycopg2.connect(database=db, user=user) as conn:
        with conn.cursor() as cur:
            sql = "SELECT data FROM repos"

            ids = request.args.get('ids')
            ids = ids.split(',') if ids else None
            if ids:
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
            language = request.args.get('language')
            labels_arg = request.args.get('labels')
            labels = [l.strip() for l in labels_arg.split(',')] if labels_arg else None

            sql = "SELECT a.data from "
            if labels:
                sql += "(SELECT * FROM issues, jsonb_array_elements(data->'labels') l WHERE l->>'name' = Any ('{%s}')) AS a" % ','.join(labels)
            else:
                sql += "(SELECT * FROM issues) AS a"
            if language:
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


if __name__ == '__main__':
    app.run(host='0.0.0.0')
