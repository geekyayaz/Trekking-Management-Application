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
              <a class="nav-link active" aria-current="page" href="/admin/bookings">Bookings</a>
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

    <div class="container mt-4">

      <div class="card">
        <div class="card-header">
          <h4 class="mb-0">All Bookings</h4>
        </div>
        <div class="card-body">

          <div class="row g-2 mb-3">
            <div class="col-md-4">
              <select v-model="statusFilter" @change="loadBookings" class="form-select">
                <option value="">All statuses</option>
                <option>Booked</option>
                <option>Cancelled</option>
                <option>Completed</option>
              </select>
            </div>
          </div>

          <p v-if="loading">Loading...</p>

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
                        <tr v-for="b in bookings" :key="b.booking_id">
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

    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_URL = 'http://127.0.0.1:5000/api/admin'

export default {
  name: 'AdminBookingsView',

  data() {
    return {
      bookings: [],
      loading: false,
      statusFilter: ''
    }
  },

  created() {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')
    if (!token || role !== 'admin') {
      this.$router.push('/login')
      return
    }
    this.loadBookings()
  },

  methods: {
    authHeader() {
      const token = localStorage.getItem('token')
      return { Authorization: 'Bearer ' + token }
    },

    async loadBookings() {
      this.loading = true
      try {
        const params = {}
        if (this.statusFilter) {
          params.status = this.statusFilter
        }
        const response = await axios.get(API_URL + '/bookings', {
          headers: this.authHeader(),
          params: params
        })
        this.bookings = response.data
      } catch (error) {
        alert('Could not load bookings.')
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