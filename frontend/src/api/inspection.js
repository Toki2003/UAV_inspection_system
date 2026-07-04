import request from './request'
import { mockInspectionTasks } from '@/mock/inspectionTasks'

const unwrapData = (response) => response?.data ?? response

export const getOverview = () => request.get('/overview/')

export const getInspectionList = (params) => {
  return request.get('/inspection/list', { params }).then(unwrapData)
}

export const getInspectionDetail = (id) => {
  return request.get(`/inspection/${id}`).then(unwrapData)
}

export const createInspection = (data) => {
  return request.post('/inspection/create', data).then(unwrapData)
}

export const updateInspection = (id, data) => {
  return request.put(`/inspection/${id}`, data).then(unwrapData)
}

export const deleteInspection = (id) => {
  return request.delete(`/inspection/${id}`).then(unwrapData)
}

export const getDeviceList = (params) => {
  return request.get('/device/list', { params })
}

export const getOnlineDeviceCount = () => {
  return request.get('/device/online/count')
}

export const getMockInspectionList = () => Promise.resolve(mockInspectionTasks)

export const getMockInspectionDetail = (id) => {
  const task = mockInspectionTasks.find(item => String(item.id) === String(id))
  return Promise.resolve(task || mockInspectionTasks[0])
}
