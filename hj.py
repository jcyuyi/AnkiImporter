#!python3
# encoding: utf-8
# -*- coding: UTF-8 -*-
import urllib.parse
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import re

def get_html(word):
    w = urllib.parse.quote(word)
    site = "http://dict.hjenglish.com/jp/jc/" + w
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    req = Request(site)
    for key in hdr:
        req.add_header(key, hdr[key])
    try:
        content = urlopen(req).read()
        return content
    except urllib2.HTTPError as e:
        print(e.fp.read())

def get_visible(element):
    if element.name in ['img','script']:
        return ""
    if element.name == "b":
        return element.string
    if element.name == "br":
        return "\n"
    return element.string

def get_examples(element):
    examples = ""
    for child in element.children:
        s = get_visible(child)
        examples = examples + s
    return examples

def parse_html(html):
    soup = BeautifulSoup(html)
    words = soup.find_all("div","jp_word_comment")
    if len(words) == 0:
        return None
    word = words[0]
    # extract fileds
    jp_title = word.find_all("span", "jpword")[0].string
    jp_kana  = word.find_all(id = "kana_1")[0].string
    jp_tone = ""
    try:
        jp_tone  = word.find_all("span", "tone_jp")[0].string
    except Exception as e:
        # jp_tone not found
        pass
    if jp_tone == None:
        jp_tone = ""
    jp_tip = ""
    try:
        for t in word.find_all("div","tip_content_item"):
            jp_tip = jp_tip + t.string
    except Exception as e:
        # jp_tip not found
        pass
    jp_explain = ""
    js = word.find_all("span","jp_explain")
    if len(js) == 0:
        js =  word.find_all("span","word_comment")
    for j in js:
        if j.string != None:
            jp_explain = jp_explain + '\n' + j.string
    if jp_explain == "":
        jp_explain = get_examples(j)
    jp_example = ""
    jes = word.find_all("span","ext_sent_ee")
    if len(jes) == 0:
        jes = word.find_all("ul","jp_definition_com")[0].find_all("li","flag")
    # for different explain
    for j in jes:
        div = j.find_all("div")
        if len(div) == 2:
            es = div[1]
            examples = get_examples(es)
            jp_example = jp_example + '\n' + examples
    if jp_example == "":
        jes = word.find_all("span","cmd_sent_ee")
        if len(jes) > 0:
            for v in jes:
                examples = get_examples(v)
                jp_example = jp_example + '\n' + examples
    if jp_example == "":
        jes = word.find_all("li","flag")
        for li in jes:
            if len(li) == 2:
                e = li.find_all("div")[1]
                examples = get_examples(e)
                jp_example = jp_example + '\n' + examples
    jp_example = jp_example.strip("\n")
    jp_example = jp_example.replace("\n","<br>")
    jp_explain = jp_explain.strip("\n")
    jp_explain = jp_explain.replace("\n","<br>")
    return {"jp_title":jp_title, "jp_kana":jp_kana, "jp_tone":jp_tone, "jp_tip":jp_tip, "jp_explain":jp_explain, "jp_example":jp_example}

def parsed_jp(dic):
    if dic == None:
        return None
    front = dic["jp_title"]
    back  = dic["jp_kana"] + " " + dic["jp_tone"] + " " + dic["jp_tip"] + '<br>' + dic["jp_explain"]
    example = dic["jp_example"]
    return {"front":front, "back":back, "example":example}

def get_card(words):
    html = get_html(words)
    c = parsed_jp(parse_html(html))
    return c

if __name__ == '__main__':
    print("Get html for word: ")
    # print(get_card("だらしない"))
    print(get_card("生粋"))
