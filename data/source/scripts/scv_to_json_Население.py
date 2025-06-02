import csv
import json
import re

filename = 'Население.csv'
output_json = 'population_data.json'

categories = [
    "Число родившихся (без мертворожденных), человек",
    "Число умерших, человек",
    "Общий коэффициент рождаемости, промилле",
    "Общий коэффициент смертности, промилле",
    "Естественный прирост (убыль), человек",
    "Общий коэффициент естественного прироста (убыли), промилле",
    "Число прибывших, человек",
    "Число выбывших, человек",
    "Миграционный прирост, человек",
]

years = [str(y) for y in range(2008, 2024)]

urban_okrugs = {"Сыктывкар", "Воркута", "Инта", "Усинск", "Ухта"}

def is_number(s):
    try:
        float(s.replace(',', '.'))
        return True
    except:
        return False

def clean_settlement_name(name):
    cleaned = re.sub(r'\s*\(до [^)]+\)', '', name).strip()
    if cleaned in urban_okrugs:
        cleaned = "Городской округ " + cleaned
    return cleaned

data = {}
current_category = None

with open(filename, encoding='windows-1251') as f:
    reader = csv.reader(f, delimiter=';')
    for idx, row in enumerate(reader):
        if not row or all(cell.strip() == '' for cell in row):
            continue
        
        first_col = row[0].strip()
        values = row[1:]
        
        if first_col in categories:
            current_category = first_col
            continue
        
        if current_category is None:
            continue
        
        if any(is_number(v) for v in values):
            settlement = clean_settlement_name(first_col)
            if settlement not in data:
                data[settlement] = {}
            
            for i, year in enumerate(years):
                if i < len(values):
                    val = values[i].strip()
                    if is_number(val):
                        try:
                            val_num = int(val)
                        except:
                            val_num = float(val.replace(',', '.'))
                        
                        if year not in data[settlement]:
                            data[settlement][year] = {}
                        data[settlement][year][current_category] = val_num

with open(output_json, 'w', encoding='utf-8') as jf:
    json.dump(data, jf, ensure_ascii=False, indent=2)

print(f"Данные успешно сохранены в {output_json}")
