import json
import numpy as np
import pandas as pd

class PrepareData:
    def __init__(self):
        self.data = None
    
    def prepare_candles_to_dataframe(self, data):
        df = pd.DataFrame(data)

        df["status_candle"] = 'sem mov'

        df['from'] = pd.to_datetime(df['from'], unit='s')
        df['at'] = pd.to_datetime(df['at'], unit='ns')

        df['from'] = df['from'].dt.tz_localize('UTC').dt.tz_convert('America/Sao_Paulo')
        df['at'] = df['at'].dt.tz_localize('UTC').dt.tz_convert('America/Sao_Paulo')

        df['from'] = df['from'].dt.strftime('%d/%m/%Y %H:%M:%S')
        df['at'] = df['at'].dt.strftime('%d/%m/%Y %H:%M:%S')

        df['status_candle'] = np.where(
                df['close'] > df['open'], 'alta',
                np.where(df['close'] < df['open'], 'baixa',
                'sem mov')
            )
        print(df)
        return df