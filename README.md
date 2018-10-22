rpi-lights
==========

This is some simple code to allow turning on and off lights via my Raspberry
Pi with the purpose of connecting to [IFTTT](https://ifttt.com/) (if this, then
that) so you can trigger lights on a variety of events such as time of day, a
button press on your phone, or when you enter or leave an area.

My hardware setup: serial pins 5 (ground) and 7 (RTS, changed between high/low
voltage) are connected to a triac
([SSRAC112](https://www.ereshop.com/shop/index.php?main_page=product_info&products_id=198))
and then to the wall (through a fuse and a couple switches) and the lights.

This is inspired by my [bell system](https://floft.net/code/bells/). I had some
hardware sitting around from that project and decided I might as well put it to
use.

# Setup

## nginx

Update your *nginx* config to point to the lights Tornado instance we'll set up
at a particular subdirectory (make sure it matches the "root" option in your
config file):

    http {
        upstream lights {
            server 127.0.0.1:8080;
        }

        ...

        server {
            ...

            location /lights/ {
                proxy_pass_header Server;
                proxy_set_header Host $http_host;
                proxy_redirect off;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Scheme $scheme;
                proxy_pass http://lights;
            }

            ...
        }
    }

Restart *nginx*:

    $ sudo systemctl restart nginx

## Arch Linux
Install program to */usr/bin*, config to */etc*, systemd script to
*/etc/systemd/system*, etc.

    $ makepkg -si

Then make sure you edit */etc/lights.yaml* changing the key, port, etc.
To enable and run:

    $ sudo systemctl enable lights
    $ sudo systemctl start lights

## If not Arch
Check and add yourself to the groups for your serial ports in */dev*:

    $ ls -l /dev | grep tty
    ...
    crw-rw---- 1 root uucp   188,   0 Oct 21 19:41 ttyUSB0
    ...
    $ sudo usermod -a -G uucp your_username
    $ logout # Only takes effect when you log back in

Install dependencies:

    $ pip install tornado pyyaml pyserial

Copy the config file and make your desired changes, making sure to change the key:

    $ cp config.yaml my_config.yaml
    $ vim my_config.yaml # ...

Edit the *lights.service* file setting the path to the Python file and config
and desired user/group you want it to run as, then install via:

    $ sudo cp lights.service /etc/systemd/system/
    $ sudo chown root:root /etc/systemd/system/lights.service
    $ sudo systemctl enable lights
    $ sudo systemctl start lights

# IFTTT

To make this easy to use on your phone, install [IFTTT](https://ifttt.com/) (if
this, then that). Then, for example, you can create a widget for your
homescreen that will toggle your lights:

 - Enable [webhooks](https://ifttt.com/maker_webhooks)
 - Go to "My Applets" (center button at bottom) in the app
 - Click top "+" icon to add your own applet
 - Make *this* a "button widget"
 - Make *that* a webhook with "https://example.com/lights/hook?action=toggle&key=..."
 - Add the IFTTT button widget to your homescreen and select this applet to
   trigger on press

Alternatively, you could turn on/off (change action to "on" or "off") your
lights when you exit an area (or similarly enter) by searching for "location"
or make it turn on/off at a certain time searching for "date & time".

## Debugging

Monitor the output of Tornado for debugging, verifying that it's receiving the
on/off/toggle requests correctly:

    $ sudo journalctl -u lights.service -f

