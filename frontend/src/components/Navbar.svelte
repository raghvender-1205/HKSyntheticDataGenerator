<script lang="ts">
  import { Link } from "svelte-routing";
  let isOpen = false;
  
  function toggleMenu() {
    isOpen = !isOpen;
  }
</script>

<nav class="bg-blue-600 text-white shadow-md">
  <div class="max-w-7xl mx-auto px-4">
    <div class="flex justify-between h-16">
      <div class="flex items-center">
        <Link to="/" class="flex-shrink-0 flex items-center font-bold text-xl">
          Synthetic Data Generator
        </Link>
      </div>
      
      <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
        <Link to="/" class="px-3 py-2 text-white hover:bg-blue-700 rounded-md">
          Home
        </Link>
        
        <Link to="/datasources" class="px-3 py-2 text-white hover:bg-blue-700 rounded-md">
          Data Sources
        </Link>
        
        <Link to="/llms" class="px-3 py-2 text-white hover:bg-blue-700 rounded-md">
          LLM Providers
        </Link>
        
        <Link to="/generators" class="px-3 py-2 text-white hover:bg-blue-700 rounded-md">
          Dataset Generators
        </Link>
        
        <Link to="/workflow" class="px-3 py-2 text-white hover:bg-blue-700 rounded-md">
          Generate Dataset
        </Link>
      </div>
      
      <div class="flex items-center sm:hidden">
        <button 
          class="inline-flex items-center justify-center p-2 rounded-md text-white hover:bg-blue-700 focus:outline-none"
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
    <div class="sm:hidden">
      <div class="px-2 pt-2 pb-3 space-y-1">
        <Link to="/" class="block px-3 py-2 text-white hover:bg-blue-700 rounded-md">
          Home
        </Link>
        
        <Link to="/datasources" class="block px-3 py-2 text-white hover:bg-blue-700 rounded-md">
          Data Sources
        </Link>
        
        <Link to="/llms" class="block px-3 py-2 text-white hover:bg-blue-700 rounded-md">
          LLM Providers
        </Link>
        
        <Link to="/generators" class="block px-3 py-2 text-white hover:bg-blue-700 rounded-md">
          Dataset Generators
        </Link>
        
        <Link to="/workflow" class="block px-3 py-2 text-white hover:bg-blue-700 rounded-md">
          Generate Dataset
        </Link>
      </div>
    </div>
  {/if}
</nav> 