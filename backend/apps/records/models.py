from django.db import models
from django.conf import settings


class AssessmentRecord(models.Model):
    RISK_CHOICES = [
        ('green', '正常（绿）'),
        ('yellow', '轻度（黄）'),
        ('red', '中度及以上（红）'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assessment_records',
        verbose_name='用户'
    )

    som_score = models.FloatField('躯体化因子分', default=0)
    oc_score = models.FloatField('强迫症状因子分', default=0)
    is_score = models.FloatField('人际关系敏感因子分', default=0)
    dep_score = models.FloatField('抑郁因子分', default=0)
    anx_score = models.FloatField('焦虑因子分', default=0)
    hos_score = models.FloatField('敌对因子分', default=0)
    phob_score = models.FloatField('恐怖因子分', default=0)
    par_score = models.FloatField('偏执因子分', default=0)
    psy_score = models.FloatField('精神病性因子分', default=0)
    oth_score = models.FloatField('其他因子分', default=0)

    gsi = models.FloatField('总症状指数(GSI)', default=0)
    positive_count = models.IntegerField('阳性项目数', default=0)
    positive_avg = models.FloatField('阳性症状均分', default=0)
    total_sum = models.IntegerField('总分', default=0)

    overall_risk = models.CharField(
        '整体风险等级',
        max_length=10,
        choices=RISK_CHOICES,
        default='green'
    )

    answers_json = models.JSONField('答案详情', default=dict)
    factors_detail = models.JSONField('因子与常模对比详情', default=dict)

    created_at = models.DateTimeField('测评时间', auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'scl90_assessment_record'
        verbose_name = '测评记录'
        verbose_name_plural = '测评记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.phone} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'

    def get_factor_scores_dict(self):
        return {
            'SOM': self.som_score,
            'O-C': self.oc_score,
            'I-S': self.is_score,
            'DEP': self.dep_score,
            'ANX': self.anx_score,
            'HOS': self.hos_score,
            'PHOB': self.phob_score,
            'PAR': self.par_score,
            'PSY': self.psy_score,
            'OTH': self.oth_score,
        }

    def save(self, *args, **kwargs):
        factor_scores = self.get_factor_scores_dict()
        red_count = sum(1 for detail in (self.factors_detail or {}).values()
                        if detail.get('risk_level') == 'red')
        yellow_count = sum(1 for detail in (self.factors_detail or {}).values()
                           if detail.get('risk_level') == 'yellow')
        if red_count > 0 or self.gsi >= 3:
            self.overall_risk = 'red'
        elif yellow_count > 0 or self.gsi >= 2:
            self.overall_risk = 'yellow'
        else:
            self.overall_risk = 'green'
        super().save(*args, **kwargs)
