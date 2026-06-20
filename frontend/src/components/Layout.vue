<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="header-inner page-container">
        <div class="logo-area" @click="$router.push('/home')">
          <el-icon :size="28" color="#409eff"><Notebook /></el-icon>
          <span class="logo-text">SCL-90 症状自评量表</span>
        </div>
        <el-menu mode="horizontal" :default-active="activeMenu" class="nav-menu" router>
          <el-menu-item index="/home">首页</el-menu-item>
          <el-menu-item index="/questionnaire">开始测评</el-menu-item>
          <el-menu-item index="/history">历史记录</el-menu-item>
          <el-menu-item v-if="isProfessional" index="/clinic">专业端</el-menu-item>
          <el-menu-item v-if="isStaff" index="/admin/dashboard">管理后台</el-menu-item>
          <el-menu-item index="/profile">个人中心</el-menu-item>
        </el-menu>
        <div class="user-area">
          <el-dropdown @command="handleCommand">
            <span class="user-name">
              <el-icon><UserFilled /></el-icon>
              {{ userInfo?.username || '用户' }}
              <el-icon><CaretBottom /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><Setting /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item v-if="isStaff" command="admin">
                  <el-icon><DataAnalysis /></el-icon>管理后台
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>
    <el-main class="layout-main">
      <transition name="fade" mode="out-in">
        <slot />
      </transition>
    </el-main>
    <el-footer class="layout-footer">
      <div class="footer-inner">
        © 2024 SCL-90 症状自评量表系统 | 心理健康自测工具
      </div>
    </el-footer>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { User } from '@/types'
import { Notebook, UserFilled, CaretBottom, Setting, DataAnalysis, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const userInfo = computed<User | null>(() => authStore.userInfo)
const isStaff = computed(() => authStore.isStaff)
const isProfessional = computed(() => authStore.isProfessional)

const activeMenu = ref(route.path)
watch(
  () => route.path,
  (p) => {
    if (p.startsWith('/admin')) activeMenu.value = '/admin/dashboard'
    else if (p.startsWith('/clinic')) activeMenu.value = '/clinic'
    else activeMenu.value = p
  }
)

async function handleCommand(cmd: string) {
  if (cmd === 'profile') router.push('/profile')
  else if (cmd === 'admin') router.push('/admin/dashboard')
  else if (cmd === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' })
      await authStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch (e) {
      // cancel
    }
  }
}
</script>

<style scoped>
.layout-container { min-height: 100vh; display: flex; flex-direction: column; background: var(--bg-gray); }
.layout-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 24px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}
.logo-area { display: flex; align-items: center; cursor: pointer; }
.logo-text {
  font-size: 20px;
  font-weight: 700;
  margin-left: 10px;
  background: linear-gradient(90deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.nav-menu { flex: 1; border-bottom: none; margin: 0 24px; justify-content: center; }
.user-area { min-width: 140px; text-align: right; }
.user-name {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 4px;
  transition: background .2s;
}
.user-name:hover { background: #f5f7fa; }
.layout-main { flex: 1; padding: 0; }
.layout-footer {
  background: #fff;
  border-top: 1px solid #e4e7ed;
  padding: 16px;
  text-align: center;
  color: #909399;
  font-size: 13px;
}
.fade-enter-active, .fade-leave-active { transition: opacity .2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
