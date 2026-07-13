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
              <a class="nav-link active" aria-current="page" href="/admin/treks">Treks</a>
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

    <div class="container mt-4">

      <div class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h4 class="mb-0">Treks</h4>
          <button class="btn btn-success btn-sm" @click="showCreateForm = !showCreateForm">
            {{ showCreateForm ? 'Cancel' : '+ New Trek' }}
          </button>
        </div>
        <div class="card-body">

          <!-- search -->
          <div class="row g-2 mb-3">
            <div class="col-md-8">
              <input v-model="searchText" class="form-control" placeholder="Search by name, location, country">
            </div>
            <div class="col-md-4">
              <button class="btn btn-primary w-100" @click="loadTreks">Search</button>
            </div>
          </div>

          <!-- create form -->
          <form v-if="showCreateForm" @submit.prevent="createTrek" class="border rounded p-3 mb-3 bg-light">
            <div class="row g-2">
              <div class="col-md-4"><input v-model="newTrek.name" class="form-control" placeholder="Name" required></div>
              <div class="col-md-4"><input v-model="newTrek.country" class="form-control" placeholder="Country" required></div>
              <div class="col-md-4"><input v-model="newTrek.location" class="form-control" placeholder="Location" required></div>
              <div class="col-md-4">
                <select v-model="newTrek.difficulty" class="form-select" required>
                  <option value="">Difficulty...</option>
                  <option>Easy</option>
                  <option>Moderate</option>
                  <option>Hard</option>
                </select>
              </div>
              <div class="col-md-4"><input v-model.number="newTrek.duration_days" type="number" class="form-control" placeholder="Duration days" required></div>
              <div class="col-md-4"><input v-model.number="newTrek.total_slots" type="number" class="form-control" placeholder="Total slots" required></div>
              <div class="col-md-6"><input v-model="newTrek.start_date" type="date" class="form-control" required></div>
              <div class="col-md-6"><input v-model="newTrek.end_date" type="date" class="form-control" required></div>
              <div class="col-12"><textarea v-model="newTrek.description" class="form-control" placeholder="Description"></textarea></div>
            </div>
            <button type="submit" class="btn btn-primary mt-2">Create Trek</button>
          </form>

          <p v-if="loading">Loading...</p>

       <div>
            <div>
                <table class="table">
                    <thead>
                        <tr>
                            <th scope="col">Name ID</th>
                            <th scope="col">Location</th>
                            <th scope="col">Slots</th>
                            <th scope="col">Assigned Staff</th>
                            <th scope="col">Status</th>
                            
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="trek in treks" :key="trek.id">
                            <th scope="row">{{ trek.name }}</th>
                            <td>{{ trek.location }}, {{ trek.country }}</td>
                            <td>{{ trek.available_slots }} / {{ trek.total_slots }}</td>
                            <td><select class="form-select form-select-sm" v-model="trek.assigned_staff_id" @change="changeStaff(trek)">
                    <option :value="null">Unassigned</option>
                    <option v-for="s in staffList" :key="s.id" :value="s.id">{{ s.name }}</option>
                  </select>
</td>
                            <td><select class="form-select form-select-sm" v-model="trek.status" @change="changeStatus(trek)">
                    <option v-for="s in statusOptions" :key="s">{{ s }}</option>
                  </select>
</td>
                            <td>                  <button class="btn btn-sm btn-outline-primary" @click="openEditForm(trek)">Edit</button>
                  <button class="btn btn-sm btn-outline-danger" @click="deleteTrek(trek)">Delete</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        </div>
      </div>

      <!-- Edit -->
<div v-if="editingTrek" class="card mb-4">
  <div class="card-header">
    Edit Trek: {{ editingTrek.name }}
  </div>
  <div class="card-body">
    <form @submit.prevent="saveEdit">

      <div class="mb-3">
        <label class="form-label">Name</label>
        <input v-model="editForm.name" class="form-control" required>
      </div>

      <div class="mb-3">
        <label class="form-label">Country</label>
        <input v-model="editForm.country" class="form-control" required>
      </div>

      <div class="mb-3">
        <label class="form-label">Location</label>
        <input v-model="editForm.location" class="form-control" required>
      </div>

      <div class="mb-3">
        <label class="form-label">Difficulty</label>
        <select v-model="editForm.difficulty" class="form-select">
          <option>Easy</option>
          <option>Moderate</option>
          <option>Hard</option>
        </select>
      </div>

      <div class="mb-3">
        <label class="form-label">Duration (days)</label>
        <input v-model.number="editForm.duration_days" type="number" class="form-control">
      </div>

      <div class="mb-3">
        <label class="form-label">Total Slots</label>
        <input v-model.number="editForm.total_slots" type="number" class="form-control">
      </div>

      <div class="mb-3">
        <label class="form-label">Start Date</label>
        <input v-model="editForm.start_date" type="date" class="form-control">
      </div>

      <div class="mb-3">
        <label class="form-label">End Date</label>
        <input v-model="editForm.end_date" type="date" class="form-control">
      </div>

      <div class="mb-3">
        <label class="form-label">Description</label>
        <textarea v-model="editForm.description" class="form-control" rows="3"></textarea>
      </div>

      <button type="submit" class="btn btn-primary">Save</button>
      <button type="button" class="btn btn-secondary" @click="editingTrek = null">Cancel</button>

    </form>
  </div>
</div>

    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_URL = 'http://127.0.0.1:5000/api/admin'

export default {
  name: 'AdminTreksView',

  data() {
    return {
      treks: [],
      staffList: [],
      loading: false,
      searchText: '',
      statusOptions: ['Pending', 'Approved', 'Open', 'Closed', 'Completed'],

      showCreateForm: false,
      newTrek: {
        name: '', country: '', location: '', difficulty: '',
        duration_days: null, total_slots: null,
        start_date: '', end_date: '', description: ''
      },

      editingTrek: null,
      editForm: {}
    }
  },

  created() {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')
    if (!token || role !== 'admin') {
      this.$router.push('/login')
      return
    }
    this.loadTreks()
    this.loadStaffList()
  },

  methods: {
    authHeader() {
      const token = localStorage.getItem('token')
      return { Authorization: 'Bearer ' + token }
    },

    async loadTreks() {
      this.loading = true
      try {
        const params = {}
        if (this.searchText) {
          params.search = this.searchText
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

    async loadStaffList() {
      try {
        const response = await axios.get(API_URL + '/staff', {
          headers: this.authHeader()
        })
        this.staffList = response.data
      } catch (error) {
        alert('Could not load staff list.')
      }
    },

    async createTrek() {
      try {
        await axios.post(API_URL + '/treks', this.newTrek, {
          headers: this.authHeader()
        })
        alert('Trek created!')
        this.showCreateForm = false
        this.newTrek = {
          name: '', country: '', location: '', difficulty: '',
          duration_days: null, total_slots: null,
          start_date: '', end_date: '', description: ''
        }
        this.loadTreks()
      } catch (error) {
        const message = error.response?.data?.message || 'Could not create trek.'
        alert(message)
      }
    },

    async changeStatus(trek) {
      try {
        await axios.put(API_URL + '/treks/' + trek.id, { status: trek.status }, {
          headers: this.authHeader()
        })
        this.loadTreks()
      } catch (error) {
        alert('Could not update status.')
        this.loadTreks()
      }
    },

    async changeStaff(trek) {
      try {
        await axios.post(API_URL + '/treks/' + trek.id + '/assign-staff',
          { staff_id: trek.assigned_staff_id },
          { headers: this.authHeader() }
        )
        this.loadTreks()
      } catch (error) {
        alert('Could not assign staff.')
        this.loadTreks()
      }
    },

    openEditForm(trek) {
      this.editingTrek = trek
      this.editForm = {
        name: trek.name,
        country: trek.country,
        location: trek.location,
        difficulty: trek.difficulty,
        duration_days: trek.duration_days,
        total_slots: trek.total_slots,
        start_date: trek.start_date,
        end_date: trek.end_date,
        description: trek.description
      }
    },

    async saveEdit() {
      try {
        await axios.put(API_URL + '/treks/' + this.editingTrek.id, this.editForm, {
          headers: this.authHeader()
        })
        alert('Trek updated!')
        this.editingTrek = null
        this.loadTreks()
      } catch (error) {
        alert('Could not save changes.')
      }
    },

    async deleteTrek(trek) {
      const sure = confirm('Delete "' + trek.name + '"? This cannot be undone.')
      if (!sure) {
        return
      }
      try {
        await axios.delete(API_URL + '/treks/' + trek.id, {
          headers: this.authHeader()
        })
        this.loadTreks()
      } catch (error) {
        const message = error.response?.data?.message || 'Could not delete trek.'
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