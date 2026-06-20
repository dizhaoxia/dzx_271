<template>
  <el-card class="card-shadow mb-16" v-loading="loading">
    <div class="section-title">我的患者</div>
    <el-alert
      v-if="!assignments.length && !loading"
      type="info"
      :closable="false"
      show-icon
      title="暂无分配给您的患者"
      description="请联系管理员将患者分配给您，分配后即可查看其测评数据并记录随访。"
    />
    <el-table v-else :data="assignments" stripe>
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column label="患者" min-width="160">
        <template #default="{ row }">
          <div class="patient-cell">
            <el-icon color="#67c23a"><User /></el-icon>
            <span>{{ row.patient_name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="手机号(脱敏)" width="160">
        <template #default="{ row }">{{ row.patient_phone }}</template>
      </el-table-column>
      <el-table-column label="分配备注" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">{{ row.note || '—' }}</template>
      </el-table-column>
      <el-table-column label="分配时间" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '进行中' : '已结束' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" align="center" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="$router.push(`/clinic/patient/${row.patient}`)">查看档案</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { clinicApi } from '@/api'
import type { PatientAssignment } from '@/types'
import { User } from '@element-plus/icons-vue'

const loading = ref(false)
const assignments = ref<PatientAssignment[]>([])

async function load() {
  loading.value = true
  try {
    const res: any = await clinicApi.getAssignments({ is_active: 'true' })
    assignments.value = res.results || res.data || res || []
  } finally {
    loading.value = false
  }
}

function formatTime(t: string) { return new Date(t).toLocaleString('zh-CN') }

onMounted(load)
</script>

<style scoped>
.section-title {
  font-size: 16px; font-weight: 600; color: #303133;
  border-left: 4px solid #67c23a; padding-left: 10px; margin-bottom: 16px;
}
.patient-cell { display: flex; align-items: center; gap: 6px; }
</style>
