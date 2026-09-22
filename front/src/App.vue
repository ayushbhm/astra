<template>
  <div class="app-layout">
    <!-- Clean Shared Editorial Navbar -->
    <Navbar />

    <!-- Active Route View (Home, Cases, UserHome, AdminHome) -->
    <main class="app-main">
      <router-view />
    </main>

    <!-- Global Google Sign-In Modal -->
    <GoogleLoginModal />

    <!-- Clean Editorial Footer -->
    <footer class="editorial-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <span class="footer-title">THE JYOTISH REGISTER</span>
          <span class="footer-tag">Open Academic Astrology Case Library</span>
        </div>
        <div class="footer-meta">
          <span>Real Lives · Verified Birth Timestamps · Peer Reviewed</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import GoogleLoginModal from './components/GoogleLoginModal.vue'
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-page);
}

.app-main {
  flex: 1;
}

.editorial-footer {
  background: #ffffff;
  border-top: 1px solid #e7e0d5;
  padding: 24px;
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.footer-brand {
  display: flex;
  flex-direction: column;
}

.footer-title {
  font-family: var(--font-serif);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #241f1a;
}

.footer-tag {
  font-size: 11px;
  color: #78716c;
}

.footer-meta {
  font-size: 12px;
  color: #a8a29e;
  font-style: italic;
}
</style>
