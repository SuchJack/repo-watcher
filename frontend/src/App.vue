<template>
  <div class="app-layout">
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
      </nav>
    </header>
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { Monitor } from '@element-plus/icons-vue'

const navItems = [
  { path: '/', label: '仪表盘', icon: 'Monitor' },
  { path: '/repos', label: '仓库管理', icon: 'FolderOpened' },
  { path: '/settings', label: '系统设置', icon: 'Setting' },
]
</script>
