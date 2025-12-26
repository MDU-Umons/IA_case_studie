This repository presents an application designed for visual search research, combining image labeling, video-based 3D Gaussian Splatting, and saliency analysis. 
We developed an interactive tool in python to annotate images by labeling targets and distractors, enabling controlled visual search datasets. 
In parallel, we use object-centered videos to train 3D Gaussian Splatting models, allowing the creation of 3D representations of objects used in the search tasks.

The pipeline includes tools to generate Gaussian splatting models from videos, render images from novel viewpoints, and analyze the resulting scenes using saliency maps to study visual attention. 
The repository provides the full codebase, datasets (images, videos, Gaussian splatting files), with a strong focus on reproducibility and experimental clarity.

This project aims to support principled visual search experiments by linking annotation, 3D scene modeling, and saliency-based analysis within a single, coherent framework.
