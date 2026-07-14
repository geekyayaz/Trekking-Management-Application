<template>
  <div>
    <!-- top bar -->
    <nav class="navbar bg-body-tertiary mb-4">
      <div class="container-fluid">
        <span class="navbar-brand">Staff Dashboard</span>
        <div>
          <span class="me-3">Hello, {{ staffName }}</span>
          <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
        </div>
      </div>
    </nav>

    <div class="container">

      <!-- stat boxes -->
      <div class="row mb-4">
        <div class="col-md-4">
          <div class="card text-center">
            <div class="card-body">
              <h2>{{ treks.length }}</h2>
              <p class="mb-0 text-muted">Assigned Treks</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card text-center">
            <div class="card-body">
              <h2>{{ openCount }}</h2>
              <p class="mb-0 text-muted">Open Treks</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card text-center">
            <div class="card-body">
              <h2>{{ totalTrekkers }}</h2>
              <p class="mb-0 text-muted">Total Trekkers</p>
            </div>
          </div>
        </div>
      </div>

      <!--ssigned treks -->
      <div class="card">
        <div class="card-header">
          <h4 class="mb-0">My Assigned Treks</h4>
        </div>
        <div class="card-body">

          <p v-if="loading">Loading...</p>

          <p v-if="!loading && treks.length === 0" class="text-muted">
            No treks assigned to you yet.
          </p>

          <table v-if="!loading && treks.length > 0" class="table table-hover">
            <thead>
              <tr>
                <th>Trek Name</th>
                <th>Status</th>
                <th>Slots</th>
                <th>Registered Trekkers</th>
                <th>Dates</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="trek in treks" :key="trek.id">
                <td>{{ trek.name }}</td>
                <td>{{ trek.status }}</td>
                <td>{{ trek.available_slots }} / {{ trek.total_slots }}</td>
                <td>{{ trek.registered_count }}</td>
                <td>{{ trek.start_date }} to {{ trek.end_date }}</td>
                <td>
                  <a :href="'/staff/trek/' + trek.id" class="btn btn-primary btn-sm">
                    Manage
                  </a>
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

// Base URL of the backend staff API - kept simple and at the top
const API_URL = 'http://127.0.0.1:5000/api/staff'

export default {
  name: 'StaffDashboardView',

  data() {
    return {
      staffName: localStorage.getItem('name') || 'Staff',
      treks: [],
      loading: false
    }
  },

  computed: {
    // computed = a value calculated FROM other data, updates automatically
    openCount() {
      let count = 0
      for (let i = 0; i < this.treks.length; i++) {
        if (this.treks[i].status === 'Open') {
          count = count + 1
        }
      }
      return count
    },
    totalTrekkers() {
      let total = 0
      for (let i = 0; i < this.treks.length; i++) {
        total = total + this.treks[i].registered_count
      }
      return total
    }
  },

  created() {
    // Simple guard: if not logged in as staff, send them to login page
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')
    if (!token || role !== 'staff') {
      this.$router.push('/login')
      return
    }
    this.loadMyTreks()
  },

  methods: {
    async loadMyTreks() {
      this.loading = true
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get(API_URL + '/treks', {
          headers: { Authorization: 'Bearer ' + token }
        })
        this.treks = response.data
      } catch (error) {
        alert('Could not load your treks. Please try again.')
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