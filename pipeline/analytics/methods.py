import pandas as pd
import numpy as np
from scipy.stats import t


class Analysis:
    def __init__(self):
        self.data = None

    def calcular_probabilidade(self, df):
        """
        Calcula a probabilidade do próximo candle fechar em alta ou baixa, com base nos dados históricos de preços.
        """
        df['Returns'] = df['close'].pct_change()
        returns_dropna = df['Returns'].dropna()
        df_params = t.fit(returns_dropna)
        prob_higher = 1 - t.cdf(0, df_params[0], df_params[1], df_params[2])
        prob_lower = t.cdf(0, df_params[0], df_params[1], df_params[2])
        return prob_higher, prob_lower

    def identificar_suportes_resistencias(self, df, num_niveis=3):
        """
        Identifica os níveis de suporte e resistência com base nos topos e fundos históricos.
        """
        df['Local_Max'] = (df['close'].shift(2) < df['close'].shift(1)) & (df['close'].shift(1) > df['close']) & (df['close'] > df['close'].shift(-1)) & (df['close'].shift(-1) > df['close'].shift(-2))
        df['Local_Min'] = (df['close'].shift(2) > df['close'].shift(1)) & (df['close'].shift(1) < df['close']) & (df['close'] < df['close'].shift(-1)) & (df['close'].shift(-1) < df['close'].shift(-2))
        support_levels = df['close'][df['Local_Min']].values[-num_niveis:]
        resistance_levels = df['close'][df['Local_Max']].values[-num_niveis:]
        return support_levels, resistance_levels

    def identificar_linhas_tendencia(self, df):
        """
        Identifica as linhas de tendência (alta ou baixa) com base nos topos e fundos históricos.
        """
        if df['close'].iloc[-1] > df['close'].iloc[0]:
            return "alta"
        elif df['close'].iloc[-1] < df['close'].iloc[0]:
            return "baixa"
        else:
            return "lateral"

    def method_1(self, df):
        try:
            # Calcula variação percentual entre preços de fechamento
            df['Returns'] = df['close'].pct_change()
            volatility = df['Returns'].std()
            df['Moving_Average'] = df['close'].rolling(window=5).mean()

            # Calcula probabilidade de alta e baixa
            prob_higher, prob_lower = self.calcular_probabilidade(df.copy())
            
            # Identifica suportes e resistências
            support_levels, resistance_levels = self.identificar_suportes_resistencias(df.copy(), num_niveis=3)

            # Identifica tendência
            tendencia = self.identificar_linhas_tendencia(df.copy())
            
            # Ajuste das probabilidades com base na tendência e níveis de suporte/resistência
            if tendencia == "alta" and df['close'].iloc[-1] > df['Moving_Average'].iloc[-1]:
                prob_higher *= 1.1  # Incrementa se a tendência e preço atual estiverem em alta
            elif tendencia == "baixa" and df['close'].iloc[-1] < df['Moving_Average'].iloc[-1]:
                prob_lower *= 1.1  # Incrementa se a tendência e preço atual estiverem em baixa
            
            prob_higher /= (prob_higher + prob_lower)
            prob_lower /= (prob_higher + prob_lower)
            
            # Imprime resultados
            print(f'Volatilidade: {volatility:.4f}')
            print(f'Tendência: {tendencia}')
            print(f'Probabilidade de alta: {prob_higher:.2f}')
            print(f'Probabilidade de baixa: {prob_lower:.2f}')

            return {
                "volatilidade": float(volatility),
                "tendencia": tendencia,
                "probalidades": {
                    "alta": float(prob_higher),
                    "baixa": float(prob_lower),
                }
            }
        except Exception as e:
            print(f"\n ### ERROR CALCULATE METHOD 1 | ERROR: {e}")
            return None

    
    def method_2(self, data, value_default=4):
        """
        Retorna o sinal para a operação ("call", "put" ou "-") baseado na análise dos últimos candles.

        :param data: DataFrame com os dados dos últimos candles (100 candles).
        :param value_default: Período das médias móveis e outros cálculos (default 4).
        :return: "call", "put" ou "-" (sem sinal).
        """
        try:
            # Converter as colunas de datas para datetime
            data['from'] = pd.to_datetime(data['from'], format='%d/%m/%Y %H:%M:%S')
            data['at'] = pd.to_datetime(data['at'], format='%d/%m/%Y %H:%M:%S')
            
            # Calcular Média Móvel Simples (SMA)
            data['SMA_5'] = data['close'].rolling(window=5).mean()
            data['SMA_20'] = data['close'].rolling(window=value_default).mean()

            # Calcular Média Móvel Exponencial (EMA)
            data['EMA_5'] = data['close'].ewm(span=5, adjust=False).mean()
            data['EMA_20'] = data['close'].ewm(span=value_default, adjust=False).mean()

            # Calcular Suporte e Resistência
            data['resistencia'] = data['max'].rolling(window=value_default).max()
            data['suporte'] = data['min'].rolling(window=value_default).min()

            # Calcular os níveis de Fibonacci
            def fibonacci_levels(data, period=value_default):
                max_price = data['max'].rolling(window=period).max()
                min_price = data['min'].rolling(window=period).min()
                diff = max_price - min_price
                levels = {
                    'level_0': max_price,
                    'level_23_6': max_price - (0.236 * diff),
                    'level_38_2': max_price - (0.382 * diff),
                    'level_50': max_price - (0.5 * diff),
                    'level_61_8': max_price - (0.618 * diff),
                    'level_100': min_price
                }
                return pd.DataFrame(levels)

            fibonacci_levels_df = fibonacci_levels(data)
            data = pd.concat([data, fibonacci_levels_df], axis=1)

            # Agora, vamos definir a lógica do sinal para CALL ou PUT
            print("\n >>> Agora, vamos definir a lógica do sinal para CALL ou PUT")
            sinal = "-"

            # Verificar tendência de alta ou baixa com base nas médias móveis
            print("\n >>> Verificar tendência de alta ou baixa com base nas médias móveis")
            if data['SMA_5'].iloc[-1] > data['SMA_20'].iloc[-1]:  # Tendência de alta
                sinal = "call"
            elif data['SMA_5'].iloc[-1] < data['SMA_20'].iloc[-1]:  # Tendência de baixa
                sinal = "put"

            # Caso o preço esteja perto de níveis importantes (suporte/resistência)
            print("\n >>> Níveis importantes (suporte/resistência)")
            if data['close'].iloc[-1] < data['suporte'].iloc[-1] * 1.01:  # Preço muito perto do suporte
                sinal = "-"  # Não entrar em operação, o mercado está em uma região de suporte
            elif data['close'].iloc[-1] > data['resistencia'].iloc[-1] * 0.99:  # Preço muito perto da resistência
                sinal = "-"  # Não entrar em operação, o mercado está em uma região de resistência

            print(f"\n >>> SINAL ENVIADO | {sinal}")

            return sinal
        
        except Exception as e:
            print(f"\n ### ERROR METHOD 2 | ERROR: {e}")
            return None

    # # Exemplo de como usar a função
    # # Carregar os últimos 100 candles
    # data = pd.read_csv('data.csv', parse_dates=['from', 'at'])

    # # Converter as colunas de datas para datetime
    # data['from'] = pd.to_datetime(data['from'], format='%d/%m/%Y %H:%M:%S')
    # data['at'] = pd.to_datetime(data['at'], format='%d/%m/%Y %H:%M:%S')

    # # Obter os últimos 100 candles
    # data_last_100 = data.tail(100)

    # # Chamar a função para obter o sinal
    # sinal = method_2(data_last_100)
    # print(f'O sinal gerado para o próximo candle é: {sinal}')
    # return sinal





if __name__ == "__main__":
    df = pd.read_csv('data.csv', encoding='latin-1')
    Analysis().method_1(df)
