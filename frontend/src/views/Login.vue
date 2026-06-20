<template>
  <div class="auth-page">
    <div class="auth-card card-shadow">
      <div class="auth-header">
        <el-icon :size="44" color="#409eff"><Notebook /></el-icon>
        <h1 class="auth-title">SCL-90 症状自评量表</h1>
        <p class="auth-subtitle">科学评估 · 专业分析 · 守护心理健康</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" size="large" label-position="top">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" :prefix-icon="Phone">
            <template #prepend>+86</template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
            :prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <div class="auth-links">
          <el-checkbox v-model="remember">记住密码</el-checkbox>
          <el-link type="primary" :underline="false" @click="$router.push('/forgot-password')">忘记密码？</el-link>
        </div>
        <el-form-item>
          <el-button type="primary" class="submit-btn" :loading="loading" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="auth-footer">
        还没有账号？
        <el-link type="primary" :underline="false" @click="$router.push('/register')">立即注册</el-link>
      </div>
      <el-alert v-if="demoInfo" class="mt-16" type="info" :closable="false" show-icon>
        <template #title>
          <div>演示账号：手机号 <strong>13800138000</strong>，密码 <strong>admin123</strong>（管理员）</div>
        </template>
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Phone, Lock, Notebook } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const remember = ref(true)
const demoInfo = ref(true)

const form = reactive({
  phone: '',
  password: '',
})

const rules: FormRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
}

onMounted(() => {
  const savedPhone = localStorage.getItem('remember_phone')
  const savedPwd = localStorage.getItem('remember_pwd')
  if (savedPhone && savedPwd) {
    form.phone = savedPhone
    form.password = savedPwd
  }
})

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  try {
    loading.value = true
    await authStore.login(form.phone, form.password)
    if (remember.value) {
      localStorage.setItem('remember_phone', form.phone)
      localStorage.setItem('remember_pwd', form.password)
    } else {
      localStorage.removeItem('remember_phone')
      localStorage.removeItem('remember_pwd')
    }
    ElMessage.success('登录成功')
    const redirect = (route.query.redirect as string) || '/home'
    router.replace(redirect)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}
.auth-card {
  width: 100%;
  max-width: 440px;
  background: #fff;
  border-radius: 12px;
  padding: 40px 40px 32px;
}
.auth-header { text-align: center; margin-bottom: 28px; }
.auth-title {
  margin: 12px 0 6px;
  font-size: 24px;
  background: linear-gradient(90deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.auth-subtitle { color: #909399; margin: 0; font-size: 13px; }
.auth-links { display: flex; justify-content: space-between; margin: -8px 0 16px; }
.submit-btn { width: 100%; height: 44px; }
.auth-footer { text-align: center; color: #606266; font-size: 14px; }
</style>
