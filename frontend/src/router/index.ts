import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/home',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false, title: '登录' },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false, title: '注册' },
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPassword.vue'),
    meta: { requiresAuth: false, title: '找回密码' },
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true, title: '首页' },
  },
  {
    path: '/questionnaire',
    name: 'Questionnaire',
    component: () => import('@/views/Questionnaire.vue'),
    meta: { requiresAuth: true, title: '自适应测评' },
  },
  {
    path: '/questionnaire-classic',
    name: 'QuestionnaireClassic',
    component: () => import('@/views/QuestionnaireClassic.vue'),
    meta: { requiresAuth: true, title: 'SCL-90问卷（完整版）' },
  },
  {
    path: '/result/:id',
    name: 'Result',
    component: () => import('@/views/Result.vue'),
    meta: { requiresAuth: true, title: '评估结果' },
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/History.vue'),
    meta: { requiresAuth: true, title: '历史记录' },
  },
  {
    path: '/clinic',
    name: 'Clinic',
    component: () => import('@/views/clinic/ClinicLayout.vue'),
    meta: { requiresAuth: true, requiresProfessional: true, title: '专业端' },
    children: [
      {
        path: '',
        name: 'ClinicPatients',
        component: () => import('@/views/clinic/Patients.vue'),
        meta: { title: '我的患者' },
      },
      {
        path: 'patient/:id',
        name: 'ClinicPatientDetail',
        component: () => import('@/views/clinic/PatientDetail.vue'),
        meta: { title: '患者档案' },
      },
    ],
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true, title: '个人中心' },
  },
  {
    path: '/admin',
    name: 'Admin',
    redirect: '/admin/dashboard',
    component: () => import('@/views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresStaff: true, title: '管理后台' },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '统计仪表盘' },
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/Users.vue'),
        meta: { title: '用户列表' },
      },
      {
        path: 'records',
        name: 'AdminRecords',
        component: () => import('@/views/admin/Records.vue'),
        meta: { title: '测评数据' },
      },
      {
        path: 'high-risk',
        name: 'AdminHighRisk',
        component: () => import('@/views/admin/HighRisk.vue'),
        meta: { title: '高危人群' },
      },
      {
        path: 'professionals',
        name: 'AdminProfessionals',
        component: () => import('@/views/admin/Professionals.vue'),
        meta: { title: '专业人员' },
      },
      {
        path: 'audit-logs',
        name: 'AdminAuditLogs',
        component: () => import('@/views/admin/AuditLogs.vue'),
        meta: { title: '操作审计' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '404' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const title = to.meta?.title
  if (title) {
    document.title = `${String(title)} - SCL-90症状自评量表`
  }

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.requiresStaff && !authStore.isStaff) {
    next({ name: 'Home' })
    return
  }

  if (to.meta.requiresProfessional && !authStore.isProfessional) {
    next({ name: 'Home' })
    return
  }

  if ((to.name === 'Login' || to.name === 'Register') && authStore.isLoggedIn) {
    next({ name: 'Home' })
    return
  }

  next()
})

export default router
