<script lang="ts">
  import { onMount } from 'svelte';
  import { datasourceService } from '../services/api';
  import { dataSources, isLoading, errorMessage, activeDataSource, documents, dataSourceConfig } from '../stores';
  import type { DataSource, DataSourceConfig } from '../types';
  import DocumentViewer from '../components/DocumentViewer.svelte';
  import FileBrowser from '../components/FileBrowser.svelte';
  import FileUploader from '../components/FileUploader.svelte';

  // Helper function to get icon for datasource type
  function getDatasourceTypeIcon(sourceType: string): string {
    switch (sourceType.toLowerCase()) {
      case 'file':
        return 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z';
      case 'pdf':
        return 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z M10 10.5a0.5 0.5 0 01-0.5 0.5H9v1h1a1 1 0 110 2H8.5a0.5 0.5 0 01-0.5-0.5v-3a0.5 0.5 0 01.5-.5h1a0.5 0.5 0 01.5.5z M13 11.5a1.5 1.5 0 01-1.5 1.5h-.5v1h.5a0.5 0.5 0 010 1h-1a0.5 0.5 0 01-.5-.5v-3a0.5 0.5 0 01.5-.5h1a1.5 1.5 0 011.5 1.5z M15.5 14a0.5 0.5 0 00.5-.5v-3a0.5 0.5 0 00-1 0v3a0.5 0.5 0 00.5.5z';
      case 'sql':
        return 'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4';
      case 'web':
        return 'M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9';
      default:
        return 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10';
    }
  }

  // Helper function to get color for datasource type
  function getDatasourceTypeColor(sourceType: string): string {
    switch (sourceType.toLowerCase()) {
      case 'file':
        return 'bg-blue-500';
      case 'pdf': 
        return 'bg-red-500';
      case 'sql':
        return 'bg-green-500';
      case 'web':
        return 'bg-purple-500';
      default:
        return 'bg-gray-500';
    }
  }

  // Helper function to get description for datasource type
  function getDatasourceTypeDescription(sourceType: string): string {
    switch (sourceType.toLowerCase()) {
      case 'file':
        return 'Load data from text, JSON, or CSV files';
      case 'pdf':
        return 'Extract text from PDF documents';
      case 'sql':
        return 'Connect to SQL databases and run queries';
      case 'web':
        return 'Crawl websites and extract content';
      default:
        return 'Generic data source';
    }
  }

  // State for adding new datasource
  let showAddForm = false;
  let selectedDataSourceId: string = '';
  let selectedDataSource: DataSource | null = null;
  let config: any = {};
  let showDocuments = false;
  
  // Options from backend
  let supportedFileTypes: string[] = [];
  let supportedEncodings: string[] = [];
  let isLoadingOptions = false;

  // Initialize data sources
  onMount(async () => {
    try {
      $isLoading = true;
      const sources = await datasourceService.getAll();
      dataSources.set(sources);
      
      // Load backend options
      await loadBackendOptions();
    } catch (error) {
      console.error('Error loading data sources:', error);
      errorMessage.set('Failed to load data sources');
    } finally {
      $isLoading = false;
    }
  });
  
  // Function to close the dialog and reset form state
  function closeDialog() {
    showAddForm = false;
    selectedDataSourceId = '';
    selectedDataSource = null;
    config = {};
  }
  
  // Load options from backend
  async function loadBackendOptions() {
    try {
      isLoadingOptions = true;
      const [fileTypes, encodings] = await Promise.all([
        datasourceService.getFileTypes(),
        datasourceService.getEncodings()
      ]);
      
      supportedFileTypes = fileTypes;
      supportedEncodings = encodings;
    } catch (error) {
      console.error('Error loading backend options:', error);
    } finally {
      isLoadingOptions = false;
    }
  }

  // Helper function to safely access properties
  function safeProp(obj, path, fallback = undefined) {
    if (!obj) return fallback;
    const parts = path.split('.');
    let current = obj;
    for (const part of parts) {
      if (current === null || current === undefined) return fallback;
      current = current[part];
    }
    return current === undefined ? fallback : current;
  }

  // Update selected data source when ID changes
  $: {
    if (selectedDataSourceId && $dataSources[selectedDataSourceId]) {
      console.log('Selected datasource:', selectedDataSourceId, $dataSources[selectedDataSourceId]);
      selectedDataSource = $dataSources[selectedDataSourceId];
      // Initialize config with default values from schema
      config = {};
      const properties = selectedDataSource.config_schema.properties;
      for (const key in properties) {
        // Initialize all fields, not just those with defaults
        if (properties[key].default !== undefined) {
          config[key] = properties[key].default;
        } else {
          // Initialize with empty values based on type
          if (properties[key].type === 'string') {
            config[key] = '';
          } else if (properties[key].type === 'integer' || properties[key].type === 'number') {
            config[key] = properties[key].minimum || 0;
          } else if (properties[key].type === 'boolean') {
            config[key] = false;
          } else if (properties[key].type === 'array') {
            config[key] = [];
          } else if (properties[key].type === 'object') {
            config[key] = {};
          }
        }
      }
      // Always set the source_id
      config.source_id = selectedDataSourceId;
      // Make sure name is set
      if (!config.name) {
        config.name = $dataSources[selectedDataSourceId].name;
      }
    } else {
      selectedDataSource = null;
      config = {};
    }
  }

  async function createDataSource() {
    if (!selectedDataSourceId || !selectedDataSource) return;
    
    try {
      $isLoading = true;
      $errorMessage = null;
      
      // Make sure source_type is set
      if (selectedDataSource.config_schema?.properties?.source_type?.default) {
        config.source_type = selectedDataSource.config_schema.properties.source_type.default;
      }
      
      // Make sure name is set (required field)
      if (!config.name || config.name.trim() === '') {
        config.name = `${selectedDataSource.id || 'Data Source'} ${new Date().toLocaleTimeString()}`;
      }
      
      // Create data source instance
      const result = await datasourceService.create(config as DataSourceConfig);
      
      // Load documents
      const docs = await datasourceService.loadDocuments(result.datasource_id);
      
      // Update stores
      activeDataSource.set(result.datasource_id);
      dataSourceConfig.set(config as DataSourceConfig);
      documents.set(docs);
      
      // Reset form
      showAddForm = false;
      selectedDataSourceId = '';
      config = {};
      
      // Refresh data sources
      const sources = await datasourceService.getAll();
      dataSources.set(sources);
      
      // Show success message
      alert(`Data source "${config.name}" created successfully with ${docs.length} documents loaded.`);
      
      return true;
    } catch (error) {
      console.error('Error creating data source:', error);
      errorMessage.set('Failed to create data source');
      return false;
    } finally {
      $isLoading = false;
    }
  }

  // Track active data sources
  let activeDataSources: {id: string, name: string, docCount: number}[] = [];

  // Function to list active data sources
  async function refreshActiveSources() {
    try {
      $isLoading = true;

      // This is a simplified approach - in a real app, you'd likely store
      // active instances in a database and retrieve them from the backend
      const instanceId = $activeDataSource;
      if (instanceId) {
        try {
          // Get info about the active instance
          const info = await datasourceService.getInfo(instanceId);
          const docs = await datasourceService.loadDocuments(instanceId);
          
          activeDataSources = [{
            id: instanceId,
            name: $dataSourceConfig?.name || "Unnamed Source",
            docCount: docs.length
          }];
        } catch (e) {
          console.error("Failed to get datasource info:", e);
        }
      }
    } catch (error) {
      console.error('Error refreshing active sources:', error);
    } finally {
      $isLoading = false;
    }
  }

  // Refresh when component mounts and when active data source changes
  $: if ($activeDataSource) {
    refreshActiveSources();
  }

  onMount(() => {
    refreshActiveSources();
  });

  // Helper functions for event handling
  function handleTextInput(e: Event, key: string): void {
    const target = e.target as HTMLInputElement;
    config[key] = target.value;
  }

  function handleNumberInput(e: Event, key: string): void {
    const target = e.target as HTMLInputElement;
    config[key] = Number(target.value);
  }

  function handleCheckboxChange(e: Event, key: string): void {
    const target = e.target as HTMLInputElement;
    config[key] = target.checked;
  }
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <section>
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Data Sources</h1>
        <p class="text-xl text-gray-600">Browse available data source plugins</p>
      </div>
      <button 
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        on:click={() => showAddForm = !showAddForm}
      >
        {showAddForm ? 'Cancel' : 'Add Data Source'}
      </button>
    </div>

    <!-- Quick Upload Section -->
    <div class="bg-white p-6 rounded-lg shadow-md mb-8">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Quick Upload</h2>
      <p class="text-gray-600 mb-4">
        Upload files directly to the data directory. These files can then be used as data sources.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 class="text-lg font-medium text-gray-800 mb-2">Upload File</h3>
          <FileUploader 
            directory=""
            acceptedFileTypes=".txt,.json,.csv,.pdf"
            onUploadComplete={(filePath) => {
              // Optionally pre-fill a data source with this path
              if (filePath) {
                // Select file datasource if available
                const fileSourceId = Object.entries($dataSources).find(
                  ([, source]) => safeProp(source, 'config_schema.properties.source_type.default') === 'file'
                )?.[0];
                
                if (fileSourceId) {
                  // First set the ID, which will trigger the reactive update
                  selectedDataSourceId = fileSourceId;
                  
                  // Then show the form after a small delay to ensure the datasource is selected
                  setTimeout(() => {
                    showAddForm = true;
                    
                    // Additional delay to ensure the form is fully rendered
                    setTimeout(() => {
                      if (selectedDataSource && config) {
                        // Set file path
                        config.file_path = filePath;
                        
                        // Try to detect file type from extension
                        const ext = filePath.split('.').pop()?.toLowerCase();
                        if (ext && supportedFileTypes.includes(ext)) {
                          config.file_type = ext;
                        }
                        
                        // Make sure source_type is set
                        config.source_type = 'file';
                        
                        // Set a default name based on filename
                        const filename = filePath.split('/').pop();
                        config.name = `File: ${filename}`;
                        
                        console.log('File source config updated for uploaded file:', config);
                      } else {
                        console.error('Failed to initialize form with uploaded file:', filePath);
                      }
                    }, 150);
                  }, 50);
                } else {
                  alert('File datasource not available. Please make sure the backend is running correctly.');
                }
              }
            }}
          />
          <p class="mt-2 text-sm text-gray-500">
            Uploaded files will be saved in the data directory and can be used as datasources.
          </p>
        </div>
        
        <div class="border-l border-gray-200 pl-6">
          <h3 class="text-lg font-medium text-gray-800 mb-2">Recent Files</h3>
          <div class="mt-4 space-y-2 max-h-52 overflow-y-auto">
            {#if $isLoading}
              <p class="text-gray-500 text-sm">Loading files...</p>
            {:else}
              {#await datasourceService.getAvailableFiles() then files}
                {#if files.length === 0}
                  <p class="text-gray-500 text-sm">No files available.</p>
                {:else}
                  {#each files.filter(f => !f.endsWith('/')).slice(0, 5) as file}
                    <div class="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div class="flex items-center">
                        <svg class="h-4 w-4 text-gray-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span class="text-sm truncate max-w-xs">{file.split('/').pop()}</span>
                      </div>
                      <button 
                        class="text-blue-500 hover:text-blue-700 text-xs"
                        on:click={async () => {
                          try {
                            $isLoading = true;
                            $errorMessage = null;
                            
                            // Store the file path for later use
                            const filePath = file;
                            const filename = file.split('/').pop();
                            
                            // Find the file datasource type
                            // Look for the file_datasource plugin ID
                            const fileSourceId = 'file_datasource'; // Use the exact plugin_id from the backend
                            
                            if (!fileSourceId) {
                              alert('No file datasource type found');
                              $isLoading = false;
                              return;
                            }
                            
                            // Create configuration for file datasource
                            const sourceConfig = {
                              source_id: fileSourceId,
                              source_type: 'file_datasource',  // This should match the plugin_id in FileDataSource
                              name: `File: ${filename}`,
                              description: `Automatically created from ${filename}`,
                              file_path: filePath  // Include file_path in the main object
                            };
                            
                            // Try to detect file type from extension
                            const ext = filePath.split('.').pop()?.toLowerCase();
                            if (ext && supportedFileTypes.includes(ext)) {
                              sourceConfig.file_type = ext;
                            }
                            
                            // Create data source instance directly
                            const result = await datasourceService.create(sourceConfig);
                            
                            // Load documents
                            const docs = await datasourceService.loadDocuments(result.datasource_id);
                            
                            // Update stores
                            activeDataSource.set(result.datasource_id);
                            dataSourceConfig.set(sourceConfig);
                            documents.set(docs);
                            
                            // Refresh data sources
                            const sources = await datasourceService.getAll();
                            dataSources.set(sources);
                            
                            // Show success message
                            alert(`File "${filename}" added as data source with ${docs.length} documents loaded.`);
                            
                            // Refresh active sources
                            refreshActiveSources();
                          } catch (error) {
                            console.error('Error creating file data source:', error);
                            $errorMessage = 'Failed to create file data source';
                          } finally {
                            $isLoading = false;
                          }
                        }}
                      >
                        Use as Source
                      </button>
                    </div>
                  {/each}
                {/if}
              {/await}
            {/if}
          </div>
        </div>
      </div>
    </div>

    <!-- Add Form Dialog -->
    {#if showAddForm}
      <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10">
        <div class="bg-white p-6 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">Configure {selectedDataSource ? safeProp(selectedDataSource, 'name', selectedDataSourceId) : 'Data Source'}</h2>
            <button class="text-gray-500 hover:text-gray-700" on:click={() => closeDialog()}>
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {#if selectedDataSource && (!safeProp(selectedDataSource, 'config_schema') || !safeProp(selectedDataSource, 'config_schema.properties'))}
            <div class="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-4">
              This datasource doesn't have a proper configuration schema.
            </div>
          {:else}
            <div class="mb-4">
              <label for="data-source-type" class="block text-sm font-medium text-gray-700 mb-1">Data Source Type</label>
              <select 
                id="data-source-type"
                bind:value={selectedDataSourceId} 
                class="block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Select a data source type</option>
                {#each Object.entries($dataSources) as [id, source]}
                  {@const sourceType = safeProp(source, 'config_schema.properties.source_type.default', "unknown")}
                  <option value={id}>
                    {safeProp(source, 'name', id)} ({sourceType})
                  </option>
                {/each}
              </select>
            </div>

            {#if selectedDataSource}
              {@const sourceType = safeProp(selectedDataSource, 'config_schema.properties.source_type.default', "unknown")}
              <form on:submit|preventDefault={createDataSource} class="space-y-4">
                <div class="mt-6">
                  <div class="flex items-center mb-4">
                    <div class={"p-2 rounded-md text-white mr-3 " + getDatasourceTypeColor(sourceType)}>
                      <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d={getDatasourceTypeIcon(sourceType)} />
                      </svg>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900">Configure {safeProp(selectedDataSource, 'name', selectedDataSourceId)}</h3>
                  </div>
                  <p class="text-gray-600 mb-6">{getDatasourceTypeDescription(sourceType)}</p>
                  
                  {#if !selectedDataSource.config_schema || !selectedDataSource.config_schema.properties}
                    <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
                      <p class="text-sm text-yellow-700">
                        This datasource doesn't have proper configuration schema. Please check the backend implementation.
                      </p>
                    </div>
                  {:else}
                    {#each Object.entries(selectedDataSource.config_schema.properties) as [key, prop]}
                      {#if key !== 'source_id' && !prop.hidden}
                        <div class="mb-4">
                          <label for={key} class="block text-sm font-medium text-gray-700 mb-1">{safeProp(prop, 'title', key)}</label>
                          <div>
                            {#if key === 'file_path'}
                              <FileBrowser 
                                bind:selectedFilePath={config[key]}
                                fileType={safeProp(config, 'file_type', 'txt')}
                              />
                            {:else if key === 'file_type' && supportedFileTypes.length > 0}
                              <select 
                                id={key}
                                bind:value={config[key]} 
                                class="block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                              >
                                {#each supportedFileTypes as fileType}
                                  <option value={fileType}>{fileType.toUpperCase()}</option>
                                {/each}
                              </select>
                            {:else if key === 'encoding' && supportedEncodings.length > 0}
                              <select 
                                id={key}
                                bind:value={config[key]} 
                                class="block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                              >
                                {#each supportedEncodings as encoding}
                                  <option value={encoding}>{encoding}</option>
                                {/each}
                              </select>
                            {:else if safeProp(prop, 'type') === 'string'}
                              {#if safeProp(prop, 'enum', []).length > 0}
                                <select 
                                  id={key}
                                  bind:value={config[key]} 
                                  class="block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                >
                                  {#each safeProp(prop, 'enum', []) as option}
                                    <option value={option}>{option}</option>
                                  {/each}
                                </select>
                              {:else}
                                <input 
                                  id={key}
                                  type="text" 
                                  value={config[key] || ''} 
                                  on:input={(e) => handleTextInput(e, key)}
                                  placeholder={safeProp(prop, 'description', '')}
                                  class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                />
                              {/if}
                            {:else if safeProp(prop, 'type') === 'number' || safeProp(prop, 'type') === 'integer'}
                              <input 
                                id={key}
                                type="number" 
                                value={config[key] || (safeProp(prop, 'minimum') || 0)} 
                                on:input={(e) => handleNumberInput(e, key)}
                                min={safeProp(prop, 'minimum')} 
                                max={safeProp(prop, 'maximum')} 
                                step={safeProp(prop, 'type') === 'integer' ? 1 : 0.1}
                                placeholder={safeProp(prop, 'description', '')}
                                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                              />
                            {:else if safeProp(prop, 'type') === 'boolean'}
                              <div class="flex items-center">
                                <input 
                                  id={key}
                                  type="checkbox"
                                  checked={config[key] || false}
                                  on:change={(e) => handleCheckboxChange(e, key)}
                                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <label for={key} class="ml-2 text-sm text-gray-700">{safeProp(prop, 'description', '')}</label>
                              </div>
                            {/if}
                          </div>
                          {#if safeProp(prop, 'description') && safeProp(prop, 'type') !== 'boolean'}
                            <p class="mt-1 text-sm text-gray-500">{safeProp(prop, 'description', '')}</p>
                          {/if}
                        </div>
                      {/if}
                    {/each}
                  {/if}
                  
                  <div class="flex space-x-3 mt-6">
                    <button
                      type="button"
                      class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                      on:click={() => closeDialog()}
                    >
                      Cancel
                    </button>
                    <button 
                      type="button"
                      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center" 
                      on:click={createDataSource} 
                      disabled={$isLoading}
                    >
                      {#if $isLoading}
                        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Creating...
                      {:else}
                        Create & Select Data Source
                      {/if}
                    </button>
                  </div>
                </div>
              </form>
            {/if}
          {/if}
        </div>
      </div>
    {/if}

    {#if $isLoading && !showAddForm}
      <div class="text-center my-6">
        <svg class="inline-block animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-2 text-gray-600">Loading data sources...</p>
      </div>
    {:else}
      {#if Object.keys($dataSources).length === 0}
        <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-yellow-700">
                No data sources available. Please check if the backend is running properly.
              </p>
            </div>
          </div>
        </div>
      {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {#each Object.entries($dataSources) as [id, source]}
            {@const sourceType = safeProp(source, 'config_schema.properties.source_type.default', "unknown")}
            <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200">
              <div class="px-4 py-3 border-b border-gray-200">
                <!-- Extract source type from schema if available -->
                <div class="flex items-center">
                  <div class="flex-shrink-0 mr-3">
                    <div class={"p-2 rounded-md text-white " + getDatasourceTypeColor(sourceType)}>
                      <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d={getDatasourceTypeIcon(sourceType)} />
                      </svg>
                    </div>
                  </div>
                  <h3 class="text-lg font-semibold text-gray-800">
                    {safeProp(source, 'name', id)}
                  </h3>
                </div>
              </div>
              <div class="px-4 py-4">
                <div>
                  {#if safeProp(source, 'description')}
                    <p class="text-gray-600">{safeProp(source, 'description', '')}</p>
                  {:else}
                    <p class="text-gray-600">{getDatasourceTypeDescription(sourceType)}</p>
                    <p class="text-gray-500 text-sm mt-2">Plugin ID: {id}</p>
                  {/if}
                </div>
              </div>
              <div class="px-4 py-3 bg-gray-50 border-t border-gray-200">
                <button 
                  class="w-full flex items-center justify-center text-blue-600 hover:text-blue-800 font-medium py-1" 
                  on:click={() => { 
                    // First set the ID, which will trigger the reactive update
                    selectedDataSourceId = id;
                    
                    // Then show the form after a small delay to ensure the datasource is selected
                    setTimeout(() => {
                      showAddForm = true;
                      
                      // Additional delay to ensure the form is fully rendered
                      setTimeout(() => {
                        if (selectedDataSource && config) {
                          // Ensure source_type is set correctly
                          if (selectedDataSource.config_schema?.properties?.source_type?.default) {
                            config.source_type = selectedDataSource.config_schema.properties.source_type.default;
                          }
                          
                          // Set a default name if not already set
                          if (!config.name) {
                            config.name = `${safeProp(source, 'name', id)} Instance`;
                          }
                          
                          console.log('Datasource config initialized:', config);
                        } else {
                          console.error('Failed to initialize form with datasource:', id);
                        }
                      }, 150);
                    }, 50);
                  }}
                  aria-label="Use this data source"
                >
                  <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span>Configure & Add</span>
                </button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    {/if}
    
    <!-- Active Data Source Instances -->
    {#if activeDataSources.length > 0}
      <section class="mt-12">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Active Data Sources</h2>
        <p class="text-lg text-gray-600 mb-6">Currently loaded data sources</p>
        
        <div class="bg-white shadow overflow-hidden sm:rounded-md mb-8">
          <ul class="divide-y divide-gray-200">
            {#each activeDataSources as source}
              <li>
                <div class="px-4 py-4 sm:px-6">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 bg-blue-500 rounded-md p-2">
                        <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                        </svg>
                      </div>
                      <div class="ml-4">
                        <h3 class="text-lg font-medium text-gray-900">{source.name}</h3>
                        <p class="text-sm text-gray-500">ID: {source.id}</p>
                      </div>
                    </div>
                    <div class="flex items-center">
                      <span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {source.docCount} Documents
                      </span>
                      <button 
                        class="ml-4 text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                        on:click={() => showDocuments = !showDocuments}
                      >
                        {showDocuments ? 'Hide Documents' : 'View Documents'}
                      </button>
                      <a href="/workflow" class="ml-4 text-indigo-600 hover:text-indigo-900 text-sm font-medium">
                        Use for Workflow
                      </a>
                    </div>
                  </div>
                </div>
              </li>
            {/each}
          </ul>
        </div>

        {#if showDocuments && $documents.length > 0}
          <div class="bg-white shadow-md rounded-lg p-6 mb-8">
            <DocumentViewer datasourceId={$activeDataSource} />
          </div>
        {/if}
      </section>
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