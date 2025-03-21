import os
from typing import Dict, List, Any, Optional, Type
from .plugin_manager import PluginManager
from .datasource import DataSource, DataSourceConfig, Document
from .llm import LLMProvider, LLMConfig
from .dataset_generator import DatasetGenerator, DatasetGeneratorConfig, Dataset

class SyntheticDataService:
    """
    Central service that manages datasources, LLMs, and dataset generators.
    """
    
    def __init__(self):
        """
        Initialize the service and load plugins.
        """
        # Set up plugin directories
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.plugins_dir = os.path.join(self.base_dir, "plugins")
        
        # Initialize plugin managers
        self.datasource_manager = PluginManager[DataSource](
            DataSource, 
            os.path.join(self.plugins_dir, "datasources")
        )
        
        self.llm_manager = PluginManager[LLMProvider](
            LLMProvider, 
            os.path.join(self.plugins_dir, "llms")
        )
        
        self.dataset_generator_manager = PluginManager[DatasetGenerator](
            DatasetGenerator, 
            os.path.join(self.plugins_dir, "dataset_generators")
        )
        
        # Instances cache
        self.datasource_instances: Dict[str, DataSource] = {}
        self.llm_instances: Dict[str, LLMProvider] = {}
        self.dataset_generator_instances: Dict[str, DatasetGenerator] = {}
    
    # DataSource methods
    
    def get_datasource_plugins(self) -> Dict[str, Type[DataSource]]:
        """
        Get all registered datasource plugins.
        
        Returns:
            A dictionary mapping plugin IDs to plugin classes
        """
        return self.datasource_manager.get_all_plugins()
    
    def get_datasource_plugin(self, plugin_id: str) -> Type[DataSource]:
        """
        Get a datasource plugin by ID.
        
        Args:
            plugin_id: The ID of the plugin to retrieve
            
        Returns:
            The plugin class
        """
        return self.datasource_manager.get_plugin(plugin_id)
    
    async def create_datasource(self, config: DataSourceConfig) -> DataSource:
        """
        Create a datasource instance.
        
        Args:
            config: Configuration for the datasource
            
        Returns:
            A datasource instance
        """
        plugin_class = self.datasource_manager.get_plugin(config.source_id)
        instance = plugin_class(config)
        self.datasource_instances[config.source_id] = instance
        return instance
    
    async def load_documents(self, datasource_id: str) -> List[Document]:
        """
        Load documents from a datasource.
        
        Args:
            datasource_id: The ID of the datasource to load from
            
        Returns:
            A list of documents
        """
        if datasource_id not in self.datasource_instances:
            raise KeyError(f"Datasource {datasource_id} not initialized")
        
        return await self.datasource_instances[datasource_id].load()
    
    # LLM methods
    
    def get_llm_plugins(self) -> Dict[str, Type[LLMProvider]]:
        """
        Get all registered LLM plugins.
        
        Returns:
            A dictionary mapping plugin IDs to plugin classes
        """
        return self.llm_manager.get_all_plugins()
    
    def get_llm_plugin(self, plugin_id: str) -> Type[LLMProvider]:
        """
        Get an LLM plugin by ID.
        
        Args:
            plugin_id: The ID of the plugin to retrieve
            
        Returns:
            The plugin class
        """
        return self.llm_manager.get_plugin(plugin_id)
    
    async def create_llm(self, config: LLMConfig) -> LLMProvider:
        """
        Create an LLM instance.
        
        Args:
            config: Configuration for the LLM
            
        Returns:
            An LLM provider instance
        """
        plugin_class = self.llm_manager.get_plugin(config.model_id)
        instance = plugin_class(config)
        self.llm_instances[config.model_id] = instance
        return instance
    
    # Dataset generator methods
    
    def get_dataset_generator_plugins(self) -> Dict[str, Type[DatasetGenerator]]:
        """
        Get all registered dataset generator plugins.
        
        Returns:
            A dictionary mapping plugin IDs to plugin classes
        """
        return self.dataset_generator_manager.get_all_plugins()
    
    def get_dataset_generator_plugin(self, plugin_id: str) -> Type[DatasetGenerator]:
        """
        Get a dataset generator plugin by ID.
        
        Args:
            plugin_id: The ID of the plugin to retrieve
            
        Returns:
            The plugin class
        """
        return self.dataset_generator_manager.get_plugin(plugin_id)
    
    async def create_dataset_generator(self, config: DatasetGeneratorConfig) -> DatasetGenerator:
        """
        Create a dataset generator instance.
        
        Args:
            config: Configuration for the dataset generator
            
        Returns:
            A dataset generator instance
        """
        plugin_class = self.dataset_generator_manager.get_plugin(config.generator_id)
        instance = plugin_class(config)
        self.dataset_generator_instances[config.generator_id] = instance
        return instance
    
    async def generate_dataset(
        self, 
        generator_id: str, 
        datasource_id: str, 
        llm_id: str, 
        **kwargs
    ) -> Dataset:
        """
        Generate a dataset using the specified dataset generator, datasource, and LLM.
        
        Args:
            generator_id: The ID of the dataset generator to use
            datasource_id: The ID of the datasource to use
            llm_id: The ID of the LLM to use
            **kwargs: Additional parameters for the dataset generation
            
        Returns:
            A dataset
        """
        # Check if all components are initialized
        if generator_id not in self.dataset_generator_instances:
            raise KeyError(f"Dataset generator {generator_id} not initialized")
        
        if datasource_id not in self.datasource_instances:
            raise KeyError(f"Datasource {datasource_id} not initialized")
        
        if llm_id not in self.llm_instances:
            raise KeyError(f"LLM {llm_id} not initialized")
        
        # Load documents
        documents = await self.datasource_instances[datasource_id].load()
        
        # Generate dataset
        return await self.dataset_generator_instances[generator_id].generate(
            documents, 
            self.llm_instances[llm_id], 
            **kwargs
        ) 