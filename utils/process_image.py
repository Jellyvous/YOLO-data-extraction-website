import os
import sqlite3
import json
import cv2
from PIL import Image
import logging
from ultralytics.utils.plotting import Annotator
from ultralytics import YOLO
from config import RESULT_FOLDER
from utils.helper import handle_overlapping_boxes, group_aligned_labels, cleanning_text, cleanning_num
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg

# Load YOLO model globally to avoid reloading each time
model = YOLO(r"yolo8v6.pt")

# Load VietOCR model
config = Cfg.load_config_from_name('vgg_transformer')
config['device'] = 'cpu'
detector = Predictor(config)

logging.basicConfig(level=logging.DEBUG)


def process_image(image_path, filename):
    # Connect to Database
    conn = sqlite3.connect('./database/detections.db')
    c = conn.cursor()

    

    # Read image and change to RGB
    img = Image.open(image_path)    
    results = model.predict(img)
    
    img_copy = img.copy()
    
    result_json = {filename: []}
    
    # Store extracted text
    extracted_text = ""  
    
    # List of Items to track if the item has existed in the list
    added_items = []
    
    # Extract bounding boxes from YOLO's results
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
                    # Crop image
                    cropped_img = img.crop((xmin-th, ymin-th, xmax+th, ymax+th))
                    b = [xmin-th, ymin-th, xmax+th, ymax+th]
                elif cls == 2:
                    th = int(4)
                    cropped_img = img.crop((xmin-th, ymin-th, xmax+th, ymax+th))
                    b = [xmin-th, ymin-th, xmax+th, ymax+th]
                elif cls == 3:
                    th = int(8)
                    cropped_img = img.crop((xmin-th, ymin-th, xmax+th, ymax+th))
                    b = [xmin-th, ymin-th, xmax+th, ymax+th]
                else:
                    cropped_img = img.crop((xmin, ymin, xmax, ymax))
                    b = [xmin, ymin, xmax, ymax]

                annotator.box_label(b, model.names[cls])
                
                

                
                #Text processing
                if cls == 0:
                    #text = pytesseract.image_to_string(cropped_img, lang='vie')
                    text = detector.predict(cropped_img)
                    clean_text = cleanning_text(text, cls)
                    item_info = {"item": clean_text}
                    extracted_text += f"Item: {clean_text}\n"
                    c.execute("INSERT INTO detections (image_name, detected_class, detected_text) VALUES (?, ?, ?)", (filename, "item", clean_text))
                elif cls == 1:
                    #text = pytesseract.image_to_string(cropped_img, lang='vie')
                    text = detector.predict(cropped_img)
                    clean_text = cleanning_text(text, cls)
                    store_data["store_name"] = clean_text
                    extracted_text += f"store_name: {clean_text}\n"
                    c.execute("INSERT INTO detections (image_name, detected_class, detected_text) VALUES (?, ?, ?)", (filename, "store", clean_text))
                elif cls == 2:
                    #num_quan = pytesseract.image_to_string(cropped_img, config='-c tessedit_char_whitelist=0123456789')
                    num_quan = detector.predict(cropped_img)
                    clean_num = cleanning_num(num_quan,  cls)
                    item_info["price"] = clean_num
                    extracted_text += f"Price: {clean_num}\n"
                    c.execute("INSERT INTO detections (image_name, detected_class, detected_text) VALUES (?, ?, ?)", (filename, "price", clean_num))
                elif cls == 3:
                    #num_quan = pytesseract.image_to_string(cropped_img, config='--psm 10 tessedit_char_whitelist=0123456789')
                    num_quan = detector.predict(cropped_img)
                    clean_num = cleanning_num(num_quan,  cls)
                    item_info["quantity"] = clean_num
                    extracted_text += f"Quantity: {clean_num}\n"
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

    return result_json_path, processed_image_path, extracted_text
    


