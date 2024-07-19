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
    