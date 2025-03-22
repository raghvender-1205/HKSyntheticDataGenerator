import asyncio
import json
import os
from pprint import pprint

from app.models import DataSourceConfig, DataSourceType
from app.services.data_source import PDFDataSource


async def test_pdf_datasource():
    """
    Test the PDFDataSource functionality
    """
    # Ensure PDF directory exists
    pdf_dir = os.path.join(os.getcwd(), "sample_pdfs")
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Configure PDF data source
    config = DataSourceConfig(
        type=DataSourceType.PDF,
        connection_string="",  # Not used for PDF but required by model
        source_path=pdf_dir
    )
    
    # Initialize the PDF data source
    pdf_source = PDFDataSource(config)
    
    # Get the schema
    schema = await pdf_source.get_schema()
    print("\nPDF Data Schema:")
    pprint(schema)
    
    # Fetch data (limited to 5 PDFs)
    print("\nChecking for PDFs in directory:", pdf_dir)
    data = await pdf_source.fetch_data(limit=5)
    
    if data:
        print(f"\nSuccessfully processed {len(data)} PDF files")
        print("\nSample data from first PDF:")
        pprint(data[0])
    else:
        print("\nNo PDF files found or processed. Please add PDFs to the sample_pdfs directory.")


if __name__ == "__main__":
    asyncio.run(test_pdf_datasource()) 