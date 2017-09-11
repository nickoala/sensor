from sensor.HTU21D import HTU21D
from flask import Flask, Response, json

app = Flask(__name__)

@app.route("/read")
def hello():
    htu = HTU21D(1, 0x40)
    h,t = htu.all()

    d = {'humidity': h.RH,
         'temperature': t.C}

    return Response(json.dumps(d), mimetype='application/json')
