import json
from dateutil import tz
from datetime import datetime, timedelta

from active_code import ACTIVE_CODE, TIMEFRAMES_NAME, TIMESTAMP_EXPIRATIONS_M5

class ExpitationsCandles:
    def __init__(self):
        self.datetime = None

    def datetime_now(self):
        self.datetime = datetime.now(tz=tz.gettz("GMT"))
        return self.datetime
    
    def timestamp_now(self):
        return int(datetime.now(tz=tz.gettz("GMT")).timestamp())

    def expiration_M5(self):
        self.datetime = self.datetime_now()
        minute = TIMESTAMP_EXPIRATIONS_M5[ self.datetime.minute ]
        self.datetime = self.datetime.replace(microsecond = 0, second = 0, minute = minute)
        print(minute, "   <<<<<<<< minute")
        if minute >= 54:
            self.datetime + timedelta(hours=2)
            self.datetime.replace(minute=minute)
        else:
            self.datetime

        expiration_timestemp = int(self.datetime.timestamp())
        return {
            "dt": self.datetime.strftime("%d/%m/%Y %H:%M:%S"),
            "tmt": expiration_timestemp,
        }

class ChannelsWSS:

    def timesTemp_converter ():
        timestamp = int(datetime.now().timestamp())
        hora = datetime.strptime(datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        hora = hora.replace(tzinfo=tz.gettz('GMT'))
        return str(hora.astimezone(tz.gettz('America/Sao Paulo')))[:-6]

    def get_candles(estrategia, active, timeframe, expiration, count):
        try:
            name = 'sendMessage'
          
            message = {
                'name': 'get-candles',
                'version': '2.0',
                'body': {
                    'active_id': int(ACTIVE_CODE[active]),
                    'size': int(TIMEFRAMES_NAME[timeframe]),
                    'to': int(expiration),
                    'count': int(count),
                }
            }
            request_id = f"GET CANDLES - {estrategia} - {active} - {timeframe}"
            msg_GET_CANDLES = dict(name=name, msg=message, request_id=request_id)
            msg_GET_CANDLES = json.dumps(msg_GET_CANDLES).replace("'", '"')
            return msg_GET_CANDLES
        except Exception as e:
            print(f"\n ### ERROR CREATE GET CANDLES PROCESS | ERROR: {e} ### \n")
            return None

    def open_position_M5(to, sinal):

        expiration = ExpitationsCandles().expiration_M5()

        print(f"""
            >>>> dt: {expiration["dt"]}
            >>>> tmt: {expiration["tmt"]}
        """)
        try:
            sinal = json.loads(sinal)
            request_id = f"volatilidade: {sinal["volatilidade"]} | tendencia: {sinal["tendencia"]} | probalidadesalta: {sinal["volatilidade"]["alta"]} | probalidades-baixa: {sinal["probalidades"]["baixa"]}"
        except:
            request_id = "-"
        
        msg = {
            "name": "sendMessage",
            "request_id": request_id,
            "msg": {
                "name": "binary-options.open-option",
                "version": "2.0",
                "body": {
                    "user_balance_id": 194260479,
                    "active_id": 76,
                    "direction": to,
                    "expired": expiration["tmt"],
                    "price": 1,
                    "profit_percent": 0,
                    "option_type_id": 3
                }
            }
        }
        return json.dumps(msg).replace("'", '"')


