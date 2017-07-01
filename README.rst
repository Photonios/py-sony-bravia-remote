``py-sony-bravia-remote`` is a Python 3 library for interfacing remotely with Sony Bravia TV's. It utilizes a undocumented HTTP
API that the TV exposes. This allows you to control things like changing the volume, channel or turn the TV on and off.

This API is the exact same API that the "Sony Remote" app uses to control the TV.

Installation
------------
For inclusion in another project, install through `pip`:

.. code-block:: bash

    pip install py-sony-bravia-remote

Example usage
-------------

.. code-block:: python

    from sonybraviaremote import TV, TVConfig

    # called the very first time you attempt to connect to your
    # tv... the tv will display a pincode that you need to enter
    # after the first connection attempt, you'll never have to do this again
    def on_auth():
        return input('Pincode: ')

    # ip address of your tv... the device name is the name under which
    # your program will be registered... note that if you change the device
    # name, you have to re-auth
    config = TVConfig('192.168.0.23', 'my device name')
    tv = TV(config, on_auth)

    tv.wake_up()
    tv.power_off()
    tv.netflix()
    tv.home()
    tv.enter()
    tv.confirm()
    tv.pause()
    tv.play()
    tv.confirm()
    tv.mute()
    tv.volume_up()
    tv.volume_down()
