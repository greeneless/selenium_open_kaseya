Public repository initiated by MSP Builder, LCC for Kaseya UI manipulation and automation of tasks not opened to REST API<br>
-- exes are created with <b>"python PyInstaller --onefile FileName.py"</b><br>
-- exes require ChromeDriver.exe to be available to the program but all other dependencies (including the Python interpreter) will be contained in the app.<br>
<br><br>
RECOMMENDED INSTALL FOR CHROMEDRIVER:<br>
--<b>Install Chocolatey in Elevated PowerShell:</b><br>
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
<br>
--<b>Install ChromeDriver with chocolatey in Elevated PowerShell/Cmd:</b><br>
choco install chromedriver
<br><br>
CHROME UPDATES: Chrome automatically updates by default. As of the time of this readme (2020/09/22), Chrome 85 is in use.<br>
-- Chrome updates may cause the application to not launch properly until ChromeDriver is updated. <br>
-- Chrome updates may cause instability after ChromeDriver is updated until reivew/recommit.<br>
-- ChromeDriver.exe requires an instance of Google Chrome installed. https://chromedriver.chromium.org/downloads<br>
<br><br>
KASEYA UPDATES: Updates to the user interface could break this application and require a review/recommit<br>
<br><br>
KASEYA UI: If your VSA has "classic UI enabled" in the System module, nothing here will work.<br>
<br><br>
LOGINS: Password is masked with built in getpass() AuthAnvil and standard Kaseya MFA XPATH references are both supported.<br>
<br><br>
COLUMN SETS APPLICATION: Option for headless is enabled - will run console only by default 

-- get_user_column_sets will retrieve all column sets for the logged in user, then logout file is c:\temp\column_sets.json

-- set_user_column_sets: <b>reads from c:\temp\column_sets.json</b> and assigns columns to the user that has logged in. Exact matches on column set names which previously existed will not be touched, rather, the column set from the file will be created with a _NEW suffix

