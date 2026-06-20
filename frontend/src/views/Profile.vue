<template>
  <Layout>
    <div class="page-container">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="card-shadow profile-card">
            <div class="avatar-area">
              <el-avatar :size="88">
                {{ userInfo?.username?.charAt(0) || 'U' }}
              </el-avatar>
              <h3 class="mt-12">{{ userInfo?.username }}</h3>
              <div class="phone mt-8">{{ userInfo?.phone }}</div>
              <el-tag v-if="userInfo?.is_staff" type="danger" effect="light" class="mt-8">管理员</el-tag>
              <el-tag v-else type="primary" effect="light" class="mt-8">普通用户</el-tag>
            </div>
            <el-divider />
            <div class="info-list">
              <div class="info-item">
                <span class="info-label">注册时间</span>
                <span class="info-value">{{ formatTime(userInfo?.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">邮箱</span>
                <span class="info-value">{{ userInfo?.email || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">性别</span>
                <span class="info-value">{{ genderText(userInfo?.gender) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">年龄</span>
                <span class="info-value">{{ userInfo?.age ? userInfo.age + ' 岁' : '未设置' }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="16">
          <el-tabs v-model="activeTab" class="card-shadow">
            <el-tab-pane label="基本信息" name="info">
              <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" size="large">
                <el-form-item label="昵称" prop="username">
                  <el-input v-model="form.username" placeholder="请输入昵称" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="form.email" placeholder="请输入邮箱" />
                </el-form-item>
                <el-form-item label="性别">
                  <el-radio-group v-model="form.gender">
                    <el-radio value="male">男</el-radio>
                    <el-radio value="female">女</el-radio>
                    <el-radio value="other">保密</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item label="年龄">
                  <el-input-number v-model="form.age" :min="1" :max="120" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :loading="saving" @click="saveProfile">保存修改</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            <el-tab-pane label="修改密码" name="password">
              <el-form :model="pwdForm" :rules="pwdRules" ref="pwdFormRef" label-width="120px" size="large">
                <el-form-item label="原密码" prop="old_password">
                  <el-input v-model="pwdForm.old_password" type="password" show-password />
                </el-form-item>
                <el-form-item label="新密码" prop="new_password">
                  <el-input v-model="pwdForm.new_password" type="password" show-password />
                </el-form-item>
                <el-form-item label="确认新密码" prop="confirm_password">
                  <el-input v-model="pwdForm.confirm_password" type="password" show-password />
                </el-form-item>
                <el-form-item>
                  <el-button type="warning" :loading="pwdSaving" @click="savePassword">修改密码</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            <el-tab-pane label="快捷入口" name="quick">
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-card class="quick-card" shadow="hover" @click="$router.push('/questionnaire')">
                    <el-icon :size="36" color="#409eff"><EditPen /></el-icon>
                    <div class="q-title mt-12">开始测评</div>
                    <div class="q-desc mt-8">填写 SCL-90 症状自评量表</div>
                  </el-card>
                </el-col>
                <el-col :span="12">
                  <el-card class="quick-card" shadow="hover" @click="$router.push('/history')">
                    <el-icon :size="36" color="#67c23a"><History /></el-icon>
                    <div class="q-title mt-12">历史记录</div>
                    <div class="q-desc mt-8">查看过往测评报告与趋势</div>
                  </el-card>
                </el-col>
                <el-col v-if="userInfo?.is_staff" :span="12">
                  <el-card class="quick-card" shadow="hover" @click="$router.push('/admin/dashboard')">
                    <el-icon :size="36" color="#e6a23c"><DataAnalysis /></el-icon>
                    <div class="q-title mt-12">管理后台</div>
                    <div class="q-desc mt-8">数据统计与用户管理</div>
                  </el-card>
                </el-col>
                <el-col :span="12">
                  <el-card class="quick-card" shadow="hover" @click="logout">
                    <el-icon :size="36" color="#f56c6c"><SwitchButton /></el-icon>
                    <div class="q-title mt-12">退出登录</div>
                    <div class="q-desc mt-8">退出当前账号</div>
                  </el-card>
                </el-col>
              </el-row>
            </el-tab-pane>
          </el-tabs>
        </el-col>
      </el-row>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import Layout from '@/components/Layout.vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api'

const router = useRouter()
const authStore = useAuthStore()
const userInfo = computed(() => authStore.userInfo)

const activeTab = ref('info')
const saving = ref(false)
const pwdSaving = ref(false)
const formRef = ref<FormInstance>()
const pwdFormRef = ref<FormInstance>()

const form = reactive({ username: '', email: '', gender: 'other' as any, age: null as number | null })
const pwdForm = reactive({ old_password: '', new_password: '', confirm_password: '' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
}
const pwdRules: FormRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_r, v, cb) => v === pwdForm.new_password ? cb() : cb(new Error('两次密码不一致')),
      trigger: 'blur',
    },
  ],
}

function formatTime(t?: string) { return t ? new Date(t).toLocaleString('zh-CN') : '-' }
function genderText(g?: string) {
  return { male: '男', female: '女', other: '保密' }[g || 'other']
}

onMounted(() => {
  if (userInfo.value) {
    form.username = userInfo.value.username
    form.email = userInfo.value.email || ''
    form.gender = userInfo.value.gender || 'other'
    form.age = userInfo.value.age ?? null
  }
})

async function saveProfile() {
  const ok = await formRef.value?.validate().catch(() => false)
  if (!ok) return
  try {
    saving.value = true
    const user = await authApi.updateProfile(form)
    authStore.setUser(user as any)
    ElMessage.success('信息已更新')
  } finally {
    saving.value = false
  }
}

async function savePassword() {
  const ok = await pwdFormRef.value?.validate().catch(() => false)
  if (!ok) return
  try {
    pwdSaving.value = true
    await authApi.changePassword(pwdForm)
    ElMessage.success('密码修改成功')
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirm_password = ''
  } finally {
    pwdSaving.value = false
  }
}

async function logout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' })
    await authStore.logout()
    router.replace('/login')
  } catch (e) { /* cancel */ }
}
</script>

<style scoped>
.profile-card { text-align: center; }
.avatar-area { padding: 12px; }
.phone { color: #909399; font-size: 13px; }
.info-list { text-align: left; }
.info-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px dashed #ebeef5;
}
.info-label { color: #909399; font-size: 13px; }
.info-value { color: #303133; font-size: 13px; }
.quick-card {
  cursor: pointer;
  text-align: center;
  transition: all .2s;
  height: 160px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-radius: 10px;
}
.quick-card:hover { transform: translateY(-3px); }
.q-title { font-size: 16px; font-weight: 600; color: #303133; }
.q-desc { color: #909399; font-size: 12px; }
:deep(.el-tabs) { background: #fff; border-radius: 8px; padding: 8px 20px 20px; }
</style>
