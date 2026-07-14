<template>
  <div>
    <nav class="navbar navbar-expand bg-body-tertiary mb-4">
      <div class="container-fluid">
        <span class="navbar-brand">My Profile</span>
        <div class="d-flex align-items-center">
          <router-link to="/user" class="btn btn-sm btn-link">Browse Treks</router-link>
          <router-link to="/user/history" class="btn btn-sm btn-link">My Bookings</router-link>
          <router-link to="/user/profile" class="btn btn-sm btn-link">Profile</router-link>
          <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
        </div>
      </div>
    </nav>

    <div class="container">

      <div class="card" style="max-width: 500px;">
        <div class="card-header">
          <h4 class="mb-0">Edit Profile</h4>
        </div>
        <div class="card-body">

          <p v-if="loading">Loading...</p>

          <form v-if="!loading" @submit.prevent="saveProfile">
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input :value="profile.username" class="form-control" disabled>
              <small class="text-muted">Username cannot be changed.</small>
            </div>

            <div class="mb-3">
              <label class="form-label">Email</label>
              <input :value="profile.email" class="form-control" disabled>
              <small class="text-muted">Email cannot be changed here.</small>
            </div>

            <div class="mb-3">
              <label class="form-label">Name</label>
              <input v-model="profile.name" class="form-control" required>
            </div>

            <div class="mb-3">
              <label class="form-label">Phone</label>
              <input v-model="profile.phone" class="form-control">
            </div>

            <div class="mb-3">
              <label class="form-label">Address</label>
              <input v-model="profile.address" class="form-control">
            </div>

            <p v-if="saveMessage" class="alert alert-info">{{ saveMessage }}</p>

            <button type="submit" class="btn btn-primary">Save Changes</button>
          </form>

        </div>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_URL = 'http://127.0.0.1:5000/api/user'

export default {
  name: 'UserProfileView',

  data() {
    return {
      profile: {
        username: '',
        email: '',
        name: '',
        phone: '',
        address: ''
      },
      loading: false,
      saveMessage: ''
    }
  },

  created() {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')
    if (!token || role !== 'user') {
      this.$router.push('/login')
      return
    }
    this.loadProfile()
  },

  methods: {
    authHeader() {
      const token = localStorage.getItem('token')
      return { Authorization: 'Bearer ' + token }
    },

    async loadProfile() {
      this.loading = true
      try {
        const response = await axios.get(API_URL + '/profile', {
          headers: this.authHeader()
        })
        this.profile = response.data
      } catch (error) {
        alert('Could not load your profile.')
      }
      this.loading = false
    },

    async saveProfile() {
      this.saveMessage = ''
      try {
        await axios.put(
          API_URL + '/profile',
          {
            name: this.profile.name,
            phone: this.profile.phone,
            address: this.profile.address
          },
          { headers: this.authHeader() }
        )
        this.saveMessage = 'Profile updated successfully!'
        // also update the name shown in the navbar right away
        localStorage.setItem('name', this.profile.name)
      } catch (error) {
        this.saveMessage = 'Could not save changes.'
      }
    },

    logout() {
      localStorage.clear()
      this.$router.push('/')
    }
  }
}
</script>