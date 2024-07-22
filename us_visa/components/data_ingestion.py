from us_visa.configuration import VisaClassficationConfiguration
from us_visa.entity.config_entity import DataIngestionConfig ,MongoDBCOnfig
from us_visa.entity.artifact_entity import DataIngestionArtifact
from us_visa.logger import logging
from us_visa.exception import ClassificationException
import os ,sys 
import tarfile 
from six.moves import urllib
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit 
import shutil
from us_visa.configuration.mogo_db_connection import MongoDBClient
from sklearn.model_selection import train_test_split 




class DataIngestion() :
    def __init__(self ,data_ingestion_config :DataIngestionConfig ,mongodb_config :MongoDBCOnfig):
        try:
            logging.info(f"{'*'*20}Data Ingestion Step Started{'*'*20}")
            self.config = data_ingestion_config  
            self.mongodb_config = mongodb_config
            # print(self.config)
        except Exception as e:
            raise ClassificationException(e ,sys) from e 
        
    def export_collection_as_dataframe(self)->pd.DataFrame:
        try:
            self.mongo_client = MongoDBClient(config=self.mongodb_config)
            collection = self.mongo_client.database[self.mongodb_config.collection]
            
            df = pd.DataFrame(list(collection.find()))
            if "_id" in df.columns.to_list():
                df = df.drop(columns=["_id"], axis=1)
            df.replace({"na":np.nan},inplace=True)
            return df
        
        except Exception as e:
            raise ClassificationException(e ,sys) from e 
        
    def save_data_to_raw_data_dir(self):
        try:
            data = self.export_collection_as_dataframe()
            raw_data_dir = self.config.raw_data_dir
            os.makedirs(raw_data_dir ,exist_ok= True)
            data.to_csv(os.path.join(raw_data_dir ,"us_visa_data.csv") ,index=False ,header=True)
        except Exception as e:
            raise ClassificationException(e ,sys) from e 
    
    def split_data_in_train_test_data(self ,dataframe :pd.DataFrame):
        try:
            dataframe = dataframe 
            test_size = self.config.train_test_split_ratio
            train_data ,test_data = train_test_split(dataframe ,
                                                     test_size= test_size)
            
            train_dir_path = self.config.ingested_train_data_dir_path 
            os.makedirs(train_dir_path ,exist_ok=True)
            
            test_dir_path = self.config.ingested_test_data_dir_path
            os.makedirs(test_dir_path ,exist_ok=True)
            
            train_data.to_csv(os.path.join(train_dir_path ,'train_data.csv') ,index=False ,header=True)
            test_data.to_csv(os.path.join(test_dir_path , 'test_data.csv') ,index=False ,header=True)
      
            
        except Exception as e:
            raise ClassificationException(e ,sys) from e 
        
    def initiate_data_ingestion(self) ->DataIngestionArtifact:
        try:
            dataframe = self.export_collection_as_dataframe()
            self.save_data_to_raw_data_dir()
            self.split_data_in_train_test_data(dataframe=dataframe)
            
            train_dir_path = self.config.ingested_train_data_dir_path 
            ingested_train_data_file_path = os.path.join(train_dir_path ,'train_data.csv')
            
            test_dir_path = self.config.ingested_test_data_dir_path
            ingested_test_data_file_path = os.path.join(test_dir_path , 'test_data.csv')
            
            data_ingestion_artifacts = DataIngestionArtifact(
                ingested_train_data_file_path= ingested_train_data_file_path,
                ingested_test_data_file_path= ingested_test_data_file_path
            )
            return data_ingestion_artifacts
        
        except Exception as e:
            raise ClassificationException(e ,sys) from e  

        

