<template>
  <div v-loading="loading">
    <div class="back-bar">
      <el-button link @click="$router.push('/clinic')">
        <el-icon><ArrowLeft /></el-icon> 返回患者列表
      </el-button>
      <span class="patient-title">患者档案 · {{ patientName }}</span>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="15">
        <el-card class="card-shadow mb-16">
          <div class="section-title">测评记录</div>
          <el-empty v-if="!records.length && !loading" description="该患者暂无测评记录" />
          <el-table v-else :data="records" stripe size="default">
            <el-table-column label="时间" min-width="160">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="模式" width="90" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="row.mode === 'adaptive' ? 'success' : 'info'" effect="plain">
                  {{ row.mode === 'adaptive' ? '自适应' : '完整90题' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="GSI" width="80" align="center">
              <template #default="{ row }"><strong :style="{ color: gsiColor(row.gsi) }">{{ row.gsi }}</strong></template>
            </el-table-column>
            <el-table-column label="风险" width="90" align="center">
              <template #default="{ row }">
                <span :class="`risk-${row.overall_risk}`">{{ riskText(row.overall_risk) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="题数" width="80" align="center">
              <template #default="{ row }">{{ row.answered_count ?? '—' }}</template>
            </el-table-column>
            <el-table-column label="操作" width="180" align="center" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="$router.push(`/result/${row.id}`)">查看报告</el-button>
                <el-button type="warning" link :loading="pdfId === row.id" @click="downloadPdf(row)">PDF</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card class="card-shadow mb-16">
          <div class="section-title">随访记录</div>
          <el-empty v-if="!notes.length && !notesLoading" description="暂无随访记录，请在右侧添加" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="n in notes"
              :key="n.id"
              :timestamp="formatTime(n.created_at)"
              placement="top"
            >
              <div class="note-card">
                <div class="note-head">
                  <el-tag size="small" :type="followUpTypeTag(n.follow_up_type)" effect="plain">{{ followUpTypeLabel(n.follow_up_type) }}</el-tag>
                  <span v-if="n.follow_up_date" class="note-date">随访日期：{{ n.follow_up_date }}</span>
                  <span class="note-author">— {{ n.professional_name || '我' }}</span>
                </div>
                <div class="note-text">{{ n.note }}</div>
                <div v-if="n.next_action" class="note-next">下一步：{{ n.next_action }}</div>
                <div class="note-actions">
                  <el-button link type="primary" @click="editNote(n)">编辑</el-button>
                  <el-button link type="danger" @click="removeNote(n)">删除</el-button>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="9">
        <el-card class="card-shadow mb-16">
          <div class="section-title">{{ editingId ? '编辑随访记录' : '新增随访记录' }}</div>
          <el-form :model="form" label-position="top" size="default">
            <el-form-item label="随访类型">
              <el-select v-model="form.follow_up_type" placeholder="选择类型" style="width: 100%;">
                <el-option v-for="o in followUpTypes" :key="o.value" :label="o.label" :value="o.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="随访日期">
              <el-date-picker v-model="form.follow_up_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="随访记录">
              <el-input v-model="form.note" type="textarea" :rows="4" placeholder="记录患者当前状态、症状变化、干预措施等" />
            </el-form-item>
            <el-form-item label="下一步计划">
              <el-input v-model="form.next_action" type="textarea" :rows="2" placeholder="下次干预建议、复诊时间等" />
            </el-form-item>
            <div class="form-actions">
              <el-button v-if="editingId" @click="cancelEdit">取消</el-button>
              <el-button type="primary" :loading="saving" @click="saveNote">
                {{ editingId ? '更新' : '保存随访记录' }}
              </el-button>
            </div>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { recordsApi, clinicApi } from '@/api'
import type { AssessmentRecord, FollowUpNote } from '@/types'

const route = useRoute()
const patientId = computed(() => Number(route.params.id))

const loading = ref(false)
const notesLoading = ref(false)
const saving = ref(false)
const pdfId = ref<number | null>(null)

const records = ref<AssessmentRecord[]>([])
const notes = ref<FollowUpNote[]>([])
const patientName = ref('患者')

const followUpTypes = [
  { value: 'initial', label: '初诊评估' },
  { value: 'followup', label: '复诊随访' },
  { value: 'phone', label: '电话随访' },
  { value: 'online', label: '线上咨询' },
  { value: 'referral', label: '转介就医' },
]

const form = reactive({
  follow_up_type: 'followup',
  follow_up_date: '',
  note: '',
  next_action: '',
})
const editingId = ref<number | null>(null)

async function loadRecords() {
  loading.value = true
  try {
    const res: any = await recordsApi.getRecords({ user: patientId.value, page_size: 100 })
    records.value = res.results || res.data || res || []
    if (records.value[0]) patientName.value = records.value[0].user_name || '患者'
  } finally {
    loading.value = false
  }
}

async function loadNotes() {
  notesLoading.value = true
  try {
    const res: any = await clinicApi.getFollowUpNotes({ patient: patientId.value, page_size: 100 })
    notes.value = (res.results || res.data || res || []).sort(
      (a: FollowUpNote, b: FollowUpNote) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    )
  } finally {
    notesLoading.value = false
  }
}

async function saveNote() {
  if (!form.note.trim()) { ElMessage.warning('请填写随访记录'); return }
  saving.value = true
  try {
    const payload = { ...form, patient: patientId.value }
    if (editingId.value) {
      await clinicApi.updateFollowUpNote(editingId.value, payload)
      ElMessage.success('随访记录已更新')
    } else {
      await clinicApi.createFollowUpNote(payload)
      ElMessage.success('随访记录已保存')
    }
    cancelEdit()
    await loadNotes()
  } finally {
    saving.value = false
  }
}

function editNote(n: FollowUpNote) {
  editingId.value = n.id
  form.follow_up_type = n.follow_up_type || 'followup'
  form.follow_up_date = n.follow_up_date || ''
  form.note = n.note || ''
  form.next_action = n.next_action || ''
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cancelEdit() {
  editingId.value = null
  form.follow_up_type = 'followup'
  form.follow_up_date = ''
  form.note = ''
  form.next_action = ''
}

async function removeNote(n: FollowUpNote) {
  try {
    await ElMessageBox.confirm('确定删除该随访记录？', '提示', { type: 'warning' })
    await clinicApi.deleteFollowUpNote(n.id)
    ElMessage.success('已删除')
    await loadNotes()
  } catch { /* cancelled */ }
}

async function downloadPdf(row: AssessmentRecord) {
  pdfId.value = row.id
  try {
    const blob = await recordsApi.downloadPdf(row.id) as unknown as Blob
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `SCL90报告_${row.id}.pdf`
    document.body.appendChild(a); a.click(); document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('PDF 已开始下载')
  } finally {
    pdfId.value = null
  }
}

function formatTime(t: string) { return new Date(t).toLocaleString('zh-CN') }
function riskText(r: string) { return { green: '正常', yellow: '轻度', red: '中度+' }[r] || r }
function gsiColor(g: number) {
  if (g < 2) return '#67c23a'
  if (g < 3) return '#e6a23c'
  return '#f56c6c'
}
function followUpTypeLabel(v: string) {
  return followUpTypes.find(t => t.value === v)?.label || v
}
function followUpTypeTag(v: string): 'success' | 'warning' | 'danger' | 'info' | 'primary' {
  const m: Record<string, any> = { initial: 'primary', followup: 'success', phone: 'info', online: 'info', referral: 'danger' }
  return m[v] || 'info'
}

onMounted(async () => {
  await Promise.all([loadRecords(), loadNotes()])
})
</script>

<style scoped>
.back-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.patient-title { font-size: 16px; font-weight: 600; color: #303133; }
.section-title {
  font-size: 16px; font-weight: 600; color: #303133;
  border-left: 4px solid #67c23a; padding-left: 10px; margin-bottom: 16px;
}
.risk-green { color: #67c23a; }
.risk-yellow { color: #e6a23c; }
.risk-red { color: #f56c6c; }
.note-card { background: #f9fafc; border: 1px solid #ebeef5; border-radius: 8px; padding: 12px 16px; }
.note-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 13px; color: #909399; }
.note-author { margin-left: auto; }
.note-text { color: #303133; line-height: 1.7; white-space: pre-wrap; }
.note-next { margin-top: 8px; color: #e6a23c; font-size: 13px; }
.note-actions { margin-top: 8px; text-align: right; }
.form-actions { display: flex; justify-content: flex-end; gap: 8px; }
</style>
