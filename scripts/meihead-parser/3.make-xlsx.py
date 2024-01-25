import glob
import json
from pprint import pprint
import xlsxwriter

########################################################################################################################
# CONSTANTS & CONFIG
########################################################################################################################

json_files = glob.glob('metadata-json/**/*.json', recursive=True)

workbook = xlsxwriter.Workbook('metadata.xlsx')
bold = workbook.add_format({'bold': True})
worksheet = workbook.add_worksheet()

########################################################################################################################
# GO
########################################################################################################################

data = []

for f in json_files:
    with open(f, 'r', encoding='utf-8') as f:
        d = json.load(f)
        for k, v in d.items():
            if k in ["score_uri", "encoding_applications"]:
                d[k] = [json.dumps(v)]
            d[k] = ' 🍄 '.join(d[k])
        d['_score'] = '/'.join(f.name.split('/')[1:]).replace('.json', '')
        data.append(d)

worksheet.write(0, 0, 'SCORE', bold)

row = 0
col = 1
for k in data[0]:
    worksheet.write(row, col, k, bold)
    col += 1

row = 1

for d in data:
    worksheet.write(row, 0, d['_score'], bold)
    del d['_score']
    row += 1

row = 1

for d in (data):
    col = 1
    for k, v in d.items():
        worksheet.write(row, col, v)
        col += 1
    row += 1

# ########################################################################################################################
# # THAT'S ALL FOLKS!
# ########################################################################################################################

worksheet.autofit()
workbook.close()
