## Installation Procedure 

For the installation process, you have to set up a virtual environment

# On Linux
Please make sure you have [Python 3.7](https://www.python.org/) or greater and [pip](https://pypi.org/project/pip/) properly installed
```
apt-get install python3 python3-pip python3-venv -y
```

Then run the following command in the root project folder
```
source installation.sh --production
```

# On Mac
Please make sure you have [Python 3.7](https://www.python.org/) or greater and [pip](https://pypi.org/project/pip/) installed.

Then run the following command in the root project folder
```
source installation.sh --production
```

# On Windows
Please make sure you have [Python 3.7](https://www.python.org/) or greater and [pip](https://pypi.org/project/pip/) installed.

Then run the script
```
.\installation.ps1 --production
```


## Play the game

You must be in the virtual environment to play the game.

on Mac or Linux:
```
source .venv/bin/activate
```

on Windows:
```
.\.venv\Scripts\Activate.ps1
```

Then simply run the following command:
```
python -m start
```

## Develop

# On Mac and Linux

Install the dependencies and setup your environment with :
```
source installation.sh
```

You have to develop inside the virtual environment to have all packages up to date. 
To activate the environment, please do :
```
source .venv/bin/activate
```

(Note: you can exit the virtual environment by executing the following command)
```
deactivate
```


# On Windows

Install the dependencies and setup your environment with :
```
.\installation.ps1
```

You have to develop inside the virtual environment to have all packages up to date. 
To activate the environment, please do :
```
.\.venv\Scripts\Activate.ps1
```

(Note: you can exit the virtual environment by executing the following command)
```
deactivate
```
