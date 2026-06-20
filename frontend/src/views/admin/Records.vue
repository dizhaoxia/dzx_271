<template>
  <div>
    <el-card class="card-shadow mb-16">
      <div class="toolbar">
        <div class="section-title" style="border:none; padding:0; margin:0;">
          <el-icon :size="22" color="#409eff"><Document /></el-icon>
          测评数据
        </div>
        <div class="tool-actions">
          <el-input v-model="search" placeholder="搜索用户手机号/昵称" clearable style="width: 240px;" :prefix-icon="Search" />
          <el-select v-model="filterRisk" placeholder="风险等级" clearable style="width: 140px;">
            <el-option label="正常(绿)" value="green" />
            <el-option label="轻度(黄)" value="yellow" />
            <el-option label="中度+(红)" value="red" />
          </el-select>
          <el-button type="success" :icon="Download" @click="exportCsv">导出 CSV</el-button>
          <el-button type="primary" :icon="Refresh" @click="loadData">刷新</el-button>
        </div>
      </div>

      <el-table :data="records" stripe v-loading="loading">
        <el-table-column type="index" label="#" width="60" align="center" />
        <el-table-column label="ID" prop="id" width="70" align="center" />
        <el-table-column label="用户" min-width="180">
          <template #default="{ row }">
            <div><strong>{{ row.user_name }}</strong></div>
            <div style="color:#909399; font-size:12px;">{{ row.user_phone }}</div>
          </template>
        </el-table-column>
        <el-table-column label="测评时间" width="160" sortable prop="created_at">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="GSI" width="90" align="center" sortable>
          <template #default="{ row }"><b :style="{ color: gsiColor(row.gsi) }">{{ row.gsi }}</b></template>
        </el-table-column>
        <el-table-column label="总分/阳性" width="130" align="center">
          <template #default="{ row }">
            <div>{{ row.total_sum }} / {{ row.positive_count }}</div>
            <div style="color:#909399; font-size:12px;">均分 {{ row.positive_avg }}</div>
          </template>
        </el-table-column>
        <el-table-column label="9因子" min-width="260">
          <template #default="{ row }">
            <div class="fs-list">
              <span>躯体<b>{{ row.som_score }}</b></span>
              <span>强迫<b>{{ row.oc_score }}</b></span>
              <span>人际<b>{{ row.is_score }}</b></span>
              <span>抑郁<b>{{ row.dep_score }}</b></span>
              <span>焦虑<b>{{ row.anx_score }}</b></span>
              <span>敌对<b>{{ row.hos_score }}</b></span>
              <span>恐怖<b>{{ row.phob_score }}</b></span>
              <span>偏执<b>{{ row.par_score }}</b></span>
              <span>精神<b>{{ row.psy_score }}</b></span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="风险" width="100" align="center">
          <template #default="{ row }">
            <span :class="`risk-${row.overall_risk}`">{{ riskText(row.overall_risk) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="$router.push(`/result/${row.id}`)">查看</el-button>
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
          @current-change="loadData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download, Document } from '@element-plus/icons-vue'
import { adminApi } from '@/api'

const loading = ref(false)
const records = ref<any[]>([])
const page = ref(1)
const pageSize = ref(15)
const total = ref(0)
const search = ref('')
const filterRisk = ref('')

async function loadData() {
  try {
    loading.value = true
    const params: any = { page: page.value, page_size: pageSize.value }
    if (search.value) params.search = search.value
    if (filterRisk.value) params.overall_risk = filterRisk.value
    const res: any = await adminApi.getRecords(params)
    records.value = res.results || res.data || res || []
    total.value = res.count || records.value.length
  } finally {
    loading.value = false
  }
}

async function exportCsv() {
  try {
    loading.value = true
    const blob = await adminApi.exportCsv() as unknown as Blob
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `scl90_records_${Date.now()}.csv`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } finally {
    loading.value = false
  }
}

function formatTime(t: string) { return t ? new Date(t).toLocaleString('zh-CN') : '-' }
function riskText(r: string) {
  return { green: '正常', yellow: '轻度', red: '中度+' }[r] || r
}
function gsiColor(g: number) {
  if (g < 2) return '#67c23a'
  if (g < 3) return '#e6a23c'
  return '#f56c6c'
}

let t: any = null
watch(search, () => {
  clearTimeout(t)
  t = setTimeout(() => { page.value = 1; loadData() }, 400)
})
watch(filterRisk, () => { page.value = 1; loadData() })

onMounted(loadData)
</script>

<style scoped>
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
.tool-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.pager { display: flex; justify-content: center; margin-top: 20px; }
.fs-list { display: flex; flex-wrap: wrap; gap: 4px 10px; font-size: 12px; color: #606266; }
.fs-list span { background: #f5f7fa; padding: 2px 6px; border-radius: 4px; }
.fs-list b { color: #303133; margin-left: 2px; }
</style>
