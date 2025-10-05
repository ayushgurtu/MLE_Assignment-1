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

def process_silver_table(snapshot_date_str,
                         bronze_loan_directory,
                         bronze_feature_directory,
                         bronze_financial_directory,
                         bronze_clickstream_directory,
                         silver_loan_daily_directory,
                         spark):

    snapshot_date = datetime.strptime(snapshot_date_str, "%Y-%m-%d")

    # ---------------- Loan Bronze ----------------
    partition_name = "bronze_loan_daily_" + snapshot_date_str.replace('-', '_') + ".csv"
    filepath = bronze_loan_directory + partition_name
    df = spark.read.csv(filepath, header=True, inferSchema=True)
    print("loaded from:", filepath, "row count:", df.count())

    column_type_map = {
        "loan_id": StringType(),
        "Customer_ID": StringType(),
        "loan_start_date": DateType(),
        "tenure": IntegerType(),
        "installment_num": IntegerType(),
        "loan_amt": FloatType(),
        "due_amt": FloatType(),
        "paid_amt": FloatType(),
        "overdue_amt": FloatType(),
        "balance": FloatType(),
        "snapshot_date": DateType(),
    }
    # for column, new_type in column_type_map.items():
    #     if column in df.columns:
    #         df = df.withColumn(column, F.col(column).cast(new_type))

    for column, new_type in column_type_map.items():
        if column in df.columns:
            if isinstance(new_type, StringType):
                df = df.withColumn(
                    column,
                    F.when(F.col(column).isNull(), "")  # replace nulls
                     .when(F.trim(F.col(column)) == "", "")  # empty -> ""
                     .otherwise(F.trim(F.col(column)))
                )
            
            elif isinstance(new_type, IntegerType):
                df = df.withColumn(
                    column,
                    F.regexp_replace(F.col(column).cast("string"), "[^0-9-]", "")  # keep only digits
                )
                df = df.withColumn(
                column,
                F.when((F.col(column) == "") | (F.col(column).isNull()), 0)
                 .when(F.col(column).cast(IntegerType()) < 0, 0)               # discard negatives
                 .otherwise(F.col(column).cast(new_type))
            )
    
            elif isinstance(new_type, FloatType):
                df = df.withColumn(
                    column,
                    F.regexp_replace(F.col(column).cast("string"), "[^0-9\\.-]", "")  # keep digits, decimal, negative sign
                )
                df = df.withColumn(
                    column,
                    F.when((F.col(column) == "") | (F.col(column).isNull()), 0.0)
                     .when(F.col(column).cast(FloatType()) < 0, 0.0)               # discard negatives
                     .otherwise(F.col(column).cast(new_type))
                )
    
            else:
                df = df.withColumn(column, F.col(column).cast(new_type))

    # ---------------- Feature Bronze ----------------
    partition_name = "bronze_feature_daily_" + snapshot_date_str.replace('-', '_') + ".csv"
    filepath = bronze_feature_directory + partition_name
    df1 = spark.read.csv(filepath, header=True, inferSchema=True)
    print("loaded from:", filepath, "row count:", df1.count())

    column_type_map = {
        "Customer_ID": StringType(),
        "Name": StringType(),
        "Age": IntegerType(),
        "SSN": StringType(),
        "Occupation": StringType(),
        "snapshot_date": DateType(),
    }

    # for column, new_type in column_type_map.items():
    #     if column in df1.columns:
    #         df1 = df1.withColumn(column, F.col(column).cast(new_type))

    # clean data: strip underscores from numeric columns before type conversion
    columns_to_clean = [
        'Age'
    ]
    for column in columns_to_clean:
        if column in df1.columns:
            df1 = df1.withColumn(column, F.regexp_replace(col(column).cast(StringType()), "_", ""))
            
    for column, new_type in column_type_map.items():
        if column in df1.columns:
            if isinstance(new_type, StringType):
                df1 = df1.withColumn(
                    column,
                    F.when(F.col(column).isNull(), "")  # replace nulls
                     .when(F.trim(F.col(column)) == "", "")  # empty -> ""
                     .otherwise(F.trim(F.col(column)))
                )
            
            elif isinstance(new_type, IntegerType):
                df1 = df1.withColumn(
                    column,
                    F.regexp_replace(F.col(column).cast("string"), "[^0-9-]", "")  # keep only digits
                )
                df1 = df1.withColumn(
                    column,
                    F.when((F.col(column) == "") | (F.col(column).isNull()), 0)
                     .otherwise(F.col(column).cast(new_type))
                )
    
            elif isinstance(new_type, FloatType):
                df1 = df1.withColumn(
                    column,
                    F.regexp_replace(F.col(column).cast("string"), "[^0-9\\.-]", "")  # keep digits, decimal, negative sign
                )
                df1 = df1.withColumn(
                    column,
                    F.when((F.col(column) == "") | (F.col(column).isNull()), 0.0)
                     .when(F.col(column).cast(FloatType()) < 0, 0.0)               # discard negatives
                     .otherwise(F.col(column).cast(new_type))
                )
    
            else: 
                df1 = df1.withColumn(column, F.col(column).cast(new_type))

    # ---------------- Financial Bronze ----------------
    partition_name = "bronze_financial_daily_" + snapshot_date_str.replace('-', '_') + ".csv"
    filepath = bronze_financial_directory + partition_name
    df2 = spark.read.csv(filepath, header=True, inferSchema=True)
    print("loaded from:", filepath, "row count:", df2.count())

    column_type_map = {
        "Customer_ID": StringType(),
        "Annual_Income": FloatType(),
        "Monthly_Inhand_Salary": FloatType(),
        "Num_Bank_Accounts": IntegerType(),
        "Num_Credit_Card": IntegerType(),
        "Interest_Rate": IntegerType(),
        "Num_of_Loan": IntegerType(),
        "Type_of_Loan": StringType(),
        "Delay_from_due_date": IntegerType(),
        "Num_of_Delayed_Payment": IntegerType(),
        "Changed_Credit_Limit": FloatType(),
        "Num_Credit_Inquiries": IntegerType(),
        "Credit_Mix": StringType(),
        "Outstanding_Debt": FloatType(),
        "Credit_Utilization_Ratio": FloatType(),
        "Credit_History_Age": StringType(),
        "Payment_of_Min_Amount": StringType(),
        "Total_EMI_per_month": FloatType(),
        "Amount_invested_monthly": FloatType(),
        "Payment_Behaviour": StringType(),
        "Monthly_Balance": FloatType(),
        "snapshot_date": DateType(),
    }

    # for column, new_type in column_type_map.items():
    #     if column in df2.columns:
    #         df2 = df2.withColumn(column, F.col(column).cast(new_type))

    # clean data: strip underscores from numeric columns before type conversion
    columns_to_clean = [
        'Annual_Income', 'Num_of_Loan', 'Num_of_Delayed_Payment', 
        'Changed_Credit_Limit', 'Outstanding_Debt', 'Amount_invested_monthly', 
        'Monthly_Balance'
    ]
    for column in columns_to_clean:
        if column in df2.columns:
            df2 = df2.withColumn(column, F.regexp_replace(col(column).cast(StringType()), "_", ""))
            
    for column, new_type in column_type_map.items():
        if column in df2.columns:
            if isinstance(new_type, StringType):
                df2 = df2.withColumn(
                    column,
                    F.when(F.col(column).isNull(), "")  # replace nulls
                     .when(F.trim(F.col(column)) == "", "")  # empty -> ""
                     .otherwise(F.trim(F.col(column)))
                )
            
            elif isinstance(new_type, IntegerType):
                df2 = df2.withColumn(
                    column,
                    F.regexp_replace(F.col(column).cast("string"), "[^0-9-]", "")  # keep only digits
                )
                df2 = df2.withColumn(
                    column,
                    F.when((F.col(column) == "") | (F.col(column).isNull()), 0)
                     .otherwise(F.col(column).cast(new_type))
                )
    
            elif isinstance(new_type, FloatType):
                df2 = df2.withColumn(
                    column,
                    F.regexp_replace(F.col(column).cast("string"), "[^0-9\\.-]", "")
                )
                # Cast to float, replace invalid with 0.0
                df2 = df2.withColumn(
                    column,
                    F.when((F.col(column) == "") | (F.col(column).isNull()), 0.0)
                     .when(F.col(column).cast(FloatType()) < 0, 0.0)               # discard negatives
                     .otherwise(F.col(column).cast(new_type))
                )
    
            else: 
                df2 = df2.withColumn(column, F.col(column).cast(new_type))

    # ---------------- Clickstream Bronze ----------------
    partition_name = "bronze_clickstream_daily_" + snapshot_date_str.replace('-', '_') + ".csv"
    filepath = bronze_clickstream_directory + partition_name
    df3 = spark.read.csv(filepath, header=True, inferSchema=True)
    print("loaded from:", filepath, "row count:", df3.count())

    column_type_map = {
        "fe_1": IntegerType(),
        "fe_2": IntegerType(),
        "fe_3": IntegerType(),
        "fe_4": IntegerType(),
        "fe_5": IntegerType(),
        "fe_6": IntegerType(),
        "fe_7": IntegerType(),
        "fe_8": IntegerType(),
        "fe_9": IntegerType(),
        "fe_10": IntegerType(),
        "fe_11": IntegerType(),
        "fe_12": IntegerType(),
        "fe_13": IntegerType(),
        "fe_14": IntegerType(),
        "fe_15": IntegerType(),
        "fe_16": IntegerType(),
        "fe_17": IntegerType(),
        "fe_18": IntegerType(),
        "fe_19": IntegerType(),
        "fe_20": IntegerType(),
        "Customer_ID": StringType(),
        "snapshot_date": DateType(),
    }

    # for column, new_type in column_type_map.items():
    #     if column in df3.columns:
    #         df3 = df3.withColumn(column, F.col(column).cast(new_type))
            
    for column, new_type in column_type_map.items():
        if column in df3.columns:
            if isinstance(new_type, StringType):
                df3 = df3.withColumn(
                    column,
                    F.when(F.col(column).isNull(), "")  # replace nulls
                     .when(F.trim(F.col(column)) == "", "")  # empty -> ""
                     .otherwise(F.trim(F.col(column)))
                )
            
            elif isinstance(new_type, IntegerType):
                df3 = df3.withColumn(
                    column,
                    F.regexp_replace(F.col(column).cast("string"), "[^0-9-]", "")  # keep only digits
                )
                df3 = df3.withColumn(
                    column,
                    F.when((F.col(column) == "") | (F.col(column).isNull()), 0)
                     .otherwise(F.col(column).cast(new_type))
                )
    
            elif isinstance(new_type, FloatType):
                df3 = df3.withColumn(
                    column,
                    F.regexp_replace(F.col(column).cast("string"), "[^0-9\\.]", "")  # keep digits + decimal point
                )
                df3 = df3.withColumn(
                    column,
                    F.when((F.col(column) == "") | (F.col(column).isNull()), 0.0)
                     .when(F.col(column).cast(FloatType()) < 0, 0.0)               # discard negatives
                     .otherwise(F.col(column).cast(new_type))
                )
    
            else: 
                df3 = df3.withColumn(column, F.col(column).cast(new_type))


    # ---------------- Join All ----------------
    # Drop duplicate Customer_ID and snapshot_date before joining
    df1 = df1.drop("snapshot_date")
    df2 = df2.drop("snapshot_date")
    df3 = df3.drop("snapshot_date")

    silver_df = (
        df.join(df1, on="Customer_ID", how="left")
          .join(df2, on="Customer_ID", how="left")
          .join(df3, on="Customer_ID", how="left")
    )

    # Keep only one snapshot_date (from df) and Customer_ID
    cols = ["Customer_ID", "snapshot_date"] + [c for c in silver_df.columns if c not in ["Customer_ID", "snapshot_date"]]
    silver_df = silver_df.select(cols)

    # ---------------- Fill Nulls ----------------
    # Identify numeric vs string columns
    numeric_cols = [f.name for f in silver_df.schema.fields 
                    if isinstance(f.dataType, (IntegerType, FloatType))]
    string_cols  = [f.name for f in silver_df.schema.fields 
                    if isinstance(f.dataType, StringType)]

    # print('numeric_cols: ',numeric_cols)

    # print('string_cols: ',string_cols)

    # Replace nulls accordingly
    # silver_df = silver_df.fillna(0, subset=numeric_cols)
    # silver_df = silver_df.fillna("", subset=string_cols)

    # augment data: add month on book
    silver_df = silver_df.withColumn("mob", col("installment_num").cast(IntegerType()))

    # augment data: add days past due
    silver_df = silver_df.withColumn("installments_missed", F.ceil(col("overdue_amt") / col("due_amt")).cast(IntegerType())).fillna(0)
    silver_df = silver_df.withColumn("first_missed_date", F.when(col("installments_missed") > 0, F.add_months(col("snapshot_date"), -1 * col("installments_missed"))).cast(DateType()))
    silver_df = silver_df.withColumn("dpd", F.when(col("overdue_amt") > 0.0, F.datediff(col("snapshot_date"), col("first_missed_date"))).otherwise(0).cast(IntegerType()))

    # ---------------- Save silver table ----------------
    if not silver_df.rdd.isEmpty():
        partition_name = "silver_loan_daily_" + snapshot_date_str.replace('-', '_') + '.parquet'
        filepath = silver_loan_daily_directory + partition_name
        silver_df.write.mode("overwrite").parquet(filepath)
        print('saved to:', filepath)
    else:
        print("silver_df is empty. Skipping write.")
    
    return silver_df

