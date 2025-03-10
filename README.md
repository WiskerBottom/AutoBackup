# AutoBackup
A set of programs to automate backups to a seprate machine.

Please note that all IP addresses are hardcoded, they will need to be changed!

  ABServerHost should be run on whatever machine is acting as the server, it is set up to create its own storage tree under /home/USERNAME/Documents/Toshiba3TB/. Toshiba3TB is where I have one of my hard drives mounted, but you should be able to change this to whatever you want. While you're creating this directory there is a variable at the top of ABServerHost that should store your username, please change it from the default to whatever your username is. This program also runs on port 2075, please make sure your firewall has port 2075 open both ways. 

  Every time a backup is made it will create a new directory with the username of the client if one does not already exist. In that folder it will check if a folder with the current time and date exists, if one doesn't it will create one. In that directory it will write any files that the client has sent it. It also will recreate the file structure of the directory if there was one on the client side has been sent. If repeated backups are made it should detect that the files are already there and tell the client to skip sending any files it already has. Once it finishes writing data from the client it should go back to checking for incoming requests.
  
  ABClient should be run on the machine you want to backup. It reads any paths from the BackupList.txt file and attempts to send all files contained in that folder over to whatever machine is running ABServerHost. It can also read paths directly to a file. If you are sending a folder please include a trailing '/'.
