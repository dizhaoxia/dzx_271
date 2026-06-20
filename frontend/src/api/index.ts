import { request } from '@/utils/request'
import type {
  Question, AssessmentResult, AssessmentRecord, TrendItem, User, DashboardStats,
  SubScale, ScreeningResult, SessionSubmitResult, Comparison,
  FollowUpNote, PatientAssignment, HighRiskItem, ProfessionalItem,
  AuditLog, ConsentInfo,
} from '@/types'

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
  getConsent: () =>
    request.get<ConsentInfo>('/api/auth/consent/'),
  acceptConsent: () =>
    request.post('/api/auth/consent/', { accepted: true }),
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
  getScreeningItems: () =>
    request.get('/api/questionnaire/questions/screening-items/'),
  getSubScales: () =>
    request.get<{ results?: SubScale[] } & any>('/api/questionnaire/subscales/'),
  submitScreening: (answers: Record<number, number>) =>
    request.post<ScreeningResult>('/api/questionnaire/screening/', { answers }),
}

export const recordsApi = {
  submitAssessment: (answers: Record<number, number>) =>
    request.post<AssessmentResult>('/api/records/submit/', { answers }),
  submitSession: (screening_answers: Record<number, number>, subscale_answers: Record<string, Record<number, number>>) =>
    request.post<SessionSubmitResult>('/api/records/submit-session/', { screening_answers, subscale_answers }),
  getRecords: (params?: any) =>
    request.get('/api/records/', { params }),
  getRecord: (id: number) =>
    request.get<AssessmentRecord>(`/api/records/${id}/`),
  getRecordDetail: (id: number) =>
    request.get<AssessmentRecord>(`/api/records/${id}/detail-full/`),
  getTrend: () =>
    request.get<TrendItem[]>('/api/records/trend/'),
  getComparison: (id: number) =>
    request.get<Comparison>(`/api/records/${id}/comparison/`),
  downloadPdf: (id: number) =>
    request.get(`/api/records/${id}/pdf/`, { responseType: 'blob' }),
}

export const clinicApi = {
  getFollowUpNotes: (params?: any) =>
    request.get('/api/records/followup-notes/', { params }),
  createFollowUpNote: (data: Partial<FollowUpNote>) =>
    request.post<FollowUpNote>('/api/records/followup-notes/', data),
  updateFollowUpNote: (id: number, data: Partial<FollowUpNote>) =>
    request.patch<FollowUpNote>(`/api/records/followup-notes/${id}/`, data),
  deleteFollowUpNote: (id: number) =>
    request.delete(`/api/records/followup-notes/${id}/`),
  getAssignments: (params?: any) =>
    request.get('/api/records/assignments/', { params }),
  createAssignment: (data: Partial<PatientAssignment>) =>
    request.post<PatientAssignment>('/api/records/assignments/', data),
  updateAssignment: (id: number, data: Partial<PatientAssignment>) =>
    request.patch<PatientAssignment>(`/api/records/assignments/${id}/`, data),
}

export const adminApi = {
  dashboard: () =>
    request.get<DashboardStats>('/api/admin-panel/dashboard/'),
  getUsers: (params?: any) =>
    request.get('/api/admin-panel/users/', { params }),
  getUser: (id: number) =>
    request.get<User>(`/api/admin-panel/users/${id}/`),
  setUserRole: (id: number, role: string) =>
    request.patch(`/api/admin-panel/users/${id}/role/`, { role }),
  getRecords: (params?: any) =>
    request.get('/api/admin-panel/records/', { params }),
  getRecord: (id: number) =>
    request.get<AssessmentRecord>(`/api/admin-panel/records/${id}/`),
  exportCsv: () =>
    request.get('/api/admin-panel/records/export-csv/', { responseType: 'blob' }),
  getHighRisk: (params?: any) =>
    request.get<{ total: number; items: HighRiskItem[] }>('/api/admin-panel/high-risk/', { params }),
  getProfessionals: () =>
    request.get<{ total: number; items: ProfessionalItem[] }>('/api/admin-panel/professionals/'),
}

export const complianceApi = {
  getAuditLogs: (params?: any) =>
    request.get('/api/compliance/audit-logs/', { params }),
  getAuditSummary: () =>
    request.get('/api/compliance/audit-logs/summary/'),
  getConsents: (params?: any) =>
    request.get('/api/compliance/consents/', { params }),
}
