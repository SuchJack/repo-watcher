import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/repos', name: 'Repos', component: () => import('../views/Repos.vue') },
  { path: '/settings', name: 'Settings', component: () => import('../views/Settings.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
