import http from './request'

export const getRepos = () => http.get('/repos')
export const addRepo = (data) => http.post('/repos', data)
export const updateRepo = (id, data) => http.put(`/repos/${id}`, data)
export const deleteRepo = (id) => http.delete(`/repos/${id}`)
export const triggerCheck = () => http.post('/check')
