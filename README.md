##Install
Make sure your system's execution policy is set to allow running PowerShell scripts.
Here's how you can do it:
Open PowerShell as Administrator:
 - Search for "PowerShell" in the Start menu.
 - Right-click on "Windows PowerShell" and select "Run as Administrator."
 - In the PowerShell window, enter the following command to allow scripts to run:
	Set-ExecutionPolicy RemoteSigned
- You may be prompted to confirm the change. Type Y and press Enter.
- After changing the execution policy, run the command below to install virtual environment:
	python -m venv venv
- After that, type ".\venv\Scripts\activate" and enter to run the virtual environment.
- Run
	pip install -r requirements.txt
