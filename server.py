from flask import Flask, render_template, request, redirect, send_file, url_for, Response
from werkzeug.utils import secure_filename, send_from_directory
import cv2
import json
import numpy as np
from scipy.ndimage import interpolation as inter
from PIL import Image
import pytesseract
import io
import os
import re
import pathlib
import sqlite3
temp = pathlib.PosixPath
from ultralytics.utils.plotting import Annotator  # ultralytics.yolo.utils.plotting is deprecated
from ultralytics import YOLO
pathlib.PosixPath = pathlib.WindowsPath
import logging
import matplotlib.pyplot as plt
from PIL import Image

from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg

logging.basicConfig(level=logging.DEBUG)

#Load model YOLO
model = YOLO(r"yolo8v6.pt")  # Adjust the path to your YOLOv8 model


app = Flask(__name__)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\VietOCR\VietOCR.exe'
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
PRE_FOLDER = 'pre'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)



# Tính Iou
def calculate_iou(box1, box2):
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    
    xi1 = max(x1_min, x2_min)
    yi1 = max(y1_min, y2_min)
    xi2 = min(x1_max, x2_max)
    yi2 = min(y1_max, y2_max)
    
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    
    box1_area = (x1_max - x1_min) * (y1_max - y1_min)
    box2_area = (x2_max - x2_min) * (y2_max - y2_min)
    
    union_area = box1_area + box2_area - inter_area
    
    iou = inter_area / union_area
    
    return iou


#Xử lý nhãn đè lên nhau
def handle_overlapping_boxes(boxes, iou_threshold=0.5):
    filtered_boxes = []
    
    for i, box1 in enumerate(boxes):
        keep = True
        for j, box2 in enumerate(boxes):
            if i != j:
                iou = calculate_iou(box1.xyxy[0], box2.xyxy[0])
                if iou > iou_threshold:
                    if box1.conf < box2.conf:
                        keep = False
                        break
        if keep:
            filtered_boxes.append(box1)
    
    return filtered_boxes

# Gom các nhãn thẳng hàng
def group_aligned_labels(boxes, tolerance=15):
    groups = []
    used = [False] * len(boxes)
    
    for i in range(len(boxes)):
        if not used[i]:
            group = [boxes[i]]
            used[i] = True
            for j in range(i + 1, len(boxes)):
                if not used[j]:
                    y1_i = (boxes[i].xyxy[0][1] + boxes[i].xyxy[0][3]) / 2  # Trung bình tọa độ y của box i
                    y1_j = (boxes[j].xyxy[0][1] + boxes[j].xyxy[0][3]) / 2  # Trung bình tọa độ y của box j
                    if abs(y1_i - y1_j) <= tolerance:
                        group.append(boxes[j])
                        used[j] = True
            groups.append(group)
    
    return groups


# Xử lý hình ảnh
def process_image(image_path, filename):
    
    #kết nối db
    conn = sqlite3.connect('./database/detections.db')
    c = conn.cursor()

    

    # Đọc ảnh
    img = cv2.imread(image_path)
    
    # Chuyển đổi sang định dạng RGB cho model YOLO
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = model.predict(img_rgb)
    
    # Tạo bản sao của img_rgb
    img_copy = img_rgb.copy()
    
    # Kết quả JSON
    result_json = {filename: []}
    
    # Danh sách tạm thời để theo dõi các mặt hàng đã được thêm vào
    added_items = []
    
    # Lấy bounding boxes từ kết quả YOLO
    for r in results:
        annotator = Annotator(img_copy)
        bboxes = handle_overlapping_boxes(r.boxes)
        logging.debug(bboxes)
        groups = group_aligned_labels(bboxes)
        extracted_text = ""
        
        for group in groups:
            store_data = {}
            items = []
            item_info = {}
            
            for bbox in group:
                xmin, ymin, xmax, ymax = bbox.xyxy[0]
                #b = bbox.xyxy[0]
                cls = bbox.cls
                conf = bbox.conf 
                xmin, ymin, xmax, ymax, cls = int(xmin), int(ymin), int(xmax), int(ymax), int (cls)
                
                if cls == 0:
                    th = int(6)
                    cropped_img = img_rgb[ymin-th:ymax+th, xmin-th:xmax+th]
                    b = [xmin-th, ymin-th, xmax+th, ymax+th]
                elif cls == 2:
                    th = int(4)
                    cropped_img = img_rgb[ymin-th:ymax+th, xmin-th:xmax+th]
                    b = [xmin-th, ymin-th, xmax+th, ymax+th]
                elif cls == 3:
                    th = int(8)
                    cropped_img = img_rgb[ymin-th:ymax+th, xmin-th:xmax+th]
                    b = [xmin-th, ymin-th, xmax+th, ymax+th]
                else:
                    cropped_img = img_rgb[ymin:ymax, xmin:xmax]
                    b = bbox.xyxy[0]

                annotator.box_label(b, model.names[cls])
                
                
                #Xử lý text
                if cls == 0:
                    text = pytesseract.image_to_string(cropped_img, lang='vie')
                    clean_text = cleanning_text(text, cls)
                    item_info = {"item": clean_text}
                    c.execute("INSERT INTO detections (image_name, detected_class, detected_text) VALUES (?, ?, ?)", (filename, "item", clean_text))
                elif cls == 1:
                    text = pytesseract.image_to_string(cropped_img, lang='vie')
                    clean_text = cleanning_text(text, cls)
                    store_data["store_name"] = clean_text
                    c.execute("INSERT INTO detections (image_name, detected_class, detected_text) VALUES (?, ?, ?)", (filename, "store", clean_text))
                elif cls == 2:
                    num_quan = pytesseract.image_to_string(cropped_img, config='-c tessedit_char_whitelist=0123456789')
                    clean_num = cleanning_num(num_quan,  cls)
                    item_info["price"] = clean_num
                    c.execute("INSERT INTO detections (image_name, detected_class, detected_text) VALUES (?, ?, ?)", (filename, "price", clean_num))
                elif cls == 3:
                    num_quan = pytesseract.image_to_string(cropped_img, config='--psm 10 tessedit_char_whitelist=0123456789')
                    clean_num = cleanning_num(num_quan,  cls)
                    item_info["quantity"] = clean_num
                    c.execute("INSERT INTO detections (image_name, detected_class, detected_text) VALUES (?, ?, ?)", (filename, "quantity", clean_num))
                else:
                    extracted_text += "EROR"
                    
                
                if item_info and "item" in item_info:
                    item_name = item_info["item"]
                    if item_name not in added_items:
                        added_items.append(item_name)
                        items.append(item_info)
                
            
            store_data["items"] = items
            result_json[filename].append(store_data)
    
            
    conn.commit()
    conn.close()
    
    # Save the image with bounding boxes
    processed_image_path = os.path.join(RESULT_FOLDER, filename)
    img = annotator.result()  
    cv2.imwrite(processed_image_path, img)

    
    result_json_path = os.path.join(RESULT_FOLDER, f"{filename.rsplit('.', 1)[0]}.json")
    with open(result_json_path, 'w', encoding='utf-8') as f:
        json.dump(result_json, f, ensure_ascii=False, indent=4)

    return result_json_path, processed_image_path

def cleanning_text(text, cls):
    clean_text = ""
    #Xoá ký tự xuống dòng
    text_without_space = text.replace('\n', ' ').strip()
    
    #Lower chữ
    final_lower = text_without_space.lower()
    clean_text = re.sub(r'[^a-zA-ZâấầẩẫậăắằẳẵặáàảãạăắằẳẵặéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđĂÂĐÊÔƠƯƵÁÀẢÃẠẮẰẲẴẶẤẦẨẪẬÉÈẺẼẸẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢÚÙỦŨỤỨỪỬỮỰÝỲỶỸỴ() ]+', '', final_lower)

    return clean_text.strip()

def cleanning_num(num, cls) :
    clean_num = ""
    #Xoá ký tự xuống dòng
    text_without_space = num.replace('\n', ' ').strip()
    
    #Lower chữ
    final_lower = text_without_space.lower()
    clean_num = re.sub(r'[^0-9]+', '', final_lower)
        
    return clean_num.strip()



@app.route('/')
def hello_world():
    return render_template('index.html', name='World')

@app.route('/', methods=['POST', 'GET'])
def predict_img():
    if request.method == 'POST':
        if 'file' in request.files:
            f = request.files['file']
            filename = secure_filename(f.filename)
            basepath = os.path.dirname(__file__)
            filepath = os.path.join(basepath, 'uploads', f.filename)
            print ("Upload folder is", filepath)
            f.save(filepath)
            global imgpath
            predict_img.imgpath = f.filename
            print("printing predict_img ::::::", predict_img)
            
            result_json_path, processed_image_path = process_image(filepath, filename)
            
            return send_file(result_json_path, as_attachment=True)
    
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)
                      

if __name__ == '__main__':
    app.run(debug=True)
