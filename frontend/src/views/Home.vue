<template>
  <Layout>
    <div class="page-container">
      <el-card class="card-shadow hero-card mb-24">
        <div class="hero-content">
          <div class="hero-text">
            <h1 class="hero-title">SCL-90 症状自评量表</h1>
            <p class="hero-desc">
              症状自评量表 (Symptom Checklist 90, SCL-90) 是世界上最著名的心理健康测试量表之一，
              包含 90 个项目，从感觉、情感、思维、意识、行为直至生活习惯、人际关系、饮食睡眠等多个角度，
              全面反映您的心理健康状况。
            </p>
            <div class="hero-btns mt-24">
              <el-button type="primary" size="large" @click="$router.push('/questionnaire')">
                <el-icon><EditPen /></el-icon>
                <span>立即测评</span>
              </el-button>
              <el-button size="large" @click="$router.push('/history')">
                <el-icon><HistoryIcon /></el-icon>
                <span>查看历史</span>
              </el-button>
            </div>
          </div>
          <div class="hero-stats">
            <div class="stat-item">
              <div class="stat-num">{{ userInfo?.username?.slice(0, 8) || '欢迎' }}</div>
              <div class="stat-label">当前用户</div>
            </div>
            <div class="stat-item">
              <div class="stat-num">90</div>
              <div class="stat-label">测评题目</div>
            </div>
            <div class="stat-item">
              <div class="stat-num">9</div>
              <div class="stat-label">因子维度</div>
            </div>
            <div class="stat-item">
              <div class="stat-num">5</div>
              <div class="stat-label">评分等级</div>
            </div>
          </div>
        </div>
      </el-card>

      <el-row :gutter="20">
        <el-col :span="8" v-for="f in factorList" :key="f.code" class="mb-16">
          <el-card class="card-shadow factor-card" :body-style="{ padding: '16px' }">
            <div class="factor-head" :style="{ borderLeftColor: f.color }">
              <div class="factor-name">{{ f.name }}</div>
              <div class="factor-sub">{{ f.title }}</div>
            </div>
            <div class="factor-desc">{{ f.desc }}</div>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="card-shadow mt-8">
        <div class="section-title">评分说明</div>
        <el-row :gutter="20">
          <el-col :span="8" v-for="l in levelList" :key="l.level">
            <div :class="['level-card', `risk-${l.level}`]" style="border-radius: 8px; padding: 16px;">
              <div class="level-title">
                <el-icon :size="22" :color="l.iconColor"><component :is="l.icon" /></el-icon>
                <strong>{{ l.title }}</strong>
              </div>
              <div class="level-range mt-8">{{ l.range }}</div>
              <div class="level-desc mt-8">{{ l.desc }}</div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Layout from '@/components/Layout.vue'
import { useAuthStore } from '@/stores/auth'
import { Sunny, Warning, CircleClose, EditPen, Clock as HistoryIcon } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const userInfo = computed(() => authStore.userInfo)

const factorList = [
  { code: 'SOM', name: '躯体化', title: 'Somatization', color: '#f56c6c', desc: '反映身体不适：头痛、胸痛、腰痛、肌肉酸痛、呼吸、消化等系统症状' },
  { code: 'O-C', name: '强迫症状', title: 'Obsessive-Compulsive', color: '#e6a23c', desc: '明知无意义却无法摆脱的无意义思想、冲动、行为，反复检查等' },
  { code: 'I-S', name: '人际关系敏感', title: 'Interpersonal Sensitivity', color: '#e6a23c', desc: '个人不自在感、自卑感，在与他人比较时尤为突出' },
  { code: 'DEP', name: '抑郁', title: 'Depression', color: '#909399', desc: '抑郁情绪、苦闷、情感淡漠、悲观、活动减退、甚至自杀意念' },
  { code: 'ANX', name: '焦虑', title: 'Anxiety', color: '#f56c6c', desc: '烦躁、坐立不安、神经过敏、紧张及由此产生的躯体征象' },
  { code: 'HOS', name: '敌对', title: 'Hostility', color: '#f56c6c', desc: '从思维、情感及行为三方面反映敌对表现：厌烦、争论、摔物等' },
  { code: 'PHOB', name: '恐怖', title: 'Phobic Anxiety', color: '#409eff', desc: '对出门、空旷场所、人群、公共交通等对象的恐惧和焦虑' },
  { code: 'PAR', name: '偏执', title: 'Paranoid Ideation', color: '#e6a23c', desc: '投射性思维、敌对、猜疑、关系观念、被动体验和夸大等' },
  { code: 'PSY', name: '精神病性', title: 'Psychoticism', color: '#909399', desc: '反映精神分裂样症状：幻听、思维播散、被控制感、思维被插入等' },
]

const levelList = [
  {
    level: 'green',
    title: '正常范围 (绿)',
    icon: Sunny,
    iconColor: '#67c23a',
    range: '因子分 ≤ 均值 + 1个标准差',
    desc: '无明显心理问题，建议保持健康生活方式，定期复查。',
  },
  {
    level: 'yellow',
    title: '轻度异常 (黄)',
    icon: Warning,
    iconColor: '#e6a23c',
    range: '均值 + 1SD < 因子分 ≤ 均值 + 2SD',
    desc: '存在轻度症状，建议自我调节、加强锻炼，必要时咨询心理专业人员。',
  },
  {
    level: 'red',
    title: '中度及以上 (红)',
    icon: CircleClose,
    iconColor: '#f56c6c',
    range: '因子分 > 均值 + 2个标准差',
    desc: '症状明显，建议尽快寻求专业心理咨询或就医评估，及时干预。',
  },
]
</script>

<style scoped>
.hero-card { border: none; }
.hero-content { display: flex; gap: 40px; }
.hero-text { flex: 1; }
.hero-title {
  margin: 0 0 12px;
  font-size: 28px;
  background: linear-gradient(90deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.hero-desc { color: #606266; line-height: 1.8; font-size: 14px; margin: 0; }
.hero-btns .el-button + .el-button { margin-left: 12px; }
.hero-stats { width: 280px; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.stat-item {
  background: linear-gradient(135deg, #ecf5ff 0%, #f0f9eb 100%);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}
.stat-num { font-size: 22px; font-weight: 700; color: #303133; }
.stat-label { color: #909399; font-size: 12px; margin-top: 4px; }
.factor-card { height: 100%; }
.factor-head { border-left: 4px solid; padding-left: 12px; }
.factor-name { font-size: 16px; font-weight: 600; color: #303133; }
.factor-sub { font-size: 12px; color: #909399; margin-top: 2px; }
.factor-desc { font-size: 13px; color: #606266; margin-top: 10px; line-height: 1.6; }
.level-title { display: flex; align-items: center; gap: 6px; font-size: 15px; }
.level-range { font-size: 12px; }
.level-desc { font-size: 13px; line-height: 1.6; }
</style>
