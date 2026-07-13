<template>
    <div class="mx-5">
        <nav class="navbar navbar-expand-lg bg-body-tertiary">
            <div class="container-fluid">
                <a class="navbar-brand" href="/">Admin Dashboard</a>
                <div class="collapse navbar-collapse show">
                    <ul class="navbar-nav mb-2 mb-lg-0 ms-auto">
                        <li class="nav-item">
                            <a class="nav-link active" aria-current="page" href="/admin/dashboard">Dashboard</a>
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
                            <a class="nav-link" href="/admin/reports">Reports</a>
                        </li>
                        <li class="nav-item">
                            <button class="btn btn-danger btn-sm" @click="logout">Logout</button>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
        <!---cards--->
        <div class="row g-3">
            <div class="col-12 col-sm-6 col-lg-3">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <h2>{{ stats.total_treks }}</h2>
                        <p class="text-muted mb-0">Total Treks</p>
                    </div>
                </div>
            </div>

            <div class="col-12 col-sm-6 col-lg-3">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <h2>{{ stats.total_users }}</h2>
                        <p class="text-muted mb-0">Total Users</p>
                    </div>
                </div>
            </div>

            <div class="col-12 col-sm-6 col-lg-3">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <h2>{{ stats.total_staff }}</h2>
                        <p class="text-muted mb-0">Total Staff</p>
                    </div>
                </div>
            </div>

            <div class="col-12 col-sm-6 col-lg-3">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <h2>{{ stats.total_bookings }}</h2>
                        <p class="text-muted mb-0">Total Bookings</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="card mb-4">
            <div class="card-header">
                <h3 id="drives">Recent Bookings</h3>
            </div>
            <div class="card-body">
                <table class="table">
                    <thead>
                        <tr>
                            <th scope="col"> Booking ID</th>
                            <th scope="col">Users</th>
                            <th scope="col">Trek Name</th>
                            <th scope="col">Booking Date</th>
                            <th scope="col">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="b in bookings.slice(0, 5)" :key="b.booking_id">
                            <td>{{ b.booking_id }}</td>
                            <td>{{ b.user_name }}</td>
                            <td>{{ b.trek_name }}</td>
                            <td>{{ new Date(b.booked_on).toLocaleString() }}</td>
                            <td>{{b.status}}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

const API_URL = 'http://127.0.0.1:5000/api/admin'

export default {
  name: 'AdminDashboardView',

  data() {
    return {
      stats: {},
      bookings: [],
      loading: false
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
    this.loadBookings()
  },

  methods: {
    authHeader() {
      const token = localStorage.getItem('token')
      return { Authorization: 'Bearer ' + token }
    },

    async loadStats() {
      this.loading = true
      try {
        const response = await axios.get(API_URL + '/dashboard', {
          headers: this.authHeader()
        })
        this.stats = response.data
      } catch (error) {
        alert('Could not load dashboard stats.')
      }
      this.loading = false
    },

    async loadBookings() {
      try {
        const response = await axios.get(API_URL + '/bookings', {
          headers: this.authHeader(),
          params: { limit: 5 } 
        })
        this.bookings = response.data
      } catch (error) {
        alert('Could not load recent bookings.')
      }
    },

    logout() {
      localStorage.clear()
      window.location.href = '/'
    }
  }
}
</script>