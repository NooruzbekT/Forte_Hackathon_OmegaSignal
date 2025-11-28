<script setup>
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="app-footer">
    <div class="footer-content">
      <p class="footer-text">
        © {{ currentYear }} Fortebank. AI Business Analyst.
      </p>
      <div class="footer-links">
        <a href="#" class="footer-link">Документация</a>
        <a href="#" class="footer-link">Поддержка</a>
        <a href="#" class="footer-link">О проекте</a>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: white;
  border-top: 1px solid var(--forte-border-light);
  padding: var(--forte-space-4) var(--forte-space-6);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1280px;
  margin: 0 auto;
}

.footer-text {
  font-size: var(--forte-text-sm);
  color: var(--forte-text-secondary);
  margin: 0;
}

.footer-links {
  display: flex;
  gap: var(--forte-space-4);
}

.footer-link {
  font-size: var(--forte-text-sm);
  color: var(--forte-text-secondary);
  text-decoration: none;
  transition: color var(--forte-transition-fast);
}

.footer-link:hover {
  color: var(--forte-primary);
}

@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    gap: var(--forte-space-3);
    text-align: center;
  }
}
</style>