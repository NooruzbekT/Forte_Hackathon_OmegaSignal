<script setup>
import ChatContainer from '@/components/chat/ChatContainer.vue'
import AppSidebar from '@/components/common/AppSidebar.vue'
</script>

<template>
  <div id="app">
    <AppSidebar />
    <ChatContainer />
  </div>
</template>

<style scoped>
#app {
  display: flex;
  height: 100vh;
  overflow: hidden;
  width: 100%;
}

#app > * {
  flex-shrink: 0;
}

#app > *:last-child {
  flex: 1;
  min-width: 0;
}
</style>