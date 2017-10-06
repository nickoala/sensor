from sensor.HTU21D import HTU21D
from flask import Flask, Response, json

app = Flask(__name__)

@app.route("/htu21d")
def read_htu21d():
    htu = HTU21D(1, 0x40)
    h,t = htu.all()

    d = {'humidity': h.RH,
         'temperature': t.C}

    return Response(json.dumps(d), mimetype='application/json')
