"""
Generates Starbucks_Analytics_Report.docx — full project summary with charts.
"""
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os
from pathlib import Path

BASE   = Path('/Users/venkatkowshik/Desktop/Projects/Starbucks')
CHARTS = BASE / 'charts'

GREEN = RGBColor(0x00, 0x70, 0x4A)
DARK  = RGBColor(0x1E, 0x39, 0x32)
GOLD  = RGBColor(0xCB, 0xA2, 0x58)
GREY  = RGBColor(0x40, 0x40, 0x40)

doc = Document()

# ── Page margins ──────────────────────────────────────────────────────────────
section = doc.sections[0]
section.page_width  = Inches(8.5)
section.page_height = Inches(11)
section.left_margin   = Inches(1)
section.right_margin  = Inches(1)
section.top_margin    = Inches(0.9)
section.bottom_margin = Inches(0.9)

# ── Style helpers ─────────────────────────────────────────────────────────────
def set_run(run, bold=False, size=11, color=GREY, italic=False):
    run.bold   = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.name = 'Calibri'

def heading1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after  = Pt(4)
    r = p.add_run(text)
    set_run(r, bold=True, size=16, color=GREEN)
    return p

def heading2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after  = Pt(2)
    r = p.add_run(text)
    set_run(r, bold=True, size=13, color=DARK)
    return p

def body(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    set_run(r, size=11)
    return p

def bullet(text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(2)
    if bold_prefix:
        r = p.add_run(bold_prefix + ' ')
        set_run(r, bold=True, size=11, color=DARK)
    r2 = p.add_run(text)
    set_run(r2, size=11)
    return p

def add_chart(filename, width=6.0, caption=None):
    path = CHARTS / filename
    if path.exists():
        doc.add_picture(str(path), width=Inches(width))
        last = doc.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if caption:
            cp = doc.add_paragraph(caption)
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.space_after = Pt(8)
            cr = cp.runs[0]
            set_run(cr, italic=True, size=9, color=RGBColor(0x88,0x88,0x88))

def shade_cell(cell, hex_color):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:fill'), hex_color)
    shd.set(qn('w:val'),  'clear')
    tcPr.append(shd)

def add_table(headers, rows, col_widths=None):
    t = doc.add_table(rows=1+len(rows), cols=len(headers))
    t.style = 'Table Grid'
    # header row
    hdr = t.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        shade_cell(cell, '1E3932')
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(10)
        r.font.name = 'Calibri'
    # data rows
    for ri, row in enumerate(rows):
        tr = t.rows[ri+1]
        bg = 'D4E9E2' if ri % 2 == 0 else 'FFFFFF'
        for ci, val in enumerate(row):
            cell = tr.cells[ci]
            shade_cell(cell, bg)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(val))
            r.font.size = Pt(10)
            r.font.name = 'Calibri'
            r.font.color.rgb = GREY
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in t.rows:
                row.cells[i].width = Inches(w)
    doc.add_paragraph()
    return t

# ══════════════════════════════════════════════════════════════════════════════
#  COVER
# ══════════════════════════════════════════════════════════════════════════════
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(40)
r = p.add_run('Starbucks Rewards Program')
set_run(r, bold=True, size=26, color=GREEN)

p2 = doc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = p2.add_run('Customer Analytics Report')
set_run(r2, bold=True, size=18, color=DARK)

p3 = doc.add_paragraph()
p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
p3.paragraph_format.space_before = Pt(6)
r3 = p3.add_run('End-to-End Analysis: Segmentation · A/B Testing · CLV · Funnel · Channel Performance')
set_run(r3, italic=True, size=12, color=GREY)

doc.add_paragraph()
p4 = doc.add_paragraph()
p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
r4 = p4.add_run('Venkat Kowshik  |  May 2026  |  University of Washington — Foster MSBA')
set_run(r4, size=11, color=GREY)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
#  1. EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
heading1('1. Executive Summary')
body(
    'This project analyses the Starbucks Rewards mobile app dataset — a simulated '
    'representation of real customer behaviour during a 30-day promotional campaign. '
    'The study covers 17,000 loyalty members, 306,534 app events, and 10 distinct offers '
    '(BOGO, Discount, Informational) delivered across four channels: Email, Mobile App, '
    'Web, and Facebook / Instagram Ads. The goal is to answer three business questions:'
)
bullet('Which customer segments drive the most value and how should they be treated differently?')
bullet('Do BOGO offers outperform Discount offers — and at what cost?')
bullet('Which channels deliver the best conversion and return on ad spend (ROAS)?')

doc.add_paragraph()
body('Key headline findings:')
bullet('Champions (2% of customers) generate 14.7% of total revenue; High Spenders (31%) drive 46.6%.', bold_prefix='Segmentation:')
bullet('Discount offers win — 62.5% conversion vs 55.5% for BOGO, with 26% lower CPA ($0.86 vs $1.15) and 26% higher ROAS (178× vs 142×).', bold_prefix='A/B Test:')
bullet('Facebook / Instagram Ads deliver the highest average spend per conversion ($111) but the highest CPA ($1.26). Web delivers the lowest CPA ($0.96).', bold_prefix='Channels:')
bullet('Offer funnel drops 44% from receipt to completion — BOGO is viewed more (83%) but completed less than Discount (51% vs 59%).', bold_prefix='Funnel:')

# ══════════════════════════════════════════════════════════════════════════════
#  2. DATA OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
heading1('2. Dataset Overview')

heading2('2.1 Source')
body(
    'Starbucks Rewards Mobile App Simulation Dataset (Udacity / Starbucks Capstone). '
    'Three raw JSON files were merged and cleaned to build the analysis pipeline.'
)

add_table(
    ['File', 'Records', 'Key Fields'],
    [
        ['portfolio.json', '10 offers', 'offer_id, offer_type, difficulty, reward, duration, channels'],
        ['profile.json',   '17,000 customers', 'customer_id, age, income, gender, became_member_on'],
        ['transcript.json','306,534 events',   'customer_id, event, time (hrs), value (nested dict)'],
    ],
    col_widths=[1.8, 1.4, 3.8]
)

heading2('2.2 Data Cleaning')
bullet('2,508 customers with placeholder age = 118 were set to NaN (along with their income) — these are customers who did not share demographic data.')
bullet('became_member_on converted from YYYYMMDD integer to datetime.')
bullet('Nested value dict in transcript unpacked: offer_id, amount, and reward extracted as separate columns.')
bullet('offer_id key appears as both "offer id" (with space) and "offer_id" (underscore) — both handled.')
bullet('"social" channel renamed to "facebook_ads" to reflect actual platform.')
bullet('14,492 customers retained after cleaning (85% of original 17,000).')

heading2('2.3 Customer Demographics')
add_chart('01_demographics.png', width=6.2,
          caption='Fig 1. Customer demographics — age distribution, income distribution, gender split, membership tenure')

add_table(
    ['Metric', 'Value'],
    [
        ['Total customers (cleaned)', '14,492'],
        ['Average age', '54.3 years (range: 18–101)'],
        ['Median income', '$63,000 (range: $30K–$120K)'],
        ['Gender split', 'Male 57% · Female 41% · Other 2%'],
        ['Average membership tenure', '~3.5 years'],
    ],
    col_widths=[2.8, 4.2]
)

# ══════════════════════════════════════════════════════════════════════════════
#  3. CUSTOMER SEGMENTATION
# ══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
heading1('3. Customer Segmentation')

heading2('3.1 RFM Analysis')
body(
    'Every customer was scored on three dimensions calculated over the 30-day observation window. '
    'Each dimension was binned into quintiles (1 = worst, 5 = best) and customers were grouped '
    'into five named RFM segments.'
)

add_table(
    ['Dimension', 'Formula', 'Interpretation'],
    [
        ['Recency (R)',   'max(0, 30 − days_since_last_purchase)', 'Higher = purchased more recently'],
        ['Frequency (F)', 'Count of transaction events',           'Higher = buys more often'],
        ['Monetary (M)',  'Sum of all transaction amounts ($)',     'Higher = spends more'],
    ],
    col_widths=[1.5, 3.0, 2.5]
)

doc.add_paragraph()
add_table(
    ['RFM Segment', 'Customers', 'Share', 'Profile'],
    [
        ['Champions',          '2,673', '18.4%', 'Recent, frequent, high-spend — brand advocates'],
        ['Loyal Customers',    '4,712', '32.5%', 'Regular purchasers, moderate spend'],
        ['Potential Loyalists','3,944', '27.2%', 'Recent but not yet high-frequency'],
        ['At Risk',            '2,020', '13.9%', 'Were good customers, declining recency'],
        ['Lost',               '1,143',  '7.9%', 'Low on all three dimensions'],
    ],
    col_widths=[1.8, 1.0, 0.7, 3.5]
)

add_chart('06_rfm_segments.png', width=5.8,
          caption='Fig 2. RFM segment distribution')
add_chart('05_rfm_distributions.png', width=6.0,
          caption='Fig 3. Distribution of Recency, Frequency, and Monetary values')

heading2('3.2 K-Means Clustering')
body(
    'K-Means clustering was applied to standardised RFM + demographic features to discover '
    'behavioural segments that go beyond rule-based RFM bins. The optimal K was selected '
    'using the Elbow Method and Silhouette Score.'
)

add_chart('07_kmeans_selection.png', width=5.5,
          caption='Fig 4. Elbow curve and Silhouette Score — K=4 selected as optimal')

body('The four clusters were auto-labelled by descending average monetary spend:')

add_table(
    ['Cluster', 'Label', 'Customers', 'Avg Spend ($)', 'Avg Frequency', 'Avg Income ($)', 'Avg Age'],
    [
        ['1', 'Champions',         '289',   '$776',  '10.6', '$76,069', '57'],
        ['2', 'High Spenders',    '4,532',  '$156',   '7.3', '$85,329', '66'],
        ['3', 'Frequent Visitors','3,273',  '$144',  '15.7', '$52,089', '48'],
        ['4', 'Casual Shoppers',  '1,885',   '$61',   '4.0', '$72,392', '60'],
    ],
    col_widths=[0.6, 1.7, 1.0, 1.2, 1.2, 1.3, 0.7]
)

add_chart('08_segment_profiles.png', width=6.0,
          caption='Fig 5. Segment profile comparison across key metrics')
add_chart('09_segment_scatter.png', width=5.8,
          caption='Fig 6. Frequency vs Monetary scatter — coloured by segment')

heading2('3.3 Key Segment Insights')
bullet('Champions are the smallest group (289 customers, 2%) but spend 5× the average — they should receive exclusive early access offers, not generic discounts.')
bullet('High Spenders have the highest income ($85K avg) but the highest average age (66). They prefer Discount offers and respond well to email channels.')
bullet('Frequent Visitors visit the most (avg 15.7 transactions) but spend only $144. Upsell strategies (bundle offers, add-ons) can convert frequency into monetary value.')
bullet('Casual Shoppers are at risk of churn — low recency, low frequency. Re-engagement BOGO offers with a short expiry window are recommended.')

# ══════════════════════════════════════════════════════════════════════════════
#  4. CUSTOMER LIFETIME VALUE (CLV)
# ══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
heading1('4. Customer Lifetime Value (CLV)')

heading2('4.1 Methodology')
body(
    'CLV was projected using a simplified annual model. Monthly spend was estimated from the '
    '30-day observation window and annualised. This gives a conservative first-year CLV baseline '
    'that can be scaled with retention rate assumptions.'
)
body('Formula:  Annual CLV = (Total Spend ÷ 1 month) × 12')

heading2('4.2 CLV by Segment')
add_table(
    ['Segment', 'Customers', 'Avg Annual CLV', 'Total Segment Value', 'Revenue Share'],
    [
        ['Champions',         '289',   '$9,312',  '$2,691,194',  '14.7%'],
        ['High Spenders',    '4,532',  '$1,877',  '$8,505,808',  '46.6%'],
        ['Frequent Visitors','3,273',  '$1,733',  '$5,671,424',  '31.1%'],
        ['Casual Shoppers',  '1,885',    '$736',  '$1,387,073',   '7.6%'],
    ],
    col_widths=[1.8, 1.0, 1.5, 1.8, 1.2]
)

add_chart('10_clv.png', width=6.0,
          caption='Fig 7. CLV by segment — average annual CLV and revenue share')

heading2('4.3 Interpretation')
bullet('Total projected annual revenue pool: $18.26 million across 14,492 active customers.')
bullet('Champions have 12.6× the CLV of Casual Shoppers — justifying significantly higher acquisition and retention spend per customer.')
bullet('High Spenders represent the largest absolute revenue pool ($8.5M, 46.6%) despite having lower individual CLV than Champions — this segment should receive the highest retention investment in absolute dollar terms.')
bullet('Frequent Visitors (31.1% share) are the growth opportunity — existing engagement habits mean small incremental spend increases yield large revenue gains.')

# ══════════════════════════════════════════════════════════════════════════════
#  5. A/B TESTING: BOGO vs DISCOUNT
# ══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
heading1('5. A/B Testing — BOGO vs. Discount Offers')

heading2('5.1 Test Design')
add_table(
    ['Attribute', 'BOGO', 'Discount'],
    [
        ['Sample size',          '30,499 customers',     '30,543 customers'],
        ['Offer mechanics',      'Buy X, get one free',  'Spend X, save Y amount'],
        ['Channels used',        'Email, Mobile, Social, Web', 'Email, Mobile, Social, Web'],
        ['Avg delivery cost',    '$0.64 per customer',   '$0.54 per customer'],
        ['Observation window',   '30 days',              '30 days'],
    ],
    col_widths=[2.0, 2.5, 2.5]
)

heading2('5.2 Statistical Tests')
body('Two independent statistical tests were run to evaluate significance:')

add_table(
    ['Test', 'What It Measures', 'Result', 'p-value', 'Conclusion'],
    [
        ['Chi-Square Test', 'Conversion rate difference',
         'BOGO 55.5% vs Discount 62.5%', 'p < 0.001', 'Statistically significant ✓'],
        ["Welch's t-Test", 'Average spend difference',
         'BOGO $107.82 vs Discount $108.43', 'p < 0.05', 'Marginal difference'],
    ],
    col_widths=[1.4, 1.8, 2.0, 0.9, 1.6]
)

heading2('5.3 Results')
add_table(
    ['Metric', 'BOGO', 'Discount', 'Winner'],
    [
        ['Conversion Rate',              '55.5%',   '62.5%',   'Discount (+7pp)'],
        ['Avg Spend per Customer',       '$107.82', '$108.43', 'Discount (marginal)'],
        ['Total Delivery Cost',          '$19,412', '$16,401', 'Discount (cheaper)'],
        ['Cost Per Acquisition (CPA)',   '$1.15',   '$0.86',   'Discount (−25%)'],
        ['Avg Revenue per Conversion',   '$162.86', '$153.44', 'BOGO (+6%)'],
        ['ROAS',                         '142×',    '178×',    'Discount (+26%)'],
    ],
    col_widths=[2.4, 1.4, 1.4, 2.0]
)

add_chart('11_ab_test_results.png', width=6.0,
          caption='Fig 8. A/B Test — Conversion Rate, Avg Spend, CPA, and ROAS comparison')

heading2('5.4 Interpretation')
bullet('Discount is the clear overall winner: higher conversion, lower cost, and 26% better ROAS.')
bullet('BOGO produces slightly higher revenue-per-conversion ($162 vs $153) — useful for high-value segment targeting where absolute spend matters more than conversion volume.')
bullet('Recommendation: Run Discount as the default mass-market offer. Reserve BOGO for Champions and High Spenders where the higher individual transaction value justifies the higher cost.')
bullet('Informational offers (no reward) achieved zero completions by definition but generated $102.23 avg spend — proving that regular non-incentive communications still drive purchases.')

# ══════════════════════════════════════════════════════════════════════════════
#  6. FUNNEL ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
heading1('6. Offer Funnel Analysis')

heading2('6.1 Funnel Stages')
body(
    'The offer lifecycle has three trackable events in the app data: '
    'Received (offer delivered to customer), Viewed (customer opened the offer), '
    'Completed (customer met the spend threshold within the offer window).'
)

add_chart('04_funnel.png', width=6.0,
          caption='Fig 9. Offer funnel — Received → Viewed → Completed by offer type')

heading2('6.2 Funnel Metrics by Offer Type')
add_table(
    ['Offer Type', 'Received', 'Viewed', 'View Rate', 'Completed', 'Completion Rate', 'Overall Rate'],
    [
        ['BOGO',          '30,499', '25,449', '83.4%', '15,669', '61.6%', '51.4%'],
        ['Discount',      '30,543', '21,445', '70.2%', '17,910', '83.5%', '58.6%'],
        ['Informational', '15,235', '10,831', '71.1%',      '—',     '—',     '—'],
    ],
    col_widths=[1.5, 1.0, 0.9, 1.0, 1.1, 1.4, 1.2]
)

heading2('6.3 Funnel Observations')
bullet('BOGO has a higher view rate (83.4% vs 70.2%) — customers notice and open it more often, likely due to the "free item" framing being more attention-grabbing.')
bullet('Despite being viewed more, BOGO has a lower completion rate (61.6% vs 83.5%) — the "buy X" requirement creates a higher action barrier than "spend X, save Y" which feels more passive.')
bullet('Discount has the better end-to-end funnel efficiency (58.6% overall vs 51.4%) despite lower top-of-funnel awareness.')
bullet('38,065 offers were sent via Facebook/Instagram Ads — those customers show the highest avg spend ($111), suggesting paid social attracts higher-intent customers.')
bullet('Funnel drop from View to Complete (BOGO): 38.4% — this is the primary optimisation lever. Simplifying BOGO redemption mechanics or reducing the minimum purchase requirement could recover significant conversions.')

# ══════════════════════════════════════════════════════════════════════════════
#  7. CHANNEL PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
heading1('7. Channel Performance')

heading2('7.1 Channel Cost Model')
body('Delivery cost was assigned per send based on standard digital marketing benchmarks:')

add_table(
    ['Channel', 'Cost per Send', 'Rationale'],
    [
        ['Email',                    '$0.10', 'ESP cost per email (Mailchimp / Salesforce tier)'],
        ['Mobile App Push',          '$0.05', 'Near-zero marginal cost for owned channel'],
        ['Facebook / Instagram Ads', '$0.50', 'Paid social CPM equivalent'],
        ['Web Banner',               '$0.15', 'Retargeting / display ad CPM'],
    ],
    col_widths=[2.0, 1.2, 3.8]
)

heading2('7.2 Channel Results')
add_table(
    ['Channel', 'Sends', 'Conversions', 'Conv Rate', 'Avg Spend', 'CPA'],
    [
        ['Facebook / Instagram Ads', '38,065', '23,213', '61.0%', '$111.02', '$1.26'],
        ['Mobile App',               '53,374', '32,301', '60.5%', '$108.86', '$1.05'],
        ['Web',                      '53,384', '32,064', '60.1%', '$107.62', '$0.96'],
        ['Email',                    '61,042', '35,997', '59.0%', '$108.12', '$0.99'],
    ],
    col_widths=[2.2, 0.9, 1.2, 1.0, 1.2, 0.8]
)

add_chart('12_channel_performance.png', width=6.0,
          caption='Fig 10. Channel performance — Conversion Rate, Avg Spend, and CPA')
add_chart('13_roi_summary.png', width=6.0,
          caption='Fig 11. ROI and ROAS summary across offer types and channels')

heading2('7.3 Channel Recommendations')
bullet('Web is the most cost-efficient channel (CPA $0.96) for volume campaigns — use it for Discount offers targeting Frequent Visitors and Loyal Customers.')
bullet('Facebook / Instagram Ads drive the highest average transaction value ($111) and should be reserved for Champions and High Spender re-targeting where premium acquisition cost is justified.')
bullet('Mobile App push is the second-cheapest channel ($0.05/send) — ideal for time-sensitive offers and flash promotions with near-zero incremental cost.')
bullet('Email has the highest send volume (61,042) and solid conversion (59%) at low cost ($0.99 CPA) — the workhorse channel for broad-based campaigns.')

# ══════════════════════════════════════════════════════════════════════════════
#  8. STRATEGIC RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
heading1('8. Strategic Recommendations')

add_table(
    ['Segment', 'Recommended Offer', 'Channel', 'Rationale'],
    [
        ['Champions',          'BOGO (exclusive, high-value)',         'Facebook Ads + Mobile', "Highest CLV; BOGO's higher revenue-per-conversion maximises yield"],
        ['High Spenders',      'Discount (moderate difficulty)',       'Email + Web',           'High income, prefer simplicity; Discount drives 26% better ROAS'],
        ['Frequent Visitors',  'Discount + bundle upsell',             'Mobile + Web',          'Already engaged; incremental spend nudge converts frequency to $'],
        ['Casual Shoppers',    'BOGO (low threshold, short window)',   'Email + Mobile',        'Needs urgency trigger; BOGO attention-grab good for re-engagement'],
        ['At Risk / Lost',     'Win-back Discount (deep save)',        'Email',                 'Low-cost channel for uncertain-return segment; test before scaling'],
    ],
    col_widths=[1.5, 2.0, 1.6, 2.2]
)

doc.add_paragraph()
heading2('Prioritised Actions')
bullet('Shift default mass-market offer from BOGO to Discount — saves ~$3,000 per 30-day campaign cycle in delivery cost alone while increasing conversions by 7pp.', bold_prefix='1.')
bullet('Invest Facebook/Instagram budget in Champions re-targeting — their $9,312 annual CLV justifies the $1.26 CPA (CLV:CPA ratio > 7,000×).', bold_prefix='2.')
bullet('Address BOGO funnel drop (View → Complete gap of 38%) by A/B testing lower minimum purchase thresholds — a 5pp improvement in completion would add ~1,500 conversions per campaign.', bold_prefix='3.')
bullet('Build a churn-prediction model on the At Risk segment (2,020 customers representing ~$1.8M potential revenue) using RFM decay signals as early warning features.', bold_prefix='4.')

# ══════════════════════════════════════════════════════════════════════════════
#  9. METHODOLOGY APPENDIX
# ══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
heading1('9. Methodology Appendix')

heading2('Statistical Tests Used')
add_table(
    ['Test', 'Applied To', 'Why'],
    [
        ['Chi-Square (χ²)',    'BOGO vs Discount conversion rates',  'Tests independence between offer type and binary conversion outcome'],
        ["Welch's t-test",     'BOGO vs Discount average spend',     'Compares means of two independent samples without assuming equal variance'],
        ['K-Means Clustering', 'RFM + demographic features',         'Groups customers into behavioural clusters without requiring pre-labelled data'],
        ['Elbow + Silhouette', 'Optimal K selection',                'Elbow finds diminishing inertia returns; Silhouette confirms cluster separation quality'],
        ['RFM Quintile Bins',  'R / F / M scores 1–5',              'Robust to outliers; quintile binning distributes customers evenly across score levels'],
    ],
    col_widths=[1.5, 2.2, 3.3]
)

heading2('Tools & Libraries')
add_table(
    ['Tool', 'Purpose'],
    [
        ['Python 3.11',               'Core analysis and pipeline'],
        ['pandas / NumPy',            'Data manipulation and cleaning'],
        ['scikit-learn',              'K-Means clustering, StandardScaler'],
        ['scipy.stats',               'Chi-Square and Welch t-test'],
        ['matplotlib / seaborn',      'Static chart generation (13 charts)'],
        ['Plotly / Streamlit',        'Interactive dashboard (6-page web app)'],
        ['Tableau Public 2026.1.1',   'Customer Segmentation and A/B Test dashboards'],
        ['Power BI',                  'Supporting data exports (7 clean CSVs)'],
    ],
    col_widths=[2.2, 4.8]
)

# ── Save ──────────────────────────────────────────────────────────────────────
out = BASE / 'Starbucks_Analytics_Report.docx'
doc.save(str(out))
print(f'✅ Report saved: {out}')
