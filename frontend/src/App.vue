<template>
  <div class="app-layout">
    <template v-if="!isLoginPage">
      <header class="app-header">
        <router-link to="/" class="header-brand">
          <div class="header-brand-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <span class="header-brand-text">仓库监控</span>
        </router-link>
        <nav class="header-nav">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: $route.path === item.path }"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            {{ item.label }}
          </router-link>
          <button type="button" class="nav-item nav-item-logout" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            退出
          </button>
        </nav>
      </header>
      <main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </template>
    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Monitor, SwitchButton } from '@element-plus/icons-vue'
import { logout } from './api/auth'

const route = useRoute()
const router = useRouter()

const isLoginPage = computed(() => route.path === '/login')

const navItems = [
  { path: '/', label: '仪表盘', icon: 'Monitor' },
  { path: '/repos', label: '仓库管理', icon: 'FolderOpened' },
  { path: '/settings', label: '系统设置', icon: 'Setting' },
]

function handleLogout() {
  logout()
  router.replace('/login')
}
</script>

<style scoped>
.nav-item-logout {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--font-body);
  margin-left: 8px;
}
.nav-item-logout:hover {
  color: var(--danger);
  background: rgba(220, 38, 38, 0.08);
}
.nav-item-logout .el-icon {
  font-size: 16px;
}
</style>
