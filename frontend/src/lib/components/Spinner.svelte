<script lang="ts">
  export let size: "small" | "medium" | "large" = "medium";
  export let class_name = "";
</script>

<div class={`spinner ${size} ${class_name}`}>
  <div class="bounce1"></div>
  <div class="bounce2"></div>
  <div class="bounce3"></div>
</div>

<style>
  .spinner {
    display: inline-flex;
    justify-content: center;
    align-items: center;
  }
  
  .spinner > div {
    width: 10px;
    height: 10px;
    margin: 0 2px;
    background-color: currentColor;
    border-radius: 100%;
    display: inline-block;
    animation: sk-bouncedelay 1.4s infinite ease-in-out both;
  }
  
  .spinner.small > div {
    width: 6px;
    height: 6px;
  }
  
  .spinner.large > div {
    width: 14px;
    height: 14px;
  }
  
  .spinner .bounce1 {
    animation-delay: -0.32s;
  }
  
  .spinner .bounce2 {
    animation-delay: -0.16s;
  }
  
  @keyframes sk-bouncedelay {
    0%, 80%, 100% { 
      transform: scale(0);
    } 
    40% { 
      transform: scale(1.0);
    }
  }
</style> 