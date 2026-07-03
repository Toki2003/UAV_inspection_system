import request from './request' 


import axios from 'axios'


const api = axios.create({
    baseURL: '/api',  
    timeout: 10000,
})

export function getAlertList(params) {
    return api.get('/alert/', { params })
}


export function getAlertDetail(id) {
    return api.get(`/alert/${id}/`)
}


export function createAlert(data) {
    return api.post('/alert/', data)
}


export function updateAlert(id, data) {
    return api.put(`/alert/${id}/`, data)
}


export function deleteAlert(id) {
    return api.delete(`/alert/${id}/`)
}