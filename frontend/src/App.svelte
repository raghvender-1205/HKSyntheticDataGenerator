<script lang="ts">
  import { Router, Route } from "svelte-routing";
  import Navbar from "./components/Navbar.svelte";
  
  // Pages
  import Home from "./pages/Home.svelte";
  import DataSources from "./pages/DataSources.svelte";
  import LLMs from "./pages/LLMs.svelte";
  import Generators from "./pages/Generators.svelte";
  import Workflow from "./pages/Workflow.svelte";
  
  // Get the base URL from the environment
  const baseUrl = import.meta.env.BASE_URL || "";
</script>

<Router url="{baseUrl}">
  <div class="flex flex-col min-h-screen bg-gray-50">
    <Navbar />
    
    <main class="flex-grow">
      <Route path="/" component={Home} />
      <Route path="/datasources" component={DataSources} />
      <Route path="/llms" component={LLMs} />
      <Route path="/generators" component={Generators} />
      <Route path="/workflow" component={Workflow} />
    </main>
    
    <footer class="bg-white shadow-inner py-6 mt-8">
      <div class="max-w-7xl mx-auto px-4 text-center text-gray-600">
        <p>
          <span class="font-bold">Synthetic Data Generator v0.1</span> - A tool for generating synthetic data for LLM training and fine-tuning.
        </p>
      </div>
    </footer>
  </div>
</Router>
