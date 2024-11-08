import os
import json
import threading
from time import sleep

from broker.http.auth import auth_broker
from broker.wss.client import WebSocketClient

# from broker.channels.channels import ExpitationsCandles, ChannelsWSS
# from pipeline.analytics.methods import Analysis
# from pipeline.prepare_data.expirations import check_datetime_to_M5

from base import URL_WSS
from broker.wss.operations_wss import OperationsWSS
from pipeline.prepare_data.prepareData import PrepareData



class ProcessAPI:

    def __init__(self):
        self.obj_wss = None
        self.threading_wss = None
        self.threading_process = None
        self.control_bool_api = False
        self.request_id_temp = None

    def connect_wss(self, identifier, password):

        auth = auth_broker(
            identifier=identifier,
            password=password
        )
        print(f"AUTH: {auth}")
        if auth == None:
            return {"auth_status": False}
        else:
            self.obj_wss = WebSocketClient(url_wss=URL_WSS)
            self.threading_wss = threading.Thread(target=self.obj_wss.wss.run_forever).start()
            msg_SSID = dict(name="ssid", msg=auth, request_id="")
            msg_SSID = json.dumps(msg_SSID).replace("'", '"')
            print(f"MSG SSID: {msg_SSID}")
            while True:
                if self.obj_wss.status_msg != False:
                    break
            
            self.obj_wss.wss.send(msg_SSID)
            return {"auth_status": True}
    
    def disconnect_wss(self):
        self.obj_wss.on_close()

    
    def get_candles(self, name_plotly, active, timeframe, count, keep_connection):

        print("\n\n Aguardando 4 segundo para a conexão com WebSocket... \n\n")
        sleep(4)
        OP = OperationsWSS(self.obj_wss)
        msg = OP.get_candles( active = active, timeframe = timeframe, count = count, keep_connection = keep_connection)
        self.obj_wss.wss.send(msg)

        print("\n\n Mensagem enviada... \n\n")
        print("\n\n Aguerdando a resposta... \n\n")
        sleep(3)

        candles = PrepareData().prepare_candles_to_dataframe( data = self.obj_wss.candles["msg"]["candles"] )
        print(candles)
        candles.to_csv(f"{name_plotly}.csv")

        self.obj_wss.on_close()
        print("\n\n Processo finalizado! \n\n")

    

if __name__ == "__main__":
    app = ProcessAPI()
    username = os.getenv("USERNAME_BROKER")
    password = os.getenv("PASSWORD_BROKER")
    print(f""""
        username: {username}
        password: {password}
    """)
    app.connect_wss(identifier=username, password=password)
    # app.get_candles( name_plotly="EURUSD-5M", active = "EURUSD", timeframe = '5M', count = 250, keep_connection = False )
