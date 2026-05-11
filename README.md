🌱 NEUROX: AI-Based Smart Waste Management System

---
## 🏆 BGI Hackathon Project
**Developed by:** Vikram Choure (Team NEUROX)

---
## 📥 Download Model

Due to GitHub size limitations, the trained model file is not included in this repository.

👉 Download the model from here:
https://drive.google.com/file/d/18ygTn3E5G_orL1tRjuJJIeul9L6IG-_m/view?usp=sharing

After downloading, place the file in the project folder before running the app.

📌 Overview

The **NEUROX Smart Waste Management System** is an AI-powered application designed to classify waste into different categories and provide appropriate disposal suggestions. This project aims to promote proper waste segregation and environmental sustainability using Machine Learning.

---

🎯 Objectives

- Develop an intelligent system for waste classification
- Assist users in proper waste disposal
- Promote environmental awareness using AI
- Apply Machine Learning to solve real-world problems in BGI Hackathon

---

❗ Problem Statement

Improper waste segregation leads to pollution, environmental damage, and inefficient recycling. Many people are unaware of how to correctly dispose of waste. This project solves this problem by providing an automated classification system.

---

💡 Proposed Solution

This system uses a **MobileNetV2-based Transfer Learning** model (optimized by NEUROX) to classify waste images into:

- Hazardous ☠️
- Non-Recyclable 🚫
- Organic 🌱
- Recyclable ♻️

It also provides disposal suggestions based on the predicted category.

---

⚙️ Features

- 📷 Image-based waste classification
- 🧠 AI-powered prediction using MobileNetV2 (High Accuracy)
- ♻️ Smart Disposal guidance for each category
- 🎨 Premium User interface using Streamlit
- 🌍 Multi-page Dashboard for better UX

---

🛠️ Tech Stack

- Python
- TensorFlow / Keras
- Streamlit
- NumPy
- Pillow
- MobileNetV2 (Transfer Learning)

---

🧠 Model Details

- Model: MobileNetV2 (Pre-trained on ImageNet)
- Input Size: 224 × 224 × 3
- Output: 4 classes
- Fine-tuning: Adam Optimizer with low learning rate
- Techniques: Data Augmentation, Dropout, GlobalAveragePooling

---

📁 Project Structure

waste-management/
│
├── database/ (Dataset)
│   ├── Hazardous/
│   ├── Non-Recyclable/
│   ├── Organic/
│   └── Recyclable/
│
├── model.py (Training Script)
├── app.py (Main Streamlit App)
├── waste_model.h5 (Trained Model)
├── requirements.txt
└── README.md

---

🚀 How to Run the Project

1. Install Dependencies
pip install -r requirements.txt

2. Train the Model
python model.py

3. Run the Application
streamlit run app.py

---

🖥️ Application Workflow

1. User uploads an image
2. Image is preprocessed (224x224)
3. NEUROX AI predicts waste category
4. Confidence score and classification result is displayed
5. Detailed disposal guidance is provided

---

📊 Results

- High accuracy classification into four categories
- Real-time predictions with confidence scores
- Optimized for mobile and desktop view

---

🔮 Future Scope

- IoT-based smart bin integration
- Real-time camera detection for public places
- Localization support (Multi-language)
- Reward system for proper recycling

---

👩‍💻 Developed By

- **Vikram Choure** (Lead Developer)
- **Team NEUROX**

---

🌍 Conclusion

This project by Team NEUROX demonstrates how Artificial Intelligence can be used to solve environmental problems. It encourages proper waste disposal and promotes sustainability.

---

♻️ Quote

"Think Green, Live Clean with NEUROX!"
