import os ,sys ,json 
import pandas as pd 
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection,CatTargetDriftProfileSection
from pandas import DataFrame 
from evidently.dashboard.tabs import DataDriftTab
from evidently.report import Report
from evidently.dashboard import Dashboard 

from us_visa.exception import ClassificationException 
from us_visa.logger import logging
from us_visa.utils.main_utils import read_yaml ,write_yaml_file ,check_lists_match
from us_visa.entity.artifact_entity import DataIngestionArtifact ,DataValidationArtifacs
from us_visa.entity.config_entity import DataValidationConfig 

class DataValidation():
    def __init__(self ,data_ingestion_artifact : DataIngestionArtifact ,
                 data_validation_config : DataValidationConfig):
        try:
            logging.info(f'\n\n{"*" * 20} Data Validation Step Started {"*" *20}')
            self.data_validation_config  = data_validation_config 
            self.data_ingestion_artifact = data_ingestion_artifact 
        except Exception as e:
            raise ClassificationException (e ,sys)
        
    def check_file_exist(self ,train_file_path ,test_file_path) ->bool:
        """
        This Function Will help me to chek weather train and test file sxisted or not 
        train_file_path = path of train dataset you get form data_ingestion_artifacts
        test_file_path = path of test dataset you get form data_ingestion_artifacts
        """
        
        try:
            logging.info('Checking Weather File Exist Or Not')
            is_train_file_exist =False 
            is_test_file_exist =False 
            
            # train_file_path = self.data_ingestion_artifact.ingested_train_data_file_path
            # test_file_path = self.data_ingestion_artifact.ingested_test_data_file_path
            
            is_train_file_exist = os.path.exists(train_file_path)
            is_test_file_exist = os.path.exists(test_file_path)
            
            is_available = is_test_file_exist and is_train_file_exist 
            logging.info(f"Checked Train and Test file exist or not and resukt is : [{is_available}]")
            
            if not is_available:
                training_file = self.data_ingestion_artifact.ingested_train_data_file_path 
                testing_file = self.data_ingestion_artifact.ingested_test_data_file_path 
                logging.info("We Cant procees because train/test file is not available")
                raise Exception(f"Training file:[{training_file}] or \
                                 Testing File :[{testing_file}] is not available")
            return is_available
                
        except Exception as e:
            raise ClassificationException (e ,sys)
        
    def validate_dataset_schema(self ,train_file_path ,test_file_path ,schema_file_path) ->bool:
        """
        This function will help me to check dataset schema of train data and test data . We will check weather all columns are available in training and testing data or not .
        
        """
        try:
            logging.info('Checking columns of train and test file')
            validation_status = False  

            schema_file = read_yaml(schema_file_path)
   
            expecting_columns = list(schema_file['columns'].keys())

            train_dataframe = pd.read_csv(train_file_path)
            test_dataframe = pd.read_csv(test_file_path)
            
            actual_train_columns = list(train_dataframe.columns)
            actual_test_columns = list(test_dataframe.columns)
       
            
            train_validation_status = check_lists_match(expecting_columns ,actual_train_columns)
            test_validation_status = check_lists_match(expecting_columns ,actual_test_columns)
            
            validation_status = train_validation_status and test_validation_status
            logging.info(f'Checked columns of train and test file : [{validation_status}]')
            if not validation_status:
                logging.info("We cant procees because there is mismatch in required columns and available columns")
                raise Exception(f"Expected and actual column mismatch")
        
            return validation_status       
            
        except Exception as e:
            raise ClassificationException (e ,sys) 
        
    def fianal_data_validation(self,train_file_path ,test_file_path ,schema_file_path):
        try:
            data_validation =False 
            data_validation = self.validate_dataset_schema(train_file_path ,test_file_path ,schema_file_path) and \
            self.check_file_exist(train_file_path ,test_file_path)
            return data_validation
        except Exception as e:
            raise ClassificationException(e,sys) from e
        
        
        
    def save_data_drift_report(self,train_file_path ,test_file_path ,report_file_path):
        """
        This function will help you to check data drift using evidently . 
        Also we will create json report which will contain all meta data.
        
        train_file_path = path of train dataset you get form data_ingestion_artifacts
        test_file_path = path of test dataset you get form data_ingestion_artifacts
        report_file_path = Location of json report
        
        """
        try:
            
            profile = Profile(sections=[DataDriftProfileSection()])
            train_df  = pd.read_csv(train_file_path)
            test_df = pd.read_csv(test_file_path)
            
            profile.calculate(train_df ,test_df)
            #json.loads used for data to json format 
            #json.load used for file to convert into json format
        
            report = json.loads(profile.json())
            n_features = report['data_drift']['data']['metrics']['n_features']
            n_drifted_features = report['data_drift']['data']['metrics']['n_drifted_features']
            drift_percentage =  (n_drifted_features / n_features ) *100  
            
            drift_status = report['data_drift']['data']['metrics']['dataset_drift']
            logging.info(f"Total Percentage Drift Detected : {drift_percentage}")
            logging.info(f"Drift Status : {drift_status}")
            report_file_dir = os.path.dirname(report_file_path)
            os.makedirs(report_file_dir ,exist_ok=True)
            
            with open(report_file_path ,'w') as report_files:
                json.dump(report ,report_files ,indent=6)
                
            return drift_status
        except Exception as e:
            raise ClassificationException(e,sys) from e
        
    def save_data_drift_report_html_page(self ,train_file_path ,test_file_path ,page_path):
        """
        Thsi function will save evidently report (Html Page in System)
        """
        try:
            train_df  = pd.read_csv(train_file_path)
            test_df = pd.read_csv(test_file_path) 
            
            dashboard = Dashboard(tabs =[DataDriftTab()])
            dashboard.calculate(train_df ,test_df)
            dashboard.save(page_path)
        except Exception as e:
            raise ClassificationException(e,sys) from e
        
    def initiate_data_validation(self):
        try:
            validation_error_msg =""
            
            train_file_path = self.data_ingestion_artifact.ingested_train_data_file_path
            test_file_path = self.data_ingestion_artifact.ingested_test_data_file_path 
            schema_file_path = self.data_validation_config.schema_file_path
            report_file_path = self.data_validation_config.report_file_path 
            report_page_file_path = self.data_validation_config.report_page_file_path
            
            
            validation_status = self.fianal_data_validation(train_file_path ,test_file_path
                                                            ,schema_file_path) #True or False
            logging.info(f'We checked all columns is test and train dataset and Validation Status is : {validation_status} ')
            
            if validation_status :
                drift_status = self.save_data_drift_report(train_file_path=train_file_path ,test_file_path=test_file_path ,
                                                           report_file_path=report_file_path)
                self.save_data_drift_report_html_page(train_file_path=train_file_path ,test_file_path=test_file_path,
                                                      page_path=report_page_file_path)
                
                if drift_status:
                    logging.info(f"Drift Detected")
                    validation_error_msg = "Drift Detected"
                else :
                    validation_error_msg = f"No Drift Is Detected So We can Proceed With Dataste"
                    
            else:
                validation_error_msg +=f"Unable to Proceed as There is schema mismatch in between expecting and actual columns"
                logging.info(f"Validation Error : {validation_error_msg}")
                
            data_validation_artifacts = DataValidationArtifacs(
                validation_status= validation_status ,
                message= validation_error_msg ,
                report_page_file_path= report_file_path
            )
            logging.info(f"validation Artifacts : {data_validation_artifacts}")
            return data_validation_artifacts
   
            
        except Exception as e:
            raise ClassificationException(e,sys) from e
        