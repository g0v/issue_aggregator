#!/usr/bin/env python3

import json
from requests import get
from subprocess import Popen, PIPE

repo_master_raw = 'https://raw.githubusercontent.com/g0v/awesome-g0v/master/'
readme = 'readme.md'
parser = 'parse.ls'
awesome_g0v = 'awesome-g0v.json'
outfile = 'url_list.json'


def get_source():
    readme_url = repo_master_raw + readme
    parser_url = repo_master_raw + parser

    with open('./data/{}'.format(readme), 'wb+') as f:
        response = get(readme_url)
        f.write(response.content)

    with open('./data/{}'.format(parser), 'wb+') as f:
        response = get(parser_url)
        f.write(response.content)


def run_parser():
    try:
        with Popen(['lsc', parser], cwd='./data/', stdout=PIPE) as p:
            print(p.stdout.read().decode('utf-8'))
    except Exception as e:
        print(e)
        pass


def output_url_list():
    with open('./data/{}'.format(awesome_g0v), 'r') as f:
        js = json.load(f)
        rs = [j['repository'] for j in js if 'github.com' in j['repository']]

    with open('./data/{}'.format(outfile), 'w+') as f:
        f.write(json.dumps(rs))

if __name__ == "__main__":
    get_source()
    run_parser()
    output_url_list()
