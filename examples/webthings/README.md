# WebThings Integration

Background:

- [Web Thing API](https://iot.mozilla.org/wot/)
- [WoT Capability Schemas](https://iot.mozilla.org/schemas/)
- [WebThings Framework](https://iot.mozilla.org/framework/)
- [Python Library](https://github.com/mozilla-iot/webthing-python)

Install:

```
sudo pip3 install webthing
```

Systemd service file in `/lib/systemd/system/`:

```
[Unit]
Description=WebThing Server
After=network.target

[Service]
ExecStart=python3 /PATH/TO/SCRIPT
User=pi

[Install]
WantedBy=multi-user.target
```
