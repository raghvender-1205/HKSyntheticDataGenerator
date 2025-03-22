<script lang="ts">
  import { documents } from '../stores';
  import type { Document } from '../types';
  import Modal from './Modal.svelte';
  
  export let datasourceId: string | null = null;
  
  let searchQuery = '';
  let filteredDocuments: Document[] = [];
  let currentPage = 1;
  const pageSize = 10;
  
  // Modal state
  let showModal = false;
  let selectedDocument: Document | null = null;
  
  // Filter documents based on search query
  $: {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filteredDocuments = $documents.filter(doc => 
        doc.content.toLowerCase().includes(query)
      );
    } else {
      filteredDocuments = [...$documents];
    }
  }
  
  // Calculate pagination
  $: totalPages = Math.ceil(filteredDocuments.length / pageSize);
  $: paginatedDocuments = filteredDocuments.slice(
    (currentPage - 1) * pageSize, 
    currentPage * pageSize
  );
  
  function nextPage() {
    if (currentPage < totalPages) {
      currentPage++;
    }
  }
  
  function prevPage() {
    if (currentPage > 1) {
      currentPage--;
    }
  }
  
  function truncateText(text: string, maxLength = 200) {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  }
  
  function viewDocument(doc: Document) {
    selectedDocument = doc;
    showModal = true;
  }
</script>

<div>
  <div class="mb-6">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold text-gray-900">Documents ({$documents.length})</h2>
      <div class="relative">
        <input
          type="text"
          bind:value={searchQuery}
          placeholder="Search documents..."
          class="pl-10 pr-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    </div>
    
    {#if $documents.length === 0}
      <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-yellow-700">
              No documents available. Please select a data source first.
            </p>
          </div>
        </div>
      </div>
    {:else}
      <div class="bg-white shadow overflow-hidden rounded-md">
        <ul class="divide-y divide-gray-200">
          {#each paginatedDocuments as doc, index}
            <li class="px-6 py-4 hover:bg-gray-50">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">Document {(currentPage - 1) * pageSize + index + 1}</h3>
                  <div class="mt-1 text-sm text-gray-600">
                    <p>{truncateText(doc.content)}</p>
                  </div>
                </div>
                <button 
                  class="ml-4 px-3 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 hover:bg-blue-200"
                  on:click={() => viewDocument(doc)}
                >
                  View Full
                </button>
              </div>
              {#if doc.metadata && Object.keys(doc.metadata).length > 0}
                <div class="mt-2 flex flex-wrap gap-2">
                  {#each Object.entries(doc.metadata) as [key, value]}
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                      {key}: {typeof value === 'object' ? JSON.stringify(value) : value}
                    </span>
                  {/each}
                </div>
              {/if}
            </li>
          {/each}
        </ul>
      </div>
      
      <!-- Pagination -->
      {#if totalPages > 1}
        <div class="flex items-center justify-between mt-4">
          <div class="flex-1 flex justify-between sm:hidden">
            <button 
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50" 
              on:click={prevPage}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            <button 
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50" 
              on:click={nextPage}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
          </div>
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                Showing <span class="font-medium">{(currentPage - 1) * pageSize + 1}</span> to <span class="font-medium">{Math.min(currentPage * pageSize, filteredDocuments.length)}</span> of <span class="font-medium">{filteredDocuments.length}</span> results
              </p>
            </div>
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button 
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50" 
                  on:click={prevPage}
                  disabled={currentPage === 1}
                  aria-label="Previous"
                >
                  <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </button>
                {#each Array(Math.min(5, totalPages)) as _, i}
                  {#if i + 1 <= totalPages}
                    <button 
                      class={`relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium ${currentPage === i + 1 ? 'text-blue-600 bg-blue-50' : 'text-gray-700 hover:bg-gray-50'}`}
                      on:click={() => currentPage = i + 1}
                    >
                      {i + 1}
                    </button>
                  {/if}
                {/each}
                <button 
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50" 
                  on:click={nextPage}
                  disabled={currentPage === totalPages}
                  aria-label="Next"
                >
                  <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                  </svg>
                </button>
              </nav>
            </div>
          </div>
        </div>
      {/if}
    {/if}
  </div>

  <!-- Document Viewer Modal -->
  <Modal
    bind:showModal
    title="Document Content"
  >
    {#if selectedDocument}
      <div class="max-h-[70vh] overflow-y-auto">
        <pre class="whitespace-pre-wrap text-sm p-4 bg-gray-50 rounded">{selectedDocument.content}</pre>
        
        {#if selectedDocument.metadata && Object.keys(selectedDocument.metadata).length > 0}
          <div class="mt-4">
            <h4 class="font-medium text-gray-900 mb-2">Metadata</h4>
            <div class="bg-gray-50 p-4 rounded">
              {#each Object.entries(selectedDocument.metadata) as [key, value]}
                <div class="mb-2">
                  <span class="font-medium">{key}:</span> 
                  <span class="text-gray-700">{typeof value === 'object' ? JSON.stringify(value) : value}</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    {:else}
      <p class="text-gray-500">No document selected.</p>
    {/if}
  </Modal>
</div> 