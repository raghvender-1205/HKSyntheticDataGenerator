<script lang="ts">
  import { onMount } from 'svelte';
  import { datasourceService } from '../services/api';
  import { isLoading, errorMessage } from '../stores';
  
  export let selectedFilePath: string = '';
  export let fileType: string = 'txt';
  
  let currentDirectory: string = '';
  let availableFiles: string[] = [];
  let error: string | null = null;
  let showBrowser: boolean = false;
  let fileInput: HTMLInputElement;
  let uploadingFile: boolean = false;
  let dragOver: boolean = false;
  
  // Load files when the component mounts
  onMount(async () => {
    await loadFiles();
  });
  
  // Load files from the current directory
  async function loadFiles() {
    try {
      $isLoading = true;
      error = null;
      availableFiles = await datasourceService.getAvailableFiles(currentDirectory);
    } catch (err) {
      console.error('Error loading files:', err);
      error = 'Failed to load files. Please try again.';
    } finally {
      $isLoading = false;
    }
  }
  
  // Navigate to a directory
  function navigateToDirectory(directory: string) {
    currentDirectory = directory;
    loadFiles();
  }
  
  // Select a file
  function selectFile(filePath: string) {
    selectedFilePath = filePath;
    showBrowser = false;
  }
  
  // Handle file type updates
  $: {
    fileType; // React to changes in fileType prop
  }
  
  // Go up one directory
  function goUpDirectory() {
    if (currentDirectory) {
      const parts = currentDirectory.split('/');
      parts.pop(); // Remove the last part
      parts.pop(); // Remove the empty string at the end (if any)
      currentDirectory = parts.join('/');
      loadFiles();
    }
  }
  
  // Toggle the file browser
  function toggleBrowser() {
    showBrowser = !showBrowser;
    if (showBrowser) {
      loadFiles();
    }
  }
  
  // Handle file upload
  async function handleFileUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;
    
    await uploadFile(input.files[0]);
    
    // Reset the input
    input.value = '';
  }
  
  // Handle file drop
  function handleDrop(event: DragEvent) {
    event.preventDefault();
    dragOver = false;
    
    if (!event.dataTransfer || !event.dataTransfer.files || event.dataTransfer.files.length === 0) return;
    
    uploadFile(event.dataTransfer.files[0]);
  }
  
  // Handle drag events
  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    dragOver = true;
  }
  
  function handleDragLeave() {
    dragOver = false;
  }
  
  // Upload file to server
  async function uploadFile(file: File) {
    try {
      uploadingFile = true;
      error = null;
      
      await datasourceService.uploadFile(file, currentDirectory);
      
      // Reload files after upload
      await loadFiles();
      
      // Set success message
      $errorMessage = `File "${file.name}" uploaded successfully.`;
    } catch (err) {
      console.error('Error uploading file:', err);
      error = 'Failed to upload file. Please try again.';
    } finally {
      uploadingFile = false;
    }
  }
</script>

<div class="file-browser">
  <div class="flex">
    <input 
      type="text" 
      bind:value={selectedFilePath}
      placeholder="Select a file..."
      class="flex-grow px-3 py-2 border border-gray-300 rounded-l-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
    />
    <button 
      type="button"
      on:click={toggleBrowser}
      class="px-3 py-2 bg-blue-600 text-white rounded-r-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
    >
      Browse
    </button>
  </div>
  
  {#if showBrowser}
    <div class="mt-2 bg-white border border-gray-300 rounded-md shadow-sm">
      <div class="p-2 border-b border-gray-300 bg-gray-50 flex justify-between items-center">
        <span class="text-sm font-medium text-gray-700">
          {currentDirectory || 'Root'}
        </span>
        <div class="flex items-center">
          <input 
            type="file" 
            id="file-upload" 
            bind:this={fileInput}
            on:change={handleFileUpload}
            class="hidden"
          />
          <button 
            type="button"
            on:click={() => fileInput.click()}
            class="px-2 py-1 text-xs bg-green-500 text-white hover:bg-green-600 rounded mr-2"
            disabled={uploadingFile}
          >
            {uploadingFile ? 'Uploading...' : 'Upload'}
          </button>
          <button 
            on:click={goUpDirectory}
            class="px-2 py-1 text-xs text-gray-700 hover:bg-gray-200 rounded"
            disabled={!currentDirectory}
          >
            Go Up
          </button>
        </div>
      </div>
      
      <!-- Drop zone for file upload -->
      <div 
        class="p-4 border-b border-gray-200 bg-gray-50 text-center cursor-pointer {dragOver ? 'bg-blue-50 border-blue-300' : ''}"
        on:dragover={handleDragOver}
        on:dragleave={handleDragLeave}
        on:drop={handleDrop}
      >
        <svg class="h-6 w-6 text-gray-400 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p class="mt-1 text-sm text-gray-500">
          Drag and drop a file here, or click the upload button
        </p>
      </div>
      
      <div class="max-h-64 overflow-y-auto p-2">
        {#if $isLoading}
          <div class="text-center py-4">
            <svg class="animate-spin h-5 w-5 text-blue-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p class="text-sm text-gray-500">Loading files...</p>
          </div>
        {:else if uploadingFile}
          <div class="text-center py-4">
            <svg class="animate-spin h-5 w-5 text-green-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p class="text-sm text-gray-500">Uploading file...</p>
          </div>
        {:else if error}
          <div class="text-center py-4">
            <p class="text-sm text-red-500">{error}</p>
          </div>
        {:else if availableFiles.length === 0}
          <div class="text-center py-4">
            <p class="text-sm text-gray-500">No files found.</p>
          </div>
        {:else}
          <ul class="divide-y divide-gray-200">
            {#each availableFiles as file}
              {@const isDirectory = file.endsWith('/')}
              <li>
                <button 
                  class="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm"
                  on:click={() => isDirectory ? navigateToDirectory(file) : selectFile(file)}
                >
                  <div class="flex items-center">
                    <svg class="h-4 w-4 mr-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      {#if isDirectory}
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                      {:else}
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      {/if}
                    </svg>
                    <span>{isDirectory ? file.split('/').slice(-2, -1).join('') : file.split('/').pop()}</span>
                  </div>
                </button>
              </li>
            {/each}
          </ul>
        {/if}
      </div>
      
      <!-- File type filter -->
      <div class="p-2 border-t border-gray-300 bg-gray-50">
        <div class="flex items-center">
          <span class="text-xs text-gray-700 mr-2">Show files of type:</span>
          <select 
            bind:value={fileType}
            class="text-xs px-2 py-1 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Files</option>
            <option value="txt">Text (.txt)</option>
            <option value="json">JSON (.json)</option>
            <option value="csv">CSV (.csv)</option>
          </select>
        </div>
      </div>
    </div>
  {/if}
</div> 