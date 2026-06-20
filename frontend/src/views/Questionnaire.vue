<template>
  <Layout>
    <div class="page-container">
      <el-card class="card-shadow mb-16" v-loading="loading">

        <div class="q-header">
          <div>
            <h2 class="q-title">SCL-90 自适应测评</h2>
            <div class="q-tip">
              智能问卷：先完成 18 道筛查题，系统将根据您的严重因子动态推送针对性子量表（如 PHQ-9 / GAD-7），题目数量智能缩短。
            </div>
          </div>
          <div class="header-tags">
            <el-tag v-if="!online" type="warning" effect="dark" size="large">
              <el-icon><Cloudy /></el-icon>&nbsp;离线模式 · 已缓存作答
            </el-tag>
            <el-tag v-else type="success" effect="dark" size="large">在线</el-tag>
          </div>
        </div>

        <el-steps :active="stepIndex" align-center finish-status="success" class="flow-steps">
          <el-step title="筛查" description="18 道核心题" />
          <el-step title="子量表" description="动态追加" />
          <el-step title="完成" description="生成报告" />
        </el-steps>

        <el-divider />

        <!-- 进度条 -->
        <div class="progress-wrap">
          <div class="progress-label">
            <span>总进度</span>
            <strong>{{ progress.percent }}%</strong>
            <span class="done-count">(已答 {{ progress.done }} / {{ progress.total }} 题)</span>
          </div>
          <el-progress :percentage="progress.percent" :stroke-width="14" :color="progressColor" :show-text="false" />
        </div>

        <!-- 介绍 -->
        <div v-if="store.step === 'intro'" class="intro-box">
          <el-result icon="info" title="自适应测评说明" sub-title="题目不再固定 90 道，依据首轮回答智能缩短">
            <template #extra>
              <el-button type="primary" size="large" @click="startScreening">
                <el-icon><EditPen /></el-icon>&nbsp;开始筛查
              </el-button>
              <router-link to="/questionnaire-classic" class="classic-link">改做完整 90 题（经典版）</router-link>
            </template>
          </el-result>
        </div>

        <!-- 筛查阶段 -->
        <div v-else-if="store.step === 'screening'">
          <div class="stage-title">
            <el-icon><Aim /></el-icon>&nbsp;第一步 · 核心筛查
            <span class="stage-sub">（共 {{ screeningItems.length }} 题，1-5 级评分）</span>
          </div>
          <div class="legend">
            <span class="legend-title">评分：</span>
            <span v-for="o in sclOptions" :key="o.value" class="legend-chip">
              <b>{{ o.value }}</b> {{ o.label }}
            </span>
          </div>
          <div class="question-list">
            <div
              v-for="(q, idx) in screeningItems"
              :key="q.number"
              :class="['question-item', { 'is-empty': store.screeningAnswers[q.number] == null }]"
            >
              <div class="q-number"><span>{{ idx + 1 }}</span></div>
              <div class="q-content">
                <div class="q-text">{{ q.content }}</div>
                <el-radio-group
                  class="q-options"
                  :model-value="store.screeningAnswers[q.number]"
                  @update:model-value="(v: any) => store.setScreeningAnswer(q.number, Number(v))"
                >
                  <el-radio-button v-for="o in sclOptions" :key="o.value" :label="o.value">{{ o.value }}</el-radio-button>
                </el-radio-group>
              </div>
            </div>
          </div>
          <div class="action-bar">
            <el-button size="large" @click="store.gotoStep('intro')">返回</el-button>
            <el-button type="primary" size="large" :loading="submitting" :disabled="screeningIncomplete" @click="submitScreening">
              <span v-if="hasRecommended">下一步 · 完成子量表</span>
              <span v-else>完成筛查 · 提交</span>
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 子量表阶段 -->
        <div v-else-if="store.step === 'subscales'">
          <el-alert
            v-if="hasRecommended"
            type="info"
            :closable="false"
            show-icon
            class="rec-alert"
            :title="`根据首轮筛查，建议您追加完成 ${store.recommendedSubscales.length} 个针对性子量表，共 ${totalSubQuestions} 题`"
          />
          <el-tabs v-model="activeScale" type="card">
            <el-tab-pane
              v-for="sc in store.recommendedSubscales"
              :key="sc.code"
              :name="sc.code"
            >
              <template #label>
                <span :class="{ 'tab-done': store.missingSubscaleQuestions(sc) === 0 }">
                  {{ sc.name }}
                  <el-tag v-if="store.missingSubscaleQuestions(sc) === 0" type="success" size="small" effect="plain">已完成</el-tag>
                  <el-tag v-else type="warning" size="small" effect="plain">剩 {{ store.missingSubscaleQuestions(sc) }}</el-tag>
                </span>
              </template>
              <div class="scale-desc">{{ sc.description }}（触发因子：{{ factorName(sc.trigger_factor) }} · 得分 {{ sc.trigger_score }}）</div>
              <div class="legend">
                <span class="legend-title">选项：</span>
                <span v-for="o in subOptions" :key="o.value" class="legend-chip">
                  <b>{{ o.value }}</b> {{ o.label }}
                </span>
              </div>
              <div class="question-list">
                <div
                  v-for="(q, idx) in sc.questions"
                  :key="q.number"
                  :class="['question-item', { 'is-empty': (store.subscaleAnswers[sc.code] || {})[q.number] == null }]"
                >
                  <div class="q-number sub"><span>{{ idx + 1 }}</span></div>
                  <div class="q-content">
                    <div class="q-text">{{ q.content }}</div>
                    <el-radio-group
                      class="q-options"
                      :model-value="(store.subscaleAnswers[sc.code] || {})[q.number]"
                      @update:model-value="(v: any) => store.setSubscaleAnswer(sc.code, q.number, Number(v))"
                    >
                      <el-radio-button v-for="o in subOptions" :key="o.value" :label="o.value">{{ o.value }}</el-radio-button>
                    </el-radio-group>
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
          <div class="action-bar">
            <el-button size="large" @click="store.gotoStep('screening')">返回筛查</el-button>
            <el-button type="success" size="large" :loading="store.submitting" :disabled="!store.allSubscalesCompleted" @click="submitSession">
              <el-icon><Check /></el-icon>&nbsp;提交全部测评
            </el-button>
          </div>
        </div>

        <!-- 完成阶段 -->
        <div v-else-if="store.step === 'done'" class="done-box">
          <el-result icon="success" title="测评完成" :sub-title="doneSubTitle">
            <template #extra>
              <el-button type="primary" size="large" @click="goResult">
                <el-icon><Document /></el-icon>&nbsp;查看详细报告
              </el-button>
              <el-button size="large" @click="restart">重新测评</el-button>
            </template>
          </el-result>
          <div v-if="store.sessionResult" class="done-summary">
            <div class="sum-item"><span>GSI 总均分</span><strong :class="riskClass">{{ store.sessionResult.gsi.toFixed(2) }}</strong></div>
            <div class="sum-item"><span>阳性项目数</span><strong>{{ store.sessionResult.positive_count }}</strong></div>
            <div class="sum-item"><span>已完成题数</span><strong>{{ store.sessionResult.answered_count }}</strong></div>
            <div class="sum-item"><span>风险等级</span><strong :class="riskClass">{{ riskLabel }}</strong></div>
          </div>
          <div v-if="store.sessionResult?.comparison" class="trend-tag">
            <el-tag :type="trendTagType" effect="dark" size="large">
              {{ store.sessionResult.comparison.overall_label }}
            </el-tag>
            <span class="trend-reminder">{{ store.sessionResult.comparison.reminder }}</span>
          </div>
        </div>

      </el-card>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Aim, ArrowRight, Check, Document, EditPen, Cloudy } from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import { useAdaptiveStore } from '@/stores/adaptive'
import { questionnaireApi } from '@/api'

const router = useRouter()
const store = useAdaptiveStore()

const loading = ref(true)
const submitting = ref(false)
const activeScale = ref('')
const online = ref(navigator.onLine)

const screeningItems = ref<{ number: number; content: string }[]>([])

const sclOptions = [
  { value: 1, label: '无' },
  { value: 2, label: '轻度' },
  { value: 3, label: '中度' },
  { value: 4, label: '偏重' },
  { value: 5, label: '严重' },
]
const subOptions = [
  { value: 0, label: '完全没有' },
  { value: 1, label: '有几天' },
  { value: 2, label: '一半以上时间' },
  { value: 3, label: '几乎每天' },
]

const factorMap: Record<string, string> = {
  SOM: '躯体化', 'O-C': '强迫症状', 'I-S': '人际敏感',
  DEP: '抑郁', ANX: '焦虑', HOS: '敌对',
  PHOB: '恐怖', PAR: '偏执', PSY: '精神病性', OTH: '其他',
}
function factorName(f: string) { return factorMap[f] || f || '—' }

const stepIndex = computed(() => {
  switch (store.step) {
    case 'intro': return 0
    case 'screening': return 0
    case 'subscales': return 1
    case 'done': return 3
    default: return 0
  }
})
const progress = computed(() => store.overallProgress)
const progressColor = computed(() => {
  if (progress.value.percent >= 100) return '#67c23a'
  if (progress.value.percent >= 60) return '#409eff'
  if (progress.value.percent >= 30) return '#e6a23c'
  return '#f56c6c'
})

const screeningIncomplete = computed(() => screeningItems.value.some(q => store.screeningAnswers[q.number] == null))
const hasRecommended = computed(() => store.recommendedSubscales.length > 0)
const totalSubQuestions = computed(() => store.recommendedSubscales.reduce((a, s) => a + s.question_count, 0))

const riskClass = computed(() => {
  const r = store.sessionResult?.overall_risk
  return r === 'red' ? 'risk-red' : r === 'yellow' ? 'risk-yellow' : 'risk-green'
})
const riskLabel = computed(() => {
  const r = store.sessionResult?.overall_risk
  return r === 'red' ? '高风险' : r === 'yellow' ? '中风险' : '低风险'
})
const doneSubTitle = computed(() => {
  if (!store.sessionResult) return '感谢您的作答'
  return `共作答 ${store.sessionResult.answered_count} 题（较固定 90 题智能缩短）`
})
const trendTagType = computed(() => {
  const t = store.sessionResult?.comparison?.overall_tag
  return t === 'improved' ? 'success' : t === 'worsened' ? 'danger' : 'info'
})

function startScreening() {
  store.reset()
  store.gotoStep('screening')
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function submitScreening() {
  submitting.value = true
  try {
    const res = await questionnaireApi.submitScreening(store.screeningAnswers) as any
    store.setScreeningResult(res)
    if (store.recommendedSubscales.length > 0) {
      activeScale.value = store.recommendedSubscales[0].code
      store.gotoStep('subscales')
      ElMessage.success(`筛查完成，已为您追加 ${store.recommendedSubscales.length} 个子量表`)
    } else {
      ElMessage.success('筛查完成，未发现需追加的子量表，正在生成报告…')
      await store.submitSession()
    }
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } finally {
    submitting.value = false
  }
}

async function submitSession() {
  try {
    await store.submitSession()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch {
    ElMessage.warning('网络不可用，您的作答已缓存，网络恢复后将自动提交')
  }
}

function goResult() {
  if (store.sessionResult) router.replace(`/result/${store.sessionResult.record_id}`)
}

function restart() {
  store.reset()
  void loadScreening()
}

async function loadScreening() {
  loading.value = true
  try {
    const res = await questionnaireApi.getScreeningItems() as any
    screeningItems.value = (res.questions || []).map((q: any) => ({ number: q.number, content: q.content }))
  } finally {
    loading.value = false
  }
}

function updateOnline() { online.value = navigator.onLine }

onMounted(async () => {
  // 如果已有未完成的筛查缓存，继续；否则重置
  if (store.step === 'done' && store.sessionResult) {
    // keep showing done
  } else if (store.screeningAnsweredCount > 0 || store.screeningResult) {
    // resume
  } else {
    store.reset()
  }
  await loadScreening()
  if (store.recommendedSubscales.length > 0 && !activeScale.value) {
    activeScale.value = store.recommendedSubscales[0].code
  }
  window.addEventListener('online', updateOnline)
  window.addEventListener('offline', updateOnline)
})

onBeforeUnmount(() => {
  window.removeEventListener('online', updateOnline)
  window.removeEventListener('offline', updateOnline)
})
</script>

<style scoped>
.q-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; gap: 12px; }
.header-tags { flex-shrink: 0; }
.q-title { margin: 0 0 6px; font-size: 22px; color: #303133; }
.q-tip { color: #909399; font-size: 13px; max-width: 640px; }
.flow-steps { margin-bottom: 8px; }
.progress-wrap { background: #f5f7fa; border-radius: 8px; padding: 16px 20px; margin-bottom: 16px; }
.progress-label { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.progress-label strong { color: #409eff; font-size: 18px; }
.done-count { color: #909399; font-size: 13px; }
.intro-box { padding: 24px 0; }
.classic-link { margin-left: 16px; color: #909399; font-size: 13px; text-decoration: underline; }
.stage-title { font-size: 17px; font-weight: 600; color: #303133; margin-bottom: 12px; display: flex; align-items: center; }
.stage-sub { font-size: 13px; color: #909399; font-weight: 400; margin-left: 4px; }
.legend { display: flex; flex-wrap: wrap; gap: 10px; padding: 10px 14px; background: #fafafa; border-radius: 6px; margin-bottom: 8px; }
.legend-title { font-weight: 600; color: #606266; }
.legend-chip { font-size: 13px; color: #606266; padding: 2px 8px; background: #fff; border-radius: 4px; }
.legend-chip b { color: #409eff; margin-right: 4px; }
.question-list { margin-top: 8px; }
.question-item { display: flex; gap: 14px; padding: 14px 0; border-bottom: 1px dashed #ebeef5; }
.question-item.is-empty { background: #fff7e6; border-radius: 6px; padding: 14px 12px; }
.q-number { width: 34px; height: 34px; flex-shrink: 0; border-radius: 50%; background: linear-gradient(135deg, #409eff, #67c23a); color: #fff; font-weight: 700; display: flex; align-items: center; justify-content: center; font-size: 14px; }
.q-number.sub { background: linear-gradient(135deg, #9b59b6, #6c5ce7); }
.is-empty .q-number { background: #e6a23c; }
.q-content { flex: 1; min-width: 0; }
.q-text { font-size: 15px; color: #303133; line-height: 1.6; margin-bottom: 10px; }
.q-options { display: flex; flex-wrap: wrap; gap: 6px; }
.rec-alert { margin-bottom: 12px; }
.scale-desc { color: #606266; font-size: 13px; margin: 8px 0; padding: 8px 12px; background: #f5f7fa; border-radius: 6px; }
.tab-done { display: inline-flex; align-items: center; gap: 6px; }
.action-bar { display: flex; justify-content: space-between; padding-top: 20px; margin-top: 8px; border-top: 1px solid #ebeef5; }
.action-bar .el-button { min-width: 160px; }
.done-box { padding: 24px 0; }
.done-summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 16px; }
.sum-item { background: #f5f7fa; border-radius: 8px; padding: 16px; text-align: center; }
.sum-item span { display: block; color: #909399; font-size: 13px; margin-bottom: 8px; }
.sum-item strong { font-size: 22px; color: #303133; }
.risk-red { color: #f56c6c; }
.risk-yellow { color: #e6a23c; }
.risk-green { color: #67c23a; }
.trend-tag { display: flex; align-items: center; gap: 12px; margin-top: 16px; justify-content: center; }
.trend-reminder { color: #606266; font-size: 14px; }
@media (max-width: 640px) {
  .done-summary { grid-template-columns: repeat(2, 1fr); }
  .q-header { flex-direction: column; }
}
</style>
