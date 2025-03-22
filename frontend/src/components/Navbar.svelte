<script lang="ts">
  import { Link } from "svelte-routing";
  import ThemeToggle from "./ThemeToggle.svelte";
  
  let isOpen = false;
  
  function toggleMenu() {
    isOpen = !isOpen;
  }
  
  // Define active class for navigation links
  function getActiveClass(path: string): string {
    const currentPath = window.location.pathname;
    const isActive = currentPath === path || (path !== '/' && currentPath.startsWith(path));
    return isActive ? 'border-accent-400 text-white dark:text-white' : 'border-transparent text-gray-100 hover:text-white dark:text-gray-300 dark:hover:text-white';
  }
</script>

<nav class="bg-primary-700 dark:bg-dark-100 text-white shadow-lg dark:shadow-dark transition-colors duration-200">
  <div class="max-w-7xl mx-auto px-4">
    <div class="flex justify-between h-16">
      <div class="flex items-center">
        <Link to="/" class="flex-shrink-0 flex items-center font-bold text-xl text-white dark:text-white">
          <svg class="h-8 w-8 mr-2" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9.25 7C9.25 8.24264 8.24264 9.25 7 9.25C5.75736 9.25 4.75 8.24264 4.75 7C4.75 5.75736 5.75736 4.75 7 4.75C8.24264 4.75 9.25 5.75736 9.25 7Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>
            <path d="M6.75 9.5V14.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>
            <path d="M10.75 12.25H15.25C16.3546 12.25 17.25 11.3546 17.25 10.25V10.25C17.25 9.14543 16.3546 8.25 15.25 8.25H12.75L16.25 4.75" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>
            <path d="M19.25 17C19.25 18.2426 18.2426 19.25 17 19.25C15.7574 19.25 14.75 18.2426 14.75 17C14.75 15.7574 15.7574 14.75 17 14.75C18.2426 14.75 19.25 15.7574 19.25 17Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path>
          </svg>
          <span class="hidden md:inline">Synthetic Data Generator</span>
          <span class="md:hidden">SDG</span>
        </Link>
      </div>
      
      <div class="hidden sm:ml-6 sm:flex sm:items-center">
        <div class="flex space-x-1">
          <Link to="/" class="px-3 py-2 text-sm font-medium border-b-2 transition-colors duration-200 {getActiveClass('/')}">
            Home
          </Link>
          
          <Link to="/datasources" class="px-3 py-2 text-sm font-medium border-b-2 transition-colors duration-200 {getActiveClass('/datasources')}">
            Data Sources
          </Link>
          
          <Link to="/llms" class="px-3 py-2 text-sm font-medium border-b-2 transition-colors duration-200 {getActiveClass('/llms')}">
            LLM Providers
          </Link>
          
          <Link to="/generators" class="px-3 py-2 text-sm font-medium border-b-2 transition-colors duration-200 {getActiveClass('/generators')}">
            Generators
          </Link>
          
          <Link to="/workflow" class="px-3 py-2 text-sm font-medium border-b-2 transition-colors duration-200 {getActiveClass('/workflow')}">
            Generate Dataset
          </Link>
        </div>
        
        <div class="ml-4">
          <ThemeToggle />
        </div>
      </div>
      
      <div class="flex items-center sm:hidden">
        <ThemeToggle />
        
        <button 
          class="ml-2 inline-flex items-center justify-center p-2 rounded-md text-gray-100 hover:text-white hover:bg-primary-600 dark:hover:bg-dark-200 focus:outline-none transition-colors duration-200"
          aria-label="Toggle menu"
          on:click={toggleMenu}
        >
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            {#if isOpen}
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            {:else}
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>
            {/if}
          </svg>
        </button>
      </div>
    </div>
  </div>
  
  {#if isOpen}
    <div class="sm:hidden bg-primary-800 dark:bg-dark-200 transition-colors duration-200">
      <div class="px-2 pt-2 pb-3 space-y-1">
        <Link to="/" class="block px-3 py-2 text-gray-100 hover:text-white hover:bg-primary-600 dark:hover:bg-dark-100 rounded-md transition-colors duration-200">
          Home
        </Link>
        
        <Link to="/datasources" class="block px-3 py-2 text-gray-100 hover:text-white hover:bg-primary-600 dark:hover:bg-dark-100 rounded-md transition-colors duration-200">
          Data Sources
        </Link>
        
        <Link to="/llms" class="block px-3 py-2 text-gray-100 hover:text-white hover:bg-primary-600 dark:hover:bg-dark-100 rounded-md transition-colors duration-200">
          LLM Providers
        </Link>
        
        <Link to="/generators" class="block px-3 py-2 text-gray-100 hover:text-white hover:bg-primary-600 dark:hover:bg-dark-100 rounded-md transition-colors duration-200">
          Dataset Generators
        </Link>
        
        <Link to="/workflow" class="block px-3 py-2 text-gray-100 hover:text-white hover:bg-primary-600 dark:hover:bg-dark-100 rounded-md transition-colors duration-200">
          Generate Dataset
        </Link>
      </div>
    </div>
  {/if}
</nav>