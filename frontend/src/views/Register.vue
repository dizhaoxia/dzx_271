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
        <el-form-item prop="consent">
          <el-checkbox v-model="form.consent">
            我已阅读并同意
            <el-link type="primary" :underline="false" @click.prevent="showConsentText = true">《数据隐私与授权协议》</el-link>
          </el-checkbox>
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

    <el-dialog v-model="showConsentText" title="数据隐私与授权协议" width="600px" align-center>
      <div class="consent-text">
        <p><b>1. 数据收集范围：</b>收集您在心理健康测评中提交的作答数据及基本账号信息。</p>
        <p><b>2. 数据用途：</b>仅用于心理健康评估、生成报告及（如您被分配）专业人员的随访干预，不用于商业营销。</p>
        <p><b>3. 数据脱敏：</b>对外展示与专业人员查看时，手机号等敏感信息将进行脱敏处理。</p>
        <p><b>4. 操作审计：</b>所有访问、导出、修改测评数据的行为均记录操作日志，可追溯。</p>
        <p><b>5. 您的权利：</b>您有权随时查看、更正、删除自己的数据，并可撤销同意。</p>
        <p><b>6. 数据安全：</b>数据加密传输并安全存储，仅授权人员可在职责范围内访问。</p>
      </div>
    </el-dialog>
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
  consent: false,
})

const showConsentText = ref(false)

const validateConfirm = (_r: any, value: string, cb: any) => {
  if (!value) return cb(new Error('请再次输入密码'))
  if (value !== form.password) return cb(new Error('两次密码输入不一致'))
  cb()
}
const validateConsent = (_r: any, _value: any, cb: any) => {
  if (!form.consent) return cb(new Error('请阅读并同意隐私授权协议'))
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
  consent: [
    { validator: validateConsent, trigger: 'change' },
  ],
}

async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  try {
    loading.value = true
    await authStore.register({
      phone: form.phone,
      password: form.password,
      confirm_password: form.confirm_password,
      username: form.username,
      email: form.email,
      gender: form.gender,
      consent_accepted: form.consent,
    })
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
.consent-text { max-height: 360px; overflow-y: auto; color: #606266; line-height: 1.8; font-size: 14px; }
.consent-text p { margin: 6px 0; }
</style>
