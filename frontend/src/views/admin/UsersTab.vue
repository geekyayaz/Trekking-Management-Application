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
              <a class="nav-link active" aria-current="page" href="/admin/users">Users</a>
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
        <div class="card-header">
          <h4 class="mb-0">Trekkers</h4>
        </div>
        <div class="card-body">

          <div class="row g-2 mb-3">
            <div class="col-md-8">
              <input v-model="searchText" class="form-control" placeholder="Search trekkers">
            </div>
            <div class="col-md-4">
              <button class="btn btn-primary w-100" @click="loadUsers">Search</button>
            </div>
          </div>

          <p v-if="loading">Loading...</p>

          <table v-if="!loading" class="table">
            <thead>
              <tr><th>Name</th><th>Username</th><th>Email</th><th>Bookings</th><th>Status</th><th></th></tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td>{{ u.name }}</td>
                <td>{{ u.username }}</td>
                <td>{{ u.email }}</td>
                <td>{{ u.total_bookings }}</td>
                <td>
                  <span v-if="u.blacklisted">Blacklisted</span>
                  <span v-else-if="!u.active">Inactive</span>
                  <span v-else>Active</span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-primary" @click="openEditForm(u)">Edit</button>
                  <button v-if="!u.blacklisted" class="btn btn-sm btn-outline-danger" @click="blacklist(u)">Blacklist</button>
                  <button v-else class="btn btn-sm btn-outline-success" @click="unblacklist(u)">Remove Blacklist</button>
                </td>
              </tr>
            </tbody>
          </table>

        </div>
      </div>

      <div v-if="editingUser" class="card mb-4 border-primary"  id="edit">
        <div class="card-header">
          <h5 class="mb-0">Edit: {{ editingUser.name }}</h5>
        </div>
        <div class="card-body">
          <form @submit.prevent="saveEdit">
            <div class="mb-2"><input v-model="editForm.name" class="form-control" placeholder="Name" required></div>
            <div class="mb-2"><input v-model="editForm.email" type="email" class="form-control" placeholder="Email" required></div>
            <div class="mb-2"><input v-model="editForm.phone" class="form-control" placeholder="Phone"></div>
            <div class="mb-2"><input v-model="editForm.address" class="form-control" placeholder="Address"></div>
            <button type="submit" class="btn btn-primary">Save</button>
            <button type="button" class="btn btn-secondary" @click="editingUser = null">Cancel</button>
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
  name: 'AdminUsersView',

  data() {
    return {
      users: [],
      loading: false,
      searchText: '',

      editingUser: null,
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
    this.loadUsers()
  },

  methods: {
    authHeader() {
      const token = localStorage.getItem('token')
      return { Authorization: 'Bearer ' + token }
    },

    async loadUsers() {
      this.loading = true
      try {
        const params = {}
        if (this.searchText) {
          params.search = this.searchText
        }
        const response = await axios.get(API_URL + '/users', {
          headers: this.authHeader(),
          params: params
        })
        this.users = response.data
      } catch (error) {
        alert('Could not load users.')
      }
      this.loading = false
    },

    async openEditForm(user) {
      try {
        // list doesn't include "address" - fetch full detail first
        const response = await axios.get(API_URL + '/users/' + user.id, {
          headers: this.authHeader()
        })
        this.editingUser = response.data
        this.editForm = {
          name: response.data.name,
          email: response.data.email,
          phone: response.data.phone,
          address: response.data.address
        }
      } catch (error) {
        console.error('openEditForm failed:', error)
        alert('Could not load user details for editing.')
      }
    },

    async saveEdit() {
      try {
        await axios.put(API_URL + '/users/' + this.editingUser.id, this.editForm, {
          headers: this.authHeader()
        })
        alert('User updated!')
        this.editingUser = null
        this.loadUsers()
      } catch (error) {
        alert('Could not save changes.')
      }
    },

    async blacklist(user) {
      const sure = confirm('Blacklist ' + user.name + '?')
      if (!sure) {
        return
      }
      try {
        await axios.put(API_URL + '/accounts/' + user.id + '/status',
          { blacklisted: true },
          { headers: this.authHeader() }
        )
        this.loadUsers()
      } catch (error) {
        alert('Could not blacklist user.')
      }
    },

    async unblacklist(user) {
      try {
        await axios.put(API_URL + '/accounts/' + user.id + '/status',
          { blacklisted: false, active: true },
          { headers: this.authHeader() }
        )
        this.loadUsers()
      } catch (error) {
        alert('Could not update user.')
      }
    },

    logout() {
      localStorage.clear()
      window.location.href = '/'
    }
  }
}
</script>