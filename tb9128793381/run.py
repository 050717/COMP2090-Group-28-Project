from app import create_app

app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("  香港大学生银行 - Backend API Server")
    print("  http://localhost:5001")
    print("=" * 50)
    app.run(debug=True, port=5001)
