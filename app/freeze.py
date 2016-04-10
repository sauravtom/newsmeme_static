#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask, flask.views
from flask import render_template
from flask import request
from flask import flash
from flask import jsonify
import os
import sys

app = flask.Flask(__name__)

from parse_rest.connection import register
from parse_rest.datatypes import Object, GeoPoint
from parse_rest.user import User


parse_credentials = {
    "application_id": "2wzSL2IYgy38Q378nNoKSJ23qqqSy5Uu1BW7Slax",
    "rest_api_key": "JwPG9NCK67Yu1Ty96CAunYDs43oRcMsSoipu5qBH",
    "master_key": "7bgt7qUcm5ein46DuaF1rYV5CboF6SbR9HfaiwoD",
}

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

register(parse_credentials["application_id"], parse_credentials["rest_api_key"])

class newsmeme(Object):
    pass

class narrators(Object):
    pass


@app.template_filter()
def foo(text):
    return text.strip()


def title_formatter(text):
    text = text.replace(" ","-")
    text = ''.join(ch for ch in text if ch.isalnum() or ch == '-')
    return text

def freeze(objectId=None):
    all_videos = newsmeme.Query.all().limit(1000).filter(published=True).order_by("-createdAt")

    if objectId:
        print 'object id in present'
        parse_object = newsmeme.Query.get(objectId=objectId)
        sub_freeze(parse_object,all_videos)

    else:
        for video in all_videos:
            sub_freeze(video,all_videos)


def sub_freeze(parse_object,all_videos):
    temp = DIR_PATH.split('/')[:-2]
    new_path = "/".join(temp) + '/newsmeme_static'

    with app.app_context():
        title = title_formatter(parse_object.video_title)
        title = title.encode('utf-8','ignore')
        print title

        try:
            print parse_object.youtube_id
        except:
            print "Youtube id does not exist, aborting"
            return

        try:
            narrator_object = narrators.Query.get(objectId = parse_object.narrator)
        except:
            narrator_object = narrators.Query.get(objectId = '1HfjOEgiJj')

        os.system("mkdir %s/v/%s"%(new_path,parse_object.objectId))
        
        try:
            os.system("mkdir %s/v/%s/%s"%(new_path,parse_object.objectId,title))
        except:
            title = parse_object.objectId
            print 'Changing title to '+ title
            os.system("mkdir %s/v/%s/%s"%(new_path,parse_object.objectId,title))
        

        parsed_html = render_template('index.html',all_videos=all_videos,main_object=parse_object,narrator_object=narrator_object)
        rdr_html = render_template('redirect.html',url="/v/%s/%s"%(parse_object.objectId,title),video=parse_object,narrator_object=narrator_object)

        os.system("touch %s/v/%s/index.html"%(new_path,parse_object.objectId))
        os.system("touch %s/v/%s/%s/index.html"%(new_path,parse_object.objectId,title))

        with open("%s/v/%s/index.html"%(new_path,parse_object.objectId), "wb") as fh:
            fh.write(rdr_html.encode('utf-8'))

        with open("%s/v/%s/%s/index.html"%(new_path,parse_object.objectId,title), "wb") as fh:
            fh.write(parsed_html.encode('utf-8'))

        n = newsmeme.Query.get(objectId=parse_object.objectId)
        print n.video_title
        n.share_url = 'http://newsmeme.in/v/%s/%s'%(parse_object.objectId,title)
        n.short_share_url = 'newsmeme.in/v/%s'%(parse_object.objectId)
        n.save()
        print 'saved object to parse'


if __name__ == '__main__':
    try:
        freeze(sys.argv[1])
    except:
        print 'Freezing all objects'
        freeze()
    

