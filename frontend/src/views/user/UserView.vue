<template>
  <div>
    <nav class="navbar navbar-expand bg-body-tertiary mb-4">
      <div class="container-fluid">
        <span class="navbar-brand">Trekker Dashboard</span>
        <div class="d-flex align-items-center">
          <router-link to="/user" class="btn btn-sm btn-link">Home</router-link>
          <router-link to="/user/history" class="btn btn-sm btn-link">My Bookings</router-link>
          <router-link to="/user/profile" class="btn btn-sm btn-link">Profile</router-link>
          <span class="me-3">Hello, {{ userName }}</span>
          <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
        </div>
      </div>
    </nav>

    <div class="container">

      <div class="card mb-4">
        <div class="card-header">
          <h4 class="mb-0">Search Treks</h4>
        </div>
        <div class="card-body">
          <div class="row g-2 align-items-end">
            <div class="col-md-3">
              <label class="form-label">Difficulty</label>
              <select v-model="filterDifficulty" class="form-select">
                <option value="">Any</option>
                <option>Easy</option>
                <option>Moderate</option>
                <option>Hard</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">Location</label>
              <input v-model="filterLocation" class="form-control" placeholder="e.g. Himachal">
            </div>
            <div class="col-md-3">
              <label class="form-label">Duration (days)</label>
              <input v-model.number="filterDuration" type="number" class="form-control" placeholder="e.g. 5">
            </div>
            <div class="col-md-3">
              <button class="btn btn-primary w-100" @click="loadTreks">Search</button>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h4 class="mb-0">Open Treks</h4>
        </div>
        <div class="card-body">

          <p v-if="loading">Loading...</p>

          <p v-if="!loading && treks.length === 0" class="text-muted">
            No treks found. Try different search filters.
          </p>

          <table v-if="!loading && treks.length > 0" class="table table-hover">
            <thead>
              <tr>
                <th>Name</th>
                <th>Location</th>
                <th>Difficulty</th>
                <th>Duration</th>
                <th>Slots Left</th>
                <th>Dates</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="trek in treks" :key="trek.id">
                <td>{{ trek.name }}</td>
                <td>{{ trek.location }}, {{ trek.country }}</td>
                <td>{{ trek.difficulty }}</td>
                <td>{{ trek.duration_days }} days</td>
                <td>{{ trek.available_slots }} / {{ trek.total_slots }}</td>
                <td>{{ trek.start_date }} to {{ trek.end_date }}</td>
                <td>
                  <button><a :href="'/user/trek/' + trek.id" class="btn btn-outline-primary btn-sm">
                    View More
                  </a></button>
                  <button
                    class="btn btn-success btn-sm"
                    :disabled="trek.available_slots === 0"
                    @click="bookTrek(trek.id)"
                  >
                    {{ trek.available_slots === 0 ? 'Full' : 'Book' }}
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
  name: 'UserDashboardView',
 
  data() {
    return {
      userName: localStorage.getItem('name') || 'Trekker',
      treks: [],
      loading: false,
 
      filterDifficulty: '',
      filterLocation: '',
      filterDuration: null
    }
  },
 
  created() {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')
    if (!token || role !== 'user') {
      this.$router.push('/login')
      return
    }
    this.loadTreks()
  },
 
  methods: {
    authHeader() {
      const token = localStorage.getItem('token')
      return { Authorization: 'Bearer ' + token }
    },
 
    async loadTreks() {
      this.loading = true
      try {
        // build the query params - only add a filter if the user actually typed one
        const params = {}
        if (this.filterDifficulty) {
          params.difficulty = this.filterDifficulty
        }
        if (this.filterLocation) {
          params.location = this.filterLocation
        }
        if (this.filterDuration) {
          params.duration = this.filterDuration
        }
 
        const response = await axios.get(API_URL + '/treks', {
          headers: this.authHeader(),
          params: params
        })
        this.treks = response.data
      } catch (error) {
        alert('Could not load treks.')
      }
      this.loading = false
    },
 
    async bookTrek(trekId) {
      try {
        await axios.post(
          API_URL + '/treks/' + trekId + '/book',
          {},
          { headers: this.authHeader() }
        )
        alert('Trek booked successfully!')
        this.loadTreks() // refresh the list so available slots updates
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