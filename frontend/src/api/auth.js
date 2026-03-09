import http from './request'

const TOKEN_KEY = 'repo_watcher_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

export function isLoggedIn() {
  return !!getToken()
}

/** 登录，成功返回 { ok, token } */
export const login = (data) => http.post('/auth/login', data)

/** 校验当前 token 是否有效 */
export const getMe = () => http.get('/auth/me')

/** 登出（仅前端清除 token） */
export function logout() {
  setToken(null)
}

/** 修改密码（需已登录），成功请重新登录 */
export const updatePassword = (data) => http.put('/auth/password', data)
