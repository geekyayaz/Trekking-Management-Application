<template>
  <div>
    <nav class="navbar navbar-expand bg-body-tertiary mb-4">
      <div class="container-fluid">
        <span class="navbar-brand">My Bookings</span>
        <div class="d-flex align-items-center">
          <router-link to="/user" class="btn btn-sm btn-link">Browse Treks</router-link>
          <router-link to="/user/history" class="btn btn-sm btn-link">My Bookings</router-link>
          <router-link to="/user/profile" class="btn btn-sm btn-link">Profile</router-link>
          <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
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
        this.loadHistory() // refresh the table
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
      // Keep checking every 2 seconds until the job finishes
      try {
        const response = await axios.get(
          API_URL + '/export-history/status/' + taskId,
          { headers: this.authHeader() }
        )
        const state = response.data.state

        if (state === 'SUCCESS') {
          this.exportMessage = 'Export ready! Check your email for the CSV file.'
        } else if (state === 'FAILURE') {
          this.exportMessage = 'Export failed. Please try again.'
        } else {
          // still running - check again in 2 seconds
          setTimeout(() => {
            this.checkExportStatus(taskId)
          }, 2000)
        }
      } catch (error) {
        this.exportMessage = 'Could not check export status.'
      }
    },

    logout() {
      localStorage.clear()
      this.$router.push('/')
    }
  }
}
</script>