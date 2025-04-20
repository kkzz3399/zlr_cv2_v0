import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api'

export default {
  login(credentials) {
    return axios.post(`${API_URL}/auth/login`, credentials)
  },
  register(userData) {
    return axios.post(`${API_URL}/auth/register`, userData)
  },
  getMe() {
    return axios.get(`${API_URL}/auth/me`)
  }
}
