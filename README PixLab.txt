README PixLab

## Authors

- Denis Albrecq  
- Margot Durou  

## Context

Script created for manual image annotation (target + distractors)  
and for generating binary masks in order to build a scoring function.  
This function is used to evaluate whether the `scanDDM` function correctly detects the target,  
based on the saliency map of the original image.

---

# PixLab Annotation Tool — Target & Distractors + Masks

This script lets you annotate `.png` images by defining:  
- **one target polygon (TARGET)**  
- **multiple distractor polygons (DISTRACTORS)**  

From these annotations, it generates:  
1. a **JSON** file containing points and descriptions  
2. an annotated image with outlines (target in red, distractors in white)  
3. two binary `.png` masks:  
   - **target mask**  
   - **distractors mask (merge of all distractors)**  

Finally, it displays a visual summary on **3 axes**:  
- original image + outlines  
- target mask  
- distractors mask  

---

## Features

### Mode 1 — Create a new JSON
The user manually selects polygons on the image:  
- left click → adds a point  
- `Backspace` or `u` → removes the last point  
- `Esc` → resets the polygon  
- `Enter` → validates the polygon  

Then the user can add as many distractors as they want.

### Mode 2 — Use an existing JSON
If you already have an annotation `.json` file, the script:  
- automatically reloads the polygons  
- recomputes the masks  
- saves the annotated image + masks  
- displays the 3 results  

No manual re-selection is needed.

---

## Produced file structure

Starting from an image:  
```
image.png
```

The script produces:  
```
image_annotations.json
image_annotated.png
image_mask_target.png
image_mask_distractors.png
```

---

## Generated JSON format

Example structure with four points:  

```json
{
  "target": {
    "points": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
    "description": "free description"
  },
  "distractors": [
    {
      "points": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
      "description": "free description"
    }
  ]
}
```

---

## Program inputs

The script asks the user several questions:

1. **Do you already have a JSON annotation file? (o/n)**  
   - `o` → switches to existing JSON mode  
   - `n` → switches to interactive annotation mode  

2. **PNG image name (without extension)**  
   - Example: if your file is `scene01.png`, answer `scene01`  
   - The image must be located in the folder defined by the `path` variable.

3. **If existing JSON mode = o**  
   → **JSON name (without extension)**  
   - Example: if your JSON is `scene01_annotations.json`, answer `scene01_annotations`

4. **If interactive annotation mode = n**  
   - Target selection by clicking  
   - Text description of the target  
   - Repeated addition of distractors, **with no predefined number**  
   - Text description for each distractor  

---

## Program outputs

After execution, you get:

1. **Annotation JSON**  
   - contains:  
     - the points (pixel coordinates)  
     - text descriptions  
   - saved as:  
     ```
     <image>_annotations.json
     ```

2. **Annotated image**  
   - target: red outline  
   - distractors: white outlines  
   - saved as:  
     ```
     <image>_annotated.png
     ```

3. **Target mask**  
   - **white pixels (255)** inside the target polygon  
   - **black pixels (0)** elsewhere  
   - saved as:  
     ```
     <image>_mask_target.png
     ```

4. **Distractors mask**  
   - merge of all distractors into a single mask  
   - **white pixels (255)** inside at least one distractor  
   - black pixels elsewhere  
   - saved as:  
     ```
     <image>_mask_distractors.png
     ```

5. **Final display**  
   - 3 matplotlib subplots:  
     1. image + outlines  
     2. target mask  
     3. distractors mask  

---

## Dependencies & Installation

Required dependencies:

- `numpy`  
- `matplotlib`  

They are listed in `requirements.txt`:

```txt
numpy>=1.23
matplotlib>=3.7
```

At launch, the script automatically checks:  
- if a dependency is missing, it runs:  
  ```bash
  pip install -r requirements.txt
  ```

> Recommended: use a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# mac / linux
source .venv/bin/activate

pip install -r requirements.txt
python script.py
```

---

## Important notes

- **At least 3 points are required** to form a valid polygon.  
- Distractors are optional:  
  - you can use 0, 1, or as many as you want.  
- Masks are generated **at the exact size of the original image**.  
- Coordinates saved in the JSON are float pixel values (x, y).  

---

## Quick customization

In `main()`, you can change the default directory:

```python
path = "C:/Users/.../PixLab"
```
