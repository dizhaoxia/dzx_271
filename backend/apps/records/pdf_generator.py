"""使用 reportlab 生成 PDF 格式的详细测评报告。"""
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from apps.accounts.serializers import mask_phone
from .comparison import compare_records


RISK_LABEL = {'green': '正常（低风险）', 'yellow': '轻度异常', 'red': '中度及以上'}
RISK_COLOR = {'green': colors.HexColor('#67c23a'), 'yellow': colors.HexColor('#e6a23c'), 'red': colors.HexColor('#f56c6c')}
FACTOR_FIELDS = [
    ('som_score', '躯体化'), ('oc_score', '强迫症状'), ('is_score', '人际敏感'),
    ('dep_score', '抑郁'), ('anx_score', '焦虑'), ('hos_score', '敌对'),
    ('phob_score', '恐怖'), ('par_score', '偏执'), ('psy_score', '精神病性'),
    ('oth_score', '其他'),
]


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ZhTitle', parent=styles['Title'],
                             fontName='Helvetica-Bold', fontSize=20, alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle(name='ZhSub', parent=styles['Normal'],
                             fontSize=10, alignment=TA_CENTER, textColor=colors.grey, spaceAfter=10))
    styles.add(ParagraphStyle(name='ZhH2', parent=styles['Heading2'],
                             fontSize=14, spaceBefore=14, spaceAfter=6, textColor=colors.HexColor('#303133')))
    styles.add(ParagraphStyle(name='ZhBody', parent=styles['Normal'],
                             fontSize=10.5, leading=16, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='ZhSmall', parent=styles['Normal'],
                             fontSize=9, textColor=colors.grey, leading=13))
    styles.add(ParagraphStyle(name='ZhWarn', parent=styles['Normal'],
                             fontSize=10.5, leading=16, textColor=colors.HexColor('#d9001b')))
    return styles


def _factor_table(record):
    styles = _styles()
    header = ['因子', '得分', '常模(均值±SD)', '状态', '风险']
    rows = [header]
    for field, name in FACTOR_FIELDS:
        d = (record.factors_detail or {}).get(_factor_code(field), {}) if record.factors_detail else {}
        score = getattr(record, field, 0)
        norm_mean = d.get('norm_mean', '-')
        norm_std = d.get('norm_std', '-')
        status = d.get('status', '-')
        risk = d.get('risk_level', '')
        risk_text = {'green': '正常', 'yellow': '轻度', 'red': '中度+'}.get(risk, '-')
        rows.append([name, f'{score}', f'{norm_mean} ± {norm_std}', status, risk_text])
    t = Table(rows, colWidths=[28 * mm, 18 * mm, 34 * mm, 22 * mm, 22 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#409eff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9.5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dcdfe6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f7fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def _factor_code(field):
    return {
        'som_score': 'SOM', 'oc_score': 'O-C', 'is_score': 'I-S', 'dep_score': 'DEP',
        'anx_score': 'ANX', 'hos_score': 'HOS', 'phob_score': 'PHOB', 'par_score': 'PAR',
        'psy_score': 'PSY', 'oth_score': 'OTH',
    }.get(field, '')


def _interpretation(record):
    parts = []
    risk = record.overall_risk
    if risk == 'green':
        parts.append('本次测评各项指标总体处于正常范围，未见明显心理健康问题。建议保持健康生活方式，定期复查。')
    elif risk == 'yellow':
        parts.append('本次测评存在轻度异常因子，提示可能存在轻度心理不适。建议加强自我调节、规律运动、改善睡眠，必要时寻求心理咨询。')
    else:
        parts.append('本次测评存在中度及以上异常因子，症状较为明显。建议尽快前往专业心理/精神卫生机构进行面诊评估，必要时接受药物或心理治疗。')

    elevated = []
    for field, name in FACTOR_FIELDS:
        d = (record.factors_detail or {}).get(_factor_code(field), {})
        if d.get('risk_level') in ('yellow', 'red'):
            elevated.append(f'{name}（{d.get("score", 0)}分）')
    if elevated:
        parts.append('需关注的因子：' + '、'.join(elevated) + '。')
    return parts


def _guidance(record):
    guidance = []
    if record.overall_risk in ('yellow', 'red'):
        guidance.append('【就医指引】 建议前往当地精神卫生中心或综合医院心理科就诊，由专业医生进一步评估。')
        guidance.append('【心理援助】 可拨打全国心理援助热线（如：北京 010-82951332）或当地心理危机干预热线获取帮助。')
    if record.overall_risk == 'red':
        guidance.append('【安全提醒】 若出现自伤、自杀念头或冲动，请立即联系亲友、拨打 120 或前往最近的急诊就医，切勿独处。')
    guidance.append('【日常调节】 保持规律作息与适度运动，建立良好社会支持系统，学习放松与情绪管理技巧。')
    return guidance


def generate_report_pdf(record, prev_record=None, professional_view=False):
    """生成测评报告 PDF，返回 BytesIO。"""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=16 * mm,
                            title='SCL-90 心理健康测评报告')
    styles = _styles()
    flow = []

    flow.append(Paragraph('SCL-90 心理健康测评报告', styles['ZhTitle']))
    phone = mask_phone(record.user.phone) if not professional_view else record.user.phone
    flow.append(Paragraph(
        f'报告编号：#{record.id} &nbsp;&nbsp; 测评时间：{record.created_at:%Y-%m-%d %H:%M} &nbsp;&nbsp; '
        f'用户：{record.user.username}（{phone}）',
        styles['ZhSub']))
    flow.append(HRFlowable(width='100%', color=colors.HexColor('#dcdfe6')))

    flow.append(Paragraph('一、测评概览', styles['ZhH2']))
    risk_text = RISK_LABEL.get(record.overall_risk, record.overall_risk)
    overview = [
        ['整体风险等级', risk_text],
        ['总症状指数 (GSI)', f'{record.gsi}'],
        ['总分', f'{record.total_sum}'],
        ['阳性项目数', f'{record.positive_count}'],
        ['阳性症状均分', f'{record.positive_avg}'],
        ['作答题数', f'{record.answered_count}（{"自适应" if record.mode == "adaptive" else "经典90题"}）'],
    ]
    t = Table(overview, colWidths=[50 * mm, 60 * mm])
    t.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10.5),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f7fa')),
        ('TEXTCOLOR', (1, 0), (1, 0), RISK_COLOR.get(record.overall_risk, colors.black)),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dcdfe6')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    flow.append(t)
    flow.append(Spacer(1, 6))

    flow.append(Paragraph('二、因子分与常模对比', styles['ZhH2']))
    flow.append(_factor_table(record))

    if record.subscale_records.exists():
        flow.append(Spacer(1, 8))
        flow.append(Paragraph('三、自适应子量表结果', styles['ZhH2']))
        sub_rows = [['量表', '得分', '严重度', '建议']]
        for sr in record.subscale_records.all():
            sub_rows.append([sr.scale_name or sr.scale_code,
                             f'{sr.total_score}/{sr.max_score}',
                             sr.severity_label or sr.severity,
                             sr.advice[:30] + '…' if len(sr.advice) > 30 else sr.advice])
        st = Table(sub_rows, colWidths=[34 * mm, 20 * mm, 24 * mm, 72 * mm])
        st.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#67c23a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dcdfe6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        flow.append(st)

    section_no = 4 if record.subscale_records.exists() else 3
    flow.append(Paragraph(f'{"四" if section_no == 4 else "三"}.文字解读', styles['ZhH2']))
    for p in _interpretation(record):
        flow.append(Paragraph(p, styles['ZhBody']))

    flow.append(Paragraph(f'{"五" if section_no == 4 else "四"}.就医与心理援助指引', styles['ZhH2']))
    for g in _guidance(record):
        flow.append(Paragraph(g, styles['ZhBody']))

    if prev_record:
        comp = compare_records(prev_record, record)
        if comp:
            flow.append(Paragraph(f'{"六" if section_no == 4 else "五"}.趋势对比', styles['ZhH2']))
            tag = comp['overall_label']
            flow.append(Paragraph(
                f'相较上次测评（{comp["prev_created_at"]:%Y-%m-%d %H:%M}），整体变化趋势：'
                f'<b><font color="{"#67c23a" if comp["overall_tag"]=="improved" else "#f56c6c" if comp["overall_tag"]=="worsened" else "#909399"}">{tag}</font></b>'
                f'（GSI 变化 {comp["delta_gsi"]:+.2f}）。',
                styles['ZhBody']))
            flow.append(Paragraph(comp['reminder'], styles['ZhSmall']))

    flow.append(Spacer(1, 14))
    flow.append(HRFlowable(width='100%', color=colors.HexColor('#dcdfe6')))
    flow.append(Paragraph(
        '免责声明：本报告由 SCL-90 症状自评量表系统自动生成，仅作心理健康自测参考，不能替代专业医疗诊断。'
        '如需确诊或治疗，请前往正规医疗机构就诊。'
        '数据已按隐私合规要求脱敏处理与访问审计。',
        styles['ZhSmall']))

    doc.build(flow)
    buf.seek(0)
    return buf
