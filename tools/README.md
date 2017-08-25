# Adding a tool

Openplotter is able to work with external Python scripts.

There is a demo script in *~/.openplotter/tools/demo_tool.py*

To enable the demo application open the OpenPlotter configuration file in *~/.openplotter/openplotter.conf*. Go to section [TOOLS] and you will see something like this:

```
[TOOLS]
py = [['Analog ads1115', 'put analog values to SignalK', 'analog_ads1115.py', '0'], ['Analog Firmata', 'put analog values to SignalK', 'oppymata.py', '0'], ['SignalK Simulator', 'change values with sliders and send values to SignalK', 'SK-simulator.py', '0'], ['Auto Setup', 'configure basic system', 'autosetup_tty.py', '0']]
```

The format of this array is:

```
[TOOLS]
py = [['title', 'description', 'file.py', 'startup'], [...], [...], [...]]
```

where "title" is the name you want to have on the menu Tools in OpenPlotter, "description" is a short sentence describing your app", "file.py" is the name of your script and "startup" will be 1 if you want your app to start at startup or 0 if not.

To enable the demo app you have to add this separated by a comma to the array:

```
['Demo tool', 'You can use this app to start your own apps', 'demo_tool.py', '0']
```

Save the config file and go to the OpenPlotter Tools menu. You should see now the option "Demo tool". When selected, a new window will be open with some options:

* **Settings**. If you have defined a config file for your app, it will be open with a text editor.
* **Start**. This option will start your app.
* **Stop**. This option will stop your app.
* **Cancel**. This option will close the window.

If you want to add your own apps you have just to create a python script on *~/.openplotter/tools* and edit the [TOOLS] section in *~/.openplotter/openplotter.conf* just the same way you did for the demo tool.

See the source of the demo tool to know how to manage config files, manage the OpenPlotter config file, interact with Signal K server or access to OpenPlotter classes.

Let us know if you make any tool that we can add to OpenPlotter core.


