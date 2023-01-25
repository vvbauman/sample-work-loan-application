import pandas as pd
import numpy as np
import pandera as pa

from src.utils.ingestion_utils import ingest_flat_file, save_flat_file, drop_nulls

class IngestMergeLoanTables():
    def __init__(self, cf : dict, cf_m : dict) -> None:
        """
        Class to ingest and merge all (bronze) tables in the loan dataset, to create a silver table with all merged data
        
        Args
        ----------
        cf : configuration file with constants used across project
        cf_m : configuration file with constants used in this specific class

        Attributes
        ----------
        cf (dict) : same as cf input argument. Configuration file with constants used across projects
        cf_m (dict) : same as cf_m input argument. Configuration file with constants used in this specific class
        account (pd.DataFrame) : table containing account data. 

        Note: any empty attributes defined here are populated/re-defined within methods in this class
        
        """
        self.cf= cf
        self.cf_m= cf_m

        self.account= pd.DataFrame([])
        self.card= pd.DataFrame([])
        self.client= pd.DataFrame([])
        self.disp= pd.DataFrame([])
        self.district= pd.DataFrame([])
        self.loan= pd.DataFrame([])
        self.order= pd.DataFrame([])
        self.transactions= pd.DataFrame([])
        self.silver= pd.DataFrame([])

        # add logger

    def get_silver_table(self, schema : pa.DataFrameSchema) -> pd.DataFrame:
        """ 
        Wrapper method for retrieving the silver table containing all merged bronze tables, by either ingesting and merging all bronze tables 
        using ingest_bronze_tables(), cast_bronze_tables(), and merge_bronze_tables() methods 
        or by ingesting a previously saved silver table using load_from_disk() method

        Option to save silver table to disk. Option available regardless if ingesting from scratch

        Populates self.silver, returns self.silver

        Parameters
        ----------
        schema : expected schema of final silver dataframe (7 of 8 bronze tables merged into a single dataframe)
        """
        if self.cf['FROM_SCRATCH']:
            self.silver= self.ingest_bronze_tables().cast_bronze_dtypes().merge_bronze_tables()
            # add validation 
        else:
            self.silver= self.load_from_disk(schema= schema)
            # add validation
        
        if self.cf['SAVE_SILVER']:
            save_flat_file(path= self.cf['SILVER_SAVE_DIR'], filename= self.cf_m['bronze_merged_save_name'], df= self.silver)
            # add log message

        return self.silver

    def ingest_bronze_tables(self):
        """ 
        Ingest bronze tables, dropping nulls when adjusting using drop_nulls utility functions
        Run validation to ensure all tables are what's expected

        Populates self attributes account, card, client, disp, district, loan, order, and transactions
        """
        self.account= drop_nulls(df= pd.read_csv(self.cf['DATA_URL'] + self.cf_m['bronze_account'], sep= self.cf_m['bronze_table_sep']))
        self.card= drop_nulls(df= pd.read_csv(self.cf['DATA_URL'] + self.cf_m['bronze_card'], sep= self.cf_m['bronze_table_sep']))
        self.client= drop_nulls(df= pd.read_csv(self.cf['DATA_URL'] + self.cf_m['bronze_client'], sep= self.cf_m['bronze_table_sep']))
        self.disp= drop_nulls(df= pd.read_csv(self.cf['DATA_URL'] + self.cf_m['bronze_disp'], sep= self.cf_m['bronze_table_sep']))
        self.district= drop_nulls(df= pd.read_csv(self.cf['DATA_URL'] + self.cf_m['bronze_district'], sep= self.cf_m['bronze_table_sep']))
        self.loan= drop_nulls(df= pd.read_csv(self.cf['DATA_URL'] + self.cf_m['bronze_loan'], sep= self.cf_m['bronze_table_sep']))
        self.order= drop_nulls(df= pd.read_csv(self.cf['DATA_URL'] + self.cf_m['bronze_order'], sep= self.cf_m['bronze_table_sep']))
        self.transactions= drop_nulls(
            df= pd.read_csv(self.cf['DATA_URL'] + self.cf_m['bronze_transactions'], sep= self.cf_m['bronze_table_sep']), 
            subset= self.cf_m['transactions_null_subset'])
        
        # add data validation on columns/dtypes

        return self
    
    def cast_bronze_dtypes(self):
        """ 
        Method to cast all bronze tables to their required dtypes. Does not include district table. Intended to be run before merging all bronze tables
        Modifies self attributes account, card, client, disp, loan, order, and transactions
        """
        self.account= self.date_convert(df= self.account.astype(self.cf_m['account_dtypes']), date_col= self.cf_m['account_date_col'], date_format= self.cf_m['date_format'])
        self.card= self.card.astype(self.cf_m['card_dtypes'])
        self.client= self.date_convert(df= self.client.astype(self.cf_m['client_dtypes']), date_col= self.cf_m['client_date_col'], date_format= self.cf_m['date_format'])
        self.disp= self.disp.astype(self.cf_m['disp_dtypes'])
        self.loan= self.date_convert(df= self.loan.astype(self.cf_m['loan_dtypes']), date_col= self.cf_m['loan_date_col'], date_format= self.cf_m['date_format'])
        self.order= self.order.astype(self.cf_m['order_dtypes'])
        self.transactions= self.date_convert(df= self.transactions.astype(self.cf_m['transactions_dtypes']), date_col= self.cf_m['transactions_date_col'], date_format= self.cf_m['date_format'])

        # add log message

        return self
    
    @staticmethod
    def date_convert(df : pd.DataFrame, date_col : str, date_format : str) -> pd.DataFrame:
        """ 
        Method for converting a str column in a pandas dataframe to a date column. Expected str format for the date column is '%y%m%d'

        Parameters
        ----------
        df : dataframe containing the str column to be converted to dates
        date_col : name of column in df with the str values to be converted to dates

        Returns
        ----------
        df : same as input df but with all values in date_col converted to datetime.datetime

        """
        df[date_col]= pd.to_datetime(df[date_col], format= date_format, errors= 'coerce')
        return df

    def merge_bronze_tables(self) -> pd.DataFrame:
        """ 
        Method for merging all bronze tables into one silver table. Two merges are run in this method: first merges all dataframes with an "account_id"
        column, second merges all dataframes with a "client_id" column. These two dataframes are then merged to create the silver dataframe
        
        Try/except blocks are used to provide informative log messages if a merge fails

        Tables/dataframes being merged are self attributes account, loan, order, transactions, disp, client, and card

        Returns
        ----------
        silver : dataframe with all bronze tables merged

        """
        try:
            account_id_merge= (self.account
            .merge(self.loan, on= self.cf_m['account_id_merge_cols'], how = self.cf_m['account_id_merge_type'], suffixes= (self.cf_m['account_suffix'], self.cf_m['loan_suffix']))
            .merge(self.order, on= self.cf_m['account_id_merge_cols'], how = self.cf_m['account_id_merge_type'], suffixes= (self.cf_m['loan_suffix'], self.cf_m['order_suffix']))
            .merge(self.transactions, on= self.cf_m['account_id_merge_cols'], how = self.cf_m['account_id_merge_type'], suffixes= (self.cf_m['order_suffix'], self.cf_m['transactions_suffix']))
            .merge(self.disp, on= self.cf_m['account_id_merge_cols'], how = self.cf_m['account_id_merge_type'], suffixes= (self.cf_m['transactions_suffix'], self.cf_m['disp_suffix']))
            )
        except:
            raise(Exception)

        try:
            other_tables_merge= (self.disp
            .merge(self.client, on= self.cf_m['client_id_merge_cols'], how= self.cf_m['client_id_merge_type'], suffixes= (self.cf_m['disp_suffix'], self.cf_m['client_suffix']))
            .merge(self.card, on= self.cf_m['client_id_card_merge_cols'], how= self.cf_m['client_id_card_merge_type'], suffixes= (self.cf_m['client_disp_suffix'], self.cf_m['card_suffix']))
            )
        except:
            raise(Exception)

        try:
            silver= other_tables_merge.merge(account_id_merge, on= self.cf_m['account_id_merge_cols'], how= self.cf_m['account_id_merge_type'], suffixes= ('', self.cf_m['disp_id_suffix']))
            # log message
        except:
            raise(Exception)
        return silver
    
    def load_from_disk(self, schema : pa.DataFrameSchema):
        silver, msg= ingest_flat_file(path= self.cf['DATA_URL'], filename= self.cf['BRONZE_MERGED_FILE'], schema= schema)
        # add log message
        return silver