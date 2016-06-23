#! /usr/bin/env python3

import getpass
import json
import os
from github import Github

# generate repo list to play with
def run(u, p):
    g = Github(u, p)
    g0v = None

    # get orgs and extract g0v
    for o in g.get_user().get_orgs():
        if o.name == 'g0v':
            g0v = o
            break

    if not g0v:
        raise Exception('g0v is None')

    # get repos
    urls = []
    count = 10
    for r in g0v.get_repos():
        if count <= 0:
            break
        count -= 1
        urls.append(r.html_url)

    os.makedirs('./data/', mode=0o755, exist_ok=True)
    out_fpath = './data/url_list.json'
    try:
        os.remove(out_fpath)
    except OSError:
        pass
    with open(out_fpath, 'a+') as f:
        f.write(json.dumps(urls))


if __name__ == '__main__':
    username = input('Enter Github username:')
    password = getpass.getpass('Enter password:')

    print('start')
    run(username, password)
    print('finished')
