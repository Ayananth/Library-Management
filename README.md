# Book Management API

A Django REST API for managing users, books, and personal reading lists.

## Features

- JWT-based authentication
- User registration and login
- User profile and avatar management
- Book management
  - Authenticated users can create books
  - All users can view all books
  - Owners can delete their books
- Reading list management
  - Users can create, update, and delete their own reading lists
  - Users can add books to reading lists in a preferred order
  - Users can reorder and remove reading list items
- Informative error responses for validation, not found, and permission issues

## Tech Stack

- Python 3.10+
- Django
- Django REST Framework
- Simple JWT
- Pillow (image upload support)

## Project Structure

- `backend/` - Django project and apps (`users`, `books`, `reading_lists`)
- `pyproject.toml` - project dependencies/config
- `uv.lock` - locked dependency versions for reproducible installs
- `main.py` - optional starter script (not used by Django API runtime)

## Setup

### 1. Clone

```bash
git clone <repo-url>
cd "Book Management"
```

### 2. Install dependencies (uv)

```bash
uv sync
```

### 3. Configure environment

Create `backend/.env`:

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
```

### 4. Run migrations

```bash
uv run python backend/manage.py migrate
```

### 5. Run server

```bash
uv run python backend/manage.py runserver
```

Base URL: `http://127.0.0.1:8000`

## Authentication

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

Use login endpoint to get `access` and `refresh` tokens.

## API Endpoints

### Users (`/api/users/`)

1. `POST /api/users/register/`
- Description: Register a new user
- Auth: No
- Body:
```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "secret123",
  "confirm_password": "secret123"
}
```

2. `POST /api/users/login/`
- Description: Get JWT access and refresh tokens
- Auth: No
- Body:
```json
{
  "username": "john",
  "password": "secret123"
}
```

3. `POST /api/users/token/refresh/`
- Description: Refresh access token
- Auth: No
- Body:
```json
{
  "refresh": "<refresh_token>"
}
```

4. `GET /api/users/profile/`
- Description: Get current user profile (`username`, `email`, `avatar`)
- Auth: Yes

5. `PATCH /api/users/avatar/`
- Description: Upload/update avatar
- Auth: Yes
- Body: `multipart/form-data`
  - `avatar`: file

6. `DELETE /api/users/avatar/delete/`
- Description: Delete current user avatar
- Auth: Yes

### Books (`/api/books/`)

1. `GET /api/books/`
- Description: List all books
- Auth: No

2. `POST /api/books/`
- Description: Create a new book
- Auth: Yes
- Body:
```json
{
  "title": "Clean Code",
  "authors": "Robert C. Martin",
  "genre": "Software Engineering",
  "publication_date": "2008-08-01",
  "description": "Optional description"
}
```

3. `GET /api/books/<id>/`
- Description: Retrieve a single book
- Auth: No

4. `DELETE /api/books/<id>/delete/`
- Description: Delete a book (only creator can delete)
- Auth: Yes

### Reading Lists (`/api/reading-lists/`)

1. `GET /api/reading-lists/`
- Description: List current user's reading lists with ordered items
- Auth: Yes

2. `POST /api/reading-lists/`
- Description: Create reading list
- Auth: Yes
- Body:
```json
{
  "name": "My Favorites"
}
```

3. `GET /api/reading-lists/<id>/`
- Description: Get reading list details
- Auth: Yes (owner only)

4. `PATCH /api/reading-lists/<id>/`
- Description: Rename reading list
- Auth: Yes (owner only)
- Body:
```json
{
  "name": "Updated List Name"
}
```

5. `DELETE /api/reading-lists/<id>/`
- Description: Delete reading list
- Auth: Yes (owner only)

6. `POST /api/reading-lists/<id>/items/`
- Description: Add a book to reading list (optionally at a given order)
- Auth: Yes (owner only)
- Body:
```json
{
  "book_id": 1,
  "order": 1
}
```
- Note: `order` is optional; if omitted, item is appended to end.

7. `PATCH /api/reading-lists/<id>/items/<item_id>/`
- Description: Reorder an item within the reading list
- Auth: Yes (owner only)
- Body:
```json
{
  "order": 2
}
```

8. `DELETE /api/reading-lists/<id>/items/<item_id>/`
- Description: Remove a book from reading list
- Auth: Yes (owner only)

## Error Handling

Typical response patterns:

- `400 Bad Request`
  - Validation errors (missing/invalid fields)
  - Duplicate book in same reading list
  - Invalid order range
- `401 Unauthorized`
  - Missing or invalid JWT token on protected routes
- `403 Forbidden`
  - User trying to access or modify another user's protected resources
- `404 Not Found`
  - Missing book, reading list, or reading list item

## Notes

- Book `publication_date` cannot be in the future.
- Avatar upload requires `multipart/form-data`.
