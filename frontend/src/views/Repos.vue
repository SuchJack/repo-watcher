<template>
  <div>
    <div class="page-header">
      <h2>仓库管理</h2>
      <p>添加、编辑或删除要监控的仓库</p>
    </div>

    <div class="actions-bar">
      <span style="font-size:13px; color:var(--text-muted)">
        共 {{ repos.length }} 个仓库
      </span>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>&nbsp;添加仓库
      </el-button>
    </div>

    <div class="card">
      <el-table :data="repos" stripe style="width:100%">
        <el-table-column label="平台" width="100">
          <template #default="{ row }">
            <el-tag :type="row.platform === 'github' ? '' : 'warning'" size="small">
              {{ row.platform }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="owner" label="Owner" min-width="140" />
        <el-table-column prop="repo" label="仓库名" min-width="180" />
        <el-table-column prop="branch" label="分支" width="120">
          <template #default="{ row }">
            <span class="mono">{{ row.branch }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <el-button size="small" text @click="openDialog(row)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button size="small" text type="danger" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑仓库' : '添加仓库'"
      width="520px"
      destroy-on-close
    >
      <el-form :model="form" label-width="90px" label-position="left">
        <el-form-item label="仓库 URL">
          <el-input
            v-model="form.repoUrl"
            placeholder="粘贴 GitHub 或 Gitee 仓库链接，如 https://github.com/vuejs/core"
            clearable
          />
        </el-form-item>
        <el-form-item label="分支">
          <el-input v-model="form.branch" placeholder="不填则使用 master" />
        </el-form-item>
        <template v-if="isEdit && parsedPreview">
          <el-divider style="margin: 12px 0" />
          <div style="font-size: 12px; color: var(--text-muted)">
            当前解析：{{ parsedPreview.platform }} / {{ parsedPreview.owner }} / {{ parsedPreview.repo }}
          </div>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          {{ isEdit ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getRepos, addRepo, updateRepo, deleteRepo } from '../api/repos'
import { ElMessage, ElMessageBox } from 'element-plus'

const DEFAULT_BRANCH = 'master'

function parseRepoUrl(url) {
  if (!url || typeof url !== 'string') return null
  const u = url.trim()
  // https://github.com/owner/repo 或 /tree/branch
  const github = u.match(/github\.com[/:]([^/]+)\/([^/#?]+)(?:\/tree\/([^/#?]+))?/i)
  if (github) {
    return {
      platform: 'github',
      owner: github[1],
      repo: github[2].replace(/\.git$/i, ''),
      branch: github[3] || '',
    }
  }
  const gitee = u.match(/gitee\.com[/:]([^/]+)\/([^/#?]+)(?:\/tree\/([^/#?]+))?/i)
  if (gitee) {
    return {
      platform: 'gitee',
      owner: gitee[1],
      repo: gitee[2].replace(/\.git$/i, ''),
      branch: gitee[3] || '',
    }
  }
  // git@github.com:owner/repo.git 或 git@gitee.com:owner/repo.git
  const sshGitHub = u.match(/git@github\.com:([^/]+)\/([^/#]+?)(?:\.git)?$/i)
  if (sshGitHub) {
    return { platform: 'github', owner: sshGitHub[1], repo: sshGitHub[2].replace(/\.git$/i, ''), branch: '' }
  }
  const sshGitee = u.match(/git@gitee\.com:([^/]+)\/([^/#]+?)(?:\.git)?$/i)
  if (sshGitee) {
    return { platform: 'gitee', owner: sshGitee[1], repo: sshGitee[2].replace(/\.git$/i, ''), branch: '' }
  }
  return null
}

function buildRepoUrl(platform, owner, repo) {
  const host = platform === 'gitee' ? 'gitee.com' : 'github.com'
  return `https://${host}/${owner}/${repo}`
}

const repos = ref([])
const dialogVisible = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const editId = ref('')

const defaultForm = () => ({
  repoUrl: '',
  platform: 'github',
  owner: '',
  repo: '',
  branch: DEFAULT_BRANCH,
})
const form = ref(defaultForm())

const parsedPreview = computed(() => {
  if (!form.value.owner && !form.value.repo) return null
  return {
    platform: form.value.platform,
    owner: form.value.owner,
    repo: form.value.repo,
  }
})

async function loadRepos() {
  try {
    repos.value = await getRepos()
  } catch (e) {
    ElMessage.error('加载失败: ' + e.message)
  }
}

function openDialog(row) {
  if (row) {
    isEdit.value = true
    editId.value = row.id
    form.value = {
      repoUrl: buildRepoUrl(row.platform, row.owner, row.repo),
      platform: row.platform,
      owner: row.owner,
      repo: row.repo,
      branch: row.branch || DEFAULT_BRANCH,
    }
  } else {
    isEdit.value = false
    editId.value = ''
    form.value = defaultForm()
  }
  dialogVisible.value = true
}

function getPayloadFromForm() {
  const url = form.value.repoUrl?.trim()
  if (isEdit.value && form.value.owner && form.value.repo) {
    return {
      platform: form.value.platform,
      owner: form.value.owner,
      repo: form.value.repo,
      branch: (form.value.branch || '').trim() || DEFAULT_BRANCH,
    }
  }
  const parsed = parseRepoUrl(url)
  if (!parsed) {
    ElMessage.warning('无法识别的仓库地址，请使用 GitHub 或 Gitee 的仓库链接')
    return null
  }
  const branch = (form.value.branch || '').trim() || parsed.branch || DEFAULT_BRANCH
  return {
    platform: parsed.platform,
    owner: parsed.owner,
    repo: parsed.repo,
    branch,
  }
}

async function handleSave() {
  const payload = getPayloadFromForm()
  if (!payload) return
  saving.value = true
  try {
    if (isEdit.value) {
      await updateRepo(editId.value, payload)
      ElMessage.success('修改成功')
    } else {
      await addRepo(payload)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    await loadRepos()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定删除 ${row.owner}/${row.repo} 吗？`,
      '删除确认',
      { type: 'warning' }
    )
    await deleteRepo(row.id)
    ElMessage.success('已删除')
    await loadRepos()
  } catch {
    // cancelled
  }
}

onMounted(loadRepos)
</script>
