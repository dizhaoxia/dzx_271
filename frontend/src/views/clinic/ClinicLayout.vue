<template>
  <Layout>
    <div class="page-container">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="6" :md="5" :lg="4">
          <el-card class="card-shadow side-menu">
            <div class="menu-title">
              <el-icon :size="20" color="#67c23a"><UserFilled /></el-icon>
              专业端工作台
            </div>
            <el-menu
              :default-active="activeMenu"
              router
              class="clinic-menu"
              background-color="#fff"
              text-color="#606266"
              active-text-color="#67c23a"
            >
              <el-menu-item index="/clinic">
                <el-icon><User /></el-icon>
                <span>我的患者</span>
              </el-menu-item>
            </el-menu>
            <div class="role-box">
              <el-tag :type="roleTagType" effect="plain">{{ roleLabel }}</el-tag>
              <div class="role-name">{{ userInfo?.title || userInfo?.username }}</div>
            </div>
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
import { useAuthStore } from '@/stores/auth'
import { UserFilled, User } from '@element-plus/icons-vue'

const route = useRoute()
const authStore = useAuthStore()
const userInfo = computed(() => authStore.userInfo)
const roleLabel = computed(() => authStore.role === 'doctor' ? '医生' : '心理咨询师')
const roleTagType = computed<'success' | 'warning' | 'info'>(() =>
  authStore.role === 'doctor' ? 'warning' : 'success')

const activeMenu = ref(route.path)
watch(() => route.path, (p) => { activeMenu.value = p.startsWith('/clinic') ? '/clinic' : p })
</script>

<style scoped>
.side-menu { padding: 16px 0; min-height: 420px; }
.menu-title {
  padding: 0 20px 16px; display: flex; align-items: center; gap: 8px;
  font-weight: 700; font-size: 16px; color: #303133;
  border-bottom: 1px solid #ebeef5; margin-bottom: 8px;
}
.clinic-menu { border: none; }
.clinic-menu .el-menu-item { border-radius: 6px; margin: 4px 8px; height: 44px; line-height: 44px; }
.clinic-menu .el-menu-item.is-active { background: #f0f9eb; }
.role-box { padding: 16px 20px; border-top: 1px solid #ebeef5; margin-top: 8px; }
.role-name { margin-top: 8px; font-weight: 600; color: #303133; }
.fade-enter-active, .fade-leave-active { transition: opacity .2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
