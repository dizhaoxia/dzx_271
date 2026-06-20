export interface User {
  id: number
  phone: string
  username: string
  email?: string
  gender?: 'male' | 'female' | 'other'
  age?: number
  avatar?: string
  is_staff: boolean
  is_active: boolean
  role: 'patient' | 'counselor' | 'doctor'
  title?: string
  license_no?: string
  consent_accepted: boolean
  consent_accepted_at?: string
  consent_version?: string
  is_professional?: boolean
  created_at: string
}

export interface Tokens {
  access: string
  refresh: string
}

export interface Question {
  number: number
  content: string
  factor: string
}

export interface FactorDetail {
  name: string
  score: number
  norm_mean: number
  norm_std: number
  status: '偏高' | '偏低' | '正常'
  risk_level: 'green' | 'yellow' | 'red'
  description: string
}

export interface AssessmentResult {
  record_id: number
  factor_scores: Record<string, number>
  gsi: number
  positive_count: number
  positive_avg: number
  total_sum: number
  comparisons: Record<string, FactorDetail>
  overall_risk: 'green' | 'yellow' | 'red'
  created_at: string
}

export interface AssessmentRecord {
  id: number
  user: number
  user_phone: string
  user_name: string
  som_score: number
  oc_score: number
  is_score: number
  dep_score: number
  anx_score: number
  hos_score: number
  phob_score: number
  par_score: number
  psy_score: number
  oth_score: number
  gsi: number
  positive_count: number
  positive_avg: number
  total_sum: number
  overall_risk: 'green' | 'yellow' | 'red'
  factors_detail: Record<string, FactorDetail>
  answers_json: Record<string, number>
  created_at: string
  mode?: 'classic' | 'adaptive'
  answered_count?: number
  subscale_records?: SubScaleRecord[]
  followup_notes?: FollowUpNote[]
}

export interface TrendItem {
  id: number
  created_at: string
  gsi: number
  som_score: number
  oc_score: number
  is_score: number
  dep_score: number
  anx_score: number
  hos_score: number
  phob_score: number
  par_score: number
  psy_score: number
  overall_risk: 'green' | 'yellow' | 'red'
}

export interface DashboardStats {
  total_users: number
  total_assessments: number
  unique_assessment_users: number
  professional_count: number
  high_risk_count: number
  risk_distribution: { green: number; yellow: number; red: number }
  avg_factor_scores: Record<string, number>
  avg_gsi: number
  daily_trend_30d: { date: string; count: number }[]
}

// ---------- 自适应子量表 ----------
export interface SubScaleOption {
  value: number
  label: string
}

export interface SubScaleQuestion {
  number: number
  content: string
}

export interface SubScale {
  code: string
  name: string
  trigger_factor: string
  description: string
  max_score: number
  questions: SubScaleQuestion[]
  options: SubScaleOption[]
}

export interface RecommendedSubScale {
  code: string
  name: string
  description: string
  trigger_factor: string
  trigger_score: number
  question_count: number
  questions: SubScaleQuestion[]
}

export interface ScreeningResult {
  factor_scores: Record<string, number>
  gsi: number
  positive_count: number
  positive_avg: number
  total_sum: number
  answered_count: number
  comparisons: Record<string, FactorDetail>
  recommended_subscales: RecommendedSubScale[]
  screening_items_count: number
}

export interface SubScaleRecord {
  id: number
  scale_code: string
  scale_name: string
  total_score: number
  max_score: number
  severity: string
  severity_label: string
  advice: string
  answers_json: Record<string, number>
  created_at: string
}

export interface SessionSubmitResult {
  record_id: number
  factor_scores: Record<string, number>
  gsi: number
  positive_count: number
  positive_avg: number
  total_sum: number
  answered_count: number
  comparisons: Record<string, FactorDetail>
  subscale_records: SubScaleRecord[]
  comparison: Comparison | null
  overall_risk: 'green' | 'yellow' | 'red'
  created_at: string
}

// ---------- 多次测评对比 ----------
export interface Comparison {
  overall_tag: 'improved' | 'worsened' | 'stable'
  overall_label: string
  reminder: string
  delta_gsi: number
  delta_total: number
  prev_risk: string
  curr_risk: string
  risk_delta: number
  improved_count: number
  worsened_count: number
  factor_changes: {
    name: string
    field: string
    prev: number
    curr: number
    delta: number
    trend: 'improved' | 'worsened' | 'stable'
  }[]
  prev_created_at: string
  curr_created_at: string
}

// ---------- 医生/咨询师端 ----------
export interface FollowUpNote {
  id: number
  patient: number
  professional?: number
  professional_name?: string
  record?: number
  note: string
  follow_up_date?: string
  follow_up_type: string
  next_action: string
  created_at: string
  updated_at: string
}

export interface PatientAssignment {
  id: number
  patient: number
  patient_phone: string
  patient_name: string
  professional: number
  professional_name: string
  is_active: boolean
  note: string
  created_at: string
}

export interface HighRiskItem {
  user_id: number
  username: string
  phone: string
  record_id: number
  gsi: number
  overall_risk: 'green' | 'yellow' | 'red'
  mode: string
  last_assessment_time: string
  dep_score: number
  anx_score: number
  subscale_severities: { code: string; severity: string; label: string }[]
  assigned_professional: string | null
  assigned_professional_id: number | null
}

export interface ProfessionalItem {
  id: number
  username: string
  phone: string
  role: 'counselor' | 'doctor'
  title: string
  license_no: string
  patient_count: number
}

// ---------- 合规审计 ----------
export interface AuditLog {
  id: number
  user?: number
  username: string
  user_phone: string
  action: string
  action_display: string
  resource_type: string
  resource_id: string
  detail: Record<string, any>
  ip_address: string
  user_agent: string
  created_at: string
}

export interface ConsentInfo {
  consent_accepted: boolean
  consent_accepted_at?: string
  consent_version?: string
  current_version: string
  needs_reconsent: boolean
}
