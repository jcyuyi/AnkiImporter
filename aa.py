#!python3
# encoding: utf-8
# -*- coding: UTF-8 -*-
import sys

import hj
import anki


# ================== Configuration ====================

# anki sql file
# Located in /Users/YOURUSER/Library/Containers/com.ankiapp.mac-client/Data/Library/WebKit/Databases/
anki_sqlite_file   = "/Users/Jcy/Library/Containers/com.ankiapp.mac-client/Data/Library/WebKit/Databases/file__0/eea33714-9c7d-4e85-a705-ad48fdef9a03.db"

# anki localstorage file
# Located in /Users/YOURUSER/Library/Containers/com.ankiapp.mac-client/Data/Library/Application Support/AnkiApp/LocalStorage/
anki_local_storage_file = "/Users/Jcy/Library/Containers/com.ankiapp.mac-client/Data/Library/Application Support/AnkiApp/LocalStorage/file__0.localstorage"

# anki card field name for knol_key_name
anki_knol_key_name = ["front", "back", "example"]

# anki deck id
# Run program once and copy deck_id
anki_deck_id   = ""

# anki device id
# Run program once and copy device_id
anki_device_id = ""

# ============== End of Configuration =================

if __name__ == '__main__':
    if anki_sqlite_file == "":
        print("Please read and set Configuration(Top of aa.py)")
        quit()
    if anki_deck_id == "" or anki_device_id == "":
        print("Reading decks info:")
        anki.check_db(anki_sqlite_file)
        anki.check_local_storage(anki_local_storage_file)
        quit()
    args = len(sys.argv)
    argv = sys.argv
    if args != 2:
        print("Usage: aa.py word")
        quit()
    word = str(argv[1])
    card = hj.get_card(word)
    if card == None:
        print("No word found!")
        quit()
    knol_key_value = []
    fields = 0
    for name in anki_knol_key_name:
        if name in card:
            fields = fields + 1;
            knol_key_value.append(card[name])
    if fields != len(anki_knol_key_name):
        print("Anki card fields mismatch!")
        quit()
    anki.insert_db(anki_sqlite_file, anki_device_id, anki_deck_id, anki_knol_key_name, knol_key_value)
    anki.increase_localstorage(anki_local_storage_file, anki_deck_id)
    print("Successful!")
