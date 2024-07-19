
from us_visa.configuration import VisaClassficationConfiguration
from us_visa.components.data_ingestion import DataIngestion
from us_visa.components.data_validation import DataValidation
from us_visa.exception import ClassificationException 
from us_visa.logger import logging
from us_visa.entity.artifact_entity import DataIngestionArtifact ,DataValidationArtifacs

import os ,sys
import pandas as pd
import uuid
from threading import Thread
from collections import namedtuple
from datetime import datetime

class TrainPipeline():
    def __init__(self ,config : VisaClassficationConfiguration):
        try:
            self.config = config 
            os.makedirs(self.config.get_training_pipeline_config().artifact_dir ,exist_ok=True) 
        except Exception as e:
            raise ClassificationException (e ,sys) from e
    
    def start_data_ingestion(self):
        try:
            data_ingestion_config = self.config.get_data_ingestion_config() 
            mongodb_config = self.config.get_mongodb_config()
            data_ingestion = DataIngestion(
                data_ingestion_config= data_ingestion_config ,
                mongodb_config= mongodb_config
            )
            
            data_ingestion_artifacts = data_ingestion.initiate_data_ingestion()
            return data_ingestion_artifacts
        except Exception as e:
            raise ClassificationException (e ,sys) from e
        
    def start_data_validation(self ,data_ingestion_artifacts: DataIngestionArtifact):
        try:
            data_validation_config = self.config.get_data_validation_config()
            data_ingestion_artifacts =  data_ingestion_artifacts 
            data_validation = DataValidation(
                data_ingestion_artifact= data_ingestion_artifacts ,
                data_validation_config= data_validation_config
            )  
            data_validation_artifacts = data_validation.initiate_data_validation()
            return data_ingestion_artifacts
        except Exception as e:
            raise ClassificationException (e ,sys) from e
        
    def run_pipeline(self):
        try:
            data_ingestion_artifacts = self.start_data_ingestion() 
            data_validation_artifacts = self.start_data_validation(data_ingestion_artifacts=data_ingestion_artifacts)
            
        except Exception as e:
            raise ClassificationException (e ,sys) from e
        
        
