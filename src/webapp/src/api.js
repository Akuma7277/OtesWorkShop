import axios from 'axios'
import { initData } from './tg'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach Telegram initData to every request
api.interceptors.request.use((config) => {
  if (initData) {
    config.headers['X-Telegram-Init-Data'] = initData
  }
  return config
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const msg = err?.response?.data?.detail || err?.message || 'Xatolik yuz berdi'
    return Promise.reject(new Error(msg))
  }
)

// ---- Products ----
export const getProducts = (params = {}) => api.get('/products', { params })
export const getProduct = (id) => api.get(`/products/${id}`)

// ---- Categories ----
export const getCategories = () => api.get('/categories')

// ---- Orders ----
export const getMyOrders = (params = {}) => api.get('/orders/me', { params })
export const getOrderDetail = (id) => api.get(`/orders/${id}`)
export const placeOrder = (data) => api.post('/orders', data)
export const cancelOrder = (id) => api.post(`/orders/${id}/cancel`)

// ---- Profile ----
export const getMe = () => api.get('/users/me')
export const updateMe = (data) => api.patch('/users/me', data)

// ---- Balance ----
export const getBalance = () => api.get('/balance/me')
export const createTopup = (data) => api.post('/topups', data)

// ---- Reviews ----
export const getReviews = (params = {}) => api.get('/reviews', { params })
export const submitReview = (data) => api.post('/reviews', data)

// ---- Admin ----
export const adminGetDashboard = () => api.get('/admin/dashboard')
export const adminGetOrders = (params = {}) => api.get('/admin/orders', { params })
export const adminApproveOrder = (id) => api.post(`/admin/orders/${id}/approve`)
export const adminRejectOrder = (id, reason) => api.post(`/admin/orders/${id}/reject`, { reason })
export const adminSetDeliveryStatus = (id, status) => api.post(`/admin/orders/${id}/delivery`, { status })
export const adminGetPendingTopups = () => api.get('/admin/topups/pending')
export const adminApproveTopup = (id) => api.post(`/admin/topups/${id}/approve`)
export const adminRejectTopup = (id, note) => api.post(`/admin/topups/${id}/reject`, { note })
export const adminGetUsers = (params = {}) => api.get('/admin/users', { params })
export const adminApproveUser = (id) => api.post(`/admin/users/${id}/approve`)
export const adminRejectUser = (id, reason) => api.post(`/admin/users/${id}/reject`, { reason })

export default api
