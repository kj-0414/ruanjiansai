<template>
  <div class="app-container">
    <router-view v-slot="{ Component }">
      <Transition name="fade" mode="out-in">
        <div class="transition-root">
          <component :is="Component" :key="$route.path" />
        </div>
      </Transition>
    </router-view>
  </div>
</template>

<script setup>
</script>

<style>
.app-container {
  min-height: 100vh;
}

.transition-root {
  width: 100%;
  min-height: 100vh;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
