import csv
import json

target_regions = {
    # Городские округа
    "Сыктывкар": "Городской округ",
    "Воркута": "Муниципальный округ",
    "Вуктыл": "Муниципальный округ",
    "Инта": "Муниципальный округ",
    "Усинск": "Муниципальный округ",
    "Ухта": "Муниципальный округ",

    # Муниципальные районы
    "Ижемский": "Муниципальный район",
    "Княжпогостский": "Муниципальный район",
    "Койгородский": "Муниципальный район",
    "Корткеросский": "Муниципальный район",
    "Печора": "Муниципальный район",
    "Прилузский": "Муниципальный район",
    "Сосногорск": "Муниципальный район",
    "Сыктывдинский": "Муниципальный район",
    "Сысольский": "Муниципальный район",
    "Троицко-Печорский": "Муниципальный район",
    "Удорский": "Муниципальный район",
    "Усть-Вымский": "Муниципальный район",
    "Усть-Куломский": "Муниципальный район",
    "Усть-Цилемский": "Муниципальный район"
}

def find_region_key_and_type(name):
    for key in target_regions:
        if key in name:
            return key, target_regions[key]
    return None, None

filename = "Занятость и зарплата.csv"

data = {}
years = []

with open(filename, encoding='cp1251') as f:
    reader = csv.reader(f, delimiter=';')
    lines = list(reader)

# Найдём строку с годами
for i, row in enumerate(lines):
    if any(cell.strip() in ['2017','2018','2019','2020','2021','2022','2023','2024'] for cell in row):
        years = [int(cell) for cell in row if cell.strip().isdigit()]
        years_row_index = i
        break

current_indicator = None
current_region = None
current_section = None

for row in lines[years_row_index+1:]:
    if not any(cell.strip() for cell in row):
        continue

    first_cell = row[0].strip()

    if first_cell.startswith("Раздел ") or first_cell == "Всего по обследуемым видам экономической деятельности":
        current_section = first_cell
        continue

    region_key, region_type = find_region_key_and_type(first_cell)
    if region_key is not None:
        current_region = f"{region_type} {region_key}"
        continue

    indicators_keywords = [
        "Среднесписочная численность работников",
        "Фонд заработной платы всех работников",
        "Среднемесячная заработная плата работников"
    ]
    if any(keyword in first_cell for keyword in indicators_keywords):
        current_indicator = first_cell
        continue

    if current_region and current_indicator and current_section:
        for idx, val in enumerate(row[1:], start=0):
            val_str = val.strip().replace(',', '.')
            if idx < len(years):
                year = years[idx]
                if val_str == '' or val_str == '-':
                    continue
                try:
                    val_num = float(val_str) if '.' in val_str else int(val_str)
                except ValueError:
                    continue

                full_indicator = f"{current_section}: {current_indicator}"
                data.setdefault(current_region, {})
                data[current_region].setdefault(str(year), {})
                data[current_region][str(year)][full_indicator] = val_num

with open("output.json", "w", encoding="utf-8") as outfile:
    json.dump(data, outfile, ensure_ascii=False, indent=4)

print(f"Обработано годов: {len(years)}")
print(f"Данные записаны в output.json")

if years:
    example_region = list(data.keys())[0]
    example_year = str(years[0])
    print(f"Пример данных для '{example_region}' за {example_year}:")
    print(json.dumps(data[example_region][example_year], ensure_ascii=False, indent=4))
