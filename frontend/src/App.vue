<template>
  <div class="app-layout">
    <aside class="app-sidebar">
      <div class="sidebar-brand">
        <h1>仓库监控</h1>
        <div class="subtitle">Repo Watcher</div>
      </div>
      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="active"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          {{ item.label }}
        </router-link>
      </nav>
    </aside>
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
const navItems = [
  { path: '/', label: '仪表盘', icon: 'Monitor' },
  { path: '/repos', label: '仓库管理', icon: 'FolderOpened' },
  { path: '/settings', label: '系统设置', icon: 'Setting' },
]
</script>
