<template>
  <Layout>
    <div class="page-container" v-loading="loading">
      <div v-if="record" class="result-wrap">
        <el-card class="card-shadow summary-card mb-24">
          <div class="summary-header">
            <div>
              <h2 class="summary-title">
                <el-icon><DocumentChecked /></el-icon>
                测评报告
              </h2>
              <div class="summary-meta">
                测评时间：{{ formatTime(record.created_at) }}
                <el-divider direction="vertical" />
                报告编号：#{{ record.id }}
              </div>
            </div>
            <div :class="['overall-risk', `risk-${record.overall_risk}`]">
              <el-icon :size="28"><component :is="riskIcon" /></el-icon>
              <div class="risk-text">
                <div class="risk-label">整体风险等级</div>
                <div class="risk-value">{{ riskText }}</div>
              </div>
            </div>
          </div>

          <el-row :gutter="20" class="mt-24">
            <el-col :span="8">
              <div class="stat-box gsi-box">
                <div class="stat-label">总症状指数 (GSI)</div>
                <div class="stat-num">{{ record.gsi }}</div>
                <el-progress type="dashboard" :percentage="gsiPercent" :color="gsiColor" :width="120" />
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-box">
                <div class="stat-label">总分</div>
                <div class="stat-num" style="color:#409eff;">{{ record.total_sum }}</div>
                <div class="stat-hint mt-16">90 项得分之和</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-box">
                <div class="stat-label">阳性项目数 / 均分</div>
                <div class="stat-num" style="color:#e6a23c;">
                  {{ record.positive_count }} <span style="font-size:20px;">/</span> {{ record.positive_avg }}
                </div>
                <div class="stat-hint mt-16">得分≥2的项目数 / 其平均分</div>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <el-card class="card-shadow mb-24">
          <div class="section-title">因子分与常模对比</div>
          <div ref="factorChartRef" class="factor-chart"></div>
        </el-card>

        <el-card class="card-shadow mb-24">
          <div class="section-title">各因子详细分析</div>
          <el-table :data="factorRows" size="default" stripe>
            <el-table-column prop="name" label="因子" width="130" />
            <el-table-column label="得分" width="100" align="center">
              <template #default="{ row }">
                <strong :style="{ color: scoreColor(row.score, row.norm_mean, row.norm_std) }">
                  {{ row.score }}
                </strong>
              </template>
            </el-table-column>
            <el-table-column label="常模 (均值±SD)" width="130" align="center">
              <template #default="{ row }">
                {{ row.norm_mean }} ± {{ row.norm_std }}
              </template>
            </el-table-column>
            <el-table-column label="对比状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="statusTag(row.status)" effect="light" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="风险等级" width="110" align="center">
              <template #default="{ row }">
                <span :class="`risk-${row.risk_level}`" style="padding:4px 10px;">
                  {{ riskLevelText(row.risk_level) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="因子说明" min-width="260" />
          </el-table>
        </el-card>

        <el-card class="card-shadow mb-24">
          <div class="section-title">答题明细（每题得分）</div>
          <el-row :gutter="12">
            <el-col :span="8" v-for="(page, pIdx) in pagedAnswers" :key="pIdx" class="mb-12">
              <div class="page-answers">
                <div class="pa-title">第 {{ pIdx + 1 }} 页</div>
                <div class="pa-list">
                  <div
                    v-for="item in page"
                    :key="item.num"
                    :class="['pa-item', `level-${answerLevel(item.val)}`]"
                  >
                    <span class="pa-num">{{ item.num }}</span>
                    <span class="pa-val">{{ item.val }}</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <div class="action-bar">
          <el-button size="large" @click="$router.push('/history')">
            <el-icon><HistoryIcon /></el-icon> 查看历史
          </el-button>
          <el-button size="large" type="primary" @click="$router.push('/questionnaire')">
            <el-icon><Refresh /></el-icon> 重新测评
          </el-button>
          <el-button size="large" type="success" @click="window.print()">
            <el-icon><Printer /></el-icon> 打印报告
          </el-button>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import Layout from '@/components/Layout.vue'
import { recordsApi } from '@/api'
import type { AssessmentRecord, FactorDetail } from '@/types'
import { Sunny, Warning, CircleClose, Clock as HistoryIcon, Refresh, Printer, DocumentChecked } from '@element-plus/icons-vue'

const route = useRoute()
const loading = ref(true)
const record = ref<AssessmentRecord | null>(null)
const factorChartRef = ref<HTMLElement>()

async function loadData() {
  const id = route.params.id as string
  try {
    loading.value = true
    record.value = await recordsApi.getRecordDetail(Number(id))
    await nextTick()
    renderChart()
  } finally {
    loading.value = false
  }
}

const comparisons = computed<Record<string, FactorDetail>>(() => {
  return record.value?.factors_detail || {}
})

const factorList = ['SOM', 'O-C', 'I-S', 'DEP', 'ANX', 'HOS', 'PHOB', 'PAR', 'PSY']

const factorRows = computed(() => {
  return factorList.map(f => {
    const c = comparisons.value[f] || {} as FactorDetail
    return {
      code: f,
      name: c.name || f,
      score: c.score || 0,
      norm_mean: c.norm_mean || 0,
      norm_std: c.norm_std || 0,
      status: c.status || '正常',
      risk_level: c.risk_level || 'green',
      description: c.description || '',
    }
  })
})

const riskText = computed(() => {
  const m: any = { green: '正常 (低风险)', yellow: '轻度异常', red: '中度及以上' }
  return m[record.value?.overall_risk || 'green']
})
const riskIcon = computed(() => {
  return record.value?.overall_risk === 'green' ? Sunny :
         record.value?.overall_risk === 'yellow' ? Warning : CircleClose
})

const gsiPercent = computed(() => Math.min(100, Math.round(((record.value?.gsi || 0) / 5) * 100)))
const gsiColor = computed(() => {
  const g = record.value?.gsi || 0
  if (g < 2) return '#67c23a'
  if (g < 3) return '#e6a23c'
  return '#f56c6c'
})

const pagedAnswers = computed(() => {
  const raw = record.value?.answers_json || {}
  const list = Object.entries(raw).map(([k, v]) => ({ num: Number(k), val: v as number }))
  list.sort((a, b) => a.num - b.num)
  const result: any[] = []
  for (let i = 0; i < list.length; i += 10) {
    result.push(list.slice(i, i + 10))
  }
  return result
})

function formatTime(t: string) {
  return new Date(t).toLocaleString('zh-CN')
}
function statusTag(s: string): 'success' | 'warning' | 'danger' | 'info' {
  if (s === '正常') return 'success'
  if (s === '偏高') return 'danger'
  if (s === '偏低') return 'info'
  return 'warning'
}
function riskLevelText(l: string) {
  return { green: '正常', yellow: '轻度', red: '中度+' }[l] || l
}
function scoreColor(score: number, mean: number, std: number) {
  if (score <= mean + std) return '#67c23a'
  if (score <= mean + 2 * std) return '#e6a23c'
  return '#f56c6c'
}
function answerLevel(v: number) { return v }

function renderChart() {
  if (!factorChartRef.value) return
  const chart = echarts.init(factorChartRef.value)
  const names = factorRows.value.map(r => r.name)
  const scores = factorRows.value.map(r => r.score)
  const norms = factorRows.value.map(r => r.norm_mean)
  const normMax = factorRows.value.map(r => +(r.norm_mean + r.norm_std).toFixed(2))
  const riskColors = factorRows.value.map(r => ({ green: '#67c23a', yellow: '#e6a23c', red: '#f56c6c' }[r.risk_level] || '#67c23a'))

  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: 0, data: ['因子得分', '全国常模均值', '均值+1SD'] },
    grid: { left: 40, right: 20, top: 50, bottom: 40 },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 15 } },
    yAxis: { type: 'value', min: 0, max: 5, axisLabel: { formatter: '{value} 分' } },
    series: [
      {
        name: '因子得分',
        type: 'bar',
        data: scores.map((v, i) => ({ value: v, itemStyle: { color: riskColors[i] } })),
        barWidth: '25%',
        label: { show: true, position: 'top', formatter: '{c}' },
      },
      {
        name: '全国常模均值',
        type: 'line',
        data: norms,
        lineStyle: { color: '#909399', type: 'dashed' },
        symbol: 'circle',
        itemStyle: { color: '#909399' },
        yAxisIndex: 0,
      },
      {
        name: '均值+1SD',
        type: 'line',
        data: normMax,
        lineStyle: { color: '#f56c6c', type: 'dotted' },
        symbol: 'triangle',
        itemStyle: { color: '#f56c6c' },
      },
    ],
  })
  window.addEventListener('resize', () => chart.resize())
}

onMounted(loadData)
</script>

<style scoped>
.summary-header { display: flex; justify-content: space-between; align-items: center; }
.summary-title { margin: 0 0 6px; display: flex; align-items: center; gap: 8px; font-size: 22px; color: #303133; }
.summary-title .el-icon { color: #67c23a; }
.summary-meta { color: #909399; font-size: 13px; }
.overall-risk { display: flex; gap: 14px; align-items: center; padding: 14px 24px; border-radius: 12px; }
.overall-risk.risk-green { background: #f0f9eb; color: #67c23a; }
.overall-risk.risk-yellow { background: #fdf6ec; color: #e6a23c; }
.overall-risk.risk-red { background: #fef0f0; color: #f56c6c; }
.risk-label { font-size: 12px; opacity: .8; }
.risk-value { font-size: 20px; font-weight: 700; margin-top: 2px; }
.stat-box { text-align: center; padding: 20px; background: #fafbfc; border-radius: 12px; border: 1px solid #ebeef5; }
.stat-label { color: #909399; font-size: 13px; }
.stat-num { font-size: 36px; font-weight: 700; color: #303133; margin: 10px 0; }
.stat-hint { color: #909399; font-size: 12px; }
.factor-chart { width: 100%; height: 360px; }
.page-answers { background: #fafafa; border-radius: 8px; padding: 12px; }
.pa-title { font-weight: 600; font-size: 13px; color: #606266; margin-bottom: 8px; }
.pa-list { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; }
.pa-item { display: flex; align-items: center; justify-content: space-between; background: #fff; padding: 4px 8px; border-radius: 4px; border: 1px solid #ebeef5; }
.pa-num { font-size: 12px; color: #909399; }
.pa-val { font-weight: 700; font-size: 13px; }
.level-1 .pa-val { color: #67c23a; }
.level-2 .pa-val { color: #409eff; }
.level-3 .pa-val { color: #e6a23c; }
.level-4 .pa-val { color: #f06a6a; }
.level-5 .pa-val { color: #d9001b; }
.action-bar { display: flex; gap: 12px; justify-content: center; padding: 24px 0; }

@media print {
  .action-bar, .layout-header, .layout-footer { display: none !important; }
  .page-container { max-width: 100%; }
}
</style>
