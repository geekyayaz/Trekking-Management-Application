<template>
  <div class="container-fluid d-flex justify-content-center align-items-center min-vh-100 bg-light">
    <div class="text-center">
      <h1 class="mb-2">Trekking Management Application</h1>
      <p class="text-muted mb-4">Plan, manage, and Book Treks all in one place.</p>
      <router-link to="/login" class="btn btn-primary btn-lg mx-2">Login</router-link>
      <router-link to="/register" class="btn btn-outline-primary btn-lg mx-2">Register</router-link>
    </div>
  </div>
</template>

<script>
export default { name: 'LandingView' }
</script>