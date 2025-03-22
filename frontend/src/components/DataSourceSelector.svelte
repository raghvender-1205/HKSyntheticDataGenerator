<script lang="ts">
  import { onMount } from 'svelte';
  import { datasourceService } from '../services/api';
  import { dataSources, activeDataSource, dataSourceConfig, documents, isLoading, errorMessage, workflowStep } from '../stores';
  import type { DataSource, DataSourceConfig } from '../types';

  // Define schema property interface
  interface SchemaProperty {
    type: string;
    title?: string;
    description?: string;
    default?: any;
    minimum?: number;
    maximum?: number;
    enum?: string[];
    hidden?: boolean;
  }

  let selectedDataSourceId: string = '';
  let selectedDataSource: DataSource | null = null;
  let config: any = {};
  
  // Add a state to track the current selection step
  let selectionStep: 'type_selection' | 'configuration' = 'type_selection';

  // Initialize data sources
  onMount(async () => {
    try {
      $isLoading = true;
      const sources = await datasourceService.getAll();
      dataSources.set(sources);
    } catch (error) {
      console.error('Error loading data sources:', error);
      errorMessage.set('Failed to load data sources');
    } finally {
      $isLoading = false;
    }
  });

  // Update selected data source when ID changes
  $: {
    if (selectedDataSourceId && $dataSources[selectedDataSourceId]) {
      selectedDataSource = $dataSources[selectedDataSourceId];
      // Initialize config with default values from schema
      config = {};
      const properties = selectedDataSource.config_schema.properties;
      for (const key in properties) {
        if (properties[key].default !== undefined) {
          config[key] = properties[key].default;
        }
      }
      // Always set the source_id
      config.source_id = selectedDataSourceId;
    } else {
      selectedDataSource = null;
      config = {};
    }
  }
  
  // Function to proceed to configuration step
  function proceedToConfiguration() {
    if (selectedDataSourceId && selectedDataSource) {
      selectionStep = 'configuration';
    }
  }
  
  // Function to go back to type selection
  function backToTypeSelection() {
    selectionStep = 'type_selection';
    selectedDataSourceId = '';
    selectedDataSource = null;
    config = {};
  }

  async function createDataSource() {
    if (!selectedDataSourceId || !selectedDataSource) return;
    
    try {
      $isLoading = true;
      $errorMessage = null;
      
      // Create data source instance
      const result = await datasourceService.create(config as DataSourceConfig);
      
      // Load documents
      const docs = await datasourceService.loadDocuments(result.datasource_id);
      
      // Update stores
      activeDataSource.set(result.datasource_id);
      dataSourceConfig.set(config as DataSourceConfig);
      documents.set(docs);
      
      // Move to the next step in the workflow
      workflowStep.set(2);
      
      return true;
    } catch (error) {
      console.error('Error creating data source:', error);
      errorMessage.set('Failed to create data source');
      return false;
    } finally {
      $isLoading = false;
    }
  }
</script>

<div class="card p-6">
  <h2 class="text-2xl font-semibold mb-4 text-gray-900 dark:text-white">Select Data Source</h2>
  
  {#if $isLoading}
    <div class="text-center py-6">
      <svg class="animate-spin h-8 w-8 text-primary-600 dark:text-primary-400 mx-auto mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="text-gray-600 dark:text-gray-300">Loading data sources...</p>
    </div>
  {:else}
    {#if Object.keys($dataSources).length === 0}
      <div class="bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 p-4 mb-4 rounded">
        <p class="text-yellow-700 dark:text-yellow-300">No data sources available. Please check if the backend is running properly.</p>
      </div>
    {:else}
      <!-- Step 1: Select Data Source Type -->
      {#if selectionStep === 'type_selection'}
        <div class="fade-in">
          <p class="text-gray-600 dark:text-gray-300 mb-4">First, select the type of data source you want to use:</p>
          
          <div class="mb-6">
            <label for="data-source-type" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Data Source Type</label>
            <select 
              id="data-source-type"
              bind:value={selectedDataSourceId} 
              class="select"
            >
              <option value="">Select a data source type</option>
              {#each Object.entries($dataSources) as [id, source]}
                <option value={id}>{source.name}</option>
              {/each}
            </select>
          </div>
          
          {#if selectedDataSourceId}
            <div class="mt-6">
              <button 
                class="btn-primary" 
                on:click={proceedToConfiguration}
              >
                Continue to Configuration
              </button>
            </div>
          {/if}
        </div>
      
      <!-- Step 2: Configure Selected Data Source -->
      {:else if selectionStep === 'configuration'}
        <div class="fade-in">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">Configure {selectedDataSource?.name}</h3>
            <button 
              class="text-sm text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300 transition-colors duration-200" 
              on:click={backToTypeSelection}
            >
              ← Change Data Source Type
            </button>
          </div>
          
          {#each Object.entries(selectedDataSource.config_schema.properties) as [key, prop]}
            {#if key !== 'source_id' && !prop.hidden}
              <div class="mb-5">
                <label for={key} class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{prop.title || key}</label>
                <div>
                  {#if prop.type === 'string'}
                    {#if prop.enum}
                      <select 
                        id={key}
                        bind:value={config[key]} 
                        class="select"
                      >
                        {#each prop.enum as option}
                          <option value={option}>{option}</option>
                        {/each}
                      </select>
                    {:else}
                      <input 
                        id={key}
                        type="text" 
                        bind:value={config[key]} 
                        placeholder={prop.description}
                        class="input"
                      >
                    {/if}
                  {:else if prop.type === 'number' || prop.type === 'integer'}
                    <input 
                      id={key}
                      type="number" 
                      bind:value={config[key]} 
                      min={prop.minimum} 
                      max={prop.maximum} 
                      step={prop.type === 'integer' ? 1 : 0.1}
                      placeholder={prop.description}
                      class="input"
                    >
                  {:else if prop.type === 'boolean'}
                    <div class="flex items-center">
                      <input 
                        id={key}
                        type="checkbox" 
                        bind:checked={config[key]}
                        class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 dark:border-gray-600 dark:bg-dark-200 rounded transition-colors duration-200"
                      >
                      <label for={key} class="ml-2 text-sm text-gray-700 dark:text-gray-300">{prop.description}</label>
                    </div>
                  {/if}
                </div>
                {#if prop.description && prop.type !== 'boolean'}
                  <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{prop.description}</p>
                {/if}
              </div>
            {/if}
          {/each}
          
          <div class="mt-6">
            <button 
              class="btn-primary flex items-center" 
              on:click={createDataSource} 
              disabled={$isLoading}
            >
              {#if $isLoading}
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white dark:text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Loading...
              {:else}
                Create & Load
              {/if}
            </button>
          </div>
        </div>
      {/if}
    {/if}
  {/if}
  
  {#if $errorMessage}
    <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-400 p-4 mt-6 rounded">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400 dark:text-red-300" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700 dark:text-red-300">{$errorMessage}</p>
        </div>
        <div class="ml-auto pl-3">
          <div class="-mx-1.5 -my-1.5">
            <button 
              class="inline-flex bg-red-50 dark:bg-red-800/30 rounded-md p-1.5 text-red-500 dark:text-red-300 hover:bg-red-100 dark:hover:bg-red-800/50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200"
              on:click={() => errorMessage.set(null)}
            >
              <span class="sr-only">Dismiss</span>
              <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div> 