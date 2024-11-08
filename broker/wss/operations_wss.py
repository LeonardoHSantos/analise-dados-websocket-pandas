import json
from time import sleep
from dateutil import tz
from datetime import datetime
from broker.channels.channels import ExpitationsCandles, ChannelsWSS
from pipeline.prepare_data.prepareData import PrepareData
from pipeline.analytics.methods import Analysis


class OperationsWSS:
    def __init__(self, obj_wss):
        self.obj_wss = obj_wss
        self.threading_wss = None
        self.threading_process = None
        self.control_bool_api = False
        self.request_id_temp = None
    
    def check_status_candles(self):
        while True:
            if self.obj_wss.candles is not None:
                break
        return self.obj_wss.candles

    def get_candles(self, active, timeframe, count, keep_connection: bool = True):

        print("\n ### COMUNICAÇÃO COM WEBSOCKET ESTABELECIDA ### \n")

        expiration=ExpitationsCandles().timestamp_now()
        msg_get_candles = ChannelsWSS.get_candles(
            estrategia="M5 Turbo", active=active, timeframe=timeframe, expiration=expiration, count=count
        )

        if msg_get_candles is not None:
            print("\n\n **************** msg_get_candles **************** ")
            return msg_get_candles
        
    def check_model_1(self, candles):
            
            # candles = self.check_status_candles()
            candles = PrepareData().prepare_candles_to_dataframe( data = candles["msg"]["candles"] )
            print(candles)
            print(candles.info())

            # data_to_IA = candles.to_json(orient='index')
            # print(data_to_IA)

            analise_api = Analysis()
            sinal = analise_api.method_1(df=candles)

            print(f"\n\n ----------------------------- SINAL ----------------------------- ")
            print(sinal)
            if sinal is not None:

                # if sinal["diferenca_probabilidades"] < 0.05:
                if sinal["probalidades"]["alta"] >= 0.50:
                    return self.open_position(to="call", sinal=sinal)
                    
                elif sinal["probalidades"]["baixa"] >= 0.50:
                    return self.open_position(to="put", sinal=sinal)
                
                else:
                    return None
    
    def check_model_2(self, candles):
            
            # candles = self.check_status_candles()
            candles = PrepareData().prepare_candles_to_dataframe( data = candles["msg"]["candles"] )
            print(candles)
            print(candles.info())

            # data_to_IA = candles.to_json(orient='index')
            # print(data_to_IA)

            analise_api = Analysis()
            sinal = analise_api.method_2(df=candles)
            if sinal != "-":
                return self.open_position(to=sinal)
    
    def open_position(self, to, sinal):
        msg = ChannelsWSS.open_position_M5(to=to, sinal=sinal)
        print(msg)
        return msg
    
    def update_log_json(self, data):
        try:
            dt = datetime.now(tz=tz.gettz("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M:%S")

            with open("datalogs.json", "r") as f:
                file = f.read()
                try:
                    file = json.loads(file)
                except:
                    file = {"data": []}
            
            file["data"].append({
                "datetime": dt, "data": data
            })

            with open("datalogs.json", "w") as f:
                file = f.write(json.dumps(file, indent=4))
            
        except Exception as e:
            print(f"\n\n ERROR SAVE DATALOGS | ERROR: {e}")