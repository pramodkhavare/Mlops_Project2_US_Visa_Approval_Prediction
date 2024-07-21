import os ,sys 
from datetime import datetime
from collections import namedtuple
from dataclasses import dataclass

@dataclass(frozen=True)
class DataIngestionArtifact:
    ingested_train_data_file_path :str 
    ingested_test_data_file_path :str  
    
@dataclass(frozen=True)
class DataValidationArtifacs:
    validation_status :bool 
    message :str 
    report_page_file_path :str 
    valid_train_data_file_path :str 
    invalid_train_data_file_path :str 
    valid_test_data_file_path :str 
    invalid_test_data_file_path :str 

@dataclass(frozen=True)
class DataTransformationArtifact:
    transformed_train_file_path :str 
    transformed_test_file_path :str 
    preprocessor_file_path :str 