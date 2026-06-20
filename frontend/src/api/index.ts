import { request } from '@/utils/request'
import type { Question, AssessmentResult, AssessmentRecord, TrendItem, User, DashboardStats } from '@/types'

export const authApi = {
  login: (phone: string, password: string) =>
    request.post('/api/auth/login/', { phone, password }),
  register: (data: any) =>
    request.post('/api/auth/register/', data),
  logout: (refresh: string) =>
    request.post('/api/auth/logout/', { refresh }),
  refresh: (refresh: string) =>
    request.post('/api/auth/refresh/', { refresh }),
  profile: () =>
    request.get<User>('/api/auth/profile/'),
  updateProfile: (data: any) =>
    request.put<User>('/api/auth/profile/', data),
  changePassword: (data: any) =>
    request.post('/api/auth/password/change/', data),
  requestPasswordReset: (phone: string) =>
    request.post('/api/auth/password-reset-request/', { phone }),
  confirmPasswordReset: (data: any) =>
    request.post('/api/auth/password-reset-confirm/', data),
}

export const questionnaireApi = {
  getQuestionsByPage: (page: number) =>
    request.get(`/api/questionnaire/questions/page/${page}/`),
  getAllQuestions: () =>
    request.get('/api/questionnaire/questions/all/'),
  getQuestion: (number: number) =>
    request.get<Question>(`/api/questionnaire/questions/${number}/`),
  getNorms: () =>
    request.get('/api/questionnaire/norms/'),
  calculateScore: (answers: Record<number, number>) =>
    request.post<AssessmentResult>('/api/questionnaire/calculate/', { answers }),
}

export const recordsApi = {
  submitAssessment: (answers: Record<number, number>) =>
    request.post<AssessmentResult>('/api/records/submit/', { answers }),
  getRecords: (params?: any) =>
    request.get('/api/records/', { params }),
  getRecord: (id: number) =>
    request.get<AssessmentRecord>(`/api/records/${id}/`),
  getRecordDetail: (id: number) =>
    request.get<AssessmentRecord>(`/api/records/${id}/detail-full/`),
  getTrend: () =>
    request.get<TrendItem[]>('/api/records/trend/'),
}

export const adminApi = {
  dashboard: () =>
    request.get<DashboardStats>('/api/admin-panel/dashboard/'),
  getUsers: (params?: any) =>
    request.get('/api/admin-panel/users/', { params }),
  getUser: (id: number) =>
    request.get<User>(`/api/admin-panel/users/${id}/`),
  getRecords: (params?: any) =>
    request.get('/api/admin-panel/records/', { params }),
  getRecord: (id: number) =>
    request.get<AssessmentRecord>(`/api/admin-panel/records/${id}/`),
  exportCsv: () =>
    request.get('/api/admin-panel/records/export-csv/', { responseType: 'blob' }),
}
