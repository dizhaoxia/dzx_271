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
  risk_distribution: { green: number; yellow: number; red: number }
  avg_factor_scores: Record<string, number>
  avg_gsi: number
  daily_trend_30d: { date: string; count: number }[]
}
