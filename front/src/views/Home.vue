<template>
  <div class="home-page">
    <section class="intro-hero">
      <div class="intro-crest">
        <span class="crest-glyph">❦</span>
        <span class="crest-label">EMPIRICAL JYOTISH ARCHIVE</span>
      </div>

      <h1 class="intro-title">
        The Jyotish Case Register
      </h1>

      <div class="divider-filigree">
        <span class="filigree-dot">◆</span>
      </div>

      <p class="intro-lead">
        A public, scholarly library of real-life astrology case studies created for students 
        to practice chart analysis on authentic human destinies.
      </p>

      <div class="intro-actions">
        <router-link to="/cases" class="btn-primary btn-large">
          Browse Charts Library →
        </router-link>

        <button v-if="!isAuthenticated" class="btn-outline btn-large" @click="openLoginModal">
          Sign in with Google
        </button>

        <router-link v-else-if="!isAdmin" to="/userhome" class="btn-outline btn-large">
          My Submitted Charts →
        </router-link>

        <router-link v-else to="/adminhome" class="btn-outline btn-large">
          Admin Dashboard →
        </router-link>
      </div>
    </section>

    <!-- Clean Pillars / Overview -->
    <section class="intro-pillars">
      <div class="pillar-box">
        <span class="pillar-roman">I</span>
        <h3 class="pillar-head">Documented Birth Timings</h3>
        <p class="pillar-text">
          Cases are cataloged with verified hospital records and municipal certificates. 
          No speculative approximations or unverified recollections.
        </p>
      </div>

      <div class="pillar-box">
        <span class="pillar-roman">II</span>
        <h3 class="pillar-head">Unvarnished Life Stories</h3>
        <p class="pillar-text">
          Study genuine biographical timelines — career pivots, marital timing, relocations, 
          and fortunes — mapped directly against planetary periods.
        </p>
      </div>

      <div class="pillar-box">
        <span class="pillar-roman">III</span>
        <h3 class="pillar-head">Student Research</h3>
        <p class="pillar-text">
          Explore cases without requiring complex calculation software. Filter by categories 
          and learn astrology through the direct witness of real lives.
        </p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useAuth } from '../composables/useAuth'

const { isAuthenticated, isAdmin, openLoginModal } = useAuth()
</script>

<style scoped>
.home-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 60px 24px 80px;
}

.intro-hero {
  text-align: center;
  padding: 40px 0 60px;
}

.intro-crest {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
}

.crest-glyph {
  color: #c89b3c;
  font-size: 16px;
}

.crest-label {
  font-family: var(--font-serif);
  font-size: 11px;
  letter-spacing: 0.18em;
  font-weight: 700;
  color: #7e2222;
}

.intro-title {
  font-size: 42px;
  font-weight: 700;
  line-height: 1.2;
  color: var(--text-main);
  margin-bottom: 18px;
}

.divider-filigree {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 180px;
  margin: 0 auto 24px;
  border-bottom: 1px solid #c89b3c;
  position: relative;
}

.filigree-dot {
  position: absolute;
  background: var(--bg-page);
  padding: 0 8px;
  color: #c89b3c;
  font-size: 10px;
}

.intro-lead {
  font-family: var(--font-reading);
  font-size: 20px;
  color: var(--text-muted);
  max-width: 680px;
  margin: 0 auto 36px;
  line-height: 1.7;
}

.intro-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.btn-large {
  padding: 12px 28px;
  font-size: 13px;
}

/* Pillars */
.intro-pillars {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  border-top: 1px solid #e7e0d5;
  padding-top: 48px;
}

.pillar-box {
  text-align: center;
  padding: 0 12px;
}

.pillar-roman {
  display: block;
  font-family: var(--font-serif);
  font-size: 22px;
  color: #c89b3c;
  font-weight: 700;
  margin-bottom: 10px;
}

.pillar-head {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text-main);
}

.pillar-text {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.6;
}

@media (max-width: 768px) {
  .intro-title { font-size: 32px; }
  .intro-lead { font-size: 17px; }
  .intro-pillars { grid-template-columns: 1fr; gap: 24px; }
}
</style>
