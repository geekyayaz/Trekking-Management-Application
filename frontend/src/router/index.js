import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

import StaffView from '../views/staff/StaffView.vue'
import UserView from '../views/user/UserView.vue'
import StaffTrekDetailView from '../views/staff/StaffTrekDetailView.vue'
import UserHistoryView from '../views/user/UserHistoryView.vue'
import UserProfileView from '../views/user/UserProfileView.vue'
import Trekdetailview from '../views/user/Trekdetailview.vue'
// admin routes
import AdminView from '../views/admin/AdminView.vue'
import BookingsTab from '../views/admin/BookingsTab.vue'
import Reportstab from '../views/admin/Reportstab.vue'
import StaffTab from '../views/admin/StaffTab.vue'
import TreksTab from '../views/admin/TreksTab.vue'
import UsersTab from '../views/admin/UsersTab.vue'


const routes = [
  { path: '/', component: LandingView },
  { path: '/login', component: LoginView },
  { path: '/register', component: RegisterView },
  { path: '/admin/dashboard', component: AdminView },
  { path: '/staff', component: StaffView },
  { path: '/user', component: UserView },
  { path: '/:pathMatch(.*)*', redirect: '/' },
  { path: '/user/history', component: UserHistoryView },
  { path: '/user/trek/:id', component: Trekdetailview },
  { path: '/user/profile', component: UserProfileView },
  { path: '/staff/trek/:id', component: StaffTrekDetailView },
  { path: '/admin/bookings', component: BookingsTab},
  { path: '/admin/staff', component: StaffTab},
  { path: '/admin/treks', component: TreksTab},
  { path: '/admin/reports', component: Reportstab},
  { path: '/admin/users', component: UsersTab},
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router