import json
DB = {123456: {'name': 'TestName',
               'Wins': {}, 'Loses': {},
               'items': {'Coins': 50000},
               'equip': {'head': '', 'chest': '', 'cape': '', 'gloves': '',
                         'legs': '', 'boots': '',
                         'mainhand': '', 'offhand': ''}}}

with open('DB.json', 'w') as f:
    json.dump(DB, f, indent=2)

with open('DB.json') as f:
    data = json.load(f)
    print(data)