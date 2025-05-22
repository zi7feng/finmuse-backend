# run.py
from app import create_app, db
from sqlalchemy import text

app = create_app()

@app.route("/ping")
def ping():
    return {"message": "pong"}

if __name__ == "__main__":
    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
            print("✅ Database connected successfully.")
        except Exception as e:
            print("❌ Database connection failed:", e)

    app.run(debug=True)
