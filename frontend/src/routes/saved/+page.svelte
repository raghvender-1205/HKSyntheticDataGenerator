<script lang="ts">
  import { onMount } from 'svelte';
  
  let configurations: any[] = [];
  let loading = true;
  let error: any = null;
  let searchQuery = '';
  let sortBy = 'date'; // date, name
  let sortOrder = 'desc'; // asc, desc
  
  // Mock data for development
  const mockConfigurations = [
    {
      id: '1',
      name: 'Medical Knowledge Base QA',
      description: 'Q&A pairs generated from medical textbooks',
      data_format: 'qa',
      sample_count: 50,
      created_at: '2023-09-15T10:30:00Z'
    },
    {
      id: '2',
      name: 'Customer Support Training',
      description: 'Instruction-response pairs for customer service scenarios',
      data_format: 'instructionResponse',
      sample_count: 25,
      created_at: '2023-10-20T14:15:00Z'
    },
    {
      id: '3',
      name: 'Product Documentation',
      description: 'Q&A from technical product documentation',
      data_format: 'qa',
      sample_count: 30,
      created_at: '2023-11-05T09:45:00Z'
    }
  ];
  
  onMount(async () => {
    await fetchConfigurations();
  });
  
  async function fetchConfigurations() {
    loading = true;
    error = null;
    
    try {
      // Use the real API endpoint
      const response = await fetch('/api/v1/config/saved');
      
      if (!response.ok) {
        throw new Error('Failed to fetch configurations');
      }
      
      configurations = await response.json();
      
      // If no configurations are returned yet, use mock data for demonstration
      if (configurations.length === 0) {
        configurations = mockConfigurations;
      }
    } catch (err) {
      console.error('Error fetching configurations:', err);
      error = err.message || 'An unexpected error occurred';
      
      // Fall back to mock data if API is not available
      configurations = mockConfigurations;
    } finally {
      loading = false;
    }
  }
  
  async function deleteConfiguration(id) {
    if (!confirm('Are you sure you want to delete this configuration?')) {
      return;
    }
    
    try {
      // Use the real API endpoint
      const response = await fetch(`/api/v1/config/saved/${id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete configuration');
      }
      
      // Remove from the list
      configurations = configurations.filter(config => config.id !== id);
    } catch (err) {
      console.error('Error deleting configuration:', err);
      alert('Failed to delete configuration: ' + (err.message || 'Unknown error'));
      
      // If using mock data, still remove from the list
      if (mockConfigurations.find(config => config.id === id)) {
        configurations = configurations.filter(config => config.id !== id);
      }
    }
  }
  
  function loadConfiguration(id) {
    window.location.href = `/generate?config=${id}`;
  }
  
  // Filter configurations based on search query
  $: filteredConfigurations = configurations.filter(config => 
    config.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (config.description && config.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );
  
  // Sort configurations
  $: sortedConfigurations = [...filteredConfigurations].sort((a, b) => {
    if (sortBy === 'date') {
      const dateA = new Date(a.created_at);
      const dateB = new Date(b.created_at);
      return sortOrder === 'asc' ? dateA - dateB : dateB - dateA;
    } else if (sortBy === 'name') {
      return sortOrder === 'asc' 
        ? a.name.localeCompare(b.name)
        : b.name.localeCompare(a.name);
    }
    return 0;
  });
  
  // Format date
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

<svelte:head>
  <title>Saved Configurations | HealthKart</title>
  <meta name="description" content="View and manage your saved synthetic data generation configurations" />
</svelte:head>

<div class="container mx-auto py-8 px-4">
  <div class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold text-primary-700">Saved Configurations</h1>
    <a href="/generate" class="btn btn-primary">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
      </svg>
      New Configuration
    </a>
  </div>
  
  <!-- Search and sort controls -->
  <div class="bg-white p-4 rounded-lg shadow mb-6 flex flex-col md:flex-row justify-between">
    <div class="relative mb-4 md:mb-0 md:w-1/2">
      <input
        type="text"
        bind:value={searchQuery}
        placeholder="Search configurations..."
        class="input pl-10 w-full"
      />
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </div>
    
    <div class="flex items-center space-x-4">
      <div class="flex items-center">
        <label for="sortBy" class="mr-2 text-secondary-700">Sort by:</label>
        <select id="sortBy" bind:value={sortBy} class="input">
          <option value="date">Date</option>
          <option value="name">Name</option>
        </select>
      </div>
      
      <button 
        on:click={() => sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'}
        class="p-2 rounded hover:bg-secondary-100"
        aria-label={sortOrder === 'asc' ? 'Sort descending' : 'Sort ascending'}
      >
        {#if sortOrder === 'asc'}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-secondary-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
          </svg>
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-secondary-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
          </svg>
        {/if}
      </button>
    </div>
  </div>
  
  {#if loading}
    <div class="flex justify-center py-12">
      <svg class="animate-spin h-8 w-8 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
  {:else if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
      <p><strong>Error:</strong> {error}</p>
      <button class="mt-2 text-red-700 underline" on:click={fetchConfigurations}>Try again</button>
    </div>
  {:else if sortedConfigurations.length === 0}
    <div class="bg-secondary-50 border border-secondary-200 rounded-lg p-8 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-secondary-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
      </svg>
      <h2 class="text-xl font-semibold text-secondary-700 mb-2">No configurations found</h2>
      <p class="text-secondary-600 mb-4">
        {searchQuery ? 'No configurations match your search query.' : 'You haven\'t created any configurations yet.'}
      </p>
      <a href="/generate" class="btn btn-primary">Create Your First Configuration</a>
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each sortedConfigurations as config}
        <div class="bg-white rounded-lg shadow-md border border-secondary-200 overflow-hidden hover:shadow-lg transition-shadow duration-200">
          <div class="p-6">
            <div class="flex justify-between items-start mb-2">
              <h2 class="text-xl font-semibold text-secondary-800 truncate">{config.name}</h2>
              <div class="flex">
                <button 
                  on:click={() => loadConfiguration(config.id)}
                  class="p-1.5 text-primary-700 hover:text-primary-900 hover:bg-primary-50 rounded mr-1" 
                  title="Load configuration"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
                <button 
                  on:click={() => deleteConfiguration(config.id)}
                  class="p-1.5 text-red-600 hover:text-red-800 hover:bg-red-50 rounded" 
                  title="Delete configuration"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
            
            {#if config.description}
              <p class="text-secondary-600 mb-4 text-sm line-clamp-2">{config.description}</p>
            {/if}
            
            <div class="mt-4 pt-4 border-t border-secondary-100">
              <div class="flex justify-between items-center text-sm text-secondary-500">
                <div>
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                    {config.data_format === 'qa' ? 'Q&A' : config.data_format === 'instructionResponse' ? 'Instruction' : 'Conversation'}
                  </span>
                  <span class="ml-2">{config.sample_count} samples</span>
                </div>
                <div title={formatDate(config.created_at)}>
                  {formatDate(config.created_at)}
                </div>
              </div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div> 