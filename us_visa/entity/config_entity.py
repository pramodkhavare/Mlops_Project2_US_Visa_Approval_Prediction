import os ,sys 
from datetime import datetime
from collections import namedtuple
from dataclasses import dataclass

def get_time_stamp():
    return datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

@dataclass(frozen=True)
class TrainingPipelineConfig:
    artifact_dir :str 
    
@dataclass(frozen=True)
class MongoDBCOnfig:
    database_name : str 
    collection :str 
    mongodb_url :str 
    
@dataclass(frozen=True)
class DataIngestionConfig:
    raw_data_dir :str 
    ingested_dir :str 
    ingested_train_data_dir_path :str 
    ingested_test_data_dir_path :str
    train_test_split_ratio: float 
    
    
@dataclass(frozen=True)
class DataValidationConfig:
    schema_file_path :str 
    report_file_path :str 
    report_page_file_path :str 