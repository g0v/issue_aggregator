# issue_aggregator
http://g0vissues.jmehsieh.com </br>
搜尋 g0v repo issues by language & labels

### 共筆
* [g0v 基礎建設 hackfoldr](http://beta.hackfoldr.org/g0v-infras)
* [g0v 基礎建設 issue aggregator](https://g0v.hackpad.com/projecthub-redux-9U6DLtdZc48#:h=issues-aggregator)

### Hosting

* 前端放在 gh-pages branch
* 主機放在 aws (1 yr free tier)
* dns: http://g0vissues.jmehsieh.com

### 如何運作
* 想辦法取得 g0v repo list: url_list.json
* 根據 url_list.json 下載所有 repos.json, issues.json, labels.json
* 將 json files 轉成 postgresql (jsonb format)
* 啟動 nginx + gunicorn + flask app

### 參與開發
##### 開發前
*  安裝 PostreSQL, Python3, Virtualenv
*  `$ createdb your_issue_aggregator_db`

##### 建置 DB
```
$ git clone https://github.com/JmeHsieh/issue_aggregator.git
$ cd issue_aggregator
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ cp config_template.json config.json
$ vim config.json
{
	user: 連線 db 的 user,
	db: postgresql database name,
	token: github personal auth token
}
$ cp your_url_list_json_file data/
$ python download_jsons.py
$ python j2jb.py
```

##### run flask app
```
$ export FLASK_APP=app.py
$ export FLASK_DEBUG=1
$ flask run
```

##### api usage
* localhost:5000/api/labels
* localhost:5000/api/repos
* localhost:5000/api/repos?ids=xxx,ooo
* localhost:5000/api/issues
* localhost:5000/api/issues?language=html
* localhost:5000/api/issues?language=html&labels=bug,enhancement