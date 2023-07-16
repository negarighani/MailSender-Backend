import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException,Form
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from celery import Celery
from models import Category, User, Letter
from database import engine,Base
import uvicorn
from tasks import send_letter_task, send_letters_task

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
celery = Celery("tasks", broker="redis://localhost:6379/0")

# Database Initialization
def get_db():
    db = SessionLocal()
    try:
         return db
    finally:
         db.close()

@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories

@app.post("/users")
async def create_user(email: str = Form(...), categories: str = Form(...), time: str = Form(...), db: Session = Depends(get_db)):
    
    # Check if the email already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already exists")

    # Create a new user in the database
    user = User(email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    selected_categories = json.loads(categories)
    for category_id in selected_categories:
        category = db.query(Category).filter(Category.id == category_id).first()
        if category:
            user.categories.append(category)

    db.commit()
    send_letters_task(user.id,time)
    
    return user

@app.post("/letters")
async def create_letter(
    subject: str = Form(...),
    content: str = Form(...),
    categories: str = Form(...),
    db: Session = Depends(get_db)):
    letter = Letter(subject=subject, content=content)
    db.add(letter)
    db.commit()
    db.refresh(letter)
    
    selected_categories = json.loads(categories)
    for category_id in selected_categories:
        category = db.query(Category).filter(Category.id == category_id).first()
        if category:
            letter.categories.append(category)

    db.commit()

    # Serialize the letter object and pass it as an argument to the Celery task
    serialized_letter = {
        "id": letter.id,
        "subject": letter.subject,
        "content": letter.content,
        "categories":[category.id for category in letter.categories]
    }
    
    with get_db() as db:
        recipients = [user.email for user in db.query(User).all()]
        
    send_letter_task(serialized_letter,recipients)
        
    return letter

    
def register_categories():
    db = SessionLocal()
    categories = [
        'Technology',
        'Sports',
        'Fashion',
        'Health and Wellness',
        'Entertainment',
        'Business and Finance',
        'Travel',
        'Food and Cooking'
    ]
    for category_name in categories:
        existing_category = db.query(Category).filter(Category.name == category_name).first()
        if existing_category:
            continue

        category = Category(name=category_name)
        db.add(category)

    db.commit()

    print("Categories registered successfully!")

@app.on_event("startup")
def startup_event():
    # Create database tables
    Base.metadata.create_all(bind=engine)  
    register_categories()
    print("Tables created successfully")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
