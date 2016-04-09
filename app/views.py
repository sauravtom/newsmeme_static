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

@app.template_filter()
def foo(text):
    return text.strip()


def get_dict(**kwargs):
    d= {}
    for k,v in kwargs.iteritems():
        d[k] = v
    return d


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
    return flask.render_template('index.html',all_videos=all_videos,main_object=main_object,narrator_object=narrator_object,title=title)


@app.route('/api')
def api():
    #freeze()
    push2github()
    return "0"

def freeze():
    all_videos = newsmeme.Query.all().limit(1000).filter(published=True).order_by("-createdAt")

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
        parsed_html = flask.render_template('index.html',all_videos=all_videos,main_object=video,narrator_object=narrator_object)
        rdr_html = flask.render_template('redirect.html',url="/v/%s/%s"%(video.objectId,title),video=video,narrator_object=narrator_object)

        os.system("touch v/%s/index.html"%(video.objectId))
        os.system("touch v/%s/%s/index.html"%(video.objectId,title))

        with open("v/%s/index.html"%(video.objectId), "wb") as fh:
            fh.write(rdr_html.encode('utf-8'))

        with open("v/%s/%s/index.html"%(video.objectId,title), "wb") as fh:
            fh.write(parsed_html.encode('utf-8'))


def push2github():
    os.system("git add -u")
    os.system("git commit -m 'auto push'")
    os.system("git push origin gh-pages")
    

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')



