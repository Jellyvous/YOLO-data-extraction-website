import re


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

#Xử lý kết quả nhận diện chữ
def cleanning_text(text, cls):
    clean_text = ""
    #Xoá ký tự xuống dòng
    text_without_space = text.replace('\n', ' ').strip()
    
    #Lower chữ
    final_lower = text_without_space.lower()
    clean_text = re.sub(r'[^a-zA-ZâấầẩẫậăắằẳẵặáàảãạăắằẳẵặéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđĂÂĐÊÔƠƯƵÁÀẢÃẠẮẰẲẴẶẤẦẨẪẬÉÈẺẼẸẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢÚÙỦŨỤỨỪỬỮỰÝỲỶỸỴ() ]+', '', final_lower)

    return clean_text.strip()

#Xử lý kết quả nhận diện số
def cleanning_num(num, cls) :
    clean_num = ""
    #Xoá ký tự xuống dòng
    text_without_space = num.replace('\n', ' ').strip()
    
    #Lower chữ
    final_lower = text_without_space.lower()
    clean_num = re.sub(r'[^0-9]+', '', final_lower)
        
    return clean_num.strip()