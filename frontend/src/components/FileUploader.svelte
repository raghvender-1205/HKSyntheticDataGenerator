<script lang="ts">
  import { datasourceService } from '../services/api';
  import { errorMessage } from '../stores';
  
  export let directory: string = '';
  export let onUploadComplete: (filePath: string) => void = () => {};
  export let acceptedFileTypes: string = '';
  
  let dragOver = false;
  let uploading = false;
  let fileInput: HTMLInputElement;
  let error: string | null = null;
  
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
      uploading = true;
      error = null;
      
      const result = await datasourceService.uploadFile(file, directory);
      
      // Call the callback with the file path
      onUploadComplete(result.path);
      
      // Set success message
      $errorMessage = `File "${file.name}" uploaded successfully.`;
    } catch (err) {
      console.error('Error uploading file:', err);
      error = 'Failed to upload file. Please try again.';
    } finally {
      uploading = false;
    }
  }
</script>

<div class="file-uploader">
  <!-- Hidden file input -->
  <input 
    type="file" 
    id="file-upload" 
    bind:this={fileInput}
    on:change={handleFileUpload}
    accept={acceptedFileTypes}
    class="hidden"
  />
  
  <!-- Drop zone -->
  <div 
    class="p-4 border border-gray-300 rounded-md cursor-pointer text-center {dragOver ? 'bg-blue-50 border-blue-300' : 'bg-gray-50'}"
    on:dragover={handleDragOver}
    on:dragleave={handleDragLeave}
    on:drop={handleDrop}
    on:click={() => fileInput.click()}
  >
    {#if uploading}
      <div class="py-4">
        <svg class="animate-spin h-8 w-8 text-blue-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-2 text-sm text-gray-600">Uploading file...</p>
      </div>
    {:else}
      <svg class="h-10 w-10 text-gray-400 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
      <p class="mt-2 text-sm text-gray-500">
        Drag and drop a file here, or click to browse
      </p>
      {#if acceptedFileTypes}
        <p class="mt-1 text-xs text-gray-400">
          Accepted file types: {acceptedFileTypes}
        </p>
      {/if}
    {/if}
    
    {#if error}
      <p class="mt-2 text-sm text-red-500">{error}</p>
    {/if}
  </div>
</div> 