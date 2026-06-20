<template>
  <el-card class="card-shadow mb-16" v-loading="loading">
    <div class="header-row">
      <div class="section-title">高危人群列表</div>
      <div class="filters">
        <el-radio-group v-model="riskFilter" @change="load">
          <el-radio-button label="red,yellow">中/高危</el-radio-button>
          <el-radio-button label="red">仅高危</el-radio-button>
          <el-radio-button label="yellow">仅中危</el-radio-button>
        </el-radio-group>
        <el-button @click="load" :icon="Refresh">刷新</el-button>
      </div>
    </div>
    <el-alert type="warning" :closable="false" show-icon class="mb-12"
      title="此列表展示每位用户最近一次测评风险为中度及以上的记录，供管理者主动干预。"
    />
    <el-empty v-if="!items.length && !loading" description="暂无高危人群" />
    <el-table v-else :data="items" stripe>
      <el-table-column label="用户" min-width="150">
        <template #default="{ row }">
          <div class="user-cell">
            <span>{{ row.username }}</span>
            <span class="phone">{{ row.phone }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="最近测评" width="160">
        <template #default="{ row }">{{ formatTime(row.last_assessment_time) }}</template>
      </el-table-column>
      <el-table-column label="GSI" width="80" align="center">
        <template #default="{ row }"><strong :style="{ color: gsiColor(row.gsi) }">{{ row.gsi }}</strong></template>
      </el-table-column>
      <el-table-column label="风险" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.overall_risk === 'red' ? 'danger' : 'warning'" effect="dark" size="small">
            {{ riskText(row.overall_risk) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="抑郁/焦虑" width="120" align="center">
        <template #default="{ row }">{{ row.dep_score }} / {{ row.anx_score }}</template>
      </el-table-column>
      <el-table-column label="子量表" min-width="200">
        <template #default="{ row }">
          <el-tag v-for="s in row.subscale_severities" :key="s.code" size="small" class="mr-6"
            :type="sevTag(s.severity)" effect="plain">
            {{ s.code }}：{{ s.label }}
          </el-tag>
          <span v-if="!row.subscale_severities.length">—</span>
        </template>
      </el-table-column>
      <el-table-column label="负责专业人员" min-width="160">
        <template #default="{ row }">
          <span v-if="row.assigned_professional">{{ row.assigned_professional }}</span>
          <el-tag v-else type="info" size="small" effect="plain">未分配</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" align="center" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="$router.push(`/admin/records`)">查看数据</el-button>
          <el-button type="success" link @click="openAssign(row)">分配</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="assignDialog" title="分配负责专业人员" width="440px">
      <div class="assign-tip">将用户 <b>{{ current?.username }}</b> 分配给：</div>
      <el-select v-model="assignProId" placeholder="选择专业人员" style="width: 100%;" v-loading="prosLoading">
        <el-option v-for="p in professionals" :key="p.id" :label="`${p.username}（${roleLabel(p.role)}）现有${p.patient_count}人`" :value="p.id" />
      </el-select>
      <el-input v-model="assignNote" class="mt-12" placeholder="分配备注（可选）" />
      <template #footer>
        <el-button @click="assignDialog = false">取消</el-button>
        <el-button type="primary" :loading="assigning" @click="doAssign">确认分配</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { adminApi, clinicApi } from '@/api'
import type { HighRiskItem, ProfessionalItem } from '@/types'

const loading = ref(false)
const items = ref<HighRiskItem[]>([])
const riskFilter = ref('red,yellow')

const assignDialog = ref(false)
const current = ref<HighRiskItem | null>(null)
const professionals = ref<ProfessionalItem[]>([])
const prosLoading = ref(false)
const assignProId = ref<number | null>(null)
const assignNote = ref('')
const assigning = ref(false)

async function load() {
  loading.value = true
  try {
    const res: any = await adminApi.getHighRisk({ risk: riskFilter.value })
    items.value = res.items || []
  } finally {
    loading.value = false
  }
}

async function loadProfessionals() {
  prosLoading.value = true
  try {
    const res: any = await adminApi.getProfessionals()
    professionals.value = res.items || []
  } finally {
    prosLoading.value = false
  }
}

function openAssign(row: HighRiskItem) {
  current.value = row
  assignProId.value = row.assigned_professional_id ?? null
  assignNote.value = ''
  assignDialog.value = true
  if (!professionals.value.length) loadProfessionals()
}

async function doAssign() {
  if (!current.value || !assignProId.value) { ElMessage.warning('请选择专业人员'); return }
  assigning.value = true
  try {
    await clinicApi.createAssignment({
      patient: current.value.user_id,
      professional: assignProId.value,
      is_active: true,
      note: assignNote.value,
    })
    ElMessage.success('已分配并通知专业人员')
    assignDialog.value = false
    await load()
  } finally {
    assigning.value = false
  }
}

function formatTime(t: string) { return new Date(t).toLocaleString('zh-CN') }
function riskText(r: string) { return r === 'red' ? '高危' : r === 'yellow' ? '中危' : '正常' }
function gsiColor(g: number) { return g < 2 ? '#67c23a' : g < 3 ? '#e6a23c' : '#f56c6c' }
function roleLabel(r: string) { return r === 'doctor' ? '医生' : '心理咨询师' }
function sevTag(sev: string): 'success' | 'warning' | 'danger' | 'info' {
  if (sev === 'minimal') return 'success'
  if (sev === 'mild') return 'info'
  if (sev === 'moderate') return 'warning'
  return 'danger'
}

onMounted(load)
</script>

<style scoped>
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 12px; }
.filters { display: flex; gap: 8px; }
.section-title { font-size: 16px; font-weight: 600; color: #303133; border-left: 4px solid #f56c6c; padding-left: 10px; }
.user-cell { display: flex; flex-direction: column; }
.user-cell .phone { font-size: 12px; color: #909399; }
.mr-6 { margin-right: 6px; margin-bottom: 4px; }
.assign-tip { margin-bottom: 12px; color: #606266; }
.mt-12 { margin-top: 12px; }
.mb-12 { margin-bottom: 12px; }
</style>
