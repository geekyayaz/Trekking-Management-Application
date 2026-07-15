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
              <a class="nav-link active" aria-current="page" href="/admin/staff">Staff</a>
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
          <h4 class="mb-0">Trek Staff</h4>
          <button class="btn btn-success btn-sm" @click="showCreateForm = !showCreateForm">
            {{ showCreateForm ? 'Cancel' : '+ New Staff' }}
          </button>
        </div>
        <div class="card-body">

          <div class="row g-2 mb-3">
            <div class="col-md-8">
              <input v-model="searchText" class="form-control" placeholder="Search staff">
            </div>
            <div class="col-md-4">
              <button class="btn btn-primary w-100" @click="loadStaff">Search</button>
            </div>
          </div>

          <form v-if="showCreateForm" @submit.prevent="createStaff" class="border rounded p-3 mb-3 bg-light">
            <div class="row g-2">
              <div class="col-md-6"><input v-model="newStaff.name" class="form-control" placeholder="Name" required></div>
              <div class="col-md-6"><input v-model="newStaff.username" class="form-control" placeholder="Username" required></div>
              <div class="col-md-6"><input v-model="newStaff.email" type="email" class="form-control" placeholder="Email" required></div>
              <div class="col-md-6"><input v-model="newStaff.password" type="password" class="form-control" placeholder="Password" required></div>
              <div class="col-md-6"><input v-model="newStaff.phone" class="form-control" placeholder="Phone"></div>
            </div>
            <button type="submit" class="btn btn-primary mt-2">Add Staff</button>
          </form>

          <p v-if="loading">Loading...</p>

          <table v-if="!loading" class="table table-hover">
            <thead>
              <tr><th>Name</th><th>Username</th><th>Email</th><th>Assigned Treks</th><th>Status</th><th></th></tr>
            </thead>
            <tbody>
              <tr v-for="s in staffList" :key="s.id">
                <td>{{ s.name }}</td>
                <td>{{ s.username }}</td>
                <td>{{ s.email }}</td>
                <td>{{ s.assigned_trek_count }}</td>
                <td>
                  <span v-if="s.blacklisted">Blacklisted</span>
                  <span v-else-if="!s.active">Inactive</span>
                  <span v-else>Active</span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-primary" @click="openEditForm(s)">Edit</button>
                  <button class="btn btn-sm btn-outline-danger" @click="toggleActive(s)">
                    {{ s.active && !s.blacklisted ? 'Deactivate' : 'Reactivate' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

        </div>
      </div>

      <div v-if="editingStaff" class="card mb-4 border-primary">
        <div class="card-header">
          <h5 class="mb-0">Edit: {{ editingStaff.name }}</h5>
        </div>
        <div class="card-body">
          <form @submit.prevent="saveEdit">
            <div class="mb-2"><input v-model="editForm.name" class="form-control" placeholder="Name" required></div>
            <div class="mb-2"><input v-model="editForm.email" type="email" class="form-control" placeholder="Email" required></div>
            <div class="mb-2"><input v-model="editForm.phone" class="form-control" placeholder="Phone"></div>
            <div class="mb-2"><input v-model="editForm.address" class="form-control" placeholder="Address"></div>
            <button type="submit" class="btn btn-primary">Save</button>
            <button type="button" class="btn btn-secondary" @click="editingStaff = null">Cancel</button>
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
  name: 'AdminStaffView',

  data() {
    return {
      staffList: [],
      loading: false,
      searchText: '',

      showCreateForm: false,
      newStaff: { name: '', username: '', email: '', password: '', phone: '' },

      editingStaff: null,
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
    this.loadStaff()
  },

  methods: {
    authHeader() {
      const token = localStorage.getItem('token')
      return { Authorization: 'Bearer ' + token }
    },

    async loadStaff() {
      this.loading = true
      try {
        const params = {}
        if (this.searchText) {
          params.search = this.searchText
        }
        const response = await axios.get(API_URL + '/staff', {
          headers: this.authHeader(),
          params: params
        })
        this.staffList = response.data
      } catch (error) {
        alert('Could not load staff.')
      }
      this.loading = false
    },

    async createStaff() {
      try {
        await axios.post(API_URL + '/staff', this.newStaff, {
          headers: this.authHeader()
        })
        alert('Staff added!')
        this.showCreateForm = false
        this.newStaff = { name: '', username: '', email: '', password: '', phone: '' }
        this.loadStaff()
      } catch (error) {
        const message = error.response?.data?.message || 'Could not add staff.'
        alert(message)
      }
    },

    async openEditForm(staff) {
      const response = await axios.get(API_URL + '/staff/' + staff.id, {
        headers: this.authHeader()
      })
      this.editingStaff = response.data
      this.editForm = {
        name: response.data.name,
        email: response.data.email,
        phone: response.data.phone,
        address: response.data.address
      }
    },

    async saveEdit() {
      try {
        await axios.put(API_URL + '/staff/' + this.editingStaff.id, this.editForm, {
          headers: this.authHeader()
        })
        alert('Staff updated!')
        this.editingStaff = null
        this.loadStaff()
      } catch (error) {
        alert('Could not save changes.')
      }
    },

    async toggleActive(staff) {
      const makeActive = !(staff.active && !staff.blacklisted)
      try {
        await axios.put(API_URL + '/accounts/' + staff.id + '/status',
          { active: makeActive, blacklisted: false },
          { headers: this.authHeader() }
        )
        this.loadStaff()
      } catch (error) {
        alert('Could not update staff status.')
      }
    },

    logout() {
      localStorage.clear()
      window.location.href = '/'
    }
  }
}
</script>