# Home Assistant Integration

[Home Assistant](https://home-assistant.io) is an open-source home automation
platform. This page describes how I integrate various components into it. Home
Assistant version is **0.95.4**, released on June 29, 2019.

## Installation

```
sudo apt-get update
sudo apt-get dist-upgrade

### Home Assistant needs Python 3.6 or later ###

sudo apt-get install libssl-dev openssl libreadline-dev libffi-dev
wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz
tar zxf Python-3.7.4.tgz
cd Python-3.7.4
./configure
make -j4
sudo make install

### Install Home Assistant ###

sudo pip3 install pip wheel --upgrade
sudo pip3 install homeassistant

hass     # start Home Assistant webserver
```

The first time running `hass` takes a while because it has to install a few more
Python packages. After a while, you should be able to access it by pointing your
browser to `http://<Raspi's IP address>:8123`

If anything fails to download, try to `wget` it manually, then install it
locally:

```
wget zzzzzz.whl
sudo pip3 install zzzzzz.whl
```

Sensor integration is done by modifying the file `/home/pi/.homeassistant/configuration.yaml`

At any time, you may check the validity of the config file with:

```
hass --script check_config --info all
```

## Remove unwanted icons

```
homeassistant:
  customize:
    person.pi:
      hidden: true
    sun.sun:
      hidden: true
    weather.home:
      hidden: true
```

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

## [TP-Link Smart Home Devices](https://home-assistant.io/components/tplink/)

I have tried **LB100** Smart LED Bulb and **HS100** Smart Plug.

```
tplink:
  discovery: false
  switch:
    - host: 192.168.0.103
  light:
    - host: 192.168.0.104
```

## Automation: Turn ON/OFF Smart Plug depending on Temperature

First, comment out the default include. We are going to put the automation
section in the same file:

```
# automation: !include automations.yaml
```

**For everything below, adjust `entity_id` accordingly.**

```
automation:
  - alias: Turn ON fan if too hot
    trigger:
      platform: numeric_state
      entity_id: sensor.ds18b20_sensor
      above: 31.5
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

## Automation: Send a [Telegram](https://home-assistant.io/components/notify.telegram/) message when Temperature gets too hot

```
telegram_bot:
  - platform: polling
    api_key: ..........TOKEN..........
    allowed_chat_ids:
      - 999999999

notify:
  - name: telegram
    platform: telegram
    chat_id: 999999999

automation:
  - alias: Notify me if too hot
    trigger:
      platform: numeric_state
      entity_id: sensor.ds18b20_sensor
      above: 32
    action:
      service: notify.telegram
      data:
        message: "\U0001f525"  # Fire emoji
```

## [Sun Trigger](https://home-assistant.io/docs/automation/trigger/#sun-trigger) and [Time Trigger](https://home-assistant.io/docs/automation/trigger/#time-trigger)

## Run on Startup

To run programs on startup, we create systemd services.

In directory `/lib/systemd/system`, create a file `homeassistant.service` and
insert the following contents:

```
[Unit]
Description=Home Assistant
After=network.target

[Service]
ExecStart=/usr/local/bin/hass
User=pi

[Install]
WantedBy=multi-user.target
```

Then, you can control the service using `systemctl`:

To run it manually: `sudo systemctl start homeassistant.service`  
To stop it manually: `sudo systemctl stop homeassistant.service`  
To check its status: `sudo systemctl status homeassistant.service`  
To make it run on startup: `sudo systemctl enable homeassistant.service`  
To stop it from running on startup: `sudo systemctl disable homeassistant.service`

## Dynamic DNS and SSL Certificate

This [blog post](https://home-assistant.io/blog/2015/12/13/setup-encryption-using-lets-encrypt/)
tells you how to set up Dynamic DNS and SSL certificate. Its instructions are not
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
   are accessible by root only. To be used by Home Assistant, permission has to
   be loosen:

   ```
   cd /etc/letsencrypt
   sudo chmod +rx live archive
   ```

   The SSL certificate is now ready.

4. Tell Home Assistant about where the certificate-related files are. Insert
   the following lines into `configuration.yaml`, which include a password to
   protect the website:

   ```
   http:
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
