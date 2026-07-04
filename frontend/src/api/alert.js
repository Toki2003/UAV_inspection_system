import request from './request'

export function getAlertList(params) {
    return request.get('/alert/', { params })
}

export function getAlertDetail(id) {
    return request.get(`/alert/${id}/`)
}

export function createAlert(data) {
    return request.post('/alert/', data)
}

export function updateAlert(id, data) {
    return request.put(`/alert/${id}/`, data)
}

export function deleteAlert(id) {
    return request.delete(`/alert/${id}/`)
}