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
      width="480px"
      destroy-on-close
    >
      <el-form :model="form" label-width="80px" label-position="left">
        <el-form-item label="平台">
          <el-select v-model="form.platform" style="width:100%">
            <el-option value="github" label="GitHub" />
            <el-option value="gitee" label="Gitee" />
          </el-select>
        </el-form-item>
        <el-form-item label="Owner">
          <el-input v-model="form.owner" placeholder="如 vuejs" />
        </el-form-item>
        <el-form-item label="仓库名">
          <el-input v-model="form.repo" placeholder="如 core" />
        </el-form-item>
        <el-form-item label="分支">
          <el-input v-model="form.branch" placeholder="默认 main" />
        </el-form-item>
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
import { ref, onMounted } from 'vue'
import { getRepos, addRepo, updateRepo, deleteRepo } from '../api/repos'
import { ElMessage, ElMessageBox } from 'element-plus'

const repos = ref([])
const dialogVisible = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const editId = ref('')

const defaultForm = { platform: 'github', owner: '', repo: '', branch: 'main' }
const form = ref({ ...defaultForm })

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
    form.value = { platform: row.platform, owner: row.owner, repo: row.repo, branch: row.branch }
  } else {
    isEdit.value = false
    editId.value = ''
    form.value = { ...defaultForm }
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.value.owner || !form.value.repo) {
    ElMessage.warning('Owner 和仓库名不能为空')
    return
  }
  saving.value = true
  try {
    if (isEdit.value) {
      await updateRepo(editId.value, form.value)
      ElMessage.success('修改成功')
    } else {
      await addRepo(form.value)
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
