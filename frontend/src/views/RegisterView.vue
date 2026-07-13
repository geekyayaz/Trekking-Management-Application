<template>
  <div class="d-flex justify-content-center align-items-center vh-100">
    <div class="card shadow">
      <div class="card-body">
        <h2 class="card-title text-center mb-4">Create account</h2>

        <form @submit.prevent="handleRegister">
          <div class="mb-3">
            <label class="form-label">Name</label>
            <input v-model="form.name" class="form-control" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Username</label>
            <input v-model="form.username" class="form-control" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="form.email" type="email" class="form-control" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="form.password" type="password" class="form-control" required>
          </div>

          <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
          <div v-if="success" class="alert alert-success py-2">Account created!</div>

          <button type="submit" class="btn btn-primary w-100">Register</button>
        </form>

        <p class="text-center text-muted mb-0">
                            Already have an account?
                            <a href="/login">Login here</a>
                        </p>

      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'RegisterView',
  data() {
    return {
      form: { name: '', username: '', email: '', password: '' },
      error: '', success: false, loading: false
    }
  },
  methods: {
    async handleRegister() {
      this.error = ''
      this.loading = true
      try {
        await axios.post('http://127.0.0.1:5000/api/auth/register', this.form)
        this.success = true
        setTimeout(() => this.$router.push('/login'), 1200)
      } catch (err) {
        this.error = err.response?.data?.message || 'Registration failed'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>