# IndustriouSlime #

## Python grid traversing GUI app ##

### App is solves issue of finding greatest (max/optimal) path on the grid ###


**Getting started**

In order to be able to run this app you will need python of version 3.6 and higher with pip and tkinter installed.

Pip is python package manager so it ships in the same box with any python installation.

Tkinter is a library for creating GUIs and is a part of python default installation (unless you deselected "install tk" option during the python installation through the python installler)
If you are on windows, the easiest way to install python is to visit [this link](https://www.python.org/downloads/) and download installer from there.

On linux you might want to use terminal installation which, if you are on debian-based destribution, might follow like:

```bash
    apt-get install python-tk
```

This command will also handle tkinter as part of the default installation

After installing python, navigate to this repository folder and in the command line run:

```bash
    pip install -r requirements.txt
```

after that with the command:

```bash
    python main.py
```

you should be able to successfully run and use the application.

**Creating executable**

If you want to create an executable file to ship this program and/or use it on systems without python installed,
you will need to type the following:

```bash
    pip install pyinstaller
```

then

```bash
    pyinstaller --onefile main.py
```

After that move executable file from the created by pyinstaller `dist` folder somewhere alongside `icons` folder and
`howTo.html` file so that application will be able to make use of them. It may crash if you don't do this.
After that you can archivate this bundle and ship this ready-to-run app wherever you want
