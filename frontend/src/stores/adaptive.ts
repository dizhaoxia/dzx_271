import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ScreeningResult, RecommendedSubScale, SessionSubmitResult } from '@/types'
import { questionnaireApi, recordsApi } from '@/api'

const SCREENING_KEY = 'scl90_screening_answers'
const SUBSCALE_KEY = 'scl90_subscale_answers'
const SCREENING_RESULT_KEY = 'scl90_screening_result'

function load<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    return raw ? (JSON.parse(raw) as T) : fallback
  } catch {
    return fallback
  }
}

function save(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    /* ignore quota errors */
  }
}

export const useAdaptiveStore = defineStore('adaptive', () => {
  const step = ref<'intro' | 'screening' | 'subscales' | 'done'>('intro')
  const screeningAnswers = ref<Record<number, number>>(load(SCREENING_KEY, {} as Record<number, number>))
  const subscaleAnswers = ref<Record<string, Record<number, number>>>(load(SUBSCALE_KEY, {} as Record<string, Record<number, number>>))
  const screeningResult = ref<ScreeningResult | null>(load<ScreeningResult | null>(SCREENING_RESULT_KEY, null))
  const submitting = ref(false)
  const pendingSubmit = ref<boolean>(load('scl90_pending_submit', false))
  const sessionResult = ref<SessionSubmitResult | null>(null)

  const screeningAnsweredCount = computed(() => Object.keys(screeningAnswers.value).length)

  function setScreeningAnswer(number: number, value: number) {
    screeningAnswers.value[number] = value
    save(SCREENING_KEY, screeningAnswers.value)
  }

  function setSubscaleAnswer(scale: string, number: number, value: number) {
    if (!subscaleAnswers.value[scale]) subscaleAnswers.value[scale] = {}
    subscaleAnswers.value[scale][number] = value
    save(SUBSCALE_KEY, subscaleAnswers.value)
  }

  function setScreeningResult(result: ScreeningResult) {
    screeningResult.value = result
    save(SCREENING_RESULT_KEY, result)
  }

  function gotoStep(s: typeof step.value) {
    step.value = s
  }

  function reset() {
    screeningAnswers.value = {}
    subscaleAnswers.value = {}
    screeningResult.value = null
    sessionResult.value = null
    pendingSubmit.value = false
    step.value = 'intro'
    localStorage.removeItem(SCREENING_KEY)
    localStorage.removeItem(SUBSCALE_KEY)
    localStorage.removeItem(SCREENING_RESULT_KEY)
    localStorage.removeItem('scl90_pending_submit')
  }

  const recommendedSubscales = computed<RecommendedSubScale[]>(() => screeningResult.value?.recommended_subscales ?? [])

  function missingSubscaleQuestions(scale: RecommendedSubScale): number {
    const answered = subscaleAnswers.value[scale.code] ?? {}
    return scale.questions.filter(q => answered[q.number] === undefined).length
  }

  const allSubscalesCompleted = computed(() =>
    recommendedSubscales.value.every(s => missingSubscaleQuestions(s) === 0),
  )

  const overallProgress = computed(() => {
    const scTotal = 18
    const scDone = screeningAnsweredCount.value
    let subTotal = 0, subDone = 0
    for (const s of recommendedSubscales.value) {
      subTotal += s.question_count
      const ans = subscaleAnswers.value[s.code] ?? {}
      subDone += Object.keys(ans).length
    }
    const total = scTotal + subTotal
    const done = scDone + subDone
    return { done, total, percent: total ? Math.round((done / total) * 100) : 0 }
  })

  async function submitSession() {
    submitting.value = true
    try {
      const result = await recordsApi.submitSession(screeningAnswers.value, subscaleAnswers.value)
      sessionResult.value = result
      step.value = 'done'
      pendingSubmit.value = false
      save('scl90_pending_submit', false)
      return result
    } catch (e) {
      // 离线/网络失败：标记待提交，待网络恢复后自动重试
      pendingSubmit.value = true
      save('scl90_pending_submit', true)
      throw e
    } finally {
      submitting.value = false
    }
  }

  /** 网络恢复后自动重试提交（离线缓存已答题目自动提交）。 */
  async function tryAutoSubmit(): Promise<SessionSubmitResult | null> {
    if (!pendingSubmit.value) return null
    if (!screeningResult.value) return null
    if (recommendedSubscales.value.length > 0 && !allSubscalesCompleted.value) return null
    try {
      return await submitSession()
    } catch {
      return null
    }
  }

  return {
    step,
    screeningAnswers,
    subscaleAnswers,
    screeningResult,
    sessionResult,
    submitting,
    pendingSubmit,
    screeningAnsweredCount,
    recommendedSubscales,
    allSubscalesCompleted,
    overallProgress,
    setScreeningAnswer,
    setSubscaleAnswer,
    setScreeningResult,
    gotoStep,
    reset,
    missingSubscaleQuestions,
    submitSession,
    tryAutoSubmit,
    loadScreeningItems: questionnaireApi.getScreeningItems,
  }
})
