import os ,sys ,json 
import pandas as pd 

from pandas import DataFrame 
from sklearn.base import BaseEstimator,TransformerMixin


from us_visa.exception import ClassificationException 
from us_visa.logger import logging
from us_visa.utils.main_utils import read_yaml ,write_yaml_file ,check_lists_match ,read_yaml ,save_numpy_array  ,save_object
from us_visa.entity.artifact_entity import DataIngestionArtifact ,DataValidationArtifacs ,DataTransformationArtifact
from us_visa.entity.config_entity import DataTransformationConfig 
from datetime import date 
import numpy as np
from sklearn.preprocessing import StandardScaler ,OneHotEncoder 
from sklearn.pipeline import Pipeline 
from sklearn.compose import ColumnTransformer
from us_visa.constants import *
from sklearn.preprocessing import OneHotEncoder, StandardScaler,OrdinalEncoder, PowerTransformer
from sklearn.compose import ColumnTransformer 
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

COMPANY_AGE = 'company_age'
YEAR_OF_ESTAB = 'yr_of_estab'
# df['company_age'] = current_year - df['yr_of_estab'] 

class FeatureGenerator(BaseEstimator ,TransformerMixin):
    """
    Feature Engineering Part will taken care by this class.
    """
    def __init__(self ,
                 add_company_age =True ,
                 yr_of_estab_ix = 3 ,
                 columns=None):
        try:
            self.columns = columns
            if self.columns is not None:
                yr_of_estab_ix = self.columns.index(YEAR_OF_ESTAB)
                
            self.add_company_age = add_company_age 
            self.yr_of_estab_ix = yr_of_estab_ix
        
        except Exception as e:
            raise ClassificationException (e ,sys)
    def fit(self ,X,y=None):
        return self  
    
    def transform(self ,X ,y=None):
        try:
            todays_date = date.today()
            current_year = todays_date.year
            company_age = current_year - X[: ,self.yr_of_estab_ix]
            if self.add_company_age:
                generated_feature = np.c_[
                    X ,company_age 
                ]
            else:
                generated_feature = X
            return generated_feature
        except Exception as e:
            raise ClassificationException (e ,sys)
        
        
        
class TargetValueMapping:
    """
    This class provides a mapping from target value strings to integers 
    and allows for reverse mapping.
    """
    def __init__(self):
        self.Certified: int = 0
        self.Denied: int = 1

    def _asdict(self):
        """
        Converts the mapping attributes to a dictionary.
        
        Returns:
            dict: A dictionary representation of the mappings.
        """
        return self.__dict__

    def reverse_mapping(self):
        """
        Creates a reverse mapping from integer values to target value strings.
        
        Returns:
            dict: A dictionary with integers as keys and target value strings as values.
        """
        mapping_response = self._asdict()
        return dict(zip(mapping_response.values(), mapping_response.keys()))
    
        
class DataTransformation():
    def __init__(self ,data_validation_artifatcts :DataValidationArtifacs ,
                 data_transformation_config : DataTransformationConfig):
        try:
            logging.info(f'\n\n{"*" * 20} Data Transformation Step Started {"*" *20}')
            self.data_validation_artifatcts = data_validation_artifatcts 
            self.data_transformation_config = data_transformation_config
        except Exception as e:
            raise ClassificationException (e ,sys) 
        
        
    def get_data_transformer_object(self) ->ColumnTransformer:
        try:
            logging.info("We are Creating Data Transformation Object") 
            schema_file_path = self.data_transformation_config.schema_file_path 
            dataset_schema = read_yaml(schema_file_path) 
          
            
            numerical_column = dataset_schema[SCHEMA_NUMERICAL_COLUMN_KEY].split(" ")
            categorical_column =dataset_schema[SCHEMA_CATEGORICAL_COLUMN_KEY].split(" ")
            ordinal_encoder_columns = dataset_schema[SCHEMA_ORDINAL_ENCODER_COLUMN_KEY].split(" ")
            one_hot_encoder_columns = dataset_schema[SCHEMA_ONE_HOT_ENCODER_COLUMN_KEY].split(" ")
            transform_columns = dataset_schema[SCHEMA_TRANSFORM_COLUMN_KEY].split(" ")
            
            num_pipeline = Pipeline(
               steps=[
                ('impute' ,SimpleImputer(strategy='median')) ,
                ('feature_generator' ,FeatureGenerator(
                    add_company_age= True ,
                    yr_of_estab_ix= 6,
                    columns = numerical_column)) ,
                ('scalar' ,StandardScaler())
                ]
            )
            
            tranform_pipeline = Pipeline(
                steps=[
                    ("transformer" ,PowerTransformer(method='yeo-johnson')) ,
                    ('scaler', StandardScaler(with_mean=False))
                ]
            )
            
            ordinal_pipeline = Pipeline(
                steps=[
                    ("ordinal_encoder" , OrdinalEncoder()) ,
                    ('scaler', StandardScaler(with_mean=False))
                ]
            )
            one_hot_pipeline = Pipeline(
                steps=[
                    ('onehot_encoder' ,OneHotEncoder(handle_unknown='ignore' ,)) ,
                    ('scaler', StandardScaler(with_mean=False))
                ]
                
            )
            preprocessor = ColumnTransformer(
                [   
                    ('num_pipeline' , num_pipeline ,numerical_column) ,
                    ("OneHotEncoder" , one_hot_pipeline , one_hot_encoder_columns) ,
                    ("OrdinalEncoder" , ordinal_pipeline ,ordinal_encoder_columns) ,
                    ("transormer" , tranform_pipeline ,transform_columns)
                ]
            )
            
            return preprocessor

   
        except Exception as e:
            raise ClassificationException (e ,sys) 
        
    def initiated_data_transformation(self)->DataTransformationArtifact:
        try:
            logging.info(f'{"*"*20}Data Transformation started {"*"*20}')
            preprocessing_obj = self.get_data_transformer_object()
             
            logging.info(f'Loading Training Data from {self.data_validation_artifatcts} and {self.data_validation_artifatcts.valid_test_data_file_path}')
            
            train_data = pd.read_csv(self.data_validation_artifatcts.valid_train_data_file_path)
            test_data = pd.read_csv(self.data_validation_artifatcts.valid_test_data_file_path)
            
            
            logging.info(f"Load Schema of Data from [{self.data_transformation_config.schema_file_path}]")
            
            schema = read_yaml(self.data_transformation_config.schema_file_path)
            
            target_column_name = schema[TARGET_COLUMN_KEY]
            
            logging.info("Separating Output column from Train and test data")
            input_train_df = train_data.drop(columns=[target_column_name])
            output_train_df = train_data[[target_column_name]]
            
            output_train_df = output_train_df.replace(
                TargetValueMapping()._asdict()
            )
            todays_date = date.today()
            current_year = todays_date.year
            input_train_df['company_age'] = current_year - input_train_df[YEAR_OF_ESTAB]
            
            
            
            
            input_test_df = test_data.drop(columns=[target_column_name])
            output_test_df = test_data[[target_column_name]]
        
            output_test_df = output_test_df.replace(
                TargetValueMapping()._asdict()
            )
            input_test_df['company_age'] = current_year - input_test_df[YEAR_OF_ESTAB]
            
            logging.info("Applying Preprocessor on Train and Test Data")
            
            
            
            input_train_arr = preprocessing_obj.fit_transform(input_train_df)
            input_test_arr = preprocessing_obj.transform(input_test_df)
            
            
            final_train_arr = np.c_[
                input_train_arr ,np.array(output_train_df)
            ]
            final_test_arr = np.c_[
                input_test_arr ,np.array(output_test_df)
            ]
            
            
            transformed_train_file_path = os.path.join(
                self.data_transformation_config.transformed_train_dir ,'valid_train.npz'
            )
            transformed_test_file_path = os.path.join(
                self.data_transformation_config.transformed_test_dir ,'valid_test.npz'
            )
            
            logging.info(f"Transformed Train Data will save at : [{transformed_train_file_path}]")
            logging.info(f"Transformed Test Data will save at : [{transformed_test_file_path}]")
            
            preprocessor_obje_file_path = os.path.join(
                self.data_transformation_config.preprocessing_obj_dir ,
                self.data_transformation_config.preprocessing_object_file_name
            )
            
            save_object(
                file_path= preprocessor_obje_file_path ,
                obj= preprocessing_obj
            )
            save_numpy_array(
                file_path= transformed_train_file_path ,
                array= final_train_arr
            )
            save_numpy_array(
                file_path= transformed_test_file_path ,
                array= final_test_arr
            )
            
            data_transformation_artifacts =DataTransformationArtifact(
                transformed_train_file_path= transformed_train_file_path ,
                transformed_test_file_path= transformed_test_file_path ,
                preprocessor_file_path= preprocessor_obje_file_path
            )
            
            return data_transformation_artifacts
            
        except Exception as e:
            raise ClassificationException (e ,sys) 