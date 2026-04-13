# Fire-detection-with-artificial-intelligence
Fire detection (based on location) with our own AI

🌲 Fire Detection: AI and Web-Based Early Warning System
This project is a comprehensive system that combines CNN-based deep learning models with modern web technologies for the early detection of forest fires. The system allows users to perform fire analysis on uploaded images, track current fire news, and provide location-based reporting.
🚀 Features
AI-Powered Detection: Analyzes images across 4 different classes: "No Fire" (y0), "Small Fire" (y1), "Large Fire" (y2), and "Sunrise/Sunset" (y3).False Alarm Prevention: Specifically trained to distinguish natural light conditions like sunrise and sunset, which are often confused with fire.News Tracking (Web Scraping): Automatically pulls the latest fire news from sources like CNN Türk.Interactive Map Integration: Features a system using Leaflet.js and OpenStreetMap to mark suspected fire locations and retrieve address information.Secure User Management: A membership and login system with strong password policies, supported by an SQLite databas

 Technologies Used
 Artificial Intelligence: Python, TensorFlow/PyTorch, ResNet50, and PIL
 .Web Backend: Flask (Python) and SQLite (DB Browser).
 Web Frontend: HTML5, CSS3, JavaScript, and Leaflet.js.
 Data Collection: BeautifulSoup/Selenium for Web Scraping.
 Development Environment: PyCharm

 📊 Model Performance
 Various models were tested during the project, and the most reliable results were obtained with Model 11.
 Test Accuracy: 82.14% 
 Best Validation Accuracy: 88.77%
 Training Duration: 35 Epochs
 Test Loss: 0.6141
 The transition from Model 9 to Model 10 was a critical turning point where class naming was standardized to ASCII (y0, y1, y2) to fix class mismatching issues, significantly increasing the reliability of the results.
 📝 Author
 Name & Surname: Ayşenur Mazak 
 University: Necmettin Erbakan University
 Department: Computer Engineering
 
