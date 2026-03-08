import http from './request'

export const getConfig = () => http.get('/config')
export const updateConfig = (data) => http.put('/config', data)
