<template>
  <div class="main-layout">
    <header class="app-header">
      <div class="header-left">
        <button class="menu-toggle" @click="sidebarCollapsed = !sidebarCollapsed" v-if="isMobile">
          <el-icon :size="20"><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
        </button>
        <div class="brand">
          <div class="brand-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </div>
          <span class="brand-name">人才智能匹配</span>
        </div>
      </div>
      <div class="header-right">
        <span class="user-info" @click="toggleUserMenu">
          <el-avatar :size="32" class="user-avatar">{{ userAvatar }}</el-avatar>
          <span class="user-phone">{{ user?.phone }}</span>
          <el-tag size="small" type="success" class="role-tag">企业</el-tag>
          <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
        </span>
        <div class="user-dropdown" v-show="userMenuVisible">
          <div class="dropdown-item" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </div>
        </div>
      </div>
    </header>
    <div class="app-body">
      <aside class="app-sidebar" :class="{ collapsed: sidebarCollapsed, 'mobile-open': isMobile && !sidebarCollapsed }">
        <div class="sidebar-mask" @click="sidebarCollapsed = true" v-if="isMobile && !sidebarCollapsed"></div>
        <nav class="sidebar-nav">
          <template v-for="item in menuItems" :key="item.path">
            <router-link 
              :to="item.path" 
              class="nav-item"
              :class="{ active: isActive(item.path) }"
              @click="isMobile && (sidebarCollapsed = true)"
            >
              <div class="nav-icon">
                <el-icon :size="20"><component :is="item.icon" /></el-icon>
              </div>
              <span class="nav-text">{{ item.label }}</span>
            </router-link>
          </template>
        </nav>
      </aside>
      <main class="app-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in" appear>
            <div class="route-wrapper">
              <keep-alive :max="5">
                <component :is="Component" :key="$route.path" />
              </keep-alive>
            </div>
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authService } from '../services/auth'
import {
  ArrowDown, House, Briefcase, PieChart, UserFilled, Message,
  Fold, Expand, SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const user = ref(null)
const sidebarCollapsed = ref(false)
const userMenuVisible = ref(false)
const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) {
    sidebarCollapsed.value = false
  }
}

const handleClickOutside = (event) => {
  const headerRight = document.querySelector('.header-right')
  if (headerRight && !headerRight.contains(event.target)) {
    userMenuVisible.value = false
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  document.addEventListener('click', handleClickOutside)
  
  try {
    const userData = authService.getCurrentUser()
    if (userData) {
      user.value = {
        ...userData,
        role: userData.role || 'company'
      }
    } else {
      ElMessage.error('登录已过期，请重新登录')
      router.push('/login')
    }
  } catch (error) {
    ElMessage.error('登录已过期，请重新登录')
    router.push('/login')
  }
})

const userAvatar = computed(() => {
  if (!user.value?.phone) return 'U'
  return user.value.phone.charAt(user.value.phone.length - 2).toUpperCase()
})

const menuItems = computed(() => [
  { path: '/company/home', label: '首页', icon: House },
  { path: '/company/my-jobs', label: '我的岗位', icon: Briefcase },
  { path: '/company/job-analysis', label: '岗位分析', icon: PieChart },
  { path: '/company/talent-match', label: '人才匹配', icon: UserFilled },
  { path: '/company/messages', label: '消息中心', icon: Message }
])

const isActive = (path) => {
  if (path === '/company/home') {
    return route.path === '/company/home'
  }
  return route.path.startsWith(path)
}

const toggleUserMenu = () => {
  userMenuVisible.value = !userMenuVisible.value
}

const handleLogout = async () => {
  try {
    await authService.logout()
    router.push('/login')
  } catch (error) {
    ElMessage.error('退出登录失败')
  }
  userMenuVisible.value = false
}

watch(() => route.path, () => {
  userMenuVisible.value = false
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkMobile)
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-page);
}

.app-header {
  height: var(--header-height);
  background: var(--color-bg-card);
  box-shadow: var(--shadow-header);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-lg);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.menu-toggle {
  display: none;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: var(--space-xs);
  border-radius: var(--radius-sm);
  transition: all var(--duration-short) var(--ease-out);
}

.menu-toggle:hover {
  background: var(--color-bg-page);
  color: var(--color-primary);
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.brand-icon {
  width: 32px;
  height: 32px;
  background: var(--gradient-ai);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.brand-icon svg {
  width: 20px;
  height: 20px;
}

.brand-name {
  font-size: var(--font-size-h4);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-short) var(--ease-out);
}

.user-info:hover {
  background: var(--color-bg-page);
}

.user-avatar {
  background: var(--gradient-primary);
  color: white;
  font-weight: var(--font-weight-semibold);
}

.user-phone {
  font-size: var(--font-size-body);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.role-tag {
  border-radius: var(--radius-sm);
}

.dropdown-icon {
  color: var(--color-text-tertiary);
  font-size: 12px;
}

.user-dropdown {
  position: absolute;
  top: calc(100% + var(--space-xs));
  right: 0;
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-modal);
  min-width: 180px;
  padding: var(--space-sm) 0;
  overflow: hidden;
  z-index: 1001;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-lg);
  font-size: var(--font-size-body);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-short) var(--ease-out);
}

.dropdown-item:hover {
  background: var(--color-bg-page);
  color: var(--color-primary);
}

.dropdown-divider {
  border-top: 1px solid var(--color-border-light);
  margin-top: var(--space-xs);
  padding-top: var(--space-md);
}

.app-body {
  flex: 1;
  display: flex;
  margin-top: var(--header-height);
}

.app-sidebar {
  width: var(--sidebar-width);
  background: var(--color-bg-card);
  border-right: 1px solid var(--color-border-light);
  position: fixed;
  top: var(--header-height);
  bottom: 0;
  left: 0;
  transition: all var(--duration-normal) var(--ease-in-out);
  z-index: 100;
  overflow: hidden;
}

.app-sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-mask {
  display: none;
}

.sidebar-nav {
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  height: 100%;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--color-text-secondary);
  transition: all var(--duration-short) var(--ease-out);
  position: relative;
  height: 48px;
}

.nav-item:hover {
  background: var(--color-bg-page);
  color: var(--color-primary);
}

.nav-item.active {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--color-primary);
  border-radius: 0 2px 2px 0;
}

.nav-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-text {
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  white-space: nowrap;
  opacity: 1;
  transition: opacity var(--duration-short) var(--ease-out);
}

.app-sidebar.collapsed .nav-text {
  opacity: 0;
  width: 0;
  overflow: hidden;
}

.app-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  padding: var(--space-lg);
  max-width: var(--content-max-width);
  width: 100%;
  transition: margin-left var(--duration-normal) var(--ease-in-out);
  min-height: calc(100vh - var(--header-height));
}

.app-sidebar.collapsed ~ .app-content,
.app-content.sidebar-collapsed {
  margin-left: var(--sidebar-collapsed-width);
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all var(--duration-normal) var(--ease-out);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

.route-wrapper {
  width: 100%;
  height: 100%;
}

@media (max-width: 768px) {
  .menu-toggle {
    display: block;
  }
  
  .brand-name {
    display: none;
  }
  
  .user-phone {
    display: none;
  }
  
  .app-sidebar {
    transform: translateX(-100%);
  }
  
  .app-sidebar.mobile-open {
    transform: translateX(0);
  }
  
  .sidebar-mask {
    display: block;
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: -1;
  }
  
  .app-content {
    margin-left: 0;
    padding: var(--space-md);
  }
}
</style>