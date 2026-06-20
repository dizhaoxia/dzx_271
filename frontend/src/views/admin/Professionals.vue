<template>
  <el-card class="card-shadow mb-16" v-loading="loading">
    <div class="header-row">
      <div class="section-title">专业人员列表</div>
      <el-button @click="load" :icon="Refresh">刷新</el-button>
    </div>
    <el-empty v-if="!items.length && !loading" description="暂无专业人员，可在用户列表中将用户设为医生/咨询师" />
    <el-table v-else :data="items" stripe>
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column label="姓名" min-width="140">
        <template #default="{ row }">{{ row.username }}</template>
      </el-table-column>
      <el-table-column label="角色" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="row.role === 'doctor' ? 'warning' : 'success'" effect="plain">{{ roleLabel(row.role) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="职称" min-width="140">
        <template #default="{ row }">{{ row.title || '—' }}</template>
      </el-table-column>
      <el-table-column label="执照编号" min-width="160">
        <template #default="{ row }">{{ row.license_no || '—' }}</template>
      </el-table-column>
      <el-table-column label="手机号(脱敏)" width="160">
        <template #default="{ row }">{{ row.phone }}</template>
      </el-table-column>
      <el-table-column label="负责患者数" width="120" align="center">
        <template #default="{ row }"><el-tag type="primary" effect="dark">{{ row.patient_count }}</el-tag></template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { adminApi } from '@/api'
import type { ProfessionalItem } from '@/types'

const loading = ref(false)
const items = ref<ProfessionalItem[]>([])

async function load() {
  loading.value = true
  try {
    const res: any = await adminApi.getProfessionals()
    items.value = res.items || []
  } finally {
    loading.value = false
  }
}

function roleLabel(r: string) { return r === 'doctor' ? '医生' : '心理咨询师' }

onMounted(load)
</script>

<style scoped>
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.section-title { font-size: 16px; font-weight: 600; color: #303133; border-left: 4px solid #409eff; padding-left: 10px; }
</style>
