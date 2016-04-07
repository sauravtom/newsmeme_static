#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask, flask.views
from flask import render_template
from flask import request
from flask import flash
from flask import jsonify
import json
import os
import json
import requests
import hashlib
from app import app

from flask.ext.httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

from parse_rest.connection import register
from parse_rest.datatypes import Object, GeoPoint
from parse_rest.user import User

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

users = {
    "john": "hello",
    "foo": "food"
    }

parse_credentials = {
    "application_id": "2wzSL2IYgy38Q378nNoKSJ23qqqSy5Uu1BW7Slax",
    "rest_api_key": "JwPG9NCK67Yu1Ty96CAunYDs43oRcMsSoipu5qBH",
    "master_key": "7bgt7qUcm5ein46DuaF1rYV5CboF6SbR9HfaiwoD",
}

register(parse_credentials["application_id"], parse_credentials["rest_api_key"])

class newsmeme(Object):
    pass

class narrators(Object):
    pass

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


def get_dict(**kwargs):
    d= {}
    for k,v in kwargs.iteritems():
        d[k] = v
    return d

def spreadsheet_query():
    url = "https://spreadsheets.google.com/feeds/list/1rOvWwcvrKj_aNy4PVGNdUZdPC49d4zE6ncu0nGeN1Xw/od6/public/values?alt=json"
    #url = "https://spreadsheets.google.com/feeds/list/11f8Nr-FehZDT7j-tK_tQSf2bNkwZmNpRQa55-6wYeRg/od6/public/values?alt=json"
    json_ob = requests.get(url).json()
    arr = []
    for i in json_ob["feed"]["entry"]:
        d= {}
        title = i["gsx$title"]["$t"]
        image_url = i["gsx$imageurl"]["$t"]
        link = i["gsx$link"]["$t"]
        summary = i["gsx$summary"]["$t"]
        news_id = hashlib.md5(title+link).hexdigest()[:6]
        d = get_dict(news_id=news_id,link=link,image_url=image_url,summary=summary,title=title)
        arr.append(d)
    return arr

def title_formatter(text):
    text = text.replace(" ","-")
    text = ''.join(ch for ch in text if ch.isalnum() or ch == '-')
    return text

@app.route('/')
def home():
    all_videos = newsmeme.Query.all().limit(10).filter(published=True).order_by("-createdAt")
    #all_videos = reversed(all_videos)
    main_object = all_videos[0]
    narrator_object = narrators.Query.get(objectId = main_object.narrator)
    return flask.redirect('/v/%s'%(main_object.objectId))
    

@app.route('/v/<object_id>/')
def home2(object_id):
    main_object = newsmeme.Query.get(objectId=object_id)
    title = title_formatter(main_object.video_title)
    return flask.redirect('/v/%s/%s'%(object_id,title))

@app.route('/v/<object_id>/<title>')
def home3(object_id,title):
    all_videos = newsmeme.Query.all().limit(10).filter(published=True).order_by("-createdAt")
    main_object = newsmeme.Query.get(objectId=object_id)
    narrator_object = narrators.Query.get(objectId = main_object.narrator)
    youtube_id = main_object.youtube_id.strip()
    return flask.render_template('index_3.html',all_videos=all_videos,main_object=main_object,narrator_object=narrator_object,youtube_id=youtube_id)


@app.route('/news/<news_id>')
def newsPage(news_id):
    arr = spreadsheet_query()
    news_data = None
    
    #news_data = [news for news in arr where news['news_id'] == news_id]

    for news in arr:
        if news['news_id'] == news_id:
            news_data = news

    if not news_data:
        return flask.render_template('404.html')
    else:
        return flask.render_template('news.html',news_data=news_data)


@app.route('/admin')
def admin():
    return flask.render_template('redirect.html',url="/foodchamber")

@app.route('/api')
def api():
    freeze()
    return "0"

@app.route('/api/<word>')
def apis(word):
    data = spreadsheet_query()
    searched_data = [news for news in data if word in news['summary']]
    return jsonify(arr=searched_data)

def freeze():
    #all_videos = newsmeme.Query.all().limit(3).filter(published='True').order_by("-createdAt")
    #all_videos = newsmeme.Query.all().filter(published=True).order_by("-createdAt")
    all_videos = newsmeme.Query.all().limit(1000).filter(published=True).order_by("-createdAt")
    
    print all_videos

    for video in all_videos:
        title = title_formatter(video.video_title)
        title = title.encode('utf-8')
        #title = title.encode('ascii','ignore')

        try:
            print video.youtube_id
        except:
            continue

        try:
            narrator_object = narrators.Query.get(objectId = video.narrator)
        except:
            narrator_object = narrators.Query.get(objectId = '1HfjOEgiJj')

        os.system("mkdir v/%s"%(video.objectId))
        os.system("mkdir v/%s/%s"%(video.objectId,title))
        parsed_html = flask.render_template('index_3.html',all_videos=all_videos,main_object=video,narrator_object=narrator_object)
        rdr_html = flask.render_template('redirect.html',url="/v/%s/%s"%(video.objectId,title))

        os.system("touch v/%s/index.html"%(video.objectId))
        os.system("touch v/%s/%s/index.html"%(video.objectId,title))

        with open("v/%s/index.html"%(video.objectId), "wb") as fh:
            fh.write(rdr_html.encode('utf-8'))

        with open("v/%s/%s/index.html"%(video.objectId,title), "wb") as fh:
            fh.write(parsed_html.encode('utf-8'))


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')



