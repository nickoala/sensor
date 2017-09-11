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

"""
export FLASK_APP=rest_sensor.py
python3 -m flask run --host=0.0.0.0

Check locally:
  curl -X GET http://127.0.0.1:5000/read

In configuration.yaml:::::

sensor:
  - platform: rest
    name: HTU21D Sensor
    resource: http://127.0.0.1:5000/read
    value_template: '{{ value_json.humidity | round(1) }}'
    unit_of_measurement: "%"
    scan_interval: 5
"""
