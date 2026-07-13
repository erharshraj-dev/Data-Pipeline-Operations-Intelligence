import os
import time
import yaml
import logging
import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


class CSVConnector:
    """
    Generic CSV Connector

    Responsibilities
    ----------------
    1. Read YAML configuration
    2. Connect to CSV source registry
    3. Read datasets
    4. Validate datasets
    5. Return Pandas DataFrames

    This class DOES NOT perform:
    - Parsing
    - Mapping
    - Normalization
    - Validation
    - Enrichment
    """

    def __init__(self, config_path: str):

        self.config_path = config_path
        self.sources = {}
        self.connected = False

    ####################################################
    # Load Configuration
    ####################################################

    def load_config(self):

        logger.info("Loading source configuration...")

        with open(self.config_path, "r") as file:
            config = yaml.safe_load(file)

        self.sources = config["sources"]

        logger.info(f"{len(self.sources)} sources loaded successfully.")

    ####################################################
    # Connect
    ####################################################

    def connect(self):

        self.load_config()

        self.connected = True

        logger.info("CSV Connector Connected.")

    ####################################################
    # Disconnect
    ####################################################

    def disconnect(self):

        self.connected = False

        logger.info("CSV Connector Disconnected.")

    ####################################################
    # Validate File
    ####################################################

    def validate_file(self, file_path):

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if os.path.getsize(file_path) == 0:
            raise ValueError(f"Empty file: {file_path}")

    ####################################################
    # Read One Dataset
    ####################################################

    def read(self, source_name):

        if not self.connected:
            raise Exception("Connector is not connected.")

        if source_name not in self.sources:
            raise Exception(f"Unknown source: {source_name}")

        file_path = self.sources[source_name]["path"]

        self.validate_file(file_path)

        logger.info(f"Reading dataset: {source_name}")

        start = time.time()

        dataframe = pd.read_csv(file_path)

        end = time.time()

        logger.info(
            f"{source_name} | "
            f"Rows={dataframe.shape[0]} | "
            f"Columns={dataframe.shape[1]} | "
            f"Time={round(end-start,3)} sec"
        )

        return dataframe

    ####################################################
    # Read All Datasets
    ####################################################

    def read_all(self):

        datasets = {}

        logger.info("Loading all datasets...")

        for source in self.sources:

            datasets[source] = self.read(source)

        logger.info(f"{len(datasets)} datasets loaded successfully.")

        return datasets

    ####################################################
    # Health Check
    ####################################################

    def health_check(self):

        logger.info("Running Health Check...")

        healthy = True

        for source in self.sources:

            path = self.sources[source]["path"]

            try:

                self.validate_file(path)

                logger.info(f"{source} : OK")

            except Exception as e:

                healthy = False

                logger.error(e)

        return healthy