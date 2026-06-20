import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Question } from '@/types'
import { questionnaireApi } from '@/api'

export const useQuestionnaireStore = defineStore('questionnaire', () => {
  const questions = ref<Question[]>([])
  const currentPage = ref(1)
  const totalPages = 9
  const answers = ref<Record<number, number>>({})

  const pageSize = 10

  const currentQuestions = computed(() => {
    const start = (currentPage.value - 1) * pageSize
    return questions.value.slice(start, start + pageSize)
  })

  const progress = computed(() => {
    return Math.round((Object.keys(answers.value).length / 90) * 100)
  })

  function setAnswer(num: number, value: number) {
    answers.value[num] = value
  }

  function isCurrentPageComplete(): boolean {
    return currentQuestions.value.every(q => answers.value[q.number] != null)
  }

  function getMissingInCurrentPage(): number[] {
    return currentQuestions.value
      .filter(q => answers.value[q.number] == null)
      .map(q => q.number)
  }

  function goNextPage() {
    if (currentPage.value < totalPages) {
      currentPage.value++
    }
  }

  function goPrevPage() {
    if (currentPage.value > 1) {
      currentPage.value--
    }
  }

  function goToPage(page: number) {
    if (page >= 1 && page <= totalPages) {
      currentPage.value = page
    }
  }

  function reset() {
    currentPage.value = 1
    answers.value = {}
  }

  async function loadAllQuestions() {
    if (questions.value.length > 0) return
    const res: any = await questionnaireApi.getAllQuestions()
    questions.value = res.questions.sort((a: Question, b: Question) => a.number - b.number)
  }

  return {
    questions,
    currentPage,
    totalPages,
    pageSize,
    answers,
    currentQuestions,
    progress,
    setAnswer,
    isCurrentPageComplete,
    getMissingInCurrentPage,
    goNextPage,
    goPrevPage,
    goToPage,
    reset,
    loadAllQuestions,
  }
})
