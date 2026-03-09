<template>
  <div class="login-page">
    <div class="login-card card">
      <div class="login-header">
        <div class="login-brand">
          <el-icon><Monitor /></el-icon>
          <span>仓库监控</span>
        </div>
        <p class="login-subtitle">请登录后使用后台功能</p>
        <p class="login-hint">默认账号 <strong>admin</strong> / 密码 <strong>admin</strong>，首次登录后请在「系统设置 → 修改密码」中修改。</p>
      </div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            size="large"
            clearable
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            clearable
            :prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Monitor } from '@element-plus/icons-vue'
import { login as apiLogin, setToken } from '../api/auth'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: 'admin',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value?.validate().catch(() => {})
  loading.value = true
  try {
    const res = await apiLogin({ username: form.username, password: form.password })
    if (res?.token) {
      setToken(res.token)
      ElMessage.success('登录成功')
      router.replace('/')
    } else {
      ElMessage.error(res?.detail || '登录失败')
    }
  } catch (e) {
    ElMessage.error(e?.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(180deg, #ffffff 0%, var(--bg-deep) 100%);
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 32px;
}

.login-header {
  text-align: center;
  margin-bottom: 28px;
}

.login-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 22px;
  font-weight: 700;
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-brand .el-icon {
  font-size: 28px;
  -webkit-text-fill-color: var(--accent);
}

.login-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 8px;
}

.login-hint {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 12px;
  line-height: 1.5;
}
.login-hint strong {
  color: var(--text-secondary);
  font-weight: 600;
}

.login-form :deep(.el-form-item__label) {
  font-weight: 500;
}

.login-btn {
  width: 100%;
}
</style>
