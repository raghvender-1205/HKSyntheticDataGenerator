<script lang="ts">
  export let showModal: boolean;
  export let title: string = '';
  
  function closeModal() {
    showModal = false;
  }
  
  // Close the modal when Escape key is pressed
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      closeModal();
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if showModal}
  <div 
    class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-0"
    on:click|self={closeModal} 
    role="dialog" 
    aria-modal="true"
  >
    <!-- Overlay -->
    <div class="fixed inset-0 transition-opacity bg-gray-800 bg-opacity-75"></div>
    
    <!-- Modal panel -->
    <div 
      class="relative z-10 w-full max-w-2xl px-4 py-8 mx-auto overflow-hidden bg-white rounded-lg shadow-xl sm:px-6 sm:pt-8 sm:pb-6 transform transition-all"
      on:click|stopPropagation
    >
      <!-- Header -->
      <div class="flex items-center justify-between mb-4 pb-3 border-b">
        <h3 class="text-lg font-medium text-gray-900">{title}</h3>
        <button 
          class="text-gray-400 bg-white rounded-md hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500" 
          on:click={closeModal}
          aria-label="Close"
        >
          <svg class="w-6 h-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <!-- Content -->
      <div class="relative flex-1 px-4 sm:px-6">
        <!-- Slot for content -->
        <slot></slot>
      </div>
      
      <!-- Footer -->
      <div class="mt-5 sm:mt-6 px-4 sm:px-6 py-3 bg-gray-50 border-t -mx-4 -mb-8 sm:-mx-6 sm:-mb-6 flex justify-end">
        <button 
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          on:click={closeModal}
        >
          Close
        </button>
      </div>
    </div>
  </div>
{/if} 