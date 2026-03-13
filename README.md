# Backend API

## Setup

1. Clone the repository.
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up .env file from .env.example
6. Run migrations: `flask db upgrade`
7. Run the app: `python run.py`

## API Endpoints

- Authentication: /auth
- Users: /users
- Apartments: /apartments
- etc.

## Testing

Run `pytest` to execute tests.