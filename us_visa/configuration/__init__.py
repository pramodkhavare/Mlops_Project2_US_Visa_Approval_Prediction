from us_visa.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig, MongoDBCOnfig ,DataValidationConfig ,DataTransformationConfig ,ModelTrainingConfig
    
from us_visa.entity.artifact_entity import DataIngestionArtifact ,DataTransformationArtifact ,ModelTrainingArtifacts

from us_visa.constants import * 
from us_visa.exception import ClassificationException
from us_visa.logger import logging 
from us_visa.utils.main_utils import read_yaml
from dotenv import load_dotenv


class VisaClassficationConfiguration():
    def __init__(self,
                 config_file_path = CONFIG_FILE_PATH ,
                 current_time_stamp = CURRENT_TIME_STAMP):
        try:
         
            self.config_info = read_yaml(yaml_file_path= config_file_path)
           
            self.time_stamp = current_time_stamp 
            self.training_pipeline_config = self.get_training_pipeline_config()
        except Exception as e:
            raise ClassificationException (e ,sys)
        
    def get_training_pipeline_config(self) ->TrainingPipelineConfig:
        try:
            config = self.config_info[TRAINING_PIPELINE_CONFIG]
            
            artifact_dir  = os.path.join(ROOT_DIR 
                                         ,config[TRAINING_PIPELINE_CONFIG_ARTIFACTS_DIR])
            
            training_pipeline_config = TrainingPipelineConfig(artifact_dir=artifact_dir)
            return training_pipeline_config

        except Exception as e:
            raise ClassificationException (e ,sys)
        
    def get_mongodb_config(self):
        try:
            load_dotenv()
            import os 
            mongodb_password = os.environ.get("mongodb_password")
            config = self.config_info[MONGODB_CONFIG_KEY]
            database_name = config[DATABASE_NAME]
            collection = config[COLLECTION_NAME]
            mongodb_url = config[CONNECTION_URL].replace('{password}', mongodb_password)
            mongodb_config = MongoDBCOnfig(
                database_name= database_name,
                collection= collection,
                mongodb_url= mongodb_url
            ) 
            
            return mongodb_config
        except Exception as e:
            raise ClassificationException (e ,sys)
        
        
    def get_data_ingestion_config(self):
        try:
            config = self.config_info[DATA_INGESTION_CONFIG_KEY]
            data_ingestion_dir_key = os.path.join(
                self.training_pipeline_config.artifact_dir ,
                self.time_stamp ,
                config[DATA_INGESTION_DIR_KEY] 
                
            )
            
            raw_data_dir = os.path.join(
                self.training_pipeline_config.artifact_dir ,
                data_ingestion_dir_key ,
                config[RAW_DATA_DIR_KEY]
            )
            
            ingested_dir = os.path.join(
                self.training_pipeline_config.artifact_dir ,
                data_ingestion_dir_key ,
                config[INGESTED_DIR_KEY]
            )
            
            ingested_train_dir = os.path.join(
                ingested_dir ,
                config[INGESTED_TRAIN_DIR]
            )
            
            ingested_test_dir = os.path.join(
                ingested_dir ,
                config[INGESTED_TEST_DIR]
            )
            

            train_test_split_ratio = config[DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO]
            
            
            data_ingestion_config = DataIngestionConfig(
                raw_data_dir= raw_data_dir,
                ingested_dir= ingested_dir,
                ingested_train_data_dir_path= ingested_train_dir,
                ingested_test_data_dir_path= ingested_test_dir,
                train_test_split_ratio= train_test_split_ratio
            )
            
            return data_ingestion_config
        
        except Exception as e:
            raise ClassificationException (e ,sys)
        
    def get_data_validation_config(self)->DataValidationConfig:
        try:
            config = self.config_info[DATA_VALIDATION_CONFIG_KEY]
            
            data_validation_dir_key = os.path.join(
                self.training_pipeline_config.artifact_dir ,
                self.time_stamp ,
                config[DATA_VALIDATION_DIR_KEY]
            ) 
            
            schema_file_path = os.path.join(
                ROOT_DIR ,
                config[DATA_VALIDATION_SCHEMA_DIR_KEY] ,
                config[DATA_VALIDATION_SCHEMA_FILE_KEY]
            )
            
            report_file_path = os.path.join(
                data_validation_dir_key ,
                config[DATA_VALIDATION_REPORT_FILE_NAME_KEY]
            )
            
            report_page_file_path = os.path.join(
                data_validation_dir_key ,
                config[DATA_VALIDATION_REPORT_PAGE_FILE_NAME_KEY]
            )
            valid_data_dir = os.path.join(
                data_validation_dir_key ,
                config[DATA_VALIDATION_VALID_DATA_DIR_KEY]
            )
            invalid_data_dir = os.path.join(
                data_validation_dir_key ,
                config[DATA_VALIDATION_INVALID_DATA_DIR_KEY]
            )
            
            data_validation_config = DataValidationConfig(
                schema_file_path= schema_file_path,
                report_file_path= report_file_path,
                report_page_file_path= report_page_file_path ,
                valid_data_dir= valid_data_dir,
                invalid_data_dir=  invalid_data_dir
            )
            return data_validation_config
        except Exception as e:
            raise ClassificationException (e ,sys)
        
    def get_data_transformation_config(self) -> DataTransformationConfig:
        try:
            config = self.config_info[DATA_TRANSFORMATION_CONFIG_KEY]
            
            data_transformation_dir_key = os.path.join(
                self.training_pipeline_config.artifact_dir ,
                self.time_stamp ,
                config[DATA_TRANSFORMATION_DIR_KEY]
            ) 
            
            transformed_train_dir = os.path.join(
                data_transformation_dir_key ,
                config[DATA_TRANSFORMATION_TRAIN_DIR_KEY]
            )
            
            transformed_test_dir = os.path.join(
                data_transformation_dir_key ,
                config[DATA_TRANSFORMATION_TEST_DIR_KEY]
            )
            
            preprocessing_obj_dir = os.path.join(
                data_transformation_dir_key ,
                config[DATA_TRANSFORMATION_PREPROCESSING_DIR_KEY]
            )
            
            preprocessing_object_file_name = config[DATA_TRANSFORMATION_PREPROCESSING_OBJECT_FILE_NAME_KEY]
            
            schema_file_path = os.path.join(
                ROOT_DIR ,
                config[DATA_TRANSFORMATION_SCHEMA_DIR_KEY] ,
                config[DATA_TRANSFORMATION_SCHEMA_FILE_NAME_KEY]
            )
            
            data_transformation_config = DataTransformationConfig(
                schema_file_path= schema_file_path,
                transformed_train_dir= transformed_train_dir,
                transformed_test_dir= transformed_test_dir,
                preprocessing_obj_dir= preprocessing_obj_dir,
                preprocessing_object_file_name= preprocessing_object_file_name
            ) 
            return data_transformation_config
        except Exception as e:
            raise ClassificationException (e ,sys) from e   
    
    def get_model_training_config(self) ->ModelTrainingConfig:
        try:
            config = self.config_info[MODEL_TRAINING_CONFIG_KEY]
            
            model_training_dir_key = os.path.join(
                self.training_pipeline_config.artifact_dir ,
                self.time_stamp ,
                config[MODEL_TRAINING_DIR_NAME_KEY]
            )
            trained_model_dir_path =os.path.join(
                model_training_dir_key ,
                config[MODEL_TRAINING_TRAINED_MODEL_DIR_KEY]
                
            )
            trained_model_name = config[MODEL_TRAINING_TRAINED_MODEL_FILE_NAME_KEY]
            
            base_accuracy = config[MODEL_TRAINING_TRAINED_MODEL_BASE_ACCURACY]
            
            model_config_file_path = os.path.join(
                ROOT_DIR ,
                CONFIG_DIR ,
                MODEL_CONFIG_FILE_NAME
            )
            
            model_training_config = ModelTrainingConfig(
                trained_model_dir_path= trained_model_dir_path,
                trained_model_name= trained_model_name,
                base_accuracy= base_accuracy ,
                model_config_file_path= model_config_file_path
            )
            print(model_training_config)
            return model_training_config
        except Exception as e:
            raise ClassificationException (e ,sys)
        
        
        
        
if __name__ == "__main__":
    visaclassification = VisaClassficationConfiguration()
    print(visaclassification.get_model_training_config())
    
    
    
    
# us_visa\configuration\__init__.py