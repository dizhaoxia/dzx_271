<template>
  <div v-loading="loading">
    <el-card class="card-shadow mb-20">
      <div class="section-title" style="border:none; padding:0; margin:0;">
        <el-icon :size="22" color="#409eff"><DataAnalysis /></el-icon>
        统计仪表盘
      </div>
    </el-card>

    <el-row :gutter="16" class="mb-20">
      <el-col :span="6">
        <div class="stat-card users-card">
          <el-icon :size="32"><User /></el-icon>
          <div class="sc-body">
            <div class="sc-value">{{ stats?.total_users || 0 }}</div>
            <div class="sc-label">总用户数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card records-card">
          <el-icon :size="32"><Document /></el-icon>
          <div class="sc-body">
            <div class="sc-value">{{ stats?.total_assessments || 0 }}</div>
            <div class="sc-label">总测评次数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card unique-card">
          <el-icon :size="32"><Avatar /></el-icon>
          <div class="sc-body">
            <div class="sc-value">{{ stats?.unique_assessment_users || 0 }}</div>
            <div class="sc-label">参与测评人数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card gsi-card">
          <el-icon :size="32"><TrendCharts /></el-icon>
          <div class="sc-body">
            <div class="sc-value">{{ stats?.avg_gsi || 0 }}</div>
            <div class="sc-label">平均 GSI</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mb-20">
      <el-col :span="10">
        <el-card class="card-shadow">
          <div class="section-title">风险等级分布</div>
          <div ref="riskChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card class="card-shadow">
          <div class="section-title">平均因子分分布</div>
          <div ref="factorChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="card-shadow">
      <div class="section-title">近30天测评趋势</div>
      <div ref="trendChartRef" class="chart-box" style="height: 320px;"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { adminApi } from '@/api'
import type { DashboardStats } from '@/types'
import { DataAnalysis, User, Document, Avatar, TrendCharts } from '@element-plus/icons-vue'

const loading = ref(true)
const stats = ref<DashboardStats | null>(null)
const riskChartRef = ref<HTMLElement>()
const factorChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()

async function loadData() {
  try {
    loading.value = true
    stats.value = await adminApi.dashboard()
    await nextTick()
    renderRiskChart()
    renderFactorChart()
    renderTrendChart()
  } finally {
    loading.value = false
  }
}

function renderRiskChart() {
  if (!riskChartRef.value || !stats.value) return
  const data = stats.value.risk_distribution
  const chart = echarts.init(riskChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      avoidLabelOverlap: false,
      label: { show: true, formatter: '{b}\n{c}' },
      data: [
        { value: data.green, name: '正常(绿)', itemStyle: { color: '#67c23a' } },
        { value: data.yellow, name: '轻度(黄)', itemStyle: { color: '#e6a23c' } },
        { value: data.red, name: '中度+(红)', itemStyle: { color: '#f56c6c' } },
      ],
    }],
  })
  window.addEventListener('resize', () => chart.resize())
}

function renderFactorChart() {
  if (!factorChartRef.value || !stats.value) return
  const data = stats.value.avg_factor_scores
  const chart = echarts.init(factorChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 50, right: 20, top: 20, bottom: 40 },
    xAxis: { type: 'category', data: Object.keys(data), axisLabel: { rotate: 15 } },
    yAxis: { type: 'value', min: 0, max: 3 },
    series: [{
      type: 'bar',
      data: Object.values(data),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#409eff' },
          { offset: 1, color: '#67c23a' },
        ]),
        borderRadius: [6, 6, 0, 0],
      },
      label: { show: true, position: 'top', formatter: '{c}' },
    }],
  })
  window.addEventListener('resize', () => chart.resize())
}

function renderTrendChart() {
  if (!trendChartRef.value || !stats.value) return
  const chart = echarts.init(trendChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 20, bottom: 40 },
    xAxis: { type: 'category', data: stats.value.daily_trend_30d.map(d => d.date), boundaryGap: false },
    yAxis: { type: 'value' },
    series: [{
      name: '测评次数',
      type: 'line',
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64,158,255,0.5)' },
          { offset: 1, color: 'rgba(64,158,255,0.05)' },
        ]),
      },
      lineStyle: { color: '#409eff', width: 3 },
      itemStyle: { color: '#409eff' },
      data: stats.value.daily_trend_30d.map(d => d.count),
    }],
  })
  window.addEventListener('resize', () => chart.resize())
}

onMounted(loadData)
</script>

<style scoped>
.mb-20 { margin-bottom: 20px; }
.stat-card {
  background: linear-gradient(135deg, #ecf5ff 0%, #f0f9ff 100%);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  gap: 16px;
  align-items: center;
  color: #409eff;
  box-shadow: 0 2px 12px rgba(64,158,255,0.08);
}
.records-card { background: linear-gradient(135deg, #f0f9eb 0%, #ecfff5 100%); color: #67c23a; }
.unique-card { background: linear-gradient(135deg, #fdf6ec 0%, #fff9f0 100%); color: #e6a23c; }
.gsi-card { background: linear-gradient(135deg, #fef0f0 0%, #fff5f5 100%); color: #f56c6c; }
.sc-value { font-size: 30px; font-weight: 700; }
.sc-label { font-size: 13px; opacity: .8; margin-top: 4px; }
.chart-box { width: 100%; height: 280px; }
</style>
