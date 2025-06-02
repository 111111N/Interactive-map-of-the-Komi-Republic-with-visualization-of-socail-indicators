import csv
import json
import re

filename = 'Жильё.csv'
output_json = 'housing_construction.json'

years = [str(y) for y in range(2008, 2024)]

categories = [
    "Число семей, получивших жилые помещения и улучшивших жилищные условия в отчетном году (с 2008 г.), единица",
    "Число семей, состоящих на учете в качестве нуждающихся в жилых помещениях на конец года (с 2008 г.), единица"
]

urban_okrugs = {"Сыктывкар", "Воркута", "Инта", "Усинск", "Ухта"}

def is_settlement_row(row):
    first_col = row[0].strip()
    rest = row[1:]
    if first_col == '':
        return False
    if first_col in categories:
        return False
    return all(cell.strip() == '' for cell in rest)

def is_number(s):
    try:
        float(s.replace(',', '.'))
        return True
    except:
        return False

def clean_settlement_name(name):
    name = re.sub(r'\s*\(до [^)]+\)', '', name).strip()
    if name in urban_okrugs:
        name = f"Городской округ {name}"
    return name

data = {}
current_settlement = None

with open(filename, encoding='windows-1251') as f:
    reader = csv.reader(f, delimiter=';')
    for idx, row in enumerate(reader):
        if idx <= 32:
            continue

        if not row or all(cell.strip() == '' for cell in row):
            continue

        if is_settlement_row(row):
            current_settlement = clean_settlement_name(row[0].strip())
            if current_settlement not in data:
                data[current_settlement] = {}
            continue

        if current_settlement is None:
            continue

        category = row[0].strip()
        if category == '':
            continue

        if category not in categories:
            continue

        values = row[1:]

        for i, year in enumerate(years):
            if i < len(values):
                val = values[i].strip()
                if is_number(val):
                    try:
                        val_num = int(val)
                    except:
                        val_num = float(val.replace(',', '.'))

                    if year not in data[current_settlement]:
                        data[current_settlement][year] = {}
                    data[current_settlement][year][category] = val_num

with open(output_json, 'w', encoding='utf-8') as jf:
    json.dump(data, jf, ensure_ascii=False, indent=2)

print(f"Данные успешно сохранены в {output_json}")
