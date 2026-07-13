import logging
import pandas as pd

logger = logging.getLogger(__name__)


class TabularParser:
    """
    Generic Tabular Parser

    Responsibilities:
    -----------------
    1. Accept DataFrames from CSV Connector
    2. Validate DataFrame
    3. Convert DataFrame into List[Dict]
    4. Preserve original schema

    It DOES NOT:
    -------------
    - Map fields
    - Normalize values
    - Enrich records
    - Validate business rules
    """

    def __init__(self):
        logger.info("Tabular Parser Initialized.")

    # ---------------------------------------------------
    # Health Check
    # ---------------------------------------------------

    def health_check(self, dataframe: pd.DataFrame):

        if dataframe is None:
            raise ValueError("DataFrame is None.")

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Input must be a Pandas DataFrame.")

        if dataframe.empty:
            raise ValueError("DataFrame is empty.")

        if dataframe.columns.duplicated().any():
            raise ValueError("Duplicate columns found.")

        logger.info("Health Check Passed.")

        return True

    # ---------------------------------------------------
    # Parse Single Dataset
    # ---------------------------------------------------

    def parse(self, dataset_name: str, dataframe: pd.DataFrame):

        logger.info(f"Parsing dataset : {dataset_name}")

        self.health_check(dataframe)

        records = []

        for _, row in dataframe.iterrows():

            record = {}

            for column in dataframe.columns:

                value = row[column]

                # Convert NaN to None
                if pd.isna(value):
                    value = None

                # Remove extra spaces
                elif isinstance(value, str):
                    value = value.strip()

                record[column] = value

            records.append(record)

        logger.info(f"{dataset_name} parsed successfully.")

        logger.info(f"Records Parsed : {len(records)}")

        return records

    # ---------------------------------------------------
    # Parse Multiple Datasets
    # ---------------------------------------------------

    def parse_all(self, datasets):

        parsed = {}

        logger.info("Parsing all datasets...")

        for dataset_name, dataframe in datasets.items():

            parsed[dataset_name] = self.parse(
                dataset_name,
                dataframe
            )

        logger.info("All datasets parsed successfully.")

        return parsed