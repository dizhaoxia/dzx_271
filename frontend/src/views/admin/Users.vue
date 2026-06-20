<template>
  <div>
    <el-card class="card-shadow mb-16">
      <div class="toolbar">
        <div class="section-title" style="border:none; padding:0; margin:0;">
          <el-icon :size="22" color="#409eff"><User /></el-icon>
          用户列表
        </div>
        <div class="tool-actions">
          <el-input v-model="search" placeholder="搜索手机号/昵称/邮箱" clearable style="width: 260px;" :prefix-icon="Search" />
          <el-button type="primary" :icon="Refresh" @click="loadData">刷新</el-button>
        </div>
      </div>

      <el-table :data="users" stripe v-loading="loading">
        <el-table-column type="index" label="#" width="60" align="center" />
        <el-table-column label="ID" prop="id" width="70" align="center" />
        <el-table-column label="手机号" prop="phone" width="140" sortable />
        <el-table-column label="昵称" prop="username" min-width="120" />
        <el-table-column label="邮箱" prop="email" min-width="180" show-overflow-tooltip />
        <el-table-column label="性别" width="80" align="center">
          <template #default="{ row }">
            {{ { male: '男', female: '女', other: '保密' }[row.gender || 'other'] }}
          </template>
        </el-table-column>
        <el-table-column label="年龄" prop="age" width="80" align="center" />
        <el-table-column label="管理员" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_staff" type="danger" effect="light" size="small">是</el-tag>
            <span v-else style="color:#909399;">否</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_active" type="success" effect="light" size="small">正常</el-tag>
            <el-tag v-else type="info" size="small">禁用</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="170" sortable prop="created_at">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
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
import { Search, Refresh, User } from '@element-plus/icons-vue'
import { adminApi } from '@/api'

const loading = ref(false)
const users = ref<any[]>([])
const page = ref(1)
const pageSize = ref(15)
const total = ref(0)
const search = ref('')

async function loadData() {
  try {
    loading.value = true
    const params: any = { page: page.value, page_size: pageSize.value }
    if (search.value) params.search = search.value
    const res: any = await adminApi.getUsers(params)
    users.value = res.results || res.data || res || []
    total.value = res.count || users.value.length
  } finally {
    loading.value = false
  }
}

function formatTime(t: string) {
  return t ? new Date(t).toLocaleString('zh-CN') : '-'
}

let t: any = null
watch(search, () => {
  clearTimeout(t)
  t = setTimeout(() => { page.value = 1; loadData() }, 400)
})
onMounted(loadData)
</script>

<style scoped>
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.tool-actions { display: flex; gap: 10px; }
.pager { display: flex; justify-content: center; margin-top: 20px; }
</style>
