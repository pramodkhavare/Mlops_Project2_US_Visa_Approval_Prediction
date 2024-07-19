import os ,sys 
from datetime import datetime 
from dotenv import load_dotenv 





load_dotenv()
import os 
password = os.environ.get("mongodb_password")

CURRENT_TIME_STAMP = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
ROOT_DIR = os.getcwd()  


CONFIG_DIR = "config"
CONFIG_FILE_NAME = "config.yaml"
CONFIG_FILE_PATH = os.path.join(ROOT_DIR , CONFIG_DIR ,CONFIG_FILE_NAME)


#Hard Coded variable related with MongoDB
MONGODB_CONFIG_KEY = "mongo_db_config"
DATABASE_NAME = 'database_name'
COLLECTION_NAME = "collection_name"
CONNECTION_URL = "connection_url"


#Hard Coded variable related with training pipeline
TRAINING_PIPELINE_CONFIG = 'training_pipeline_config' 
TRAINING_PIPELINE_CONFIG_PIPELINE_NAME :str = 'visa_pipeline' 
TRAINING_PIPELINE_CONFIG_ARTIFACTS_DIR :str = 'artifact_dir'


#VARIABLE RELATED WITH DATA INGESTION
DATA_INGESTION_CONFIG_KEY = 'data_ingestion_config'
DATA_INGESTION_DIR_KEY = 'data_ingestion_dir'
RAW_DATA_DIR_KEY :str= 'raw_data_dir'
INGESTED_DIR_KEY :str = 'ingested_dir'
INGESTED_TRAIN_DIR = 'ingested_train_dir'
INGESTED_TEST_DIR = 'ingested_test_dir'
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO = 'data_ingestion_split_ratio'


#VARIABLE RELATED WITH DATA VALIDATION
DATA_VALIDATION_CONFIG_KEY = 'data_validation_config'
DATA_VALIDATION_DIR_KEY = 'data_validation_dir'
DATA_VALIDATION_SCHEMA_DIR_KEY = 'schema_dir'
DATA_VALIDATION_SCHEMA_FILE_KEY = 'schema_file_name'
DATA_VALIDATION_REPORT_FILE_NAME_KEY = 'report_file_name' 
DATA_VALIDATION_REPORT_PAGE_FILE_NAME_KEY = 'report_page_file_name'
SCHEMA_COLUMN_KEY = 'columns'
SCHEMA_TARGET_COLUMN_KEY = 'target_columns'
