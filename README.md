rpi-lights
==========

This is some simple code to allow turning on and off lights via my Raspberry
Pi. Serial pins 5 (ground) and 7 (RTS, changed between high/low voltage) are
connected to a triac 
([SSRAC112](https://www.ereshop.com/shop/index.php?main_page=product_info&products_id=198))
and then to the wall (through a fuse and a couple switches) and the lights.

This is inspired by my [bell system](https://floft.net/code/bells/). I had some
hardware sitting around from that project and decided I might as well put it to
use.

# Setup
Check and add yourself to the groups for your serial ports in /dev:

    $ ls -l /dev | grep tty
    ...
    crw--w---- 1 root tty    204,  64 Oct 18 23:34 ttyAMA0
    crw-rw---- 1 root uucp   188,   0 Oct 21 19:41 ttyUSB0
    ...
    $ sudo usermod -a -G tty,uucp your_username
    $ logout # Only takes effect when you log back in

Install [pyserial](https://github.com/pyserial/pyserial) with
`sudo pacman -S python-pyserial` if on Arch, or more generally
`pip install pyserial`.

Edit the *lights.service* file setting the path to the Python file and the
desired user/group you want it to run as, then install via:

    $ sudo mv lights.service /etc/systemd/system/
    $ sudo systemctl enable lights
    $ sudo systemctl start lights
