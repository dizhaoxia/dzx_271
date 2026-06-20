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
