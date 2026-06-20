<template>
  <Layout>
    <div class="page-container" v-loading="loading">
      <el-card class="card-shadow mb-24">
        <div class="header-row">
          <div class="section-title" style="border: none; padding: 0; margin: 0;">
            <el-icon :size="22" color="#409eff"><TrendCharts /></el-icon>
            历史测评记录
          </div>
          <el-button type="primary" size="large" @click="$router.push('/questionnaire')">
            <el-icon><EditPen /></el-icon> 新测评
          </el-button>
        </div>
      </el-card>

      <el-card v-if="trendData.length > 0" class="card-shadow mb-24">
        <div class="section-title">因子分变化趋势</div>
        <div ref="chartRef" class="trend-chart"></div>
      </el-card>

      <el-card class="card-shadow">
        <div class="section-title">测评列表</div>
        <el-empty v-if="records.length === 0 && !loading" description="还没有测评记录，快来做一次测评吧～">
          <el-button type="primary" @click="$router.push('/questionnaire')">立即测评</el-button>
        </el-empty>
        <el-table v-else :data="records" stripe>
          <el-table-column type="index" label="#" width="60" align="center" />
          <el-table-column label="测评时间" min-width="170" sortable>
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="GSI" width="90" align="center" sortable>
            <template #default="{ row }">
              <strong :style="{ color: gsiColor(row.gsi) }">{{ row.gsi }}</strong>
            </template>
          </el-table-column>
          <el-table-column label="阳性项目" width="100" align="center">
            <template #default="{ row }">{{ row.positive_count }}</template>
          </el-table-column>
          <el-table-column label="各因子分" min-width="460">
            <template #default="{ row }">
              <div class="factor-scores">
                <span class="fs-item" :title="`躯体化: ${row.som_score}`">躯体化 <b>{{ row.som_score }}</b></span>
                <span class="fs-item" :title="`强迫: ${row.oc_score}`">强迫 <b>{{ row.oc_score }}</b></span>
                <span class="fs-item" :title="`人际: ${row.is_score}`">人际 <b>{{ row.is_score }}</b></span>
                <span class="fs-item" :title="`抑郁: ${row.dep_score}`">抑郁 <b>{{ row.dep_score }}</b></span>
                <span class="fs-item" :title="`焦虑: ${row.anx_score}`">焦虑 <b>{{ row.anx_score }}</b></span>
                <span class="fs-item" :title="`敌对: ${row.hos_score}`">敌对 <b>{{ row.hos_score }}</b></span>
                <span class="fs-item" :title="`恐怖: ${row.phob_score}`">恐怖 <b>{{ row.phob_score }}</b></span>
                <span class="fs-item" :title="`偏执: ${row.par_score}`">偏执 <b>{{ row.par_score }}</b></span>
                <span class="fs-item" :title="`精神病性: ${row.psy_score}`">精神 <b>{{ row.psy_score }}</b></span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="风险等级" width="110" align="center">
            <template #default="{ row }">
              <span :class="`risk-${row.overall_risk}`">
                {{ riskText(row.overall_risk) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="$router.push(`/result/${row.id}`)">
                查看报告
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="total > pageSize" class="pager">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :total="total"
            layout="total, prev, pager, next, jumper"
            background
            @current-change="loadRecords"
          />
        </div>
      </el-card>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import Layout from '@/components/Layout.vue'
import { recordsApi } from '@/api'
import type { AssessmentRecord, TrendItem } from '@/types'
import { TrendCharts, EditPen } from '@element-plus/icons-vue'

const loading = ref(false)
const records = ref<AssessmentRecord[]>([])
const trendData = ref<TrendItem[]>([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const chartRef = ref<HTMLElement>()

async function loadRecords() {
  try {
    loading.value = true
    const res: any = await recordsApi.getRecords({ page: page.value, page_size: pageSize.value })
    records.value = res.results || res.data || res || []
    total.value = res.count || records.value.length
  } finally {
    loading.value = false
  }
}

async function loadTrend() {
  try {
    trendData.value = await recordsApi.getTrend()
    await nextTick()
    renderChart()
  } catch (e) {
    // ignore
  }
}

const factorDefs = [
  { key: 'som_score', name: '躯体化', color: '#f56c6c' },
  { key: 'oc_score', name: '强迫症状', color: '#e6a23c' },
  { key: 'is_score', name: '人际关系', color: '#f06a6a' },
  { key: 'dep_score', name: '抑郁', color: '#909399' },
  { key: 'anx_score', name: '焦虑', color: '#d9001b' },
  { key: 'hos_score', name: '敌对', color: '#c23531' },
  { key: 'phob_score', name: '恐怖', color: '#2f4554' },
  { key: 'par_score', name: '偏执', color: '#61a0a8' },
  { key: 'psy_score', name: '精神病性', color: '#d48265' },
]

function renderChart() {
  if (!chartRef.value || trendData.value.length === 0) return
  const chart = echarts.init(chartRef.value)
  const dates = trendData.value.map(d => d.created_at)
  const series = factorDefs.map(f => ({
    name: f.name,
    type: 'line',
    smooth: true,
    symbol: 'circle',
    symbolSize: 6,
    itemStyle: { color: f.color },
    lineStyle: { width: 2 },
    data: trendData.value.map(d => (d as any)[f.key]),
  }))
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { top: 0, data: factorDefs.map(f => f.name), type: 'scroll' },
    grid: { left: 40, right: 20, top: 50, bottom: 50 },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', min: 0, max: 5, axisLabel: { formatter: '{value}' } },
    dataZoom: [{ type: 'inside' }, { type: 'slider', height: 16, bottom: 10 }],
    series,
  })
  window.addEventListener('resize', () => chart.resize())
}

function formatTime(t: string) { return new Date(t).toLocaleString('zh-CN') }
function riskText(r: string) {
  return { green: '正常', yellow: '轻度', red: '中度+' }[r] || r
}
function gsiColor(g: number) {
  if (g < 2) return '#67c23a'
  if (g < 3) return '#e6a23c'
  return '#f56c6c'
}

onMounted(async () => {
  await Promise.all([loadRecords(), loadTrend()])
})

watch(page, loadRecords)
</script>

<style scoped>
.header-row { display: flex; justify-content: space-between; align-items: center; }
.trend-chart { width: 100%; height: 380px; }
.factor-scores { display: flex; flex-wrap: wrap; gap: 6px 12px; }
.fs-item {
  font-size: 12px; color: #606266;
  padding: 2px 8px; background: #f5f7fa;
  border-radius: 4px;
}
.fs-item b { color: #303133; margin-left: 2px; }
.pager { display: flex; justify-content: center; margin-top: 20px; }
</style>
