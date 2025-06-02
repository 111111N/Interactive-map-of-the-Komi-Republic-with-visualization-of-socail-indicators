import csv
import json

filename = 'Культура.csv'

categories = [
    "Число организаций культурно-досугового типа, единица",
    "Число общедоступных (публичных) библиотек, единица",
    "Число музеев, единица",
    "Численность работников музеев с учетом обособленных подразделений, человек",
    "Численность научных сотрудников и экскурсоводов в музеях с учетом обособленных подразделений, человек",
    "Число профессиональных театров, единица",
    "Численность работников профессиональных театров, всего, человек",
    "Численность художественного и артистического персонала профессиональных театров, человек",
    "Число парков культуры и отдыха (городских садов), единица",
    "Число зоопарков, единица",
    "Число цирков, единица",
    "Число кинотеатров и киноустановок, единица"
]

urban_districts = ["Сыктывкар", "Воркута", "Инта", "Усинск", "Ухта"]

def clean_name(name):
    """Remove (до ... года) from names"""
    if "(" in name and "год" in name:
        return name.split("(")[0].strip()
    return name

def extract_values(parts, years_count):
    values = []
    idx = 1
    while len(values) < years_count and idx < len(parts):
        v = parts[idx].strip()
        if v == '':
            values.append(None)
        else:
            try:
                values.append(int(v))
            except:
                values.append(None)
        idx += 1
    while len(values) < years_count:
        values.append(None)
    return values

data = {}
pending_district_name = None
pending_subdivision_name = None
pending_urban_district = None
current_category = None
years = []

with open(filename, encoding='windows-1251') as f:
    lines = [line.strip() for line in f if line.strip()]

years_line = lines[1]
years = [y.strip() for y in years_line.split(';')[1:-1]]

i = 2
while i < len(lines):
    line = lines[i]
    parts = line.split(';')
    first_col = parts[0].strip()

    # Handle categories
    if first_col in categories:
        current_category = first_col
        pending_district_name = None
        pending_subdivision_name = None
        pending_urban_district = None
        i += 1
        continue

    # Handle urban districts (name on current line, values on next line)
    cleaned_name = clean_name(first_col)
    is_urban_district = any(ud in cleaned_name for ud in urban_districts)
    
    if is_urban_district and i + 1 < len(lines):
        next_line = lines[i + 1]
        next_parts = next_line.split(';')
        next_first_col = next_parts[0].strip()
        
        if next_first_col == "Городской округ, городской округ с внутригородским делением":
            district_name = f"Городской округ {cleaned_name.split('(')[0].strip()}"
            values = extract_values(next_parts, len(years))
            
            for y, v in zip(years, values):
                if v is not None:
                    data.setdefault(district_name, {}).setdefault(y, {})[current_category] = v
            
            i += 2  # Skip both lines
            continue

    # Handle municipal districts
    if "Муниципальный район" in first_col and all(not c.isdigit() for c in first_col) and first_col != "Муниципальный район":
        pending_district_name = "Муниципальный район " + first_col.replace("Муниципальный район", "").strip()
        pending_subdivision_name = None
        pending_urban_district = None
        i += 1
        continue

    # Handle settlements
    if ("Городское поселение" in first_col or "Сельское поселение" in first_col) and all(not c.isdigit() for c in first_col):
        pending_subdivision_name = first_col
        i += 1
        continue

    # Handle values for municipal districts
    if first_col == "Муниципальный район" and pending_district_name and current_category:
        values = extract_values(parts, len(years))
        for y, v in zip(years, values):
            if v is not None:
                data.setdefault(pending_district_name, {}).setdefault(y, {})[current_category] = v
        pending_district_name = None
        i += 1
        continue

    # Handle values for settlements
    if first_col in {"Городское поселение", "Сельское поселение"} and pending_subdivision_name and pending_district_name and current_category:
        values = extract_values(parts, len(years))
        full_name = f"{pending_district_name}, {pending_subdivision_name}"
        for y, v in zip(years, values):
            if v is not None:
                data.setdefault(full_name, {}).setdefault(y, {})[current_category] = v
        pending_subdivision_name = None
        i += 1
        continue

    i += 1  # Move to next line if nothing matched

with open('culture_data.json', 'w', encoding='utf-8') as f_out:
    json.dump(data, f_out, ensure_ascii=False, indent=4)

print("Данные успешно обработаны и сохранены в culture_data.json")