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
export const getOrderSecretInfo = (id) => api.get(`/orders/${id}/secret`)
export const confirmOrderReceipt = (id) => api.post(`/orders/${id}/confirm-receipt`)
export const reportOrderIssue = (id, data) => api.post(`/orders/${id}/report-issue`, data)

// ---- Profile ----
export const getMe = () => api.get('/users/me')
export const updateMe = (data) => api.patch('/users/me', data)

// ---- Balance ----
export const getBalance = () => api.get('/balance/me')
export const createTopup = (data) => api.post('/topups', data)

// ---- News & Registration ----
export const registerUser = (data) => api.post('/register', data)
export const getNews = () => api.get('/news')
export const adminCreateNews = (data) => api.post('/admin/news', data)
export const adminDeleteNews = (id) => api.delete(`/admin/news/${id}`)

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
export const adminBlockUser = (id) => api.post(`/admin/users/${id}/block`)
export const adminUnblockUser = (id) => api.post(`/admin/users/${id}/unblock`)

// ---- Admin Product Management ----
export const adminCreateProduct = (data) => api.post('/admin/products', data)
export const adminUpdateProduct = (id, data) => api.patch(`/admin/products/${id}`, data)
export const adminDeleteProduct = (id) => api.delete(`/admin/products/${id}`)

// ---- Admin Reviews ----
export const adminGetPendingReviews = () => api.get('/admin/reviews/pending')
export const adminApproveReview = (id) => api.post(`/admin/reviews/${id}/approve`)
export const adminRejectReview = (id) => api.post(`/admin/reviews/${id}/reject`)

// ---- Admin Settings ----
export const adminGetSettings = () => api.get('/admin/settings')
export const adminUpdateSettings = (data) => api.patch('/admin/settings', data)

// ---- Chat API ----
export const getChatMessages = () => api.get('/chat/messages')
export const sendChatMessage = (data) => api.post('/chat/messages', data)
export const adminGetChatRooms = () => api.get('/admin/chat/rooms')
export const adminGetRoomMessages = (userId) => api.get(`/admin/chat/rooms/${userId}/messages`)
export const adminSendRoomMessage = (userId, data) => api.post(`/admin/chat/rooms/${userId}/messages`, data)

// ---- Admin Audit Log ----
export const adminGetAuditLog = (params = {}) => api.get('/admin/audit', { params })

// ---- Jobs & Applications ----
export const getJobs = () => api.get('/jobs')
export const applyJob = (data) => api.post('/jobs/apply', data)
export const getMyJobApplications = () => api.get('/jobs/my-applications')

export const adminGetJobs = () => api.get('/admin/jobs')
export const adminCreateJob = (data) => api.post('/admin/jobs', data)
export const adminUpdateJob = (id, data) => api.patch(`/admin/jobs/${id}`, data)
export const adminDeleteJob = (id) => api.delete(`/admin/jobs/${id}`)

export const adminGetJobApplications = () => api.get('/admin/jobs/applications')
export const adminApproveJobApplication = (id, data = {}) => api.post(`/admin/jobs/applications/${id}/approve`, data)
export const adminRejectJobApplication = (id, data = {}) => api.post(`/admin/jobs/applications/${id}/reject`, data)

export default api


