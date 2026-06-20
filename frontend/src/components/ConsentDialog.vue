<template>
  <el-dialog
    v-model="visible"
    title="数据隐私与同意授权"
    width="640px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    align-center
  >
    <div class="consent-body">
      <el-alert type="info" :closable="false" show-icon class="mb-12"
        title="依据 GDPR 级别的数据保护要求，请您在继续使用前阅读并同意以下条款。" />
      <div class="consent-text">
        <p><b>1. 数据收集范围：</b>本系统收集您在心理健康测评中提交的作答数据、基本账号信息（手机号、昵称）及相关测评结果。</p>
        <p><b>2. 数据用途：</b>仅用于心理健康评估、生成报告、趋势对比及（如您被分配）专业人员的随访干预。数据不会用于商业营销。</p>
        <p><b>3. 数据脱敏：</b>对外展示与专业人员查看时，手机号等敏感信息将进行脱敏处理（如 138****56）。</p>
        <p><b>4. 操作审计：</b>所有访问、导出、修改测评数据的行为均记录操作日志，可追溯，保障数据安全。</p>
        <p><b>5. 您的权利：</b>您有权随时查看、更正、删除自己的数据，并可撤销同意。撤销后系统将停止处理您的相关数据。</p>
        <p><b>6. 数据存储与传输：</b>数据加密传输并安全存储，仅授权人员可在职责范围内访问。</p>
      </div>
      <el-checkbox v-model="agreed" class="mt-12">
        我已阅读并同意《数据隐私与授权协议》{{ version ? `（版本 ${version}）` : '' }}
      </el-checkbox>
    </div>
    <template #footer>
      <el-button type="primary" :loading="submitting" :disabled="!agreed" @click="confirm">同意并继续</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{ modelValue: boolean; version?: string }>()
const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'accepted'): void
}>()

const authStore = useAuthStore()
const agreed = ref(false)
const submitting = ref(false)

const visible = ref(props.modelValue)
watch(() => props.modelValue, (v) => {
  visible.value = v
  if (v) agreed.value = false
})
watch(visible, (v) => emit('update:modelValue', v))

async function confirm() {
  submitting.value = true
  try {
    await authApi.acceptConsent()
    await authStore.fetchProfile()
    ElMessage.success('已记录您的同意授权')
    emit('accepted')
    visible.value = false
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.consent-text { max-height: 280px; overflow-y: auto; color: #606266; line-height: 1.8; font-size: 14px; }
.consent-text p { margin: 6px 0; }
.mt-12 { margin-top: 12px; }
.mb-12 { margin-bottom: 12px; }
</style>
