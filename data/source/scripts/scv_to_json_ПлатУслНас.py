import csv
import json
import re

filename = 'Платные услуги населению.csv'
output_json = 'paid_services_data.json'

years = [str(y) for y in range(2008, 2024)]

categories = [
    "Техническое обслуживание и ремонт транспортных средств, машин и оборудования",
    "Число объектов бытового обслуживания населения, оказывающих услуги (по okpd2), единица",
    "Ремонт и строительство жилья и других построек",
    "Ремонт, окраска и пошив обуви",
    "Ремонт и пошив швейных, меховых и кожаных изделий, головных уборов и изделий текстильной галантереи, ремонт, пошив и вязание трикотажных изделий",
    "Ремонт и техническое обслуживание бытовой радиоэлектронной аппаратуры, бытовых машин и приборов, ремонт и изготовление металлоизделий",
    "Изготовление и ремонт мебели",
    "Химическая чистка и крашение, услуги прачечных",
    "Услуги бань и душевых",
    "Услуги парикмахерских",
    "Услуги фотоателье",
    "Ритуальные услуги",
    "Прочие виды бытовых услуг",
    "Число приемных пунктов бытового обслуживания  населения, принимающих заказы от населения на оказание услуг (по okpd2), единица",
    "Число приемных пунктов бытового обслуживания, принимающих заказы от населения на оказание услуг"
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

        values = row[11:]

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
