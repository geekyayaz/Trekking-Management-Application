<template>
  <div>
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
      <div class="container-fluid">
        <a class="navbar-brand" href="/">My Bookings</a>
        <div class="collapse navbar-collapse show">
          <ul class="navbar-nav mb-2 mb-lg-0 ms-auto">
            <li class="nav-item">
              <a class="nav-link" href="/user">Browse Treks</a>
            </li>
            <li class="nav-item">
              <a class="nav-link active" aria-current="page" href="/user/history">My Bookings</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/user/profile">Profile</a>
            </li>
            <li class="nav-item">
              <button class="btn btn-danger btn-sm" @click="logout">Logout</button>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container">

      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h4 class="mb-0">Booking History</h4>
          <button class="btn btn-outline-primary btn-sm" @click="exportHistory">
            Export as CSV
          </button>
        </div>
        <div class="card-body">

          <p v-if="exportMessage" class="alert alert-info">{{ exportMessage }}</p>

          <p v-if="loading">Loading...</p>

          <p v-if="!loading && bookings.length === 0" class="text-muted">
            You have not booked any treks yet.
          </p>

          <table v-if="!loading && bookings.length > 0" class="table table-hover">
            <thead>
              <tr>
                <th>Trek Name</th>
                <th>Location</th>
                <th>Dates</th>
                <th>Status</th>
                <th>Booked On</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="booking in bookings" :key="booking.booking_id">
                <td>{{ booking.trek_name }}</td>
                <td>{{ booking.location }}</td>
                <td>{{ booking.start_date }} to {{ booking.end_date }}</td>
                <td>{{ booking.status }}</td>
                <td>{{ new Date(booking.booked_on).toLocaleDateString() }}</td>
                <td>
                  <button
                    v-if="booking.status === 'Booked'"
                    class="btn btn-outline-danger btn-sm"
                    @click="cancelBooking(booking.booking_id)"
                  >
                    Cancel
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

        </div>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_URL = 'http://127.0.0.1:5000/api/user'

export default {
  name: 'UserHistoryView',

  data() {
    return {
      bookings: [],
      loading: false,
      exportMessage: ''
    }
  },

  created() {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')
    if (!token || role !== 'user') {
      this.$router.push('/login')
      return
    }
    this.loadHistory()
  },

  methods: {
    authHeader() {
      const token = localStorage.getItem('token')
      return { Authorization: 'Bearer ' + token }
    },

    async loadHistory() {
      this.loading = true
      try {
        const response = await axios.get(API_URL + '/bookings/history', {
          headers: this.authHeader()
        })
        this.bookings = response.data
      } catch (error) {
        alert('Could not load your booking history.')
      }
      this.loading = false
    },

    async cancelBooking(bookingId) {
      const sure = confirm('Are you sure you want to cancel this booking?')
      if (!sure) {
        return
      }
      try {
        await axios.post(
          API_URL + '/bookings/' + bookingId + '/cancel',
          {},
          { headers: this.authHeader() }
        )
        alert('Booking cancelled.')
        this.loadHistory()
      } catch (error) {
        alert('Could not cancel this booking.')
      }
    },

    async exportHistory() {
      this.exportMessage = 'Starting export...'
      try {
        const response = await axios.post(
          API_URL + '/export-history',
          {},
          { headers: this.authHeader() }
        )
        const taskId = response.data.task_id
        this.exportMessage = 'Export started! Checking status...'
        this.checkExportStatus(taskId)
      } catch (error) {
        this.exportMessage = 'Could not start export.'
      }
    },

    async checkExportStatus(taskId) {
      try {
        const response = await axios.get(
          API_URL + '/export-history/status/' + taskId,
          { headers: this.authHeader() }
        )
        const state = response.data.state

        if (state === 'SUCCESS') {
          this.exportMessage = 'Export ready! Your download should start automatically.'
          this.downloadFile(taskId)
        } else if (state === 'FAILURE') {
          this.exportMessage = 'Export failed. Please try again.'
        } else {
          setTimeout(() => {
            this.checkExportStatus(taskId)
          }, 2000)
        }
      } catch (error) {
        this.exportMessage = 'Could not check export status.'
      }
    },

    downloadFile(taskId) {
      const token = localStorage.getItem('token')
      const url = API_URL + '/export-history/download/' + taskId + '?token=' + token
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', '')
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },

    logout() {
      localStorage.clear()
      window.location.href = '/'
    }
  }
}
</script>