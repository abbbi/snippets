#!/usr/bin/env python
# parse tv info from german tvspielfilm
# blockbusters only
import feedparser
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--detail", help="print detailed description of movie",  type=int)
args = parser.parse_args()

urls = [ 'http://www.tvspielfilm.de/tv-programm/rss/heute2015.xml',
         'http://www.tvspielfilm.de/tv-programm/rss/heute2200.xml'
       ];

detail=[]
for url in urls:
    try:
        feed = feedparser.parse(url)
    except:
        print "Error parsing"

    count=0
    for e in feed['entries']:
        count=count+1
        if not args.detail:
            print "{0} | Detail ID: {1}".format( e['title'].encode('utf-8'), count)
        detail.append(e['summary_detail']['value'].encode('utf-8'));

if args.detail:
    if len(detail[args.detail]) == 0:
        print "no detailed information available"
    else:
        print detail[args.detail]
