import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Welcome from '../views/Welcome.vue'
import MFAVerify from '../views/MFAVerify.vue'
import MFASetup from '../views/MFASetup.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/mfa/verify',
    name: 'MFAVerify',
    component: MFAVerify
  },
  {
    path: '/mfa/setup',
    name: 'MFASetup',
    component: MFASetup
  },
  {
    path: '/welcome',
    name: 'Welcome',
    component: Welcome,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
