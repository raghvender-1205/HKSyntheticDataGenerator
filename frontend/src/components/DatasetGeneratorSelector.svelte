<script lang="ts">
  import { onMount } from 'svelte';
  import { datasetService } from '../services/api';
  import { 
    datasetGenerators, 
    activeGenerator, 
    generatorConfig,
    activeDataSource,
    activeLlm,
    isLoading, 
    errorMessage,
    workflowStep
  } from '../stores';
  import type { DatasetGenerator, DatasetGeneratorConfig } from '../types';

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

  let selectedGeneratorId: string = '';
  let selectedGenerator: DatasetGenerator | null = null;
  let config: any = {};

  // Initialize dataset generators
  onMount(async () => {
    try {
      $isLoading = true;
      const generators = await datasetService.getAll();
      datasetGenerators.set(generators);
    } catch (error) {
      console.error('Error loading dataset generators:', error);
      errorMessage.set('Failed to load dataset generators');
    } finally {
      $isLoading = false;
    }
  });

  // Update selected generator when ID changes
  $: {
    if (selectedGeneratorId && $datasetGenerators[selectedGeneratorId]) {
      selectedGenerator = $datasetGenerators[selectedGeneratorId];
      // Initialize config with default values from schema
      config = {};
      const properties = selectedGenerator.config_schema.properties;
      for (const key in properties) {
        if (properties[key].default !== undefined) {
          config[key] = properties[key].default;
        }
      }
      // Always set the generator_id
      config.generator_id = selectedGeneratorId;
    } else {
      selectedGenerator = null;
      config = {};
    }
  }

  // Check if we have the required prerequisites
  $: canProceed = $activeDataSource && $activeLlm;

  async function createGenerator() {
    if (!selectedGeneratorId || !selectedGenerator) return;
    if (!$activeDataSource || !$activeLlm) {
      errorMessage.set('Please select data source and LLM provider first');
      return false;
    }
    
    try {
      $isLoading = true;
      $errorMessage = null;
      
      // Add data source and llm IDs to the config
      config.data_source_id = $activeDataSource;
      config.llm_id = $activeLlm;
      
      // Create generator instance
      const result = await datasetService.create(config as DatasetGeneratorConfig);
      
      // Update stores
      activeGenerator.set(result.generator_id);
      generatorConfig.set(config as DatasetGeneratorConfig);
      
      // Move to the next step in the workflow
      workflowStep.set(4);
      
      return true;
    } catch (error) {
      console.error('Error creating dataset generator:', error);
      errorMessage.set('Failed to create dataset generator');
      return false;
    } finally {
      $isLoading = false;
    }
  }
</script>

<div class="bg-white shadow-md rounded-lg p-6">
  <h2 class="text-2xl font-semibold mb-4">Select Dataset Generator</h2>
  
  {#if !canProceed}
    <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
      <p class="text-yellow-700">Please complete the previous steps (Data Source and LLM Provider) before configuring a dataset generator.</p>
    </div>
  {:else}
    {#if $isLoading}
      <div class="text-center py-6">
        <svg class="animate-spin h-8 w-8 text-blue-600 mx-auto mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-gray-600">Loading dataset generators...</p>
      </div>
    {:else}
      {#if Object.keys($datasetGenerators).length === 0}
        <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
          <p class="text-yellow-700">No dataset generators available. Please check if the backend is running properly.</p>
        </div>
      {:else}
        <div class="mb-4">
          <label for="generator-type" class="block text-sm font-medium text-gray-700 mb-1">Dataset Generator Type</label>
          <select 
            id="generator-type"
            bind:value={selectedGeneratorId} 
            class="block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="">Select a dataset generator</option>
            {#each Object.entries($datasetGenerators) as [id, generator]}
              <option value={id}>{generator.name}</option>
            {/each}
          </select>
        </div>

        {#if selectedGenerator}
          <div class="mt-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Configure Dataset Generator</h3>
            
            {#each Object.entries(selectedGenerator.config_schema.properties) as [key, prop]}
              {#if key !== 'generator_id' && key !== 'data_source_id' && key !== 'llm_id' && !prop.hidden}
                <div class="mb-4">
                  <label for={key} class="block text-sm font-medium text-gray-700 mb-1">{prop.title || key}</label>
                  <div>
                    {#if prop.type === 'string'}
                      {#if prop.enum}
                        <select 
                          id={key}
                          bind:value={config[key]} 
                          class="block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
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
                          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
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
                        class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      >
                    {:else if prop.type === 'boolean'}
                      <div class="flex items-center">
                        <input 
                          id={key}
                          type="checkbox" 
                          bind:checked={config[key]}
                          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        >
                        <label for={key} class="ml-2 text-sm text-gray-700">{prop.description}</label>
                      </div>
                    {/if}
                  </div>
                  {#if prop.description && prop.type !== 'boolean'}
                    <p class="mt-1 text-sm text-gray-500">{prop.description}</p>
                  {/if}
                </div>
              {/if}
            {/each}
            
            <div class="mt-6">
              <button 
                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center" 
                on:click={createGenerator} 
                disabled={$isLoading}
              >
                {#if $isLoading}
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Loading...
                {:else}
                  Create
                {/if}
              </button>
            </div>
          </div>
        {/if}
      {/if}
    {/if}
  {/if}
  
  {#if $errorMessage}
    <div class="bg-red-50 border-l-4 border-red-400 p-4 mt-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{$errorMessage}</p>
        </div>
        <div class="ml-auto pl-3">
          <div class="-mx-1.5 -my-1.5">
            <button 
              class="inline-flex bg-red-50 rounded-md p-1.5 text-red-500 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
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