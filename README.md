# adbez
**Simplify your ADB workflow:** *Python GUI for Android device management and Nmap integration.*

### why adbez?
**New to using ADB?**
**Do you want to use ADB in a easier way?**
**Do you want to manage everything easily with a simple interface?**
> **Then this repo is just for you.**
### Key features
**Easy interface with Tkinter**

### Current features
* You can search with nmap
* You can connect to ip adresses with adb
* The ip adresses from the results when you search with nmap are automatically added into the "Founded ips" option located next to the adb connection box, so you can easily connect to ip adresses.
* You can apply input key events to the selected IP addresses
* You can view all the processes running in the background using Process Monitor.

### Requirements
- Python 3.x
- [nmap](https://nmap.org/download.html) installed on your system
- ADB (adbez will try to find it automatically)
- Psutil

### Installation
```bash
git clone https://github.com/yhy557/adbez.git
cd adbez
pip install -r requirements.txt
python adbez.py
```


<table>
  <tr>
    <td align="center"><b>Main tab</b></td>
    <td align="center"><b>Input Keyevents tab</b></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/4e62727e-19d7-45b5-9346-52e9dcfe6e89" width="400"/></td>
    <td><img src="https://github.com/user-attachments/assets/40fbd4de-911b-4be7-87a7-0bf3b6a60d4d" width="400"></td>
  </tr>
  
  <tr>
    <td align="center"><b>Settings tab</b></td>
    <td align="center"><b>Process Monitor</b></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/f02a83a9-4bdc-4814-896a-48d07bbeaae3" width="400"></td>
    <td><img src="https://github.com/user-attachments/assets/6ce0d3b4-a258-4210-990a-c5ba7e2b5e9f" width="400"></td>
  </tr>
</table>


*Portugese translation by:* **[@FetoyuDev](https://github.com/FetoyuDev)**
