<template>
  <div class="auth-page">
    <div class="auth-card card-shadow">
      <div class="auth-header">
        <el-icon :size="44" color="#e6a23c"><Key /></el-icon>
        <h1 class="auth-title">找回密码</h1>
        <p class="auth-subtitle">输入手机号获取验证码重置密码</p>
      </div>
      <el-steps :active="step" simple class="mt-16 mb-24">
        <el-step title="验证手机" />
        <el-step title="重置密码" />
        <el-step title="完成" />
      </el-steps>

      <el-form v-if="step === 1" ref="formRef1" :model="form1" :rules="rules1" size="large" label-position="top">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form1.phone" placeholder="请输入注册手机号" :prefix-icon="Phone">
            <template #prepend>+86</template>
          </el-input>
        </el-form-item>
        <el-form-item label="验证码" prop="code">
          <div class="code-row">
            <el-input v-model="form1.code" placeholder="请输入验证码" :prefix-icon="Lock" />
            <el-button :disabled="countdown > 0" @click="sendCode">
              {{ countdown > 0 ? `${countdown}s后重发` : '获取验证码' }}
            </el-button>
          </div>
          <div v-if="fakeCode" class="demo-tip">
            演示模式：验证码已发送（实际验证码为 <strong>{{ fakeCode }}</strong>）
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="warning" class="submit-btn" @click="nextStep">下一步</el-button>
        </el-form-item>
      </el-form>

      <el-form v-if="step === 2" ref="formRef2" :model="form2" :rules="rules2" size="large" label-position="top">
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="form2.new_password" type="password" placeholder="请输入新密码" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input v-model="form2.confirm_password" type="password" placeholder="再次输入新密码" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item>
          <el-button type="warning" class="submit-btn" @click="resetPassword">确认重置</el-button>
        </el-form-item>
      </el-form>

      <div v-if="step === 3" class="text-center mt-24 mb-24">
        <el-icon :size="64" color="#67c23a"><CircleCheck /></el-icon>
        <div class="success-text mt-16">密码重置成功！</div>
        <el-button class="mt-24" type="primary" @click="$router.replace('/login')">
          返回登录
        </el-button>
      </div>

      <div class="auth-footer">
        <el-link type="primary" :underline="false" @click="$router.push('/login')">← 返回登录</el-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Phone, Lock, Key, CircleCheck } from '@element-plus/icons-vue'
import { authApi } from '@/api'

const router = useRouter()
const step = ref(1)
const countdown = ref(0)
const fakeCode = ref('')
const formRef1 = ref<FormInstance>()
const formRef2 = ref<FormInstance>()

const form1 = reactive({ phone: '', code: '' })
const form2 = reactive({ new_password: '', confirm_password: '' })

const rules1: FormRules = {
  phone: [{ required: true, pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }],
  code: [{ required: true, len: 6, message: '请输入6位验证码', trigger: 'blur' }],
}

const rules2: FormRules = {
  new_password: [{ required: true, min: 6, message: '密码至少6位', trigger: 'blur' }],
  confirm_password: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: (_r, v, cb) => v === form2.new_password ? cb() : cb(new Error('两次密码不一致')), trigger: 'blur' }
  ],
}

async function sendCode() {
  if (!/^1[3-9]\d{9}$/.test(form1.phone)) {
    ElMessage.warning('请先输入正确的手机号')
    return
  }
  try {
    const res: any = await authApi.requestPasswordReset(form1.phone)
    fakeCode.value = res.code
    ElMessage.success('验证码已发送')
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) clearInterval(timer)
    }, 1000)
  } catch (e: any) { /* api handled */ }
}

async function nextStep() {
  const valid = await formRef1.value?.validate().catch(() => false)
  if (!valid) return
  if (fakeCode.value && form1.code !== fakeCode.value) {
    ElMessage.error('验证码错误')
    return
  }
  step.value = 2
}

async function resetPassword() {
  const valid = await formRef2.value?.validate().catch(() => false)
  if (!valid) return
  try {
    await authApi.confirmPasswordReset({
      phone: form1.phone,
      code: form1.code,
      new_password: form2.new_password,
      confirm_password: form2.confirm_password,
    })
    step.value = 3
  } catch (e: any) { /* api handled */ }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 20px;
}
.auth-card {
  width: 100%;
  max-width: 480px;
  background: #fff;
  border-radius: 12px;
  padding: 36px 40px 28px;
}
.auth-header { text-align: center; margin-bottom: 8px; }
.auth-title { margin: 12px 0 6px; font-size: 24px; color: #303133; }
.auth-subtitle { color: #909399; margin: 0; font-size: 13px; }
.code-row { display: flex; gap: 10px; }
.code-row .el-input { flex: 1; }
.demo-tip { margin-top: 8px; font-size: 12px; color: #e6a23c; }
.submit-btn { width: 100%; height: 44px; }
.auth-footer { text-align: center; }
.success-text { font-size: 20px; color: #67c23a; font-weight: 600; }
</style>
