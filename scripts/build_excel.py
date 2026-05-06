"""
Builds Starbucks_PowerBI_Dashboard.xlsx — a multi-sheet Excel workbook
with formatted tables and charts, ready to upload to Power BI web.
"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import (PatternFill, Font, Alignment, Border, Side,
                              GradientFill)
from openpyxl.chart import BarChart, Reference, PieChart
from openpyxl.chart.series import DataPoint
from openpyxl.utils import get_column_letter
from openpyxl.chart.label import DataLabelList
from pathlib import Path

BASE = Path('/Users/venkatkowshik/Desktop/Projects/Starbucks')
OUT  = BASE / 'final_output' / 'powerbi' / 'Starbucks_PowerBI_Dashboard.xlsx'

# ── Brand colours ──────────────────────────────────────────────────────────────
GREEN  = '00704A'
DARK   = '1E3932'
GOLD   = 'CBA258'
LIGHT  = 'D4E9E2'
WHITE  = 'FFFFFF'
GREY   = 'F5F5F5'

wb = Workbook()
wb.remove(wb.active)   # remove default sheet

# ── Helpers ────────────────────────────────────────────────────────────────────
def hdr_fill():  return PatternFill('solid', fgColor=DARK)
def sub_fill():  return PatternFill('solid', fgColor=GREEN)
def alt_fill():  return PatternFill('solid', fgColor=LIGHT)
def gold_fill(): return PatternFill('solid', fgColor=GOLD)

def thin_border():
    s = Side(style='thin', color='CCCCCC')
    return Border(left=s, right=s, top=s, bottom=s)

def write_header(ws, row, headers, fill=None):
    f = fill or hdr_fill()
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=row, column=c, value=h)
        cell.fill = f
        cell.font = Font(bold=True, color=WHITE, name='Calibri', size=10)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = thin_border()

def write_row(ws, row, values, alt=False):
    f = alt_fill() if alt else PatternFill('solid', fgColor=WHITE)
    for c, v in enumerate(values, 1):
        cell = ws.cell(row=row, column=c, value=v)
        cell.fill = f
        cell.font = Font(name='Calibri', size=10)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border()

def set_col_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

def title_cell(ws, text, row=1, col=1, span=6):
    cell = ws.cell(row=row, column=col, value=text)
    cell.font  = Font(bold=True, size=14, color=WHITE, name='Calibri')
    cell.fill  = PatternFill('solid', fgColor=GREEN)
    cell.alignment = Alignment(horizontal='left', vertical='center')
    ws.merge_cells(start_row=row, start_column=col,
                   end_row=row, end_column=col+span-1)
    ws.row_dimensions[row].height = 28

def kpi_cell(ws, row, col, label, value, color=GREEN):
    lc = ws.cell(row=row, column=col, value=label)
    lc.font  = Font(bold=True, size=9, color='888888', name='Calibri')
    lc.alignment = Alignment(horizontal='center')
    vc = ws.cell(row=row+1, column=col, value=value)
    vc.font  = Font(bold=True, size=16, color=color, name='Calibri')
    vc.alignment = Alignment(horizontal='center')


# ══════════════════════════════════════════════════════════════════════════════
#  1. EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
ws = wb.create_sheet('Executive Summary')
ws.sheet_view.showGridLines = False
ws.row_dimensions[1].height = 28

title_cell(ws, '  ☕  Starbucks Rewards — Customer Analytics Dashboard', 1, 1, 8)

# KPI row
ws.row_dimensions[3].height = 18
ws.row_dimensions[4].height = 30

kpi_cell(ws, 3, 1, 'TOTAL CUSTOMERS', '14,492')
kpi_cell(ws, 3, 2, 'AVG ANNUAL CLV', '$1,877', GOLD)
kpi_cell(ws, 3, 3, 'DISCOUNT ROAS', '178×', GREEN)
kpi_cell(ws, 3, 4, 'BOGO ROAS', '142×', '888888')
kpi_cell(ws, 3, 5, 'FUNNEL COMPLETION', '55.9%', GREEN)
kpi_cell(ws, 3, 6, 'TOP CHANNEL CPA', '$0.96 (Web)', DARK)

# Summary table
ws.row_dimensions[6].height = 18
headers = ['Analysis Area', 'Key Finding', 'Business Impact']
write_header(ws, 6, headers)
rows = [
    ('Customer Segmentation',
     'Champions (2%) → $9,312 CLV | High Spenders (31%) → $8.5M revenue pool',
     'Tiered offer strategy — premium offers for top 2%, volume discounts for middle 31%'),
    ('A/B Test: BOGO vs Discount',
     'Discount wins: 62.5% conversion vs 55.5%, CPA $0.86 vs $1.15, ROAS 178× vs 142×',
     'Switch default campaign to Discount — saves ~$3K per cycle, lifts conversions by 7pp'),
    ('Offer Funnel',
     'BOGO viewed more (83%) but completed less (51%) than Discount (70% / 59%)',
     'BOGO view-to-complete gap of 38% — reduce purchase threshold to unlock ~1,500 extra conversions'),
    ('Channel Performance',
     'Web lowest CPA ($0.96) | Facebook highest avg spend ($111)',
     'Use Web for mass campaigns; reserve Facebook/Instagram for Champion re-targeting'),
    ('Customer Lifetime Value',
     'Total portfolio value: $18.26M/yr across 4 K-Means segments',
     'Retaining 289 Champions alone protects $2.7M — justify VIP programme investment'),
]
for i, r in enumerate(rows):
    write_row(ws, 7+i, r, alt=(i % 2 == 0))

set_col_widths(ws, [22, 52, 52])


# ══════════════════════════════════════════════════════════════════════════════
#  2. CUSTOMER SEGMENTATION
# ══════════════════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet('Customer Segmentation')
ws2.sheet_view.showGridLines = False
title_cell(ws2, '  Customer Segmentation — K-Means Clusters', 1, 1, 7)

headers = ['Segment', 'Customers', 'Share %', 'Avg Spend ($)',
           'Avg Frequency', 'Avg Income ($)', 'Avg Age']
write_header(ws2, 3, headers)
seg_rows = [
    ('Champions',          289,  '2.0%',  776.01, 10.6, 76069, 57),
    ('High Spenders',     4532, '31.3%',  156.40,  7.3, 85329, 66),
    ('Frequent Visitors', 3273, '22.6%',  144.40, 15.7, 52089, 48),
    ('Casual Shoppers',   1885, '13.0%',   61.32,  4.0, 72392, 60),
]
for i, r in enumerate(seg_rows):
    write_row(ws2, 4+i, r, alt=(i % 2 == 0))

set_col_widths(ws2, [20, 12, 10, 15, 15, 16, 10])

# Bar chart — Customers per segment
chart = BarChart()
chart.type   = 'col'
chart.title  = 'Customers per Segment'
chart.y_axis.title = 'Count'
chart.x_axis.title = 'Segment'
chart.style  = 10
chart.height = 12
chart.width  = 18
data  = Reference(ws2, min_col=2, min_row=3, max_row=7)
cats  = Reference(ws2, min_col=1, min_row=4, max_row=7)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.series[0].graphicalProperties.solidFill = GREEN
ws2.add_chart(chart, 'A9')

# Bar chart — Avg Spend
chart2 = BarChart()
chart2.type   = 'col'
chart2.title  = 'Average Spend by Segment ($)'
chart2.y_axis.title = 'Avg Spend ($)'
chart2.style  = 10
chart2.height = 12
chart2.width  = 18
data2 = Reference(ws2, min_col=4, min_row=3, max_row=7)
chart2.add_data(data2, titles_from_data=True)
chart2.set_categories(cats)
chart2.series[0].graphicalProperties.solidFill = GOLD
ws2.add_chart(chart2, 'J9')


# ══════════════════════════════════════════════════════════════════════════════
#  3. CLV ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
ws3 = wb.create_sheet('CLV Analysis')
ws3.sheet_view.showGridLines = False
title_cell(ws3, '  Customer Lifetime Value by Segment', 1, 1, 6)

clv_headers = ['Segment', 'Customers', 'Avg Annual CLV ($)',
               'Total Segment Value ($)', 'Revenue Share (%)']
write_header(ws3, 3, clv_headers)
clv_rows = [
    ('Champions',          289,  9312,  2691194, 14.7),
    ('High Spenders',     4532,  1877,  8505808, 46.6),
    ('Frequent Visitors', 3273,  1733,  5671424, 31.1),
    ('Casual Shoppers',   1885,   736,  1387073,  7.6),
]
for i, r in enumerate(clv_rows):
    write_row(ws3, 4+i, r, alt=(i % 2 == 0))

set_col_widths(ws3, [20, 12, 20, 24, 18])

# CLV bar chart
chart3 = BarChart()
chart3.type   = 'col'
chart3.title  = 'Average Annual CLV by Segment ($)'
chart3.y_axis.title = 'CLV ($)'
chart3.style  = 10
chart3.height = 13
chart3.width  = 20
data3  = Reference(ws3, min_col=3, min_row=3, max_row=7)
cats3  = Reference(ws3, min_col=1, min_row=4, max_row=7)
chart3.add_data(data3, titles_from_data=True)
chart3.set_categories(cats3)
chart3.series[0].graphicalProperties.solidFill = GREEN
ws3.add_chart(chart3, 'A9')

# Pie chart — Revenue share
pie = PieChart()
pie.title  = 'Revenue Share by Segment'
pie.style  = 10
pie.height = 13
pie.width  = 16
pdata = Reference(ws3, min_col=5, min_row=3, max_row=7)
pcats = Reference(ws3, min_col=1, min_row=4, max_row=7)
pie.add_data(pdata, titles_from_data=True)
pie.set_categories(pcats)
slice_colors = [GREEN, '2E7D32', GOLD, LIGHT]
for idx, color in enumerate(slice_colors):
    pt = DataPoint(idx=idx)
    pt.graphicalProperties.solidFill = color
    pie.series[0].dPt.append(pt)
ws3.add_chart(pie, 'J9')


# ══════════════════════════════════════════════════════════════════════════════
#  4. A/B TEST RESULTS
# ══════════════════════════════════════════════════════════════════════════════
ws4 = wb.create_sheet('AB Test Results')
ws4.sheet_view.showGridLines = False
title_cell(ws4, '  A/B Test — BOGO vs. Discount Offers', 1, 1, 8)

ab_headers = ['Metric', 'BOGO', 'Discount', 'Winner', 'Delta']
write_header(ws4, 3, ab_headers)
ab_rows = [
    ('Conversion Rate',            '55.5%', '62.5%', 'Discount', '+7.0 pp'),
    ('Avg Spend per Customer ($)', '$107.82','$108.43','Discount', '+$0.61'),
    ('Total Delivery Cost ($)',    '$19,412','$16,401','Discount', '-$3,011'),
    ('Cost Per Acquisition ($)',   '$1.15',  '$0.86', 'Discount', '-25%'),
    ('Avg Revenue / Conversion ($)','$162.86','$153.44','BOGO',   '+$9.42'),
    ('ROAS',                        '142×',   '178×', 'Discount', '+26%'),
    ('Sample Size',                '30,499','30,543', '—',        '—'),
    ('Statistical Test',     'Chi-Square p<0.001', "Welch's t p<0.05", '—', '—'),
]
for i, r in enumerate(ab_rows):
    write_row(ws4, 4+i, r, alt=(i % 2 == 0))

set_col_widths(ws4, [26, 16, 16, 14, 12])

# Conversion rate comparison
chart4 = BarChart()
chart4.type   = 'col'
chart4.title  = 'Conversion Rate: BOGO vs Discount (%)'
chart4.y_axis.title = 'Conversion Rate (%)'
chart4.style  = 10
chart4.height = 12
chart4.width  = 16

# Write mini data for chart
ws4['H3'] = 'Offer Type'
ws4['I3'] = 'Conversion Rate'
ws4['H4'] = 'BOGO'
ws4['I4'] = 55.5
ws4['H5'] = 'Discount'
ws4['I5'] = 62.5
for cell in ['H3','I3','H4','I4','H5','I5']:
    ws4[cell].font = Font(name='Calibri', size=9)

cdata = Reference(ws4, min_col=9, min_row=3, max_row=5)
ccats = Reference(ws4, min_col=8, min_row=4, max_row=5)
chart4.add_data(cdata, titles_from_data=True)
chart4.set_categories(ccats)
chart4.series[0].graphicalProperties.solidFill = GREEN
ws4.add_chart(chart4, 'A14')

# CPA comparison
chart5 = BarChart()
chart5.type   = 'col'
chart5.title  = 'Cost Per Acquisition ($): BOGO vs Discount'
chart5.y_axis.title = 'CPA ($)'
chart5.style  = 10
chart5.height = 12
chart5.width  = 16
ws4['H7'] = 'Offer Type'
ws4['I7'] = 'CPA ($)'
ws4['H8'] = 'BOGO'
ws4['I8'] = 1.15
ws4['H9'] = 'Discount'
ws4['I9'] = 0.86
cdata2 = Reference(ws4, min_col=9, min_row=7, max_row=9)
ccats2 = Reference(ws4, min_col=8, min_row=8, max_row=9)
chart5.add_data(cdata2, titles_from_data=True)
chart5.set_categories(ccats2)
chart5.series[0].graphicalProperties.solidFill = GOLD
ws4.add_chart(chart5, 'J14')


# ══════════════════════════════════════════════════════════════════════════════
#  5. FUNNEL ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
ws5 = wb.create_sheet('Funnel Analysis')
ws5.sheet_view.showGridLines = False
title_cell(ws5, '  Offer Funnel — Received → Viewed → Completed', 1, 1, 7)

fn_headers = ['Offer Type', 'Received', 'Viewed', 'View Rate',
              'Completed', 'Completion Rate', 'End-to-End Rate']
write_header(ws5, 3, fn_headers)
fn_rows = [
    ('BOGO',          30499, 25449, '83.4%', 15669, '61.6%', '51.4%'),
    ('Discount',      30543, 21445, '70.2%', 17910, '83.5%', '58.6%'),
    ('Informational', 15235, 10831, '71.1%',   '—',    '—',    '—'),
]
for i, r in enumerate(fn_rows):
    write_row(ws5, 4+i, r, alt=(i % 2 == 0))

set_col_widths(ws5, [16, 12, 12, 12, 12, 16, 16])

# Funnel bar chart
chart6 = BarChart()
chart6.type   = 'bar'  # horizontal
chart6.title  = 'Offer Funnel Volume by Stage'
chart6.x_axis.title = 'Customers'
chart6.style  = 10
chart6.height = 12
chart6.width  = 22

ws5['I3']  = 'Stage'
ws5['J3']  = 'BOGO'
ws5['K3']  = 'Discount'
ws5['I4']  = 'Received'
ws5['J4']  = 30499
ws5['K4']  = 30543
ws5['I5']  = 'Viewed'
ws5['J5']  = 25449
ws5['K5']  = 21445
ws5['I6']  = 'Completed'
ws5['J6']  = 15669
ws5['K6']  = 17910

fdata = Reference(ws5, min_col=10, max_col=11, min_row=3, max_row=6)
fcats = Reference(ws5, min_col=9,  min_row=4, max_row=6)
chart6.add_data(fdata, titles_from_data=True)
chart6.set_categories(fcats)
chart6.series[0].graphicalProperties.solidFill = GREEN
chart6.series[1].graphicalProperties.solidFill = GOLD
ws5.add_chart(chart6, 'A8')


# ══════════════════════════════════════════════════════════════════════════════
#  6. CHANNEL PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
ws6 = wb.create_sheet('Channel Performance')
ws6.sheet_view.showGridLines = False
title_cell(ws6, '  Channel Performance — Conversion, Spend & CPA', 1, 1, 7)

ch_headers = ['Channel', 'Sends', 'Conversions', 'Conv Rate (%)',
              'Avg Spend ($)', 'CPA ($)', 'Cost/Send ($)']
write_header(ws6, 3, ch_headers)
ch_rows = [
    ('Facebook / Instagram Ads', 38065, 23213, 61.0, 111.02, 1.26, 0.50),
    ('Mobile App',               53374, 32301, 60.5, 108.86, 1.05, 0.05),
    ('Web',                      53384, 32064, 60.1, 107.62, 0.96, 0.15),
    ('Email',                    61042, 35997, 59.0, 108.12, 0.99, 0.10),
]
for i, r in enumerate(ch_rows):
    write_row(ws6, 4+i, r, alt=(i % 2 == 0))

set_col_widths(ws6, [26, 12, 14, 14, 14, 12, 14])

# CPA bar chart
chart7 = BarChart()
chart7.type   = 'col'
chart7.title  = 'Cost Per Acquisition by Channel ($)'
chart7.y_axis.title = 'CPA ($)'
chart7.style  = 10
chart7.height = 12
chart7.width  = 18
cdata7 = Reference(ws6, min_col=6, min_row=3, max_row=7)
ccats7 = Reference(ws6, min_col=1, min_row=4, max_row=7)
chart7.add_data(cdata7, titles_from_data=True)
chart7.set_categories(ccats7)
chart7.series[0].graphicalProperties.solidFill = DARK
ws6.add_chart(chart7, 'A9')

# Conv rate chart
chart8 = BarChart()
chart8.type   = 'col'
chart8.title  = 'Conversion Rate by Channel (%)'
chart8.y_axis.title = 'Conv Rate (%)'
chart8.style  = 10
chart8.height = 12
chart8.width  = 18
cdata8 = Reference(ws6, min_col=4, min_row=3, max_row=7)
chart8.add_data(cdata8, titles_from_data=True)
chart8.set_categories(ccats7)
chart8.series[0].graphicalProperties.solidFill = GREEN
ws6.add_chart(chart8, 'J9')


# ══════════════════════════════════════════════════════════════════════════════
#  7. RAW DATA TABS (for Power BI web semantic model)
# ══════════════════════════════════════════════════════════════════════════════
raw_files = {
    'Data - Segments':     'powerbi_customer_segments.csv',
    'Data - AB Test':      'powerbi_ab_test.csv',
    'Data - CLV':          'powerbi_clv_segments.csv',
    'Data - CPA':          'powerbi_cpa_summary.csv',
    'Data - Channel':      'powerbi_channel_performance.csv',
    'Data - Funnel':       'powerbi_funnel.csv',
}
BASE_P = Path('/Users/venkatkowshik/Desktop/Projects/Starbucks')
for sheet_name, csv_file in raw_files.items():
    csv_path = BASE_P / csv_file
    if not csv_path.exists():
        continue
    df = pd.read_csv(csv_path)
    wsR = wb.create_sheet(sheet_name)
    wsR.sheet_view.showGridLines = False
    title_cell(wsR, f'  Raw Data — {sheet_name.replace("Data - ", "")}', 1, 1, len(df.columns))
    write_header(wsR, 3, list(df.columns))
    for ri, row in df.iterrows():
        for ci, val in enumerate(row.values, 1):
            cell = wsR.cell(row=4+ri, column=ci, value=val)
            cell.font = Font(name='Calibri', size=9)
            cell.alignment = Alignment(horizontal='center')
            cell.border = thin_border()
            if ri % 2 == 0:
                cell.fill = alt_fill()
    for ci in range(1, len(df.columns)+1):
        wsR.column_dimensions[get_column_letter(ci)].width = 18


# ── Save ───────────────────────────────────────────────────────────────────────
wb.save(str(OUT))
print(f'✅ Excel workbook saved: {OUT}')
