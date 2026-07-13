<template>
  <div>
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
      <div class="container-fluid">
        <a class="navbar-brand" href="/">Admin Dashboard</a>
        <div class="collapse navbar-collapse show">
          <ul class="navbar-nav mb-2 mb-lg-0 ms-auto">
            <li class="nav-item">
              <a class="nav-link" href="/admin/dashboard">Dashboard</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/admin/treks">Treks</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/admin/staff">Staff</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/admin/users">Users</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/admin/bookings">Bookings</a>
            </li>
            <li class="nav-item">
              <a class="nav-link active" aria-current="page" href="/admin/reports">Reports</a>
            </li>
            <li class="nav-item">
              <button class="btn btn-danger btn-sm" @click="logout">Logout</button>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container mt-4">

      <div class="row g-3">
        <div class="col-md-3">
          <div class="card text-center">
            <div class="card-body">
              <h4>{{ stats.open_treks }}</h4>
              <small class="text-muted">Open Treks</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-center">
            <div class="card-body">
              <h4>{{ stats.completed_treks }}</h4>
              <small class="text-muted">Completed Treks</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-center">
            <div class="card-body">
              <h4>{{ stats.cancellation_rate_percent }}%</h4>
              <small class="text-muted">Cancellation Rate</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-center">
            <div class="card-body">
              <h4>{{ stats.active_staff }}</h4>
              <small class="text-muted">Active Staff</small>
            </div>
          </div>
        </div>

        <div class="col-12">
          <div class="card">
            <div class="card-body">
              <h5>Most Popular Treks</h5>
              <ul class="list-group">
                <li v-for="t in stats.popular_treks" :key="t.trek_id" class="list-group-item d-flex justify-content-between">
                  {{ t.trek_name }}
                  <span class="badge bg-primary rounded-pill">{{ t.booking_count }} bookings</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_URL = 'http://127.0.0.1:5000/api/admin'

export default {
  name: 'AdminReportsView',

  data() {
    return {
      stats: {},
    }
  },

  created() {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')
    if (!token || role !== 'admin') {
      this.$router.push('/login')
      return
    }
    this.loadStats()
  },

  methods: {
    authHeader() {
      const token = localStorage.getItem('token')
      return { Authorization: 'Bearer ' + token }
    },

    async loadStats() {
      this.loading = true
      try {
        const response = await axios.get(API_URL + '/reports/stats', {
          headers: this.authHeader()
        })
        this.stats = response.data
      } catch (error) {
        alert('Could not load reports.')
      }
      this.loading = false
    },

    logout() {
      localStorage.clear()
      window.location.href = '/'
    }
  }
}
</script>