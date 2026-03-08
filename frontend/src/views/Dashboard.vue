<template>
  <div>
    <!-- 首屏：胶囊 + 大标题 + 副标题 -->
    <div class="dashboard-hero">
      <div class="hero-capsule">
        <el-icon><Star /></el-icon>
        基于轮询的 GitHub / Gitee 仓库变更监控
      </div>
      <h1 class="hero-title">
        <span class="gradient">仓库监控</span>
        <span class="hero-title-dot">·</span>
        <span class="gradient">Repo Watcher</span>
      </h1>
      <p class="hero-subtitle">有更新，第一时间知道</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon primary">
          <el-icon><FolderOpened /></el-icon>
        </div>
        <div>
          <div class="stat-value">{{ repos.length }}</div>
          <div class="stat-label">监控仓库</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div>
          <div class="stat-value">{{ updatedCount }}</div>
          <div class="stat-label">最近有更新</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon warning">
          <el-icon><Timer /></el-icon>
        </div>
        <div>
          <div class="stat-value">{{ lastCheckDisplay }}</div>
          <div class="stat-label">最后检查</div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="actions-bar">
      <span style="font-size:13px; color:var(--text-muted)">
        共 {{ repos.length }} 个仓库
      </span>
      <div class="actions-bar-buttons">
        <el-button
          class="btn-mark-all-read"
          :loading="clearingAll"
          @click="handleClearAll"
        >
          <el-icon><Check /></el-icon>
          <span>标记全部已读</span>
        </el-button>
        <el-button type="primary" :loading="checking" @click="handleCheck">
          <el-icon><Refresh /></el-icon>
          <span>立即检查</span>
        </el-button>
      </div>
    </div>

    <!-- 仓库表格 -->
    <div class="card">
      <el-table :data="repos" stripe style="width:100%">
        <el-table-column label="平台" width="90">
          <template #default="{ row }">
            <el-tag :type="row.platform === 'github' ? '' : 'warning'" size="small">
              {{ row.platform }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="仓库" min-width="200">
          <template #default="{ row }">
            <span style="font-weight:600">{{ row.owner }}/{{ row.repo }}</span>
          </template>
        </el-table-column>
        <el-table-column label="分支" width="120">
          <template #default="{ row }">
            <span class="mono">{{ row.branch }}</span>
          </template>
        </el-table-column>
        <el-table-column label="最新提交" min-width="260">
          <template #default="{ row }">
            <template v-if="row.state?.last_sha">
              <a
                :href="row.state.last_url"
                target="_blank"
                class="mono"
                style="color:var(--accent); text-decoration:none"
              >{{ row.state.last_sha?.slice(0, 8) }}</a>
              <span style="margin-left:8px; color:var(--text-secondary); font-size:12px">
                {{ row.state.last_message }}
              </span>
            </template>
            <span v-else style="color:var(--text-muted)">暂无数据</span>
          </template>
        </el-table-column>
        <el-table-column label="最后检查" width="170">
          <template #default="{ row }">
            <span class="mono" style="color:var(--text-muted); font-size:12px">
              {{ formatTime(row.state?.last_check_time) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="更新次数" width="90" align="center">
          <template #default="{ row }">
            <span class="mono">{{ row.state?.update_count ?? 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.state?.updated" type="success" size="small" effect="dark">
              有更新
            </el-tag>
            <el-tag v-else-if="row.state?.last_sha" size="small" effect="plain">
              无变化
            </el-tag>
            <el-tag v-else type="info" size="small">待检查</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="110" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              class="btn-mark-read"
              link
              size="small"
              :loading="clearingId === row.id"
              :disabled="!(row.state?.update_count > 0)"
              @click="handleClearRow(row)"
            >
              <el-icon><Check /></el-icon>
              <span>标为已读</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 检查结果弹窗 -->
    <el-dialog v-model="resultVisible" title="检查结果" width="520px">
      <div v-if="checkResult">
        <p style="margin-bottom:12px; color:var(--text-secondary)">
          共检查 {{ checkResult.checked }} 个仓库，发现 {{ checkResult.updated }} 个更新
        </p>
        <el-table v-if="checkResult.details?.length" :data="checkResult.details" size="small">
          <el-table-column prop="owner" label="Owner" width="120" />
          <el-table-column prop="repo" label="Repo" />
          <el-table-column prop="branch" label="Branch" width="100" />
          <el-table-column label="Commit" width="100">
            <template #default="{ row }">
              <span class="mono">{{ row.commit?.sha?.slice(0, 8) }}</span>
            </template>
          </el-table-column>
        </el-table>
        <p v-else style="color:var(--text-muted)">全部仓库均无新更新。</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Star, FolderOpened, CircleCheck, Timer, Refresh, Check } from '@element-plus/icons-vue'
import { getRepos, triggerCheck, clearRepoUpdates, clearAllUpdates } from '../api/repos'
import { ElMessage } from 'element-plus'

const repos = ref([])
const checking = ref(false)
const clearingAll = ref(false)
const clearingId = ref(null)
const resultVisible = ref(false)
const checkResult = ref(null)

const updatedCount = computed(() =>
  repos.value.reduce((sum, r) => sum + (r.state?.update_count ?? 0), 0)
)

const lastCheckDisplay = computed(() => {
  const times = repos.value
    .map(r => r.state?.last_check_time)
    .filter(Boolean)
    .sort()
    .reverse()
  if (!times.length) return '--'
  return formatTime(times[0])
})

function formatTime(iso) {
  if (!iso) return '--'
  try {
    const d = new Date(iso)
    return d.toLocaleString('zh-CN', { hour12: false })
  } catch {
    return iso
  }
}

async function loadRepos() {
  try {
    repos.value = await getRepos()
  } catch (e) {
    ElMessage.error('加载仓库列表失败: ' + e.message)
  }
}

async function handleCheck() {
  checking.value = true
  try {
    checkResult.value = await triggerCheck()
    resultVisible.value = true
    await loadRepos()
  } catch (e) {
    ElMessage.error('检查失败: ' + e.message)
  } finally {
    checking.value = false
  }
}

async function handleClearRow(row) {
  clearingId.value = row.id
  try {
    await clearRepoUpdates(row.id)
    ElMessage.success('已标为已读')
    await loadRepos()
  } catch (e) {
    ElMessage.error('标为已读失败: ' + e.message)
  } finally {
    clearingId.value = null
  }
}

async function handleClearAll() {
  clearingAll.value = true
  try {
    await clearAllUpdates()
    ElMessage.success('已全部标为已读')
    await loadRepos()
  } catch (e) {
    ElMessage.error('标记全部已读失败: ' + e.message)
  } finally {
    clearingAll.value = false
  }
}

onMounted(loadRepos)
</script>
