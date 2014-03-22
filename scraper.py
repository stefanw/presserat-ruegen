# -*- encoding: utf-8 -*-
import re

import dataset
from lxml import etree
import requests

URL = 'http://www.presserat.de/pressekodex/uebersicht-der-ruegen/'

LINE_RE = re.compile(u'^(.*?) ?\((.*?)\)?( ?- ?nicht[ -]öffentlich ?-)?.?,? ?Ziffern? ?(.*)$')


def get_reprimands(root):
    for yeardiv in root.xpath('//div[@class="csc-default"]'):
        year = yeardiv.xpath('.//h1')
        if not year:
            continue
        year = year[0].text
        print(year)
        for content in yeardiv.xpath('./p/*'):
            if content.tail is not None:
                text = content.tail
                try:
                    match = LINE_RE.match(text)
                    yield year, match.groups()
                except AttributeError:
                    print(text, match)
                    continue


def main():
    db = dataset.connect('sqlite:///data.sqlite')
    table = db['data']

    response = requests.get(URL)
    root = etree.HTML(response.content)
    for year, reprimand in get_reprimands(root):
        print(year, reprimand)
        table.upsert({
            'year': year,
            'name': reprimand[0],
            'issue': reprimand[1],
            'public': False if reprimand[2] is None else True,
            'rules': ','.join(reprimand[3].strip().split('+'))
        }, ['name', 'issue'])

if __name__ == '__main__':
    main()
