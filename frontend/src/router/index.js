import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn } from '../api/auth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { public: true } },
  { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/repos', name: 'Repos', component: () => import('../views/Repos.vue') },
  { path: '/settings', name: 'Settings', component: () => import('../views/Settings.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.public) {
    if (isLoggedIn() && to.path === '/login') return { path: '/' }
    return true
  }
  if (!isLoggedIn()) return { path: '/login' }
  return true
})

export default router
