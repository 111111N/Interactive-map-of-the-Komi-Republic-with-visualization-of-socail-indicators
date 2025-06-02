import csv
import json
import re

filename = 'Спорт.csv'

def clean_name(name):
    if name:
        name = re.sub(r'\(до.*?\)', '', name)
        name = re.sub(r'\(.*?\)', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        return name
    return name

def extract_values(parts, years_count):
    result = []
    for v in parts[1:1+years_count]:
        v = v.strip().replace(',', '.')
        try:
            result.append(float(v))
        except ValueError:
            result.append(None)
    return result + [None] * (years_count - len(result))

def has_numbers(parts):
    return any(v.strip().replace(',', '.').replace('.', '', 1).isdigit() for v in parts[1:] if v.strip())

territory_markers = [
    "Городской округ", 
    "Городской округ с внутригородским делением",
    "Муниципальный район", 
    "Городское поселение", 
    "Сельское поселение"
]

city_names = {"Сыктывкар", "Воркута", "Инта", "Усинск", "Ухта"}

def contains_territory_marker(text):
    parts = [p.strip() for p in text.split(',')]
    return any(p in territory_markers for p in parts)

with open(filename, encoding='windows-1251') as f:
    lines = [line.strip() for line in f if line.strip()]

years = [y.strip() for y in lines[1].split(';')[1:] if y.strip()]
data = {}

current_territory = None
current_category = None
territory_active = False
current_region = None

for line in lines[2:]:
    parts = line.split(';')
    first_col = clean_name(parts[0])

    if "Муниципальные районы" in first_col or "Городские округа" in first_col:
        current_region = first_col
        continue

    if contains_territory_marker(first_col):
        territory_active = True
        current_territory = None
        continue

    if (territory_active or first_col in city_names) and not has_numbers(parts) and first_col:
        territory_active = False
        if current_region:
            region_type = "Муниципальный район" if "район" in current_region.lower() else "Городской округ"
        else:
            region_type = ""  # безопасное значение по умолчанию
        current_territory = f"{region_type.strip()} {first_col.strip()}".strip()
        continue

    if not has_numbers(parts) and first_col:
        current_category = first_col
        continue

    if has_numbers(parts):
        category = current_category if current_category else first_col
        values = extract_values(parts, len(years))

        if current_territory:
            data.setdefault(current_territory, {})
            for year, value in zip(years, values):
                if value is not None:
                    data[current_territory].setdefault(year, {})
                    data[current_territory][year][category] = value

with open('sport_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Данные успешно сохранены в sport_data.json")
