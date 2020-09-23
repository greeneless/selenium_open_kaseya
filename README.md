Public repository initiated by MSP Builder, LCC for Kaseya UI manipulation and automation of tasks not opened to REST API

-- exes are created with "python PyInstaller --onefile FileName.py"

-- exes require ChromeDriver.exe to be available to the program but all other dependencies (including the Python interpreter) will be contained in the app.

RECOMMENDED INSTALL FOR CHROMEDRIVER:

--<b>Install Chocolatey in Elevated PowerShell</b>:
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

--Install ChromeDriver with chocolatey in Elevated PowerShell/Cmd:
choco install chromedriver

CHROME UPDATES: Chrome automatically updates by default. As of the time of this readme (2020/09/22), Chrome 85 is in use. Chrome updates may cause the application to not launch properly until ChromeDriver is updated. Chrome updates may cause instability after ChromeDriver is updated until reivew/recommit occurrs ChromeDriver.exe requires an instance of Google Chrome installed https://chromedriver.chromium.org/downloads

KASEYA UPDATES: Updates to the user interface could break this application and require a review/recommit

KASEYA UI: If your VSA has "classic UI enabled" in the System module, nothing here will work.

LOGINS: Password is masked with built in getpass() AuthAnvil and standard Kaseya MFA XPATH references are both supported.

COLUMN SETS APPLICATION: Option for headless is enabled - will run console only by default 

-- get_user_column_sets will retrieve all column sets for the logged in user, then logout file is c:\temp\column_sets.json

-- set_user_column_sets: reads from c:\temp\column_sets.json and assign to the user that has logged in exact matches on column set names which previously existed will not be touched, rather, the column set from the file will be created with a _NEW suffix

