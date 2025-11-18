"""
Synthetic data preparation utility using SDV library.

This is a utility script for generating synthetic test data.
Move to examples/ or notebooks/ directory if not used in production.
"""

import logging
from sdv.datasets.demo import download_demo

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_synthetic_data(
    modality: str = 'multi_table',
    dataset_name: str = 'fake_hotels'
):
    """
    Downloads synthetic demo data from SDV.
    
    Args:
        modality: Type of data ('single_table', 'multi_table', 'sequential')
        dataset_name: Name of the demo dataset
        
    Returns:
        Tuple of (data, metadata)
    """
    logger.info(f"Downloading {dataset_name} dataset...")
    real_data, metadata = download_demo(
        modality=modality,
        dataset_name=dataset_name
    )
    logger.info(f"✅ Downloaded {dataset_name}")
    return real_data, metadata


def main() -> None:
    """Main function to download and display synthetic data."""
    real_data, metadata = download_synthetic_data()
    
    logger.info(f"Tables in dataset: {list(real_data.keys())}")
    
    if 'hotels' in real_data:
        hotel_count = len(real_data['hotels'])
        logger.info(f"Hotels table has {hotel_count} rows")
        logger.info(f"Columns: {list(real_data['hotels'].columns)}")


if __name__ == "__main__":
    main()
