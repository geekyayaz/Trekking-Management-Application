<template>
  <div class="container-fluid d-flex justify-content-center align-items-center vh-100">
    <div class="card" style="width: 18rem;">
      <div class="card-body">
        <h2 class="card-title text-center mb-4">Log in</h2>

        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label class="form-label">Username</label>
            <input v-model="username" type="text" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="password" type="password" class="form-control" required />
          </div>
          <button type="submit" class="btn btn-primary">Login</button>
        </form>

        <div v-if="error" class="alert alert-danger mt-3 mb-0">{{ error }}</div>

        <p style="font-size: small; margin: 15px;">Donot have an account? <a href="/register">Register</a></p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.error = ''
      try {
        const res = await axios.post('http://127.0.0.1:5000/api/auth/login', {
          username: this.username,
          password: this.password
        })
        const userData = res.data.data
        localStorage.setItem('token', userData.access_token)
        localStorage.setItem('role', userData.role)
        localStorage.setItem('user', JSON.stringify(userData))

        if (userData.role === 'admin') {
          this.$router.push('/admin/dashboard/')
        } else if (userData.role === 'staff') {
          this.$router.push('/staff')
        } else {
          this.$router.push('/user')
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Login failed'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>