<script>
  import '../app.css';
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
</script>

<div class="min-h-screen flex flex-col bg-secondary-50">
  <Header />
  <main class="flex-1 container mx-auto py-6 px-4">
    <slot />
  </main>
  <Footer />
</div> 