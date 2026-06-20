from django.db import models
from django.conf import settings


class AssessmentSession(models.Model):
    """一次自适应测评会话：串联首轮筛查 + 追加子量表。"""
    MODE_CHOICES = [
        ('classic', '经典90题'),
        ('adaptive', '自适应'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assessment_sessions',
        verbose_name='用户'
    )
    mode = models.CharField('测评模式', max_length=16, choices=MODE_CHOICES, default='classic')
    screening_items_count = models.IntegerField('筛查题数', default=0)
    is_completed = models.BooleanField('是否完成', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)

    class Meta:
        db_table = 'scl90_assessment_session'
        verbose_name = '测评会话'
        verbose_name_plural = '测评会话'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user_id} {self.mode} {self.created_at:%Y-%m-%d %H:%M}'


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
    session = models.ForeignKey(
        AssessmentSession,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='records',
        verbose_name='所属会话'
    )
    mode = models.CharField('测评模式', max_length=16, choices=AssessmentSession.MODE_CHOICES, default='classic')

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
    answered_count = models.IntegerField('作答题数', default=90)

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


class SubScaleRecord(models.Model):
    """自适应追加子量表的作答记录。"""
    SEVERITY_ORDER = ['minimal', 'mild', 'moderate', 'moderately_severe', 'severe']
    record = models.ForeignKey(
        AssessmentRecord,
        on_delete=models.CASCADE,
        related_name='subscale_records',
        verbose_name='关联测评记录'
    )
    scale_code = models.CharField('量表代码', max_length=16, db_index=True)
    scale_name = models.CharField('量表名称', max_length=64, blank=True, default='')
    total_score = models.IntegerField('总分', default=0)
    max_score = models.IntegerField('满分', default=0)
    severity = models.CharField('严重度', max_length=24, blank=True, default='')
    severity_label = models.CharField('严重度标签', max_length=32, blank=True, default='')
    advice = models.TextField('建议', blank=True, default='')
    answers_json = models.JSONField('答案详情', default=dict)
    created_at = models.DateTimeField('记录时间', auto_now_add=True)

    class Meta:
        db_table = 'scl90_subscale_record'
        verbose_name = '子量表记录'
        verbose_name_plural = '子量表记录'
        ordering = ['scale_code']

    def __str__(self):
        return f'{self.scale_code} {self.total_score}/{self.max_score}'


class FollowUpNote(models.Model):
    """专业人员对患者的在线备注与随访记录，形成闭环干预。"""
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followup_notes_received',
        verbose_name='患者'
    )
    professional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='followup_notes_written',
        verbose_name='专业人员'
    )
    record = models.ForeignKey(
        AssessmentRecord,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='followup_notes',
        verbose_name='关联测评记录'
    )
    note = models.TextField('备注内容')
    follow_up_date = models.DateField('随访日期', null=True, blank=True)
    follow_up_type = models.CharField('随访方式', max_length=24, blank=True, default='')
    next_action = models.CharField('下一步计划', max_length=255, blank=True, default='')
    created_at = models.DateTimeField('记录时间', auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'scl90_followup_note'
        verbose_name = '随访备注'
        verbose_name_plural = '随访备注'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.patient_id} <- {self.professional_id} {self.created_at:%Y-%m-%d}'


class PatientAssignment(models.Model):
    """医患分配：将患者分配给医生/咨询师。"""
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignments_as_patient',
        verbose_name='患者'
    )
    professional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignments_as_professional',
        verbose_name='专业人员'
    )
    is_active = models.BooleanField('是否生效', default=True)
    note = models.CharField('分配备注', max_length=255, blank=True, default='')
    created_at = models.DateTimeField('分配时间', auto_now_add=True)

    class Meta:
        db_table = 'scl90_patient_assignment'
        verbose_name = '医患分配'
        verbose_name_plural = '医患分配'
        ordering = ['-created_at']
        unique_together = ('patient', 'professional')

    def __str__(self):
        return f'{self.patient_id} -> {self.professional_id}'
