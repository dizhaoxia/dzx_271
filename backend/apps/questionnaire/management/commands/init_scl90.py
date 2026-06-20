from django.core.management.base import BaseCommand
from apps.questionnaire.models import Question, NormData
from apps.questionnaire.scl90_data import SCL90_QUESTIONS, NORM_DATA


class Command(BaseCommand):
    help = '初始化SCL-90问卷题目和常模数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化SCL-90问卷数据...')

        question_count = 0
        for num, content, factor in SCL90_QUESTIONS:
            _, created = Question.objects.update_or_create(
                number=num,
                defaults={'content': content, 'factor': factor}
            )
            if created:
                question_count += 1
        self.stdout.write(self.style.SUCCESS(f'题目数据完成：新增 {question_count} 条，共 {len(SCL90_QUESTIONS)} 条'))

        norm_count = 0
        for factor, factor_name, mean, std, desc in NORM_DATA:
            _, created = NormData.objects.update_or_create(
                factor=factor,
                defaults={'factor_name': factor_name, 'mean': mean, 'std': std, 'description': desc}
            )
            if created:
                norm_count += 1
        self.stdout.write(self.style.SUCCESS(f'常模数据完成：新增 {norm_count} 条，共 {len(NORM_DATA)} 条'))

        self.stdout.write(self.style.SUCCESS('SCL-90问卷数据初始化完成！'))
