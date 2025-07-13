// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
//import { getAnalytics } from "firebase/analytics";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyB444WUw0gRwHpGGozpuU38RWr_sAMK-F4",
  authDomain: "vibescape-58630.firebaseapp.com",
  projectId: "vibescape-58630",
  storageBucket: "vibescape-58630.firebasestorage.app",
  messagingSenderId: "977381358007",
  appId: "1:977381358007:web:d712f41b2d5a6be4f51032",
  measurementId: "G-7RC94HLNJS"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
//const analytics = getAnalytics(app);

// Initialize Firebase Auth
export const auth = getAuth(app);

// Initialize Google Auth Provider only
export const googleProvider = new GoogleAuthProvider();

// Configure Google Provider (optional)
googleProvider.setCustomParameters({
  prompt: 'select_account'
});

export default app; 