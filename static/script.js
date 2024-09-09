function loadImage(event) {
    const imageBox = document.getElementById('image-box');
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            imageBox.innerHTML = '<img src="' + e.target.result + '" class="img-fluid" />';
        };
        reader.readAsDataURL(file);
    }
}

const form = document.querySelector('form');
form.addEventListener('submit', function(event) {
    event.preventDefault();
    
    const formData = new FormData(form);
    fetch('/', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.extracted_text) {
            document.getElementById('extracted_text').value = data.extracted_text;
        } else if (data.error) {
            console.error('Error:', data.error);
        }
    })
    .catch(error => console.error('Error:', error));
});

function processTextToJSON(text) {
    const lines = text.split('\n');
    const result = [];
    let currentItem = null;

    lines.forEach(line => {
        if (line.startsWith('Item:')) {
            if (currentItem) {
                result.push({ items: [currentItem] });
            }
            currentItem = { item: line.replace('Item: ', '').trim() };
        } else if (line.startsWith('Quantity:')) {
            if (currentItem) {
                currentItem.quantity = line.replace('Quantity: ', '').trim();
            }
        } else if (line.startsWith('Price:')) {
            if (currentItem) {
                currentItem.price = line.replace('Price: ', '').trim();
            }
        } else if (line.startsWith('store_name:')) {
            result.push({ store_name: line.replace('store_name: ', '').trim(), items: [] });
        }
    });

    if (currentItem) {
        result.push({ items: [currentItem] });
    }

    const finalJSON = {
        "results.jpg": result
    };

    return finalJSON;
}

function downloadText(type) {
    const text = document.getElementById('extracted_text').value;
    let blob;
    let filename;
    
    if (type === 'json') {
        const jsonObject = processTextToJSON(text);
        const jsonString = JSON.stringify(jsonObject, null, 2);
        blob = new Blob([jsonString], { type: 'application/json' });
        filename = 'extracted_text.json';
    } else {
        blob = new Blob([text], { type: 'text/plain' });
        filename = 'extracted_text.txt';
    }
    
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}