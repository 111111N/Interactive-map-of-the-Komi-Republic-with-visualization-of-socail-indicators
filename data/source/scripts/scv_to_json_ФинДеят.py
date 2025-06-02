import csv
import json
from pathlib import Path

target_regions = {
    "Сыктывкар": "Городской округ",
    "Воркута": "Городской округ",
    "Инта": "Городской округ",
    "Усинск": "Городской округ",
    "Ухта": "Городской округ",

    "Вуктыл": "Муниципальный район",
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

def clean_text(text):
    return text.strip().lower().replace('\xa0', ' ')

def find_region_key_and_type(name):
    name_clean = clean_text(name)
    for key in target_regions:
        key_clean = clean_text(key)
        if key_clean in name_clean:
            return key, target_regions[key]
    return None, None

def process_financial_data():
    base_dir = Path(__file__).parent
    input_file = base_dir / 'Финансовая деятельность.csv'
    output_file = base_dir / 'sorted' / 'financial_data.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    years = []
    current_section = None
    current_region = None

    with open(input_file, encoding='windows-1251', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        lines = list(reader)

    # Находим строку с годами
    years_row_index = None
    for i, row in enumerate(lines):
        if any(cell.strip().isdigit() and len(cell.strip()) == 4 for cell in row):
            years = [int(cell.strip()) for cell in row if cell.strip().isdigit()]
            years_row_index = i
            break

    if years_row_index is None:
        print("Не удалось найти строку с годами.")
        return

    i = years_row_index + 1
    while i < len(lines):
        row = lines[i]
        if not row:
            i += 1
            continue
        first_cell = row[0].strip() if row else ""

        # Обнаружение региона
        region_key, region_type = find_region_key_and_type(first_cell)
        if region_key is not None:
            current_region = f"{region_type} {region_key}"
            i += 1
            continue

        # Обнаружение раздела
        if first_cell.startswith("Раздел"):
            current_section = first_cell
            i += 1
            continue

        # Обработка строки с индикатором (с запятой)
        if ',' in first_cell and current_section and current_region:
            current_indicator = first_cell
            i += 1

            # Обрабатываем подряд следующие строки с категориями и значениями
            while i < len(lines):
                next_row = lines[i]
                if not next_row:
                    i += 1
                    continue
                next_first_cell = next_row[0].strip() if next_row else ""

                # Прерываем, если начинается новый раздел, регион или индикатор
                if not next_first_cell:
                    i += 1
                    continue
                if next_first_cell.startswith("Раздел"):
                    break
                region_key_check, _ = find_region_key_and_type(next_first_cell)
                if region_key_check is not None:
                    break
                if ',' in next_first_cell:
                    break

                # Если это строка с категорией "Всего" или "Муниципальная собственность"
                if next_first_cell.lower() in ["всего", "муниципальная собственность"]:
                    for idx, val in enumerate(next_row[1:1+len(years)]):
                        if idx >= len(years):
                            break
                        val_str = val.strip().replace(',', '.')
                        if val_str and val_str != '-':
                            try:
                                val_num = float(val_str) if '.' in val_str else int(val_str)
                                year = years[idx]
                                full_indicator = f"{current_section}: {current_indicator} ({next_first_cell})"
                                data.setdefault(current_region, {})
                                data[current_region].setdefault(str(year), {})
                                data[current_region][str(year)][full_indicator] = val_num
                            except ValueError:
                                pass
                i += 1
            continue

        i += 1

    with open(output_file, 'w', encoding='utf-8') as out_f:
        json.dump(data, out_f, ensure_ascii=False, indent=4)

    print(f"Обработано годов: {len(years)}")
    print(f"Данные сохранены в {output_file}")

    if years and data:
        example_region = list(data.keys())[0]
        example_year = str(years[0])
        print(f"Пример данных для '{example_region}' в {example_year}:")
        print(json.dumps(data[example_region][example_year], ensure_ascii=False, indent=4))

if __name__ == '__main__':
    process_financial_data()
