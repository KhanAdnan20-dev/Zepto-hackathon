# Zepto Hackathon - User Authentication App

A simple Flask web application with user registration and login functionality.

## Features

- User registration with username, email, password, and address
- User login with JWT token authentication  
- Clean, responsive HTML forms with CSS styling
- SQLite database for user storage
- Password hashing for security

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Usage

- **Register**: Create a new account with username, email, and password
- **Login**: Sign in with your credentials to receive a JWT token
- Navigate between registration and login pages using the provided links

## API Endpoints

- `GET /` - Home page (redirects to login)
- `GET /login` - Login page  
- `GET /register` - Registration page
- `POST /api/register` - Register new user (JSON)
- `POST /api/login` - Login user (JSON) 
- `GET /api/users` - List all users (for testing)

The application is now fully functional and ready to use!