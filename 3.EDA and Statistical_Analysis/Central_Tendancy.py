import pandas as pd
import numpy as np

class CT:
    
    @staticmethod
    def QuanQualDates(df):
        quan = []
        qual = []
        dates = []
        
        for columnName in df.columns:
            if df[columnName].dtype == 'O':
                qual.append(columnName)
            elif pd.api.types.is_datetime64_any_dtype(df[columnName]):
                dates.append(columnName)
            else:
                quan.append(columnName)
                
        return quan, qual, dates

    def compute_descriptive_statistics(self, df, quan):
        descriptive = pd.DataFrame(index=["Mean", "Median", "Mode", "Q1:25%", "Q2:50%", "Q3:75%", "99%", "Q4:100%", "IQR", "1.5rule", "Lesser", "Greater", "Min", "Max", "Skew", "Kurtosis", "Var", "Std"], columns=quan)
        
        for columnName in quan:
            descriptive.at["Mean", columnName] = df[columnName].mean()
            descriptive.at["Median", columnName] = df[columnName].median()
            descriptive.at["Mode", columnName] = df[columnName].mode()[0]
            descriptive.at["Q1:25%", columnName] = df[columnName].quantile(0.25)
            descriptive.at["Q2:50%", columnName] = df[columnName].quantile(0.50)
            descriptive.at["Q3:75%", columnName] = df[columnName].quantile(0.75)
            descriptive.at["99%", columnName] = np.percentile(df[columnName], 99)
            descriptive.at["Q4:100%", columnName] = df[columnName].max()
            descriptive.at["IQR", columnName] = descriptive.at["Q3:75%", columnName] - descriptive.at["Q1:25%", columnName]
            descriptive.at["1.5rule", columnName] = 1.5 * descriptive.at["IQR", columnName]
            descriptive.at["Lesser", columnName] = descriptive.at["Q1:25%", columnName] - descriptive.at["1.5rule", columnName]
            descriptive.at["Greater", columnName] = descriptive.at["Q3:75%", columnName] + descriptive.at["1.5rule", columnName]
            descriptive.at["Min", columnName] = df[columnName].min()
            descriptive.at["Max", columnName] = df[columnName].max()
            descriptive.at["Skew", columnName] = df[columnName].skew()
            descriptive.at["Kurtosis", columnName] = df[columnName].kurtosis()
            descriptive.at["Var", columnName] = df[columnName].var()
            descriptive.at["Std", columnName] = df[columnName].std()

        return descriptive

    @staticmethod
    def freqTable(columnName, df):
        freqTable = pd.DataFrame(columns=["Unique_values", "Frequency", "Relative_Frequency", "Cumulative"])
        freqTable["Unique_values"] = df[columnName].value_counts().index
        freqTable["Frequency"] = df[columnName].value_counts().values
        freqTable["Relative_Frequency"] = freqTable["Frequency"] / len(df)
        freqTable["Cumulative"] = freqTable["Relative_Frequency"].cumsum()
        return freqTable

    def find_outlier(self, descriptive, quan):
        lesser = []
        greater = []
        
        # Find columns with outliers
        for columnName in quan:
            if descriptive.at["Min", columnName] < descriptive.at["Lesser", columnName]:
                lesser.append(columnName)
            if descriptive.at["Max", columnName] > descriptive.at["Greater", columnName]:
                greater.append(columnName)
        return lesser, greater

    def replace_outlier(self, descriptive, quan, df):
        lesser, greater = self.find_outlier(descriptive, quan)
        
        for columnName in lesser:
            df.loc[df[columnName] < descriptive.at["Lesser", columnName], columnName] = descriptive.at["Lesser", columnName]
        for columnName in greater:
            df.loc[df[columnName] > descriptive.at["Greater", columnName], columnName] = descriptive.at["Greater", columnName]
        
        return df
