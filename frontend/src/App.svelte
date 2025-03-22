<script lang="ts">
  import { Router, Route } from "svelte-routing";
  import Navbar from "./components/Navbar.svelte";
  import { onMount } from 'svelte';
  
  // Pages
  import Home from "./pages/Home.svelte";
  import DataSources from "./pages/DataSources.svelte";
  import LLMs from "./pages/LLMs.svelte";
  import Generators from "./pages/Generators.svelte";
  import Workflow from "./pages/Workflow.svelte";
  
  // Get the base URL from the environment
  const baseUrl = import.meta.env.BASE_URL || "";
  
  // Initialize theme on mount
  onMount(() => {
    // Check if user has previously set a theme preference
    const savedTheme = localStorage.getItem('theme');
    
    // If user has a saved preference, use that
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else if (savedTheme === 'light') {
      document.documentElement.classList.remove('dark');
    } else {
      // Otherwise, check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (prefersDark) {
        document.documentElement.classList.add('dark');
      }
    }
  });
</script>

<Router url="{baseUrl}">
  <div class="flex flex-col min-h-screen bg-gray-50 dark:bg-dark-200 transition-colors duration-200">
    <Navbar />
    
    <main class="flex-grow">
      <Route path="/" component={Home} />
      <Route path="/datasources" component={DataSources} />
      <Route path="/llms" component={LLMs} />
      <Route path="/generators" component={Generators} />
      <Route path="/workflow" component={Workflow} />
    </main>
    
    <footer class="bg-white dark:bg-dark-100 shadow-inner dark:shadow-dark py-6 mt-8 transition-colors duration-200">
      <div class="max-w-7xl mx-auto px-4 text-center text-gray-600 dark:text-gray-300">
        <p>
          <span class="font-bold">Synthetic Data Generator v0.1</span> - A tool for generating synthetic data for LLM training and fine-tuning.
        </p>
      </div>
    </footer>
  </div>
</Router>
