import request from './request'

// 获取数据示例
export const getData = () => {
  return request.get('/data')
}

export const getInspectionList = (params) => {
  return request.get('/inspection/list', { params })
}

export const getInspectionDetail = (id) => {
  return request.get(`/inspection/${id}`)
}
