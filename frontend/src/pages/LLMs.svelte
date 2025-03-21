<script lang="ts">
  import { onMount } from 'svelte';
  import { llmService } from '../services/api';
  import { llmProviders, isLoading, errorMessage } from '../stores';
  import type { LLMProvider } from '../types';

  // Initialize LLM providers
  onMount(async () => {
    try {
      $isLoading = true;
      const providers = await llmService.getAll();
      llmProviders.set(providers);
    } catch (error) {
      console.error('Error loading LLM providers:', error);
      errorMessage.set('Failed to load LLM providers');
    } finally {
      $isLoading = false;
    }
  });
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <section>
    <h1 class="text-3xl font-bold text-gray-900 mb-2">LLM Providers</h1>
    <p class="text-xl text-gray-600 mb-6">Select an LLM provider for generating synthetic data</p>

    {#if $isLoading}
      <div class="text-center my-6">
        <svg class="inline-block animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-2 text-gray-600">Loading LLM providers...</p>
      </div>
    {:else}
      {#if Object.keys($llmProviders).length === 0}
        <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-yellow-700">
                No LLM providers available. Please check if the backend is running properly.
              </p>
            </div>
          </div>
        </div>
      {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {#each Object.entries($llmProviders) as [id, provider]}
            <div class="bg-white rounded-lg shadow-md overflow-hidden">
              <div class="px-4 py-3 border-b border-gray-200">
                <h3 class="text-lg font-semibold text-gray-800">
                  {provider.name}
                </h3>
              </div>
              <div class="px-4 py-4">
                <div>
                  {#if provider.description}
                    <p class="text-gray-600">{provider.description}</p>
                  {:else}
                    <p class="text-gray-500">Provider ID: {id}</p>
                  {/if}
                  
                  {#if provider.supported_models && provider.supported_models.length > 0}
                    <div class="mt-3">
                      <p class="text-sm font-medium text-gray-700">Supported Models:</p>
                      <div class="flex flex-wrap gap-1 mt-1">
                        {#each provider.supported_models as model}
                          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {model}
                          </span>
                        {/each}
                      </div>
                    </div>
                  {/if}
                </div>
              </div>
              <div class="px-4 py-3 bg-gray-50 border-t border-gray-200">
                <a href="/workflow" class="flex items-center justify-center text-blue-600 hover:text-blue-800" aria-label="Use this LLM provider">
                  <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span>Use This Provider</span>
                </a>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    {/if}
    
    {#if $errorMessage}
      <div class="bg-red-50 border-l-4 border-red-400 p-4 mt-6">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3 flex justify-between items-center w-full">
            <p class="text-sm text-red-700">
              {$errorMessage}
            </p>
            <button 
              class="inline-flex text-red-500 hover:text-red-800" 
              on:click={() => errorMessage.set(null)}
              aria-label="Dismiss error"
            >
              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    {/if}
  </section>
</div> 