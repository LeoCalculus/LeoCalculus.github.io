---
tags: [linux, vscode]
---

# Using WSL to compile projects  
It is well-known that on windows 'wsl2' compiles projects much faster than window itself, here is a short 
tutorial on how to set up 'wsl2' on windows 11 with platformio extension.

Reference:  
[WSL2+VSCODE](https://www.bilibili.com/video/BV1MGrTYVE93/?vd_source=aa7cc77bf0072ed75925e316de7bf0b8)  
This reference was on windows 10 and for esp-idf(extension on vscode).

---
# Pre-requirements  
1. enable the feature: Windows Subsystem for Linux  
This is located at: win key-> search for 'control panel' (view by Large icons! not category) -> Programs and Features(disk icon) -> Turn Windows features on or off(on the left) -> Windows Subsystem for Linux (at bottom of scroll bar)  
2. Use command `wsl --install` with PowerShell in administrator mode  
[Note](https://learn.microsoft.com/en-us/windows/wsl/install): New Linux installations, installed using the `wsl --install` command, will be set to WSL 2 by default.  
3. Download Ubuntu from Microsoft Store, the version I select is: Ubuntu 24.04.1 LTS
4. Open Windows Powershell and install usbipd (USB over IP) via following command:
```powershell
winget install usbipd
```
connect your esp32 with your computer, list all ports and find out which one corresponding to esp32 with such command:
```powershell
usbipd list
```
In DEVICE list, focus on (COMX) style keywords, record its BUSID, you can see that within the STATE list, it shows 'Not shared'.



---
# Launch Ubuntu & Install packages
By Launching the downloaded Ubuntu, we need to set up new UNIX name and password.   
Set the password as easy as you can since later we will use sudo command which require password.  
The system then will show you the welcome infomation and show a prefix in terminal with:
`<username>@<your computer name>:~$`  
This means installation is successful.

Now we will install necessary packages:
```bash
sudo apt update
sudo apt-get install git wget flex bison gperf python3 python3-pip python3-venv cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0
```
Keep your ubuntu opened at the background!

---
# Vscode section & Make connection to WSL
1. Install WSL extension from extension store, you can simply type `wsl` in extension store
2. Now we connect the Ubuntu by clicking the 'Remote Explorer', this is located between 'Run and Debug' and 'Extensions' icon, there you can find 'Connect in current window', when you click this it will open a new vscode window. Open the terminal by clicking Terminal->new terminal, you should see Linux style terminal, if you remain in windows one it may begin with 'PS ...'
3. Go to the extension store and find platformio and install for this environment
4. Right now our compilation will be based on wsl, but we haven't set up for upload ports, we can connect them with usbipd in windows powershell.
Use your previous recorded BUSID, for example in my case (COM4): 1-7 
RUN following command in powershell to bind your port: (The command was using my case 1-7)
```powershell
usbipd bind --busid 1-7
usbipd attach --wsl --busid 1-7 
```
You may head sound that windows disconnect from usb sound, which means you got that connected.  
5. Finally, in your vscode, for platformio project file add a line: `upload_port = /dev/ttyUSB0` which is used for upload the code.   
6. All set! Now you can Build and Upload with WSL2, if you want to turn of the ubuntu, in powershell use: `wsl --shutdown`

---
# Common problem
1. If you meet /dev/ttyUSB0 during upload gives failure like:
```txt
Serial port /dev/ttyUSB0

A fatal error occurred: Could not open /dev/ttyUSB0, the port doesn't exist
```
It means insufficient permissions, try following commands:
```Linux
$ sudo adduser <username> dialout
$ sudo chmod a+rw /dev/ttyUSB0
```
Credit for this: [solution](https://stackoverflow.com/questions/73923341/unable-to-flash-esp32-the-port-doesnt-exist)

