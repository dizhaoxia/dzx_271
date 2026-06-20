<template>
  <el-card class="card-shadow mb-16" v-loading="loading">
    <div class="header-row">
      <div class="section-title">操作审计日志</div>
      <div class="filters">
        <el-select v-model="filters.action" placeholder="操作类型" clearable style="width: 140px;" @change="load">
          <el-option v-for="a in actionOptions" :key="a.value" :label="a.label" :value="a.value" />
        </el-select>
        <el-select v-model="filters.resource_type" placeholder="资源类型" clearable style="width: 160px;" @change="load">
          <el-option v-for="r in resourceOptions" :key="r" :label="r" :value="r" />
        </el-select>
        <el-button @click="load" :icon="Refresh">刷新</el-button>
      </div>
    </div>

    <el-row :gutter="12" class="mb-12" v-if="summary">
      <el-col :span="6"><div class="sum-card"><span>日志总数</span><strong>{{ summary.total }}</strong></div></el-col>
      <el-col :span="9"><div class="sum-card"><span>按操作</span>
        <div class="chips">
          <el-tag v-for="(v, k) in summary.by_action" :key="k" size="small" class="chip">{{ actionLabel(k as string) }}: {{ v }}</el-tag>
        </div>
      </div></el-col>
      <el-col :span="9"><div class="sum-card"><span>按资源</span>
        <div class="chips">
          <el-tag v-for="(v, k) in summary.by_resource" :key="k" size="small" type="info" class="chip">{{ k }}: {{ v }}</el-tag>
        </div>
      </div></el-col>
    </el-row>

    <el-table :data="logs" stripe>
      <el-table-column label="时间" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="用户" min-width="150">
        <template #default="{ row }">
          <div>{{ row.username || '匿名' }}</div>
          <div class="phone">{{ row.user_phone }}</div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="actionTag(row.action)" size="small">{{ row.action_display || actionLabel(row.action) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="资源" width="140">
        <template #default="{ row }">{{ row.resource_type }} <span v-if="row.resource_id">#{{ row.resource_id }}</span></template>
      </el-table-column>
      <el-table-column label="详情" min-width="240" show-overflow-tooltip>
        <template #default="{ row }">{{ row.detail ? JSON.stringify(row.detail) : '—' }}</template>
      </el-table-column>
      <el-table-column label="IP" width="140">
        <template #default="{ row }">{{ row.ip_address || '—' }}</template>
      </el-table-column>
    </el-table>

    <div v-if="total > pageSize" class="pager">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total"
        layout="total, prev, pager, next" background @current-change="load" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { complianceApi } from '@/api'
import type { AuditLog } from '@/types'

const loading = ref(false)
const logs = ref<AuditLog[]>([])
const summary = ref<any>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive<{ action: string; resource_type: string }>({ action: '', resource_type: '' })

const actionOptions = [
  { value: 'view', label: '查看' },
  { value: 'create', label: '创建' },
  { value: 'update', label: '更新' },
  { value: 'delete', label: '删除' },
  { value: 'export', label: '导出' },
  { value: 'login', label: '登录' },
  { value: 'logout', label: '登出' },
]
const resourceOptions = ['record', 'user_role', 'high_risk_list', 'dashboard', 'comparison', 'record_pdf', 'followup_note', 'patient_assignment']

async function load() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (filters.action) params.action = filters.action
    if (filters.resource_type) params.resource_type = filters.resource_type
    const res: any = await complianceApi.getAuditLogs(params)
    logs.value = res.results || res.data || res || []
    total.value = res.count || logs.value.length
    const sum: any = await complianceApi.getAuditSummary()
    summary.value = sum
  } finally {
    loading.value = false
  }
}

function formatTime(t: string) { return new Date(t).toLocaleString('zh-CN') }
function actionLabel(a: string) {
  return actionOptions.find(o => o.value === a)?.label || a
}
function actionTag(a: string): 'success' | 'warning' | 'danger' | 'info' | 'primary' {
  const m: Record<string, any> = { view: 'info', create: 'success', update: 'warning', delete: 'danger', export: 'warning', login: 'primary', logout: 'info' }
  return m[a] || 'info'
}

onMounted(load)
</script>

<style scoped>
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.filters { display: flex; gap: 8px; }
.section-title { font-size: 16px; font-weight: 600; color: #303133; border-left: 4px solid #909399; padding-left: 10px; }
.sum-card { background: #f5f7fa; border-radius: 8px; padding: 14px 16px; }
.sum-card span { display: block; color: #909399; font-size: 13px; margin-bottom: 8px; }
.sum-card strong { font-size: 22px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { margin: 0; }
.phone { font-size: 12px; color: #909399; }
.mb-12 { margin-bottom: 12px; }
.pager { display: flex; justify-content: center; margin-top: 16px; }
</style>
