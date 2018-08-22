# openHAB Integration

Platform: Raspbian Stretch

## Install latest Java 8 version

OpenHAB requires Java 8 and recommends **at least revision "101"**. Check your
version:

```
$ java -version
```

Raspbian Stretch likely comes with a lower revision than "101". We need to
install a newer JDK. Instructions below are taken from
[ribasco](https://gist.github.com/ribasco/fff7d30b31807eb02b32bcf35164f11f).

1. Create a file `key.txt` and insert the following lines of text:

```
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: SKS 1.1.5
Comment: Hostname: keyserver.ubuntu.com

mI0ES9/P3AEEAPbI+9BwCbJucuC78iUeOPKl/HjAXGV49FGat0PcwfDd69MVp6zUtIMbLgkU
OxIlhiEkDmlYkwWVS8qy276hNg9YKZP37ut5+GPObuS6ZWLpwwNus5PhLvqeGawVJ/obu7d7
gM8mBWTgvk0ErnZDaqaU2OZtHataxbdeW8qH/9FJABEBAAG0DUxhdW5jaHBhZCBWTEOImwQQ
AQIABgUCVsN4HQAKCRAEC6TrO3+B2tJkA/jM3b7OysTwptY7P75sOnIu+nXLPlzvja7qH7Wn
A23itdSker6JmyJrlQeQZu7b9x2nFeskNYlnhCp9mUGu/kbAKOx246pBtlaipkZdGmL4qXBi
+bi6+5Rw2AGgKndhXdEjMxx6aDPq3dftFXS68HyBM3HFSJlf7SmMeJCkhNRwiLYEEwECACAF
Akvfz9wCGwMGCwkIBwMCBBUCCAMEFgIDAQIeAQIXgAAKCRDCUYJI7qFIhucGBADQnY4V1xKT
1Gz+3ERly+nBb61BSqRx6KUgvTSEPasSVZVCtjY5MwghYU8T0h1PCx2qSir4nt3vpZL1luW2
xTdyLkFCrbbIAZEHtmjXRgQu3VUcSkgHMdn46j/7N9qtZUcXQ0TOsZUJRANY/eHsBvUg1cBm
3RnCeN4C8QZrir1CeA==
=CziK
-----END PGP PUBLIC KEY BLOCK-----
```

2. Add the key:

```
$ sudo apt-key add key.txt
```

3. Add the repository. Create a file `webupd8team-java.list` in the directory
   `/etc/apt/sources.list.d/`, and insert the following lines:

```
deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main
deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main
```

4. Tell `apt-get` about the new repository and install:

```
$ sudo apt-get update
$ sudo apt-get install oracle-java8-installer
```

5. Verify:

```
$ java -version
```

## Install openHAB 2

Steps are similar to above. Instructions are summarized from [openHAB
installation guide](https://www.openhab.org/docs/installation/linux.html).

1. Add the key:

```
$ wget -qO - 'https://bintray.com/user/downloadSubjectPublicKey?username=openhab' | sudo apt-key add -
$ sudo apt-get install apt-transport-https
```

2. Add the repository:

```
$ echo 'deb https://dl.bintray.com/openhab/apt-repo2 stable main' | sudo tee /etc/apt/sources.list.d/openhab2.list
```

3. Install:

```
$ sudo apt-get update
$ sudo apt-get install openhab2
```

4. Start openHAB and install the Standard setup:

```
$ sudo systemctl start openhab2.service
```

The first start may take a while. After a while, you should be able to access it
at: `http://<IP-address>:8080`

**Choose the Standard setup**.

### How to monitor?

Logs are stored in the directory `/var/log/openhab2/`. You can follow openHAB's
activities by monitoring these files:

```
$ tail -f /var/log/openhab2/openhab.log
$ tail -f /var/log/openhab2/events.log
```

## Configuration workflow

Integrating a sensor or appliance to openHAB follows a common workflow.

1. Use **Paper UI** to add the appropriate *binding*

2. Define a *thing* in a `*.things` file in `/etc/openhab2/things/`. A thing
   represents a physical entity, e.g. a temperature sensor, a light bulb.

3. Define an *item* in a `*.items` file in `/etc/openhab2/items/`. An item
   represents an element on the user interface, and is usually linked to a thing's
   *channel*.

4. Optionally define some *rules* in a `*.rules` file in `/etc/openhab2/rules/`.
   Rules govern how the system reacts to changes. They are the "smart" of the
   system.

5. Put items in a `*.sitemap` file in `/etc/openhab2/sitemaps/`. A *sitemap*
   defines how items are laid out on the user interface.

## DS18B20 on [Exec Binding](https://www.openhab.org/addons/bindings/exec/)

Paper UI → Add-ons → Install **Exec Binding** and **RegEx Transformation**

The Exec binding extracts information by executing a command. So, we make a
[Python script](./temperature.py) that prints out the temperature. Make sure the
script can be run by user `openhab`:

```
$ sudo -u openhab python3 temperature.py
```

#### things
```
Thing exec:command:ds18 [ command="/usr/bin/python3 /home/pi/smarthome/temperature.py", interval=5, timeout=3 ]
```

#### items
```
String TemperatureStr { channel="exec:command:ds18:output" }
Number Temperature "Temperature [%.1f °C]" <temperature>
```

#### rules
```
rule "Convert temperature string to number"
when
    Item TemperatureStr changed
then
    val newValue = transform("REGEX", "(\\d*.\\d*).*", TemperatureStr.state.toString)
    Temperature.postUpdate(newValue)
end
```

#### home.sitemap
```
sitemap home label="Sham Shui Po" {
    Frame {
        Text item=Temperature
    }
}
```

## SHT20 on [Exec Binding](https://www.openhab.org/addons/bindings/exec/)

I leave it as an exercise to make a script that prints out humidity.

If user `openhab` has trouble running the script, it is likely because he is not
included in the appropriate groups. Try:

```
sudo usermod -aG gpio,i2c,spi openhab
```

#### things
```
Thing exec:command:sht [ command="/usr/bin/python3 /home/pi/smarthome/humidity.py", interval=5, timeout=3 ]
```

#### items
```
String HumidityStr { channel="exec:command:sht:output" }
Number Humidity "Humidity [%.1f %%]" <humidity>
```

#### rules
```
rule "Convert humidity string to number"
when
    Item HumidityStr changed
then
    val newValue = transform("REGEX", "(\\d*.\\d*).*", HumidityStr.state.toString)
    Humidity.postUpdate(newValue)
end
```

#### home.sitemap
```
... {
    ... {
        Text item=Humidity
    }
}
```

## Use [myopenhab.org](http://www.myopenhab.org/) for remote access

1. Paper UI → Add-ons → Misc → Install **openHAB Cloud Connector**

2. Paper UI → Configuration → Services → Configure openHAB Cloud

3. Register for an account on [myopenhab.org](http://www.myopenhab.org/). You
   will be asked for **openHAB UUID** and **openHAB secret**:

   - Find UUID in `/var/lib/openhab2/uuid`
   - Find secret in `/var/lib/openhab2/openhabcloud/secret`

## LB100 Smart LED Bulb on [TPLinkSmartHome Binding](https://www.openhab.org/addons/bindings/tplinksmarthome/)

Paper UI → Add-ons → Install **TP-Link Smart Home Binding**

#### things
```
Thing tplinksmarthome:lb100:bookroom_light [ ipAddress="192.168.0.100", refresh=5 ]
```

#### items
```
Dimmer BookRoom_Light "Book Room" <slider> { channel="tplinksmarthome:lb100:bookroom_light:brightness" }
```

#### home.sitemap
```
... {
    ... {
        Slider item=BookRoom_Light
    }
}
```

## HS100 Smart Plug on [TPLinkSmartHome Binding](https://www.openhab.org/addons/bindings/tplinksmarthome/)

#### things
```
Thing tplinksmarthome:hs100:fan_plug [ ipAddress="192.168.0.101", refresh=5 ]
```

#### items
```
Switch Fan_Plug "Fan" { channel="tplinksmarthome:hs100:fan_plug:switch" }
```

#### home.sitemap
```
... {
    ... {
        Switch item=Fan_Plug
    }
}
```

## Automation

#### rules
```
rule "Turn on/off fan, adjust light"
when
    Item Temperature changed
then
    if (Temperature.state > 29) {
        Fan_Plug.sendCommand(ON)
        BookRoom_Light.sendCommand(10)
    }
    else if (Temperature.state < 28.5) {
        Fan_Plug.sendCommand(OFF)
        BookRoom_Light.sendCommand(90)
    }
end
```
