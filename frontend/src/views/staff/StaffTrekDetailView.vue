<template>
  <div>
    <nav class="navbar bg-body-tertiary mb-4">
      <div class="container-fluid">
        <span class="navbar-brand">Manage Trek</span>
        <a href="/staff" class="btn btn-outline-secondary btn-sm">
          &larr; Back to Dashboard
        </a>
      </div>
    </nav>

    <div class="container">

      <p v-if="loading">Loading...</p>

      <div v-if="!loading">

        <!-- trek info -->
        <div class="card mb-4">
          <div class="card-header">
            <h3 class="mb-0">{{ trek.name }}</h3>
          </div>
          <div class="card-body">
            <p><strong>Location:</strong> {{ trek.location }}, {{ trek.country }}</p>
            <p><strong>Difficulty:</strong> {{ trek.difficulty }}</p>
            <p><strong>Dates:</strong> {{ trek.start_date }} to {{ trek.end_date }}</p>
            <p><strong>Current Status:</strong> {{ trek.status }}</p>
          </div>
        </div>

        <!-- update slots -->
        <div class="card mb-4">
          <div class="card-header">
            <h4 class="mb-0">Update Available Slots</h4>
          </div>
          <div class="card-body">
            <p class="text-muted">Total slots: {{ trek.total_slots }}</p>
            <div class="row g-2 align-items-end">
              <div class="col-md-4">
                <label class="form-label">Available Slots</label>
                <input v-model.number="newSlots" type="number" class="form-control">
              </div>
              <div class="col-md-4">
                <button class="btn btn-primary" @click="updateSlots">Save Slots</button>
              </div>
            </div>
          </div>
        </div>

        <!-- update status -->
        <div class="card mb-4">
          <div class="card-header">
            <h4 class="mb-0">Update Trek Status</h4>
          </div>
          <div class="card-body">
            <div class="row g-2 align-items-end">
              <div class="col-md-4">
                <label class="form-label">Status</label>
                <select v-model="newStatus" class="form-select">
                  <option v-for="option in statusOptions" :key="option" :value="option">
                    {{ option }}
                  </option>
                </select>
              </div>
              <div class="col-md-4">
                <button class="btn btn-primary" @click="updateStatus">Save Status</button>
              </div>
            </div>
            <p class="text-muted mt-2 mb-0">
              Tip: you can move Open &rarr; Closed &rarr; Completed, or Closed &rarr; Open again.
            </p>
          </div>
        </div>

        <!-- registered participants -->
        <div class="card mb-4">
          <div class="card-header">
            <h4 class="mb-0">Registered Trekkers</h4>
          </div>
          <div class="card-body">
            <p v-if="participants.length === 0" class="text-muted">
              No one has booked this trek yet.
            </p>
            <table v-if="participants.length > 0" class="table table-hover">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in participants" :key="p.booking_id">
                  <td>{{ p.name }}</td>
                  <td>{{ p.email }}</td>
                  <td>{{ p.phone }}</td>
                  <td>{{ p.status }}</td>
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

const API_URL = 'http://127.0.0.1:5000/api/staff'

export default {
  name: 'StaffTrekDetailView',

  data() {
    return {
      trekId: this.$route.params.id, // comes from the URL, e.g. /staff/trek/5
      trek: {},
      participants: [],
      loading: false,

      newSlots: 0,
      newStatus: '',
      statusOptions: ['Open', 'Closed', 'Completed']
    }
  },

  created() {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')
    if (!token || role !== 'staff') {
      this.$router.push('/login')
      return
    }
    this.loadTrek()
    this.loadParticipants()
  },

  methods: {
    authHeader() {
      const token = localStorage.getItem('token')
      return { Authorization: 'Bearer ' + token }
    },

    async loadTrek() {
      this.loading = true
      try {
        const response = await axios.get(
          API_URL + '/treks/' + this.trekId,
          { headers: this.authHeader() }
        )
        this.trek = response.data
        this.newSlots = response.data.available_slots
        this.newStatus = response.data.status
      } catch (error) {
        alert('Could not load this trek.')
      }
      this.loading = false
    },

    async loadParticipants() {
      try {
        const response = await axios.get(
          API_URL + '/treks/' + this.trekId + '/participants',
          { headers: this.authHeader() }
        )
        this.participants = response.data
      } catch (error) {
        alert('Could not load participant list.')
      }
    },

    async updateSlots() {
      try {
        await axios.put(
          API_URL + '/treks/' + this.trekId + '/slots',
          { available_slots: this.newSlots },
          { headers: this.authHeader() }
        )
        alert('Slots updated!')
        this.loadTrek()
      } catch (error) {
        const message = error.response?.data?.message || 'Could not update slots.'
        alert(message)
      }
    },

    async updateStatus() {
      try {
        await axios.put(
          API_URL + '/treks/' + this.trekId + '/status',
          { status: this.newStatus },
          { headers: this.authHeader() }
        )
        alert('Status updated!')
        this.loadTrek()
      } catch (error) {
        const message = error.response?.data?.message || 'Could not update status.'
        alert(message)
      }
    }
  }
}
</script>