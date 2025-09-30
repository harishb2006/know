import pytesseract
import cv2
import numpy as np
from PIL import Image
import io
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class OCRService:
    def extract_text_from_image(self, image_data: bytes) -> Dict[str, Any]:
        """Extract text from image using OCR"""
        try:
            # Load and preprocess image
            image = Image.open(io.BytesIO(image_data))
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            processed_image = self._preprocess_image(opencv_image)
            
            # Extract text with OCR
            text_content = pytesseract.image_to_string(processed_image, lang='eng')
            
            # Get word-level confidence data
            data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
            words = []
            confidences = []
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 30:  # Filter low confidence
                    words.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i])
                    })
                    confidences.append(int(data['conf'][i]))
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': text_content.strip(),
                'words': words,
                'extraction_confidence': avg_confidence,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return {
                'text': '',
                'words': [],
                'extraction_confidence': 0,
                'error': str(e),
                'success': False
            }
    
    def _preprocess_image(self, image):
        """Preprocess image for better OCR"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        return thresh