# YOLO model application invoice data extraction website
## Introduction
Hello, this is my capstone project. In this project, I researched the YOLO model, conducted training on a [dataset](https://drive.google.com/drive/folders/1Pw_AQ8OJTzQQV8z6lQJmiHUEjN6856HI?usp=sharing) consisting of 1,000 images by using google colab, developed a basic web page using Flask, and utilized the trained model to extract information from an invoice. Additionally, I implemented text recognition using [VietOCR](https://github.com/pbcquoc/vietocr).  

## Install
Make sure your system's execution policy is set to allow running PowerShell scripts.  
Here's how you can do it:  
- Open PowerShell as Administrator
- In the PowerShell window, enter the following command to allow scripts to run: `Set-ExecutionPolicy RemoteSigned`
- You may be prompted to confirm the change. Type Y and press Enter.
- After changing the execution policy, go to the project's folder and run the command in the terminal to install virtual environment: `python -m venv venv`
- After that, run `.\venv\Scripts\activate` to activate the virtual environment.
- Now your virtual environment is activated, you will need to install all the requirement libraries by running `pip install -r requirements.txt`
