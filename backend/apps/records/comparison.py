"""多次测评结果对比：自动生成改善/恶化标签与提醒。"""


def compare_records(prev, curr):
    """对比前后两次测评记录，返回变化标签与各因子趋势。"""
    if prev is None or curr is None:
        return None

    factor_fields = [
        ('som_score', '躯体化'), ('oc_score', '强迫症状'), ('is_score', '人际敏感'),
        ('dep_score', '抑郁'), ('anx_score', '焦虑'), ('hos_score', '敌对'),
        ('phob_score', '恐怖'), ('par_score', '偏执'), ('psy_score', '精神病性'),
    ]

    delta_gsi = round(curr.gsi - prev.gsi, 2)
    delta_total = curr.total_sum - prev.total_sum

    factor_changes = []
    improved = 0
    worsened = 0
    for field, name in factor_fields:
        prev_v = getattr(prev, field) or 0
        curr_v = getattr(curr, field) or 0
        delta = round(curr_v - prev_v, 2)
        if delta < -0.1:
            trend = 'improved'
            improved += 1
        elif delta > 0.1:
            trend = 'worsened'
            worsened += 1
        else:
            trend = 'stable'
        factor_changes.append({
            'name': name, 'field': field,
            'prev': prev_v, 'curr': curr_v, 'delta': delta, 'trend': trend,
        })

    risk_order = {'green': 0, 'yellow': 1, 'red': 2}
    risk_delta = risk_order.get(curr.overall_risk, 0) - risk_order.get(prev.overall_risk, 0)

    if delta_gsi <= -0.2 or risk_delta < 0:
        overall_tag = 'improved'
        overall_label = '改善'
        reminder = '相较上次测评，症状整体有所好转，请继续保持，建议定期复查。'
    elif delta_gsi >= 0.2 or risk_delta > 0:
        overall_tag = 'worsened'
        overall_label = '恶化'
        reminder = '相较上次测评，症状有所加重，建议尽快寻求专业评估或复诊。'
    else:
        overall_tag = 'stable'
        overall_label = '稳定'
        reminder = '相较上次测评，症状基本稳定，建议保持观察并定期复查。'

    return {
        'overall_tag': overall_tag,
        'overall_label': overall_label,
        'reminder': reminder,
        'delta_gsi': delta_gsi,
        'delta_total': delta_total,
        'prev_risk': prev.overall_risk,
        'curr_risk': curr.overall_risk,
        'risk_delta': risk_delta,
        'improved_count': improved,
        'worsened_count': worsened,
        'factor_changes': factor_changes,
        'prev_created_at': prev.created_at,
        'curr_created_at': curr.created_at,
    }
