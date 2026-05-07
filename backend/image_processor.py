"""
ZeroHour - Image Processing and OCR Module

Handles image upload, preprocessing, and text extraction using OCR.
Integrates with the sentiment analysis pipeline for crisis detection from images.
"""

import os
import uuid
import time
import io
from typing import Dict, Tuple, Optional
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import numpy as np

from backend.sentiment import analyze

# Configure pytesseract path for Windows if needed
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ImageProcessor:
    """Handles image processing and OCR for crisis intelligence."""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        # Apply slight blur to reduce noise
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        # Convert to OpenCV format for additional processing
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_GRAY2BGR)
        
        # Apply adaptive thresholding
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        
        # Convert back to PIL
        processed_image = Image.fromarray(thresh)
        
        return processed_image
    
    def extract_text(self, image: Image.Image, preprocess: bool = True) -> Dict[str, any]:
        """
        Extract text from image using OCR.
        
        Args:
            image: PIL Image object
            preprocess: Whether to preprocess image for better OCR
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        start_time = time.time()
        
        try:
            if preprocess:
                processed_image = self.preprocess_image(image)
            else:
                processed_image = image
            
            # Configure Tesseract for better text recognition
            custom_config = r'--oem 3 --psm 6 -l eng+hin+spa+fra+deu'  # Multiple languages
            
            # Extract text with confidence scores
            data = pytesseract.image_to_data(processed_image, config=custom_config, output_type=pytesseract.Output.DICT)
            
            # Extract text and calculate average confidence
            extracted_text = ""
            confidences = []
            word_boxes = []
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:  # Filter out low confidence results
                    text = data['text'][i].strip()
                    if text:
                        extracted_text += text + " "
                        confidences.append(int(data['conf'][i]))
                        
                        # Store bounding box information
                        word_boxes.append({
                            'text': text,
                            'confidence': int(data['conf'][i]),
                            'bbox': {
                                'x': data['left'][i],
                                'y': data['top'][i],
                                'width': data['width'][i],
                                'height': data['height'][i]
                            }
                        })
            
            extracted_text = extracted_text.strip()
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            processing_time = time.time() - start_time
            
            return {
                'text': extracted_text,
                'confidence': avg_confidence,
                'word_count': len(extracted_text.split()),
                'processing_time': processing_time,
                'word_boxes': word_boxes,
                'success': True
            }
            
        except Exception as e:
            return {
                'text': '',
                'confidence': 0,
                'word_count': 0,
                'processing_time': time.time() - start_time,
                'word_boxes': [],
                'success': False,
                'error': str(e)
            }
    
    def analyze_image_text(self, image: Image.Image) -> Dict[str, any]:
        """
        Extract text from image and analyze it for crisis intelligence.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary containing OCR results and sentiment analysis
        """
        # Extract text using OCR
        ocr_result = self.extract_text(image)
        
        if not ocr_result['success'] or not ocr_result['text']:
            return {
                **ocr_result,
                'sentiment_analysis': None,
                'crisis_detected': False,
                'severity': 'NEUTRAL'
            }
        
        # Analyze extracted text for crisis intelligence
        sentiment_result = analyze(ocr_result['text'])
        
        # Determine if crisis is detected
        crisis_keywords = ['emergency', 'explosion', 'fire', 'flood', 'attack', 'bomb', 
                          'shooting', 'accident', 'disaster', 'evacuation', 'danger']
        text_lower = ocr_result['text'].lower()
        crisis_detected = any(keyword in text_lower for keyword in crisis_keywords)
        
        return {
            **ocr_result,
            'sentiment_analysis': sentiment_result,
            'crisis_detected': crisis_detected,
            'severity': sentiment_result.get('llm_label', 'NEUTRAL')
        }
    
    def save_uploaded_image(self, image_data: bytes, filename: str = None) -> Tuple[str, str]:
        """
        Save uploaded image to disk.
        
        Args:
            image_data: Raw image bytes
            filename: Original filename (optional)
            
        Returns:
            Tuple of (saved_path, unique_filename)
        """
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(__file__), "..", "data", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        if filename:
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        else:
            unique_filename = f"image_{uuid.uuid4().hex[:8]}.jpg"
        
        # Save image
        saved_path = os.path.join(upload_dir, unique_filename)
        
        try:
            # Open image from bytes and save
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            image.save(saved_path, 'JPEG', quality=85)
            return saved_path, unique_filename
            
        except Exception as e:
            raise ValueError(f"Failed to save image: {str(e)}")
    
    def validate_image(self, image_data: bytes, filename: str = None) -> bool:
        """
        Validate if the uploaded file is a valid image.
        
        Args:
            image_data: Raw image bytes
            filename: Original filename (optional)
            
        Returns:
            True if valid image, False otherwise
        """
        try:
            # Check file extension if provided
            if filename:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in self.supported_formats:
                    return False
            
            # Try to open the image
            image = Image.open(io.BytesIO(image_data))
            image.verify()  # Verify without loading
            
            # Reopen for size check
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            # Check minimum size (too small images are not useful)
            if width < 50 or height < 50:
                return False
            
            # Check maximum size (too large images may cause memory issues)
            if width > 5000 or height > 5000:
                return False
            
            return True
            
        except Exception:
            return False

# Global instance
image_processor = ImageProcessor()

def process_uploaded_image(image_data: bytes, filename: str = None) -> Dict[str, any]:
    """
    Process an uploaded image for crisis intelligence.
    
    Args:
        image_data: Raw image bytes
        filename: Original filename
        
    Returns:
        Dictionary containing processing results
    """
    try:
        # Validate image
        if not image_processor.validate_image(image_data, filename):
            return {
                'success': False,
                'error': 'Invalid image format or size',
                'filename': filename
            }
        
        # Save image
        saved_path, unique_filename = image_processor.save_uploaded_image(image_data, filename)
        
        # Open image for processing
        image = Image.open(saved_path)
        
        # Analyze image text
        analysis_result = image_processor.analyze_image_text(image)
        
        return {
            'success': True,
            'filename': unique_filename,
            'saved_path': saved_path,
            'analysis': analysis_result
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'filename': filename
        }
