from django.core.management.base import BaseCommand
from apps.questionnaire.models import SubScale, SubScaleQuestion
from apps.questionnaire.scl90_data import SUBSCALES, SUBSCALE_QUESTIONS


class Command(BaseCommand):
    help = '初始化自适应子量表（PHQ-9 / GAD-7）题目数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化子量表数据...')
        scale_count = 0
        q_count = 0
        for sub in SUBSCALES:
            obj, created = SubScale.objects.update_or_create(
                code=sub['code'],
                defaults={
                    'name': sub['name'],
                    'trigger_factor': sub['trigger_factor'],
                    'description': sub['description'],
                    'max_score': sub['max_score'],
                }
            )
            if created:
                scale_count += 1
            for num, content in SUBSCALE_QUESTIONS.get(sub['code'], []):
                _, c = SubScaleQuestion.objects.update_or_create(
                    scale=obj, number=num,
                    defaults={'content': content}
                )
                if c:
                    q_count += 1
        self.stdout.write(self.style.SUCCESS(
            f'子量表完成：新增 {scale_count} 个量表，{q_count} 道题目'
        ))
