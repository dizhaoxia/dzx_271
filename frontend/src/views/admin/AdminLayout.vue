<template>
  <Layout>
    <div class="page-container">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="6" :md="5" :lg="4">
          <el-card class="card-shadow side-menu">
            <div class="menu-title">
              <el-icon :size="20" color="#409eff"><Setting /></el-icon>
              管理后台
            </div>
            <el-menu
              :default-active="activeMenu"
              router
              class="admin-menu"
              background-color="#fff"
              text-color="#606266"
              active-text-color="#409eff"
            >
              <el-menu-item index="/admin/dashboard">
                <el-icon><DataAnalysis /></el-icon>
                <span>统计仪表盘</span>
              </el-menu-item>
              <el-menu-item index="/admin/users">
                <el-icon><User /></el-icon>
                <span>用户列表</span>
              </el-menu-item>
              <el-menu-item index="/admin/records">
                <el-icon><Document /></el-icon>
                <span>测评数据</span>
              </el-menu-item>
              <el-menu-item index="/admin/high-risk">
                <el-icon><WarnTriangleFilled /></el-icon>
                <span>高危人群</span>
              </el-menu-item>
              <el-menu-item index="/admin/professionals">
                <el-icon><UserFilled /></el-icon>
                <span>专业人员</span>
              </el-menu-item>
              <el-menu-item index="/admin/audit-logs">
                <el-icon><Lock /></el-icon>
                <span>操作审计</span>
              </el-menu-item>
            </el-menu>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="18" :md="19" :lg="20">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-col>
      </el-row>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { Setting, DataAnalysis, User, Document, WarnTriangleFilled, UserFilled, Lock } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = ref(route.path)
watch(() => route.path, (p) => { activeMenu.value = p })
</script>

<style scoped>
.side-menu { padding: 16px 0; }
.menu-title {
  padding: 0 20px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 16px;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 8px;
}
.admin-menu { border: none; }
.admin-menu .el-menu-item {
  border-radius: 6px;
  margin: 4px 8px;
  height: 44px;
  line-height: 44px;
}
.admin-menu .el-menu-item.is-active { background: #ecf5ff; }
.fade-enter-active, .fade-leave-active { transition: opacity .2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
