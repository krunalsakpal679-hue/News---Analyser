# backend/app/services/ocr/column_detector.py
"""
Detects multiple columns in a newspaper page for separate OCR extraction.
"""
import numpy as np

class ColumnDetector:
    def detect_columns(self, binary: np.ndarray) -> list[tuple[int, int, int, int]]:
        """
        Detects vertical white-space separators between columns.
        Returns list of (x1, y1, x2, y2) bounding boxes.
        """
        h, w = binary.shape[:2]
        
        # 1. col_sum = sum of white pixels in each column
        # Assuming background is white (255) and text is black (0) because of ADAPTIVE_THRESH_GAUSSIAN_C
        col_sum = np.sum(binary == 255, axis=0)
        
        # 2. threshold
        threshold = h * 0.85
        
        # 3. Find contiguous separator regions (min 5px wide)
        separators = []
        in_sep = False
        start_x = 0
        
        for x in range(w):
            if col_sum[x] > threshold:
                if not in_sep:
                    start_x = x
                    in_sep = True
            else:
                if in_sep:
                    if (x - start_x) >= 5:
                        separators.append((start_x, x))
                    in_sep = False
        if in_sep and (w - start_x) >= 5:
            separators.append((start_x, w))
            
        # 4. Convert separators to (x1, 0, x2, height) column boxes
        if not separators:
            return [(0, 0, w, h)]
            
        columns = []
        current_x = 0
        
        for sep_start, sep_end in separators:
            if sep_start > current_x:
                columns.append((current_x, 0, sep_start, h))
            current_x = sep_end
            
        if current_x < w:
            columns.append((current_x, 0, w, h))
            
        # 5. Filter columns < 100px wide
        columns = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in columns if (x2 - x1) >= 100]
        
        if len(columns) <= 1:
            return [(0, 0, w, h)] # If 1 or 0 columns, return full box
            
        return columns
