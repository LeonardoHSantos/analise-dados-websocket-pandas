import json
import websocket

from broker.wss.operations_wss import OperationsWSS
from pipeline.prepare_data.expirations import check_datetime_to_M5

class WebSocketClient:
    def __init__(self, url_wss):
        self.url_wss = url_wss
        self.status_wss = False
        self.status_msg = False
        self.candles = None
        self.message_wss = None
        self.last_msg_to_operation = None
        self.OP = None

        self.wss = websocket.WebSocketApp(
            url=url_wss,
            on_message=self.on_message,
            on_open=self.on_open,
            on_close=self.on_close,
            # on_error=self.on_error
        )
    
    def on_message(self, message):
        self.status_msg = True
        self.message_wss = json.loads(message)

        if self.message_wss["name"] != "timeSync":
            print("\n >>> new message")
            print(self.message_wss.keys())
            print(self.message_wss)
        

        if self.message_wss["name"] == "timeSync":
            if check_datetime_to_M5(timestamp_ms=self.message_wss["msg"]):
                msg_get_candles = self.OP.get_candles( active = "EURUSD-OTC", timeframe = '5M', count = 100, keep_connection = False)
                print(msg_get_candles)
                self.wss.send(msg_get_candles)

        if self.message_wss["name"] == "candles" and self.message_wss["msg"]["candles"]:
            self.candles = self.message_wss
            check = self.OP.check_model_1(candles=self.message_wss)
            if check is not None and self.last_msg_to_operation != check:
                self.wss.send(check)
                self.last_msg_to_operation = check
                self.OP.update_log_json(data=check)
            
    
    def on_open(self):
        self.status_wss = True
        self.OP = OperationsWSS(obj_wss=self.wss)
        print(f" ### CONNECTION OPEN WEBSOCKET ### | STATUS WSS: {self.status_wss}")
    
    def on_close(self):
        self.wss.close()
        self.status_wss = False
        self.status_msg = False
        print(f" ### CONNECTION CLOSED WEBSOCKET ### | STATUS WSS: {self.status_wss} | STATUS MSg: {self.status_msg}")