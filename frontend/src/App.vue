<template>
  <el-config-provider :locale="zhCn" size="default">
    <router-view />
    <ConsentDialog v-model="showConsent" :version="consentVersion" @accepted="onConsentAccepted" />
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import ConsentDialog from '@/components/ConsentDialog.vue'
import { useAuthStore } from '@/stores/auth'
import { useAdaptiveStore } from '@/stores/adaptive'
import { authApi } from '@/api'

const authStore = useAuthStore()
const adaptiveStore = useAdaptiveStore()
const showConsent = ref(false)
const consentVersion = ref<string>('')

async function checkConsent() {
  if (!authStore.isLoggedIn) return
  try {
    const info: any = await authApi.getConsent()
    consentVersion.value = info.current_version
    if (!info.consent_accepted || info.needs_reconsent) {
      showConsent.value = true
    }
  } catch {
    /* ignore */
  }
}

function onConsentAccepted() {
  showConsent.value = false
}

// 离线缓存已答题目，网络恢复后自动提交
async function handleOnline() {
  const res = await adaptiveStore.tryAutoSubmit()
  if (res) {
    ElMessage.success('网络已恢复，您的测评已自动提交成功')
  }
}

watch(() => authStore.accessToken, (tok) => {
  if (tok) checkConsent()
}, { immediate: true })

onMounted(() => {
  window.addEventListener('online', handleOnline)
  if (navigator.onLine) handleOnline()
})
onBeforeUnmount(() => {
  window.removeEventListener('online', handleOnline)
})
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}
</style>
