# Vibe Scape 

> Discover places by vibe, not just reviews.

**Vibe Scape** is a mood-based location explorer — fetching real-time place data via TomTom, analyzing vibes using OpenRouter LLM, and storing results in MongoDB. Firebase handles secure user auth and image uploads. Built with React, Flask, and AI integration.

---

## 🔧 Features

- 🌐 Real-time place lookup (TomTom API)
- 🤖 Vibe analysis via OpenRouter LLM (context-aware review summarization)
- 🗄️ MongoDB Atlas database with Flask backend
- 🔒 Firebase Auth & Storage for secure user data and images
- ⚛️ Clean, mobile-first UI using React + Tailwind CSS

---

## 📹 Demo Walkthrough

🎥 [Watch the project demo video](https://www.youtube.com/watch?v=4BcVZ33jgdE)

---

## 🛠️ How to Run Locally

### ✅ Prerequisites

- Node.js ≥ 18  
- Python ≥ 3.10  
- MongoDB Atlas URI  
- Firebase Project (Admin SDK and Config)  
- OpenRouter API key  
- TomTom API key  

---

### 🔙 Backend Setup (`/server`)

```bash
cd server
python -m venv venv
venv\Scripts\activate       # For Windows
# source venv/bin/activate  # For Mac/Linux

pip install -r requirements.txt
Create a .env file inside server:

env
Copy
Edit
MONGO_URI=your-mongodb-uri
OPENROUTER_KEY=your-openrouter-key
TOMTOM_API_KEY=your-tomtom-api-key
FIREBASE_PROJECT_ID=your-firebase-id
# Load Firebase credentials securely in your app
Start Flask server:

bash
Copy
Edit
flask run
🔜 Frontend Setup (/client)
bash
Copy
Edit
cd ../client
npm install
Create a .env.local in client:

env
Copy
Edit
VITE_BACKEND_URL=http://localhost:5000
VITE_FIREBASE_APIKEY=your-key
VITE_FIREBASE_AUTHDOMAIN=your-domain
VITE_FIREBASE_PROJECT_ID=your-id
VITE_FIREBASE_STORAGE_BUCKET=your-bucket
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
Start React app:

bash
Copy
Edit
npm run dev
Visit: http://localhost:3000

## 🧠 Tech Stack

### Frontend
- ⚛️ React
- 💨 Tailwind CSS
- 🔥 Firebase (Auth + Storage)
- 🌐 Vite

### Backend
- 🐍 Flask
- 🌿 PyMongo (MongoDB driver for Python)
- 🔐 Python-dotenv (for environment management)
- 🌐 CORS and REST API structure

### Database & APIs
- MongoDB 
- 🗺️ TomTom API (Place search + coordinates)
- 🤖 OpenRouter (LLM API layer – Gemini, Claude, etc.)

### Deployment
- ▲ Vercel (for frontend)
- 🛤️ Railway / Render (for backend Flask server)

## Walkthrough
-https://www.youtube.com/watch?v=4BcVZ33jgdE