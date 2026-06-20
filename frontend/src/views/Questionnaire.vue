<template>
  <Layout>
    <div class="page-container">
      <el-card class="card-shadow mb-16" v-loading="loading">
        <div class="q-header">
          <div>
            <h2 class="q-title">SCL-90 症状自评量表</h2>
            <div class="q-tip">
              请根据最近一周的实际感觉，对下列问题进行评分，每题必答。
            </div>
          </div>
          <el-tag type="primary" size="large" effect="dark">
            第 {{ store.currentPage }} / {{ store.totalPages }} 页
          </el-tag>
        </div>

        <div class="progress-wrap">
          <div class="progress-label">
            <span>答题进度</span>
            <strong>{{ store.progress }}%</strong>
            <span class="done-count">
              (已答 {{ answeredCount }} / 90 题)
            </span>
          </div>
          <el-progress
            :percentage="store.progress"
            :stroke-width="14"
            :color="progressColor"
            show-text="false"
          />
        </div>

        <div class="legend">
          <div class="legend-title">评分标准：</div>
          <div class="legend-options">
            <div v-for="o in options" :key="o.value" :class="['legend-item', `opt-${o.value}`]">
              <span class="opt-num">{{ o.value }}</span>
              <span class="opt-text">{{ o.label }}</span>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="question-list">
          <div
            v-for="(q, idx) in store.currentQuestions"
            :key="q.number"
            :class="['question-item', { 'is-empty': store.answers[q.number] == null, 'has-error': showError && missingSet.has(q.number) }]"
          >
            <div class="q-number">
              <span>{{ q.number }}</span>
            </div>
            <div class="q-content">
              <div class="q-text">
                <span class="q-index">{{ idx + 1 }}.</span>
                {{ q.content }}
                <el-tag size="small" effect="plain" class="factor-tag" :type="factorTagType(q.factor)">
                  {{ factorName(q.factor) }}
                </el-tag>
              </div>
              <el-radio-group
                class="q-options"
                v-model="store.answers[q.number]"
                @change="() => clearError(q.number)"
              >
                <el-radio-button
                  v-for="o in options"
                  :key="o.value"
                  :label="o.value"
                  size="large"
                >
                  {{ o.label }}
                </el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </div>

        <div v-if="showError && missingSet.size > 0" class="err-msg">
          <el-icon><Warning /></el-icon>
          以下题目尚未作答：
          <span v-for="n in Array.from(missingSet).sort((a,b)=>a-b)" :key="n" class="err-num">{{ n }}</span>
          ，请完成后再翻页。
        </div>

        <div class="pager-wrap">
          <el-pagination
            layout="prev, pager, next"
            :page-size="store.pageSize"
            :total="90"
            :current-page="store.currentPage"
            background
            @current-change="handlePageChange"
            :prev-text="`上一页`"
            :next-text="`下一页`"
          />
        </div>

        <div class="action-bar">
          <el-button size="large" @click="goPrev" :disabled="store.currentPage === 1">
            <el-icon><ArrowLeft /></el-icon> 上一页
          </el-button>
          <el-button size="large" :type="isLastPage ? 'success' : 'primary'" @click="goNext" :loading="submitting">
            <span v-if="!isLastPage">下一页 <el-icon><ArrowRight /></el-icon></span>
            <span v-else><el-icon><Check /></el-icon> 提交测评</span>
          </el-button>
        </div>
      </el-card>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Warning, ArrowLeft, ArrowRight, Check } from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import { useQuestionnaireStore } from '@/stores/questionnaire'
import { recordsApi } from '@/api'
import type { AssessmentResult } from '@/types'

const router = useRouter()
const store = useQuestionnaireStore()

const loading = ref(true)
const submitting = ref(false)
const showError = ref(false)
const missingSet = reactive(new Set<number>())

const options = [
  { value: 1, label: '1 无' },
  { value: 2, label: '2 轻度' },
  { value: 3, label: '3 中度' },
  { value: 4, label: '4 偏重' },
  { value: 5, label: '5 严重' },
]

const factorMap: Record<string, string> = {
  SOM: '躯体化', 'O-C': '强迫症状', 'I-S': '人际敏感',
  DEP: '抑郁', 'ANX': '焦虑', 'HOS': '敌对',
  PHOB: '恐怖', 'PAR': '偏执', 'PSY': '精神病性', OTH: '其他',
}

const answeredCount = computed(() => Object.keys(store.answers).length)
const progressColor = computed(() => {
  if (store.progress >= 100) return '#67c23a'
  if (store.progress >= 60) return '#409eff'
  if (store.progress >= 30) return '#e6a23c'
  return '#f56c6c'
})
const isLastPage = computed(() => store.currentPage === store.totalPages)

function factorName(f: string) { return factorMap[f] || f }
function factorTagType(f: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' {
  const m: any = { SOM: 'danger', ANX: 'danger', DEP: 'info', O_C: 'warning', 'O-C': 'warning', 'I-S': 'warning', HOS: 'danger', PHOB: 'primary', PAR: 'warning', PSY: 'info', OTH: '' }
  return m[f] || ''
}

function clearError(num: number) {
  missingSet.delete(num)
  if (missingSet.size === 0) showError.value = false
}

function collectMissing(validateAll: boolean) {
  missingSet.clear()
  if (validateAll) {
    for (let i = 1; i <= 90; i++) {
      if (store.answers[i] == null) missingSet.add(i)
    }
  } else {
    for (const q of store.currentQuestions) {
      if (store.answers[q.number] == null) missingSet.add(q.number)
    }
  }
  return missingSet.size > 0
}

async function goNext() {
  showError.value = false
  if (isLastPage.value) {
    // validate all
    if (collectMissing(true)) {
      showError.value = true
      ElMessage.warning(`还有 ${missingSet.size} 道题未完成`)
      // jump to first missing page
      const first = Math.min(...Array.from(missingSet))
      const page = Math.ceil(first / store.pageSize)
      if (page !== store.currentPage) store.goToPage(page)
      return
    }
    try {
      await ElMessageBox.confirm('确定提交测评吗？提交后将无法修改。', '提示', { type: 'warning' })
    } catch { return }
    try {
      submitting.value = true
      const res = await recordsApi.submitAssessment(store.answers) as unknown as AssessmentResult
      ElMessage.success('测评提交成功')
      store.reset()
      router.replace(`/result/${res.record_id}`)
    } finally {
      submitting.value = false
    }
  } else {
    if (collectMissing(false)) {
      showError.value = true
      ElMessage.warning('本页题目未全部完成')
      return
    }
    store.goNextPage()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function goPrev() {
  showError.value = false
  store.goPrevPage()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handlePageChange(page: number) {
  showError.value = false
  store.goToPage(page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(() => store.currentPage, () => {
  showError.value = false
})

onMounted(async () => {
  try {
    store.reset()
    await store.loadAllQuestions()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.q-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.q-title { margin: 0 0 6px; font-size: 22px; color: #303133; }
.q-tip { color: #909399; font-size: 13px; }
.progress-wrap { background: #f5f7fa; border-radius: 8px; padding: 16px 20px; margin-bottom: 16px; }
.progress-label { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.progress-label strong { color: #409eff; font-size: 18px; }
.done-count { color: #909399; font-size: 13px; }
.legend { display: flex; align-items: center; gap: 14px; padding: 12px 16px; background: #fafafa; border-radius: 6px; }
.legend-title { font-weight: 600; color: #606266; }
.legend-options { display: flex; gap: 10px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 4px; background: #fff; }
.opt-num { font-weight: 700; font-size: 13px; }
.opt-1 .opt-num { color: #67c23a; }
.opt-2 .opt-num { color: #409eff; }
.opt-3 .opt-num { color: #e6a23c; }
.opt-4 .opt-num { color: #f06a6a; }
.opt-5 .opt-num { color: #d9001b; }
.question-item { display: flex; gap: 14px; padding: 16px 0; border-bottom: 1px dashed #ebeef5; transition: all .2s; }
.question-item:last-child { border-bottom: none; }
.question-item.is-empty { background: #fff7e6; border-radius: 6px; padding: 16px; }
.question-item.has-error { background: #fef0f0; border-radius: 6px; padding: 16px; border: 1px dashed #fbc4c4; }
.q-number {
  width: 36px; height: 36px; flex-shrink: 0;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: #fff; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px;
}
.is-empty .q-number { background: #e6a23c; }
.has-error .q-number { background: #f56c6c; }
.q-content { flex: 1; }
.q-text { font-size: 15px; color: #303133; line-height: 1.6; margin-bottom: 12px; }
.q-index { color: #909399; margin-right: 6px; }
.factor-tag { margin-left: 10px; }
.q-options { display: flex; flex-wrap: wrap; gap: 6px; }
.err-msg {
  background: #fef0f0;
  color: #f56c6c;
  padding: 12px 16px;
  border-radius: 6px;
  display: flex; align-items: flex-start; gap: 8px;
  margin: 16px 0;
}
.err-num {
  display: inline-block;
  background: #fff;
  border: 1px solid #fbc4c4;
  padding: 2px 8px;
  border-radius: 4px;
  margin: 0 4px 4px 0;
  font-size: 12px;
}
.pager-wrap { display: flex; justify-content: center; margin: 24px 0 16px; }
.action-bar { display: flex; justify-content: space-between; padding-top: 20px; border-top: 1px solid #ebeef5; }
.action-bar .el-button { min-width: 160px; }
</style>
