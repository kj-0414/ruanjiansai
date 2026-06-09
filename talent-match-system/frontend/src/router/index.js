import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import AdminLogin from '../views/AdminLogin.vue'
import JobSeekerLayout from '../layouts/JobSeekerLayout.vue'
import CompanyLayout from '../layouts/CompanyLayout.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import { setupRouterGuard } from './guard'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLogin
  },
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/job-seeker',
    component: JobSeekerLayout,
    children: [
      {
        path: 'home',
        name: 'JobSeekerHome',
        component: () => import('../views/Home.vue'),
        meta: { role: 'job_seeker' }
      },
      {
        path: 'resume',
        name: 'JobSeekerResumeList',
        component: () => import('../views/ResumeList.vue'),
        meta: { role: 'job_seeker' }
      },
      {
        path: 'resume/create',
        name: 'JobSeekerResumeCreate',
        component: () => import('../views/MyResume.vue'),
        meta: { role: 'job_seeker' }
      },
      {
        path: 'ability-analysis',
        name: 'JobSeekerAbilityAnalysis',
        component: () => import('../views/AbilityAnalysis.vue'),
        meta: { role: 'job_seeker' }
      },
      {
        path: 'job-match',
        name: 'JobSeekerJobMatch',
        component: () => import('../views/JobMatch.vue'),
        meta: { role: 'job_seeker' }
      },
      {
        path: 'job-detail/:id',
        name: 'JobSeekerJobDetail',
        component: () => import('../views/JobDetail.vue'),
        meta: { role: 'job_seeker' }
      },
      {
        path: 'messages',
        name: 'JobSeekerMessages',
        component: () => import('../views/Messages.vue'),
        meta: { role: 'job_seeker' }
      }
    ]
  },
  {
    path: '/company',
    component: CompanyLayout,
    children: [
      {
        path: 'home',
        name: 'CompanyHome',
        component: () => import('../views/Home.vue'),
        meta: { role: 'company' }
      },
      {
        path: 'my-jobs',
        name: 'CompanyMyJobs',
        component: () => import('../views/MyJobs.vue'),
        meta: { role: 'company' }
      },
      {
        path: 'job-analysis',
        name: 'CompanyJobAnalysis',
        component: () => import('../views/JobAnalysis.vue'),
        meta: { role: 'company' }
      },
      {
        path: 'talent-match',
        name: 'CompanyTalentMatch',
        component: () => import('../views/TalentMatch.vue'),
        meta: { role: 'company' }
      },
      {
        path: 'job-requirement-upload',
        name: 'CompanyJobRequirementUpload',
        component: () => import('../views/JobRequirementUpload.vue'),
        meta: { role: 'company' }
      },
      {
        path: 'messages',
        name: 'CompanyMessages',
        component: () => import('../views/Messages.vue'),
        meta: { role: 'company' }
      }
    ]
  },
  {
    path: '/admin',
    component: AdminLayout,
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('../views/admin/Dashboard.vue'),
        meta: { role: 'admin' }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('../views/admin/UserManagement.vue'),
        meta: { role: 'admin' }
      },
      {
        path: 'stats',
        name: 'AdminStats',
        component: () => import('../views/admin/Statistics.vue'),
        meta: { role: 'admin' }
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('../views/admin/Settings.vue'),
        meta: { role: 'admin' }
      },
      {
        path: 'messages',
        name: 'AdminMessages',
        component: () => import('../views/admin/MessageManagement.vue'),
        meta: { role: 'admin' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

setupRouterGuard(router)

router.afterEach(() => {
  setTimeout(() => {
    document.querySelectorAll('input, textarea').forEach(element => {
      element.style.pointerEvents = 'auto'
      element.style.userSelect = 'auto'
    })
  }, 100)
})

export default router
export { router }