#!python3
# encoding: utf-8
# -*- coding: UTF-8 -*-
import sqlite3 as sqlite
import unicodedata
import uuid
import time
import datetime
import json
import re

def check_local_storage(sql_file):
    try:
        con = sqlite.connect(sql_file)
        con.text_factory = str
        cur = con.cursor()
        cur.execute("SELECT * FROM ItemTable WHERE key=\"AnkiApp.device.id\"")
        row = cur.fetchone()
        device_id = str(row[1].decode("utf-8"))
        print("Anki_device_id:")
        print("    " + device_id);
    except sqlite.Error as e:
        print(e)
        quit()

def check_db(sql_file):
    try:
        con = sqlite.connect(sql_file)
        con.text_factory = str
        cur = con.cursor()
        cur.execute("SELECT * FROM decks")
        rows = cur.fetchall()
        s = '{0:^40} {1}'.format('==== deck_id ====','==== deck name ====',)
        print(s)
        decks = []
        for row in rows:
            deck_id = row[0]
            deck_name = row[2]
            decks.append(deck_id)
            s = '{0:^40} {1}'.format(deck_id, deck_name)
            print(s)
    except sqlite.Error as e:
        print(e)

def get_guid():
    s = str(uuid.uuid4()).replace('-', '')
    return s

def get_layouts(sql_file, deck_id):
    layouts = []
    try:
        con = sqlite.connect(sql_file)
        con.text_factory = str
        cur = con.cursor()
        cur.execute("SELECT * FROM decks_layouts")
        rows = cur.fetchall()
        for row in rows:
            layouts.append(row[1])
    except sqlite.Error as e:
        print(e)
    return layouts

def get_response_type_id(sql_file):
    try:
        con = sqlite.connect(sql_file)
        con.text_factory = str
        cur = con.cursor()
        cur.execute("SELECT * FROM response_types")
        rows = cur.fetchall()
        for row in rows:
            return row[0]
    except sqlite.Error as e:
        print(e)
        quit()
    return ""

def new_decks_info(value, deck_id):
    s = value.decode("utf-16", "strict")
    s1 = s.find(deck_id)
    e2 = s.find("\"modified_at", s1)
    s2 = s.find("\"num_knols", s1)
    fs = str(s[:s2])
    ms = str(s[s2:e2]) #"num_knols":11,"saved_knols":11,
    es = str(s[e2:])
    p = re.compile('\d+')
    num = p.findall(ms)[0]
    n = int(num) + 1
    num = str(n)
    new_ms = "\"num_knols\":" + num + "," + "\"saved_knols\":" + num + ","
    new_s = fs + new_ms + es;
    bs = new_s.encode("utf-16")
    return bs[2:]

def increase_localstorage(local_storage_file, deck_id):
    try:
        con = sqlite.connect(local_storage_file)
        cur = con.cursor()
        cur.execute("SELECT * FROM ItemTable WHERE key=\"AnkiApp.decks\"")
        value = cur.fetchone()[1]
        if value == None:
            print("ERROR: can not modify localstorage file! ")
            quit()
        new_value = new_decks_info(value, deck_id)
        sql = u"INSERT INTO ItemTable VALUES(?,?)"
        cur.execute(sql, ("AnkiApp.decks", new_value))
        con.commit()
    except sqlite.Error as e:
        print(e)
        quit()

# insert to DB:
# 1. Add id to [knols], like:
#  18ada1c729f34bb0a19cb70108642b50 // UUID
# 2. Add id, knol_id, knol_key_name, value to [knol_values], like:
# 3. Add knol_id, deck_id to [decks_knols], like:
# For every layout:
#   4.1 Add id, knol_id, layout_id, created_at, modified_at, num_responses to [cards]
#   4.2 Add card_id, deck_id, to [cards_decks]
# 5. Insert operation to [operations]

def insert_db(sql_file, device_id, deck_id, knol_key_name, knol_key_value):
    knol_id = get_guid()
    knol_values = []
    layouts = get_layouts(sql_file, deck_id)
    try:
        con = sqlite.connect(sql_file)
        con.text_factory = str
        cur = con.cursor()
        # 1. Add id to [knols]
        # print("Add id to [knols]: " + knol_id)
        sql = u"INSERT INTO knols VALUES(?)"
        cur.execute(sql, (knol_id,))
        # 2. Add id, knol_id, knol_key_name, value to [knol_values]
        for idx in range(len(knol_key_name)):
            id = get_guid()
            sql = u"INSERT INTO knol_values VALUES(?,?,?,?)"
            cur.execute(sql, (id, knol_id, knol_key_name[idx], knol_key_value[idx]))
            knol_values.append({"id":id, "key": knol_key_name[idx], "value": knol_key_value[idx], "blobs":[]})
        # 3. Add knol_id, deck_id to [decks_knols]
        sql = u"INSERT INTO decks_knols VALUES(?,?)"
        cur.execute(sql, (knol_id, deck_id))
        # For every layout:
        for layout_id in layouts:
            # 4.1 Add id, knol_id, layout_id, created_at, modified_at, num_responses to [cards]
            sql = u"INSERT INTO cards VALUES(?,?,?,?,?,?,?,?,?)"
            t = int(time.time() * 1000)
            card_id = get_guid()
            cur.execute(sql, (card_id, knol_id, layout_id, t, t, None, None, None, 0))
            # 4.2 Add card_id, deck_id, to [cards_decks]
            sql2 = u"INSERT INTO cards_decks VALUES(?,?)"
            cur.execute(sql2, (card_id, deck_id))
        # 5. insert operation to [operations]
        opeartion_id = get_guid()
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        type = "INSERT"
        created_at = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        object_type = "knol"
        response_type_id = get_response_type_id(sql_file)
        object_parameters = json.JSONEncoder().encode({"response_type_id": response_type_id, "deck_id": deck_id, "knol_id": knol_id, "knol_values": knol_values, "knol_tags":[] })
        sql = u"INSERT INTO operations VALUES(?,?,?,?,?,?,?)"
        cur.execute(sql, (opeartion_id, device_id, timestamp, type, created_at, object_type, object_parameters))
        con.commit()
    except sqlite.Error as e:
        con.rollback()
        print(e)
