from pathlib import Path
import json
import re

def clean_region_name(name: str) -> str:
    return re.sub(r"\s*\(.*?\)", "", name).strip()

def process_postal_and_phone_data():
    base_dir = Path(__file__).parent
    input_file = base_dir / 'Почтовая и телефонная связь.csv'
    output_file = base_dir / 'sorted' / 'Почтовая_и_телефонная_связь_data.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    city_districts = {"Сыктывкар", "Воркута", "Инта", "Усинск", "Ухта"}

    municipal_districts = {
        "Вуктыл", "Ижемский", "Княжпогостский", "Койгородский", "Корткеросский",
        "Печора", "Прилузский", "Сосногорск", "Сыктывдинский", "Сысольский",
        "Троицко-Печорский", "Удорский", "Усть-Вымский", "Усть-Куломский", "Усть-Цилемский"
    }

    indicators = [
        "Число сельских населенных пунктов, обслуживаемых почтовой связью, единица",
        "Число телефонизированных сельских населенных пунктов, единица",
        "Число телефонизированных объектов социальной сферы, единица"
    ]

    result = {}
    current_region = None
    current_subregion_type = None
    current_subregion = None
    current_indicator = None
    years = []
    data_lines = []

    def split_line(line):
        return [p.strip() for p in (line.split('\t') if '\t' in line else line.split(';'))]

    try:
        with open(input_file, 'r', encoding='windows-1251') as f:
            lines = [line.strip() for line in f if line.strip()]

        # Найдём строку с годами
        for idx, line in enumerate(lines):
            parts = split_line(line)
            if any(p.isdigit() and len(p) == 4 for p in parts):
                years = parts[1:]
                data_lines = lines[idx + 1:]
                break

        if not years:
            raise ValueError("Не найдена строка с годами.")

        i = 0
        while i < len(data_lines):
            parts = split_line(data_lines[i])
            if not parts:
                i += 1
                continue

            first_cell = parts[0]

            # Обработка региона (например, Муниципальный район Вуктыл)
            if first_cell.startswith("Муниципальный район"):
                raw_name = first_cell.replace("Муниципальный район", "").strip()
                clean_name = clean_region_name(raw_name)
                current_region = f"Муниципальный район {clean_name}"
                current_subregion_type = None
                current_subregion = None
                i += 1
                continue

            # Обработка типа подрегиона
            elif first_cell in ["Городское поселение", "Сельское поселение"]:
                current_subregion_type = first_cell
                current_subregion = None
                i += 1
                continue

            # Обработка подрегиона (например, название поселения или городского округа)
            elif current_subregion_type and first_cell not in indicators:
                current_subregion = clean_region_name(first_cell)
                i += 1
                continue

            # Обработка показателя
            elif first_cell in indicators:
                current_indicator = first_cell
                if len(parts) > 1 and any(p.strip() for p in parts[1:]):
                    values = parts[1:]
                    i += 1
                else:
                    i += 1
                    if i < len(data_lines):
                        next_parts = split_line(data_lines[i])
                        values = next_parts[1:] if len(next_parts) > 1 else []
                        i += 1
                    else:
                        values = []

                # Формируем ключ
                if current_subregion:
                    if current_subregion in city_districts:
                        data_key = f"Городской округ {current_subregion}"
                    elif current_subregion in municipal_districts:
                        data_key = f"Муниципальный район {current_subregion}"
                    else:
                        # Если не входит в городские или муниципальные, считаем это поселением и пишем просто имя
                        data_key = current_subregion
                elif current_subregion_type:
                    data_key = f"{current_region} - {current_subregion_type}"
                else:
                    data_key = current_region

                for j, value in enumerate(values):
                    if j >= len(years):
                        continue
                    year = years[j]
                    val_clean = value.replace(",", ".").strip()
                    if val_clean in ("", "-", "—", None):
                        continue
                    try:
                        parsed_val = float(val_clean) if '.' in val_clean else int(val_clean)
                    except ValueError:
                        continue
                    result.setdefault(data_key, {}).setdefault(year, {})[current_indicator] = parsed_val

                continue

            i += 1

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print("✅ Успешно сохранено:", output_file)
        return result

    except Exception as e:
        print("❌ Ошибка:", str(e))
        return {}

if __name__ == "__main__":
    process_postal_and_phone_data()
