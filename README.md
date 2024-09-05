# YOLO model application invoice data extraction website
## Introduction
Hello, this is my capstone project. In this project, I researched the YOLO model, conducted training on a [dataset](https://drive.google.com/drive/folders/1Pw_AQ8OJTzQQV8z6lQJmiHUEjN6856HI?usp=sharing) consisting of 1,000 images by using google colab, developed a basic web page using Flask, and utilized the trained model to extract information from an invoice. Additionally, I implemented text recognition using [VietOCR](https://github.com/pbcquoc/vietocr).  

## Install
Make sure your system's execution policy is set to allow running PowerShell scripts.  
Here's how you can do it:  
- Open PowerShell as Administrator
- In the PowerShell window, enter the following command to allow scripts to run: `Set-ExecutionPolicy RemoteSigned`
- You may be prompted to confirm the change. Type Y and press Enter.

After changing the execution policy, we will install the virtual environment:
- Go to the project's folder, paste the command `python -m venv venv` in the terminal and enter.
- After that, run `.\venv\Scripts\activate` to activate the virtual environment.
- Now your virtual environment is activated, you will need to install all the requirement libraries by running `pip install -r requirements.txt`.

All right, now everything is ready, run `python server.py` and the website will run on your computer host.

## Usage
Open your web browser and enter the URL of the host where the application is running (Usually http://127.0.0.1:5000/).  
On the main interface of the website, you will see a "Import Image" button. Click this button to open a file selection window and select the invoice image you want to extract data from. I have provided some sample invoices in the 'bills' folder of the project.  
After selecting the invoice image, return to the main interface of the website and click the "Detect" button. The application will begin analyzing and extracting data from the selected invoice image.  
Once the extraction process is complete, a JSON file containing the extracted invoice data will be automatically downloaded to your computer and the result will be saved in the 'result' folder of the project.  
If you need further assistance or encounter any issues during use, please feel free to contact me.  
