from django.db import models


class Question(models.Model):
    FACTOR_CHOICES = [
        ('SOM', '躯体化'),
        ('O-C', '强迫症状'),
        ('I-S', '人际关系敏感'),
        ('DEP', '抑郁'),
        ('ANX', '焦虑'),
        ('HOS', '敌对'),
        ('PHOB', '恐怖'),
        ('PAR', '偏执'),
        ('PSY', '精神病性'),
        ('OTH', '其他'),
    ]

    number = models.PositiveIntegerField('题号', unique=True, db_index=True)
    content = models.TextField('题目内容')
    factor = models.CharField('因子', max_length=10, choices=FACTOR_CHOICES, db_index=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'scl90_question'
        verbose_name = '问卷题目'
        verbose_name_plural = '问卷题目'
        ordering = ['number']

    def __str__(self):
        return f'{self.number}. {self.content[:30]}'


class NormData(models.Model):
    factor = models.CharField('因子', max_length=10, unique=True, db_index=True)
    factor_name = models.CharField('因子名称', max_length=50)
    mean = models.FloatField('全国常模均值')
    std = models.FloatField('标准差')
    description = models.TextField('因子说明', blank=True, null=True)

    class Meta:
        db_table = 'scl90_norm'
        verbose_name = '常模数据'
        verbose_name_plural = '常模数据'

    def __str__(self):
        return f'{self.factor_name}: {self.mean}±{self.std}'


class SubScale(models.Model):
    """自适应追加的子量表定义（如 PHQ-9 抑郁、GAD-7 焦虑）。"""
    SCALE_CHOICES = [
        ('PHQ9', 'PHQ-9 抑郁症筛查量表'),
        ('GAD7', 'GAD-7 广泛性焦虑量表'),
    ]
    code = models.CharField('量表代码', max_length=16, unique=True, choices=SCALE_CHOICES, db_index=True)
    name = models.CharField('量表名称', max_length=64)
    trigger_factor = models.CharField(
        '触发因子', max_length=10, blank=True, default='',
        help_text='当 SCL-90 该因子升高时建议追加此量表'
    )
    description = models.TextField('量表说明', blank=True, default='')
    max_score = models.PositiveIntegerField('满分', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'scl90_subscale'
        verbose_name = '子量表'
        verbose_name_plural = '子量表'
        ordering = ['code']

    def __str__(self):
        return f'{self.code} {self.name}'


class SubScaleQuestion(models.Model):
    scale = models.ForeignKey(SubScale, on_delete=models.CASCADE, related_name='questions', verbose_name='量表')
    number = models.PositiveIntegerField('题号', db_index=True)
    content = models.TextField('题目内容')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'scl90_subscale_question'
        verbose_name = '子量表题目'
        verbose_name_plural = '子量表题目'
        ordering = ['number']
        unique_together = ('scale', 'number')

    def __str__(self):
        return f'{self.scale.code}-{self.number}. {self.content[:30]}'
