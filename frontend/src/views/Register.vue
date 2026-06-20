<template>
  <div class="auth-page">
    <div class="auth-card card-shadow">
      <div class="auth-header">
        <el-icon :size="44" color="#67c23a"><Avatar /></el-icon>
        <h1 class="auth-title">创建新账号</h1>
        <p class="auth-subtitle">完成注册即可开始心理健康测评</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" size="large" label-position="top">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" :prefix-icon="Phone">
            <template #prepend>+86</template>
          </el-input>
        </el-form-item>
        <el-form-item label="昵称" prop="username">
          <el-input v-model="form.username" placeholder="请输入昵称（可选）" :prefix-icon="User" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱（可选）" :prefix-icon="Message" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio value="male">男</el-radio>
            <el-radio value="female">女</el-radio>
            <el-radio value="other">保密</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="至少6位" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="form.confirm_password" type="password" placeholder="再次输入密码" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item>
          <el-button type="success" class="submit-btn" :loading="loading" @click="handleRegister">
            立即注册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="auth-footer">
        已有账号？
        <el-link type="primary" :underline="false" @click="$router.push('/login')">去登录</el-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Phone, User, Lock, Message, Avatar } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  phone: '',
  username: '',
  email: '',
  gender: 'other',
  password: '',
  confirm_password: '',
})

const validateConfirm = (_r: any, value: string, cb: any) => {
  if (!value) return cb(new Error('请再次输入密码'))
  if (value !== form.password) return cb(new Error('两次密码输入不一致'))
  cb()
}

const rules: FormRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, validator: validateConfirm, trigger: 'blur' },
  ],
}

async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  try {
    loading.value = true
    await authStore.register(form)
    ElMessage.success('注册成功')
    router.replace('/home')
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
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
  padding: 20px;
}
.auth-card {
  width: 100%;
  max-width: 480px;
  background: #fff;
  border-radius: 12px;
  padding: 36px 40px 28px;
}
.auth-header { text-align: center; margin-bottom: 24px; }
.auth-title { margin: 12px 0 6px; font-size: 24px; color: #303133; }
.auth-subtitle { color: #909399; margin: 0; font-size: 13px; }
.submit-btn { width: 100%; height: 44px; }
.auth-footer { text-align: center; color: #606266; font-size: 14px; }
</style>
