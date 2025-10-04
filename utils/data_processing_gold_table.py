import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pprint
import pyspark
import pyspark.sql.functions as F
import argparse

from pyspark.sql.functions import col
from pyspark.sql.types import StringType, IntegerType, FloatType, DateType


def process_labels_gold_table(snapshot_date_str, silver_loan_daily_directory, gold_label_store_directory, spark, dpd, mob):
    
    # prepare arguments
    snapshot_date = datetime.strptime(snapshot_date_str, "%Y-%m-%d")
    
    # connect to bronze table
    partition_name = "silver_loan_daily_" + snapshot_date_str.replace('-','_') + '.parquet'
    filepath = silver_loan_daily_directory + partition_name
    df = spark.read.parquet(filepath)
    print('loaded from:', filepath, 'row count:', df.count())

    # get customer at mob
    df = df.filter(col("mob") == mob)

    # get label
    df = df.withColumn("label", F.when(col("dpd") >= dpd, 1).otherwise(0).cast(IntegerType()))
    df = df.withColumn("label_def", F.lit(str(dpd)+'dpd_'+str(mob)+'mob').cast(StringType()))

    # select columns to save
    df = df.select("loan_id", "Customer_ID", "label", "label_def", "snapshot_date")

    # save gold table - IRL connect to database to write
    partition_name = "gold_label_store_" + snapshot_date_str.replace('-','_') + '.parquet'
    filepath = gold_label_store_directory + partition_name
    df.write.mode("overwrite").parquet(filepath)
    # df.toPandas().to_parquet(filepath,
    #           compression='gzip')
    print('saved to:', filepath)
    
    return df


def process_features_gold_table(snapshot_date_str, silver_loan_daily_directory, gold_feature_store_directory, spark, mob = 0):

    # prepare arguments
    snapshot_date = datetime.strptime(snapshot_date_str, "%Y-%m-%d")
    
    # connect to bronze table
    partition_name = "silver_loan_daily_" + snapshot_date_str.replace('-','_') + '.parquet'
    filepath = silver_loan_daily_directory + partition_name
    df = spark.read.parquet(filepath)
    print('loaded from:', filepath, 'row count:', df.count())

    # get customer at mob
    df = df.filter(col("mob") == mob)

    # --- Feature Creation ---

    # # Debt-to-Income Ratio
    # df = df.withColumn("debt_to_income_ratio",(col("Outstanding_Debt") + col("loan_amt")) / col("Annual_Income"))

    # Installment-to-Income Ratio
    df = df.withColumn("installment_to_income_ratio",col("due_amt") / col("Monthly_Inhand_Salary"))

    # Disposable Income Ratio
    df = df.withColumn("disposable_income_ratio",(col("Monthly_Inhand_Salary") - col("Total_EMI_per_month")) / col("Monthly_Inhand_Salary"))
    
    # Overdue Ratio
    df = df.withColumn("overdue_ratio",col("overdue_amt") / col("loan_amt"))
    
    # Missed Payment Ratio
    df = df.withColumn("missed_payment_ratio",col("installments_missed") / col("tenure"))
    
    # # Loan-to-Income Ratio
    # df = df.withColumn("loan_to_income_ratio",col("loan_amt") / col("Annual_Income"))
    
    # Credit Inquiry Stress
    df = df.withColumn("credit_inquiry_stress",col("Num_Credit_Inquiries") / F.when(col("Num_of_Loan") > 0, col("Num_of_Loan")).otherwise(F.lit(1)))

    # select columns to save
    df = df.select("loan_id", "Customer_ID", "installment_to_income_ratio", "disposable_income_ratio", "overdue_ratio","missed_payment_ratio" ,"credit_inquiry_stress" ,"snapshot_date")

    # save gold table - IRL connect to database to write
    partition_name = "gold_feature_store_" + snapshot_date_str.replace('-','_') + '.parquet'
    filepath = gold_feature_store_directory + partition_name
    df.write.mode("overwrite").parquet(filepath)
    # df.toPandas().to_parquet(filepath,
    #           compression='gzip')
    print('saved to:', filepath)
    
    return df
    