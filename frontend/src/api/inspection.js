import request from './request'

export const getOverview = () => request.get('/overview/')

export const getInspectionList = (params) => {
  return request.get('/inspection/list', { params })
}

export const getInspectionDetail = (id) => {
  return request.get(`/inspection/${id}`)
}

export const createInspection = (data) => {
  return request.post('/inspection/create', data)
}

export const updateInspection = (id, data) => {
  return request.put(`/inspection/${id}`, data)
}

export const deleteInspection = (id) => {
  return request.delete(`/inspection/${id}`)
}

export const getDeviceList = (params) => {
  return request.get('/device/list', { params })
}

export const getOnlineDeviceCount = () => {
  return request.get('/device/online/count')
}
