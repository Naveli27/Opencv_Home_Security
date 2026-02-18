import cv2
import os
import json
from deepface import DeepFace
import mediapipe as mp
from twilio.rest import Client
from keys import gemini_api_key, account_sid, auth_token, twilio_number, target
import google.generativeai as genai
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Flask App Initialization (if you are using the database)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///security_questions.db'  # Or your database URI
db = SQLAlchemy(app)

# Database Model (ensure this matches your models.py)
class SecurityQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Question: {self.question}>"

with app.app_context():
    db.create_all()

# Configure Gemini and Twilio
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("models/gemini-1.5-flash")
client = Client(account_sid, auth_token)

# Load known face images
known_faces_dir = "C:/AI security/training images"  # <--- ENSURE THIS PATH IS CORRECT
known_faces = {
    os.path.splitext(f)[0]: os.path.join(known_faces_dir, f)
    for f in os.listdir(known_faces_dir) if os.path.isfile(os.path.join(known_faces_dir, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg'))
}
print(f"Loaded known faces: {list(known_faces.keys())}")

# Load household database from JSON
users_json_path = "users.json"  # <--- ENSURE THIS PATH IS CORRECT
try:
    with open(users_json_path, "r") as f:
        household_data = json.load(f)
    print(f"Loaded household data from: {users_json_path}")
    print(f"Household members: {household_data.keys()}")
except Exception as e:
    print(f"❌ Error loading {users_json_path}: {e}")
    household_data = {}

# Setup MediaPipe face detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

def run_security_camera():
    print("Face database loaded. Camera started.")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Error: Could not open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Warning: Could not read frame. Exiting loop.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                h, w, _ = frame.shape
                x, y = int(bboxC.xmin * w), int(bboxC.ymin * h)
                width, height = int(bboxC.width * w), int(bboxC.height * h)
                face_crop = frame[y:y + height, x:x + width]

                if face_crop.size > 0:
                    temp_face_path = "temp_face.jpg"
                    cv2.imwrite(temp_face_path, face_crop)

                    match_found = False
                    label = "Unknown"

                    for name, known_path in known_faces.items():
                        try:
                            result = DeepFace.verify(
                                img1_path=temp_face_path,
                                img2_path=known_path,
                                model_name="Facenet",
                                enforce_detection=False
                            )
                            if result["verified"]:
                                match_found = True
                                label = name
                                break
                        except Exception as e:
                            print(f"❌ Error comparing face with {name}: {e}")

                    if not match_found:
                        print("🧠 Unknown person detected! Initiating LLM interrogation...")

                        try:
                            # === Step 1: Generate simple questions ===
                            q_prompt = (
                                "Generate 3 very simple and easy questions that can verify if someone is familiar with a household. "
                                "Avoid technical or detailed questions. Prefer questions like:\n"
                                "- What color is the front door?\n"
                                "- Do we have pets? If yes, name one.\n"
                                "- Where do we usually keep the keys?\n"
                                "The questions should be suitable for someone who casually lives or visits the home."
                            )
                            questions_response = model.generate_content(q_prompt)
                            questions = [q.strip("- ").strip() for q in questions_response.text.strip().split("\n") if q.strip()]
                            answers = []

                            print("\n🤖 Gemini asks:")
                            with app.app_context():
                                for q in questions:
                                    print(q)
                                    ans = input("👤 Answer: ")
                                    answers.append((q, ans))
                                    db.session.add(SecurityQuestion(question=q, answer=ans))
                                db.session.commit()

                            # === Step 2: Evaluate answers using household JSON ===
                            json_context = json.dumps(household_data, indent=2)
                            conversation = "\n".join([f"{q}\nAnswer: {a}" for q, a in answers])
                            decision_prompt = (
                                f"The following is the JSON household data:\n{json_context}\n\n"
                                f"The person has answered the following questions:\n{conversation}\n\n"
                                "Based on the household data, determine if this person is familiar with the household.\n"
                                "Respond in this format:\nSummary: <brief summary of answers>\nDecision: <KNOWN or UNKNOWN>\nConfidence: <0-100>"
                            )

                            decision_response = model.generate_content(decision_prompt)
                            result = decision_response.text.strip()

                            print("\n🔍 Gemini Decision:\n", result)

                            # === Step 3: Alert via Twilio if needed ===
                            if "UNKNOWN" in result.upper():
                                try:
                                    message = client.messages.create(
                                        body=f"⚠️ Alert: Unknown person detected!\n\n{result}",
                                        from_=twilio_number,
                                        to=target
                                    )
                                    print(f"🚨 Alert sent: {message.sid}")
                                except Exception as e:
                                    print(f"❌ Twilio error: {e}")
                            else:
                                print("✅ Person allowed by AI.")

                        except Exception as e:
                            print(f"❌ Gemini error during interrogation: {e}")

                    # Draw bounding box and label
                    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 255), 2)
                    cv2.putText(frame, label, (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.imshow("AI Security", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_security_camera()