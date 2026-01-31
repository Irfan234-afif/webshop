<template>
  <div class="splash-screen">
    <div class="splash-content">
      <div class="spinner"></div>
      <h2 class="loading-text">Loading Webshop...</h2>
    </div>
  </div>
</template>

<style scoped>
.splash-screen {
  width: 100vw;
  height: 100%;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #ffffff; /* Or your app's background color */
  z-index: 9999;
}

.splash-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: #3b82f6; /* Primary color */
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  font-size: 1.25rem;
  color: #374151;
  font-weight: 500;
  animation: pulse 2s infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
</style>
