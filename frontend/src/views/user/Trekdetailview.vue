<template>
  <div>
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
      <div class="container-fluid">
        <a class="navbar-brand" href="/">My Bookings</a>
        <div class="collapse navbar-collapse show">
          <ul class="navbar-nav mb-2 mb-lg-0 ms-auto">
            <li class="nav-item">
              <a class="nav-link active" aria-current="page" href="/user">Browse Treks</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/user/history">My Bookings</a>
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

    <div class="container mt-4">

      <a href="/user" class="btn btn-outline-secondary btn-sm mb-3">&larr; Back to Treks</a>

      <p v-if="loading">Loading...</p>

      <div v-if="!loading && trek" class="card mb-4">
        <div class="card-header text-center">
          <h2 class="mb-0">{{ trek.name }}</h2>
        </div>

        <table class="table mb-0">
          <tbody>
            <tr>
              <td>Country</td>
              <td>{{ trek.country }}</td>
            </tr>
            <tr>
              <td>Location</td>
              <td>{{ trek.location }}</td>
            </tr>
            <tr>
              <td>Difficulty</td>
              <td>{{ trek.difficulty }}</td>
            </tr>
            <tr>
              <td>Duration</td>
              <td>{{ trek.duration_days }} days</td>
            </tr>
            <tr>
              <td>Available Slots</td>
              <td>{{ trek.available_slots }} / {{ trek.total_slots }}</td>
            </tr>
            <tr>
              <td>Dates</td>
              <td>{{ trek.start_date }} to {{ trek.end_date }}</td>
            </tr>
            <tr>
              <td>Status</td>
              <td>{{ trek.status }}</td>
            </tr>
            <tr>
              <td>Assigned Staff Name</td>
              <td>{{ trek.assigned_staff_name || 'Not yet assigned' }}</td>
            </tr>
            <tr>
              <td>Assigned Staff Phone</td>
              <td>{{ trek.assigned_staff_phone || '-' }}</td>
            </tr>
            <tr>
              <td>Description</td>
              <td>{{ trek.description || 'No description provided.' }}</td>
            </tr>
          </tbody>
        </table>

        <div class="card-body">
          <button
            class="btn btn-success"
            :disabled="trek.available_slots === 0 || trek.status !== 'Open'"
            @click="bookTrek"
          >
            {{ bookButtonLabel }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_URL = 'http://127.0.0.1:5000/api/user'

export default {
  name: 'TrekDetailView',

  data() {
    return {
      trekId: this.$route.params.id,
      trek: null,
      loading: false
    }
  },

  computed: {
    bookButtonLabel() {
      if (this.trek.status !== 'Open') {
        return 'Not Open for Booking'
      }
      if (this.trek.available_slots === 0) {
        return 'Full'
      }
      return 'Book This Trek'
    }
  },

  created() {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')
    if (!token || role !== 'user') {
      window.location.href = '/login'
      return
    }
    this.loadTrek()
  },

  methods: {
    authHeader() {
      const token = localStorage.getItem('token')
      return { Authorization: 'Bearer ' + token }
    },

    async loadTrek() {
      this.loading = true
      try {
        const response = await axios.get(API_URL + '/treks/' + this.trekId, {
          headers: this.authHeader()
        })
        this.trek = response.data
      } catch (error) {
        alert('Could not load trek details.')
      }
      this.loading = false
    },

    async bookTrek() {
      try {
        await axios.post(
          API_URL + '/treks/' + this.trekId + '/book',
          {},
          { headers: this.authHeader() }
        )
        alert('Trek booked successfully!')
        this.loadTrek() // refresh so slot count updates
      } catch (error) {
        const message = error.response?.data?.message || 'Could not book this trek.'
        alert(message)
      }
    },

    logout() {
      localStorage.clear()
      window.location.href = '/'
    }
  }
}
</script>