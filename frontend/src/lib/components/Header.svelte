<script lang="ts">
  import { page } from '$app/stores';
</script>

<header class="bg-white shadow-sm border-b border-secondary-200">
  <div class="container mx-auto px-4 py-3">
    <div class="flex justify-between items-center">
      <div class="flex items-center space-x-2">
        <img src="/logo.svg" alt="Logo" class="h-8 w-8" />
        <span class="text-xl font-semibold text-primary-700">HK Synthetic Data</span>
      </div>

      <nav class="hidden md:flex items-center space-x-6">
        <a 
          href="/" 
          class="{$page.url.pathname === '/' ? 'text-primary-600 border-b-2 border-primary-600' : 'text-secondary-600 hover:text-primary-600'} font-medium transition-colors"
        >
          Home
        </a>
        <a 
          href="/generate" 
          class="{$page.url.pathname === '/generate' ? 'text-primary-600 border-b-2 border-primary-600' : 'text-secondary-600 hover:text-primary-600'} font-medium transition-colors"
        >
          Generate
        </a>
        <a 
          href="/saved" 
          class="{$page.url.pathname === '/saved' ? 'text-primary-600 border-b-2 border-primary-600' : 'text-secondary-600 hover:text-primary-600'} font-medium transition-colors"
        >
          Saved Configs
        </a>
        <a 
          href="/settings" 
          class="{$page.url.pathname === '/settings' ? 'text-primary-600 border-b-2 border-primary-600' : 'text-secondary-600 hover:text-primary-600'} font-medium transition-colors"
        >
          Settings
        </a>
      </nav>

      <button class="md:hidden flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-secondary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
    </div>
  </div>
</header> 