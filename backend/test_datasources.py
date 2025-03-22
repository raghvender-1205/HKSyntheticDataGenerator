import asyncio
from core.service import SyntheticDataService

async def test_datasources():
    """Test that all datasource plugins are loaded correctly."""
    service = SyntheticDataService()
    
    # Get all datasource plugins
    plugins = service.get_datasource_plugins()
    
    print(f"Found {len(plugins)} datasource plugins:")
    for plugin_id, plugin_class in plugins.items():
        print(f"  - {plugin_id}: {plugin_class.__name__}")
        
        # Print source type
        schema = plugin_class.get_config_schema()
        source_type = schema.get('properties', {}).get('source_type', {}).get('default', 'unknown')
        print(f"    Type: {source_type}")

if __name__ == "__main__":
    asyncio.run(test_datasources()) 