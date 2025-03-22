import { writable } from 'svelte/store';

// Create a writable store for toast messages
const toasts = writable([]);

// Toast manager to handle toast notifications
export const ToastManager = {
  /**
   * Show a toast notification
   * @param {string} message - Message to display
   * @param {string} type - Type of toast (success, error, warning, info)
   * @param {number} duration - Duration in milliseconds
   */
  show: (message, type = 'info', duration = 3000) => {
    const id = Math.floor(Math.random() * 10000);
    
    // Add toast to the store
    toasts.update(all => [
      { id, message, type, duration },
      ...all
    ]);
    
    // Remove toast after duration
    setTimeout(() => {
      ToastManager.remove(id);
    }, duration);
    
    return id;
  },
  
  /**
   * Remove a toast by ID
   * @param {number} id - Toast ID to remove
   */
  remove: (id) => {
    toasts.update(all => all.filter(t => t.id !== id));
  },
  
  /**
   * Get the toast store
   */
  subscribe: toasts.subscribe
};

export default ToastManager; 