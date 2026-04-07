<template>
  <div class="app-shell">
    <button class="mobile-toggle" @click="menuOpen = !menuOpen">
      {{ menuOpen ? "Close menu" : "Open menu" }}
    </button>

    <SidebarNav :open="menuOpen" @navigate="closeMenu" />

    <div class="content">
      <NuxtPage />
    </div>
  </div>
</template>

<script setup>
import SidebarNav from "~/components/SidebarNav.vue"

const menuOpen = ref(false)
const closeMenu = () => {
  menuOpen.value = false
}

useHead({
  link: [
    {
      rel: "stylesheet",
      href: "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL,GRAD@400,0,0&display=swap",
    },
  ],
})
</script>

<style>
:global(body) {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  background:
    radial-gradient(circle at top, rgba(125, 211, 252, 0.18), transparent 30%),
    linear-gradient(180deg, #020617 0%, #0b1020 100%);
  color: #e2e8f0;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  padding: 24px;
  border-right: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(2, 6, 23, 0.88);
  backdrop-filter: blur(18px);
}

.brand {
  padding: 16px 14px 24px;
}

.brand p {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.35em;
  text-transform: uppercase;
  color: #7dd3fc;
}

.brand strong {
  font-size: 1.4rem;
}

.menu {
  display: grid;
  gap: 10px;
}

.menu-link {
  padding: 14px 16px;
  border-radius: 16px;
  text-decoration: none;
  color: #e2e8f0;
  border: 1px solid rgba(51, 65, 85, 1);
  background: rgba(15, 23, 42, 0.8);
  font-weight: 700;
}

.menu-link.router-link-active {
  background: #7dd3fc;
  color: #08111f;
  border-color: #7dd3fc;
}

.content {
  min-width: 0;
}

.mobile-toggle {
  display: none;
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 50;
  border: 0;
  border-radius: 999px;
  background: #7dd3fc;
  color: #08111f;
  font-weight: 700;
  padding: 12px 14px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

@media (max-width: 1024px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    width: 280px;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
    z-index: 40;
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .mobile-toggle {
    display: inline-flex;
  }

  .content {
    padding-top: 56px;
  }
}
</style>
