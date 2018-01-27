# Home Assistant Integration

[Home Assistant](https://home-assistant.io) is an open-source home automation
platform. This page describes how I integrate various components into it. Home
Assistant version is **0.61.1**, released on January 16, 2018.

## Installation

```
sudo apt-get update
sudo apt-get upgrade
sudo pip3 install homeassistant

hass     # start Home Assistant webserver
```

The first time running `hass` takes a little long because it has to install a
few more Python packages. After a while, you should be able to access it by
pointing your browser to `http://<Raspi's IP address>:8123`

Sensor integration is done by modifying the file `/home/pi/.homeassistant/configuration.yaml`

## DS18B20 as [Command Line Sensor](https://home-assistant.io/components/sensor.command_line/)

Home Assistant has this concept of a Command Line Sensor. It allows you to
integrate any type of sensor as long as the sensor's data can be read from the
command line.

The script [temperature.py](./temperature.py) displays the reading of DS18B20.
It can serve as a Command Line Sensor. Add these lines to `configuration.yaml`:

```
sensor:
  - platform: command_line
    name: DS18B20 Sensor
    command: python3 /path/to/temperature.py
    value_template: '{{ value | round(1) }}'
    unit_of_measurement: "°C"
    scan_interval: 3
```

## HTU21D as [RESTful Sensor](https://home-assistant.io/components/sensor.rest/)

If a sensor is remote, expose it as a REST service.

The script [rest_sensor.py](./rest_sensor.py) is a simple Flask server which
returns HTU21D's humidity and temperature readings in JSON format. In my case,
the HTU21D sensor is local and not actually remote, but it illustrates the
principle nonetheless.

First, install [Flask](http://flask.pocoo.org) web framework:

```
sudo pip3 install Flask
```

Then, run `rest_sensor.py` as a Flask server at default port 5000:

```
export FLASK_APP=/path/to/rest_sensor.py
python3 -m flask run --host=0.0.0.0
```

The following lines in `configuration.yaml` tells Home Assistant to query the
REST service to obtain the humidity:

```
sensor:
  - platform: rest
    name: HTU21D Sensor
    resource: http://127.0.0.1:5000/htu21d
    value_template: '{{ value_json.humidity | round(1) }}'
    unit_of_measurement: "%"
    scan_interval: 5
```

## PIR motion as [GPIO Binary Sensor](https://home-assistant.io/components/binary_sensor.rpi_gpio/)

A PIR motion sensor is binary and is read by GPIO directly:

```
binary_sensor:
  - platform: rpi_gpio
    ports:
      18: PIR Bedroom    # BCM pin numbering
```

## [TP-Link LB100](https://home-assistant.io/components/light.tplink/) Smart Wi-Fi LED Bulb

```
light:
  - platform: tplink
    name: Book Room Light
    host: 192.168.0.103
```

## [TP-Link HS100](https://home-assistant.io/components/switch.tplink/) Smart Wi-Fi Plug

```
switch:
  - platform: tplink
    name: Fan Plug
    host: 192.168.0.104
```

## [Telegram Bot](https://home-assistant.io/components/notify.telegram/)

```
telegram_bot:
  - platform: polling
    api_key: ..........TOKEN..........
    allowed_chat_ids:
      - 999999999

notify:
  - name: TelegramBot
    platform: telegram
    chat_id: 999999999
```

## Comment out default automation file

Find the following line, **comment it out** because we are going to add
automation sections in file:

```
# automation: !include automations.yaml
```

#### For everything below, adjust `entity_id` accordingly

## Automation: Turn ON/OFF Smart Plug depending on Temperature

```
automation:
  - alias: Turn ON fan if too hot
    trigger:
      platform: numeric_state
      entity_id: sensor.ds18b20_sensor
      above: 32
    action:
      service: switch.turn_on
      entity_id: switch.fan_plug

  - alias: Turn OFF fan if too cool
    trigger:
      platform: numeric_state
      entity_id: sensor.ds18b20_sensor
      below: 31
    action:
      service: switch.turn_off
      entity_id: switch.fan_plug
```

## Automation: Turn ON/OFF Smart Bulb depending on Human Presense

```
automation:
  - alias: Turn ON light if somebody
    trigger:
      platform: state
      entity_id: binary_sensor.pir_bedroom
      to: 'on'
    action:
      service: light.turn_on
      entity_id: light.book_room_light

  - alias: Turn OFF light if nobody
    trigger:
      platform: state
      entity_id: binary_sensor.pir_bedroom
      to: 'off'
    action:
      service: light.turn_off
      entity_id: light.book_room_light
```

## Automation: Send a Telegram message when Someone is Home

```
automation:
  - alias: Notify me if someone comes home
    trigger:
      platform: state
      entity_id: binary_sensor.pir_bedroom
      to: 'on'
    action:
      service: notify.TelegramBot
      data:
        message: 'Somebody is home'
```

## Automation: Refresh LCD Display on State Changes

The script [lcd_display.py](./lcd_display.py) accepts a temperature and humidity
as command line arguments, and displays them on an LCD1602. It can be exposed as
a [Shell Command](https://home-assistant.io/components/shell_command/) service,
and triggered on HomeAssistant startup and on temperature or humidity changes,
effectively keeping the LCD display up-to-date. Note the `-` in front of
`platform` for the refreshing trigger. This is how you specify multiple triggers
for an automation rule.

```
shell_command:
  lcd_display: 'python3 /path/to/lcd_display.py \
                        {{ states.sensor.ds18b20_sensor.state }} \
                        {{ states.sensor.htu21d_sensor.state }}'

automation:
  - alias: Refresh LCD display
    trigger:
      - platform: state
        entity_id: sensor.ds18b20_sensor
      - platform: state
        entity_id: sensor.htu21d_sensor
    action:
      service: shell_command.lcd_display

  - alias: LCD display on startup
    trigger:
      platform: homeassistant
      event: start
    action:
      service: shell_command.lcd_display
```

## [Sun Trigger](https://home-assistant.io/docs/automation/trigger/#sun-trigger) and [Time Trigger](https://home-assistant.io/docs/automation/trigger/#time-trigger)

## [Raspberry Pi Camera](https://home-assistant.io/components/camera.rpi_camera/)

```
camera:
  - platform: rpi_camera
    file_path: /path/to/temporary.jpg
```

## Run on Startup

Remember, there are two things to run: the **Home Assistant** platform itself, and the
**HTU21D REST sensor service**. The latter should be run first, because the former
depends on it.

To run programs on startup, we create systemd services.

In directory `/lib/systemd/system`, create a file `restsensor.service` and
insert the following contents:

```
[Unit]
Description=RESTful Sensor
After=network.target

[Service]
Environment=FLASK_APP=/path/to/rest_sensor.py
ExecStart=/usr/bin/python3 -m flask run --host=0.0.0.0
User=pi

[Install]
WantedBy=multi-user.target
```

Also in directory `/lib/systemd/system`, create another file
`homeassistant.service` and insert the following contents:

```
[Unit]
Description=Home Assistant
After=network.target restsensor.service

[Service]
ExecStart=/usr/local/bin/hass
User=pi

[Install]
WantedBy=multi-user.target
```

Then, you can control the services in standardized ways. I use
`homeassistant.service` as examples. The same applies to `restsensor.service`:

To run it manually: `sudo systemctl start homeassistant.service`  
To stop it manually: `sudo systemctl stop homeassistant.service`  
To check its status: `sudo systemctl status homeassistant.service`  
To make it run on startup: `sudo systemctl enable homeassistant.service`  
To stop it from running on startup: `sudo systemctl disable homeassistant.service`

## Dynamic DNS and SSL Certificate

This [blog post](https://home-assistant.io/blog/2015/12/13/setup-encryption-using-lets-encrypt/)
tells you how to set up Dynamic DNS and SSL certificate. Its intructions are not
tailored to Raspberry Pi and seem a little out-of-date. I summarize my
experiences below:

1. Obtain a domain on **[Duck DNS](https://www.duckdns.org)**

2. Follow the **[installation instructions](https://www.duckdns.org/install.jsp)**.
   Choose **pi** for Raspberry Pi-specific instructions. Basically, this is what
   you do:
   - Create a shell script which updates the IP address of your Duck DNS domain
   - Set up a cron job to run the shell script every 5 minutes

   After this, Dynamic DNS is completely set up. You have your own domain, and
   you can use that domain to reach your home's router. Next, we set up an SSL
   certificate to encrypt all HTTP communications.

3. We use a software utility called **[Certbot](https://certbot.eff.org)** to
   obtain a 90-day SSL certificate from **[Let's Encrypt](https://letsencrypt.org/how-it-works/)**.

   During the process, Certbot will spin up a temporary webserver on Raspberry
   Pi's port 80 for Let's Encrypt to verify the control of domain. Normally,
   incoming traffic cannot get through the router, unless a port-forward exists.

   So, set up a **port-forward `Router port 80` → `Pi Port 80`**.

   Install certbot and use it to obtain a certificate:

   ```
   sudo apt-get install certbot
   sudo certbot certonly --standalone -d yourdomain.duckdns.org
   ```

   Resulting contents are put in the directory `/etc/letsencrypt`.
   Certificate-related files are in `/etc/letsencrypt/live`. Most stuff there
   are accessible by root only. To be used by Home Assistant, their accessibility
   has to be loosen:

   ```
   cd /etc/letsencrypt
   sudo chmod +rx live
   sudo chmod +rx archive
   ```

   The SSL certificate is now ready.

4. Tell Home Assistant about where the certificate-related files are. Insert
   the following lines into `configuration.yaml`, which include a password to
   protect the website:

   ```
   http:
     api_password: raspberry
     ssl_certificate: /etc/letsencrypt/live/yourdomain.duckdns.org/fullchain.pem
     ssl_key: /etc/letsencrypt/live/yourdomain.duckdns.org/privkey.pem
     base_url: yourdomain.duckdns.org
   ```

   Finally, we are ready to access Home Assistant on **HTTPS**. HTTPS runs on
   port 443, while Home Assistant starts on port 8123. So, modify the router's
   **port-forward `Router port 443` → `Pi Port 8123`**.

On the browser, remember to explicitly **force the communication protocol by
typing `https://` before the domain**. Otherwise, the browser may default to
contacting port 80 (HTTP), which should be blocked by the router.

## [Python Remote API](https://home-assistant.io/developers/python_api/)

```
import homeassistant.remote as remote

api = remote.API('yourdomain.duckdns.org', '***password***', port=443, use_ssl=True)

remote.validate_api(api)
remote.get_config(api)

remote.get_state(api, 'sensor.ds18b20_sensor')

remote.call_service(api, 'light', 'turn_on')
remote.call_service(api, 'light', 'turn_off')
remote.call_service(api, 'light', 'turn_on', {'entity_id': 'light.book_room_light'})
remote.call_service(api, 'light', 'toggle', {'entity_id': 'light.book_room_light'})
```
