# Blog Platform API

A comprehensive blogging platform backend built with FastAPI, MongoDB, and JWT authentication. Features include user management, blog posts, comments, likes, tags, and image handling.

## Features

- **User Authentication**: JWT-based authentication with access and refresh tokens
- **Blog Management**: Create, read, update, delete blog posts
- **Comments System**: Add and manage comments on blog posts
- **Like/Dislike System**: Like or dislike blog posts
- **Tag System**: Categorize blogs with tags
- **Image Management**: Handle multiple images per blog post
- **Search Functionality**: Search blogs by title and content
- **Cookie-based Refresh Tokens**: Secure refresh token storage in HTTP-only cookies

## Technology Stack

- **FastAPI**: Modern, fast Python web framework
- **MongoDB**: NoSQL database with Motor async driver
- **JWT**: JSON Web Tokens for authentication
- **Pydantic**: Data validation using Python type annotations
- **Passlib**: Password hashing
- **Uvicorn**: ASGI server

## Project Structure

```
blog-backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration settings
├── database.py            # MongoDB connection setup
├── models.py              # Pydantic models
├── auth.py                # Authentication utilities
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── README.md             # Project documentation
└── routers/              # API route modules
    ├── __init__.py
    ├── auth.py           # Authentication routes
    ├── blogs.py          # Blog management routes
    ├── comments.py       # Comment system routes
    ├── likes.py          # Like/dislike routes
    ├── tags.py           # Tag management routes
    └── images.py         # Image handling routes
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Update the `.env` file with your MongoDB credentials:

```env
MONGODB_URL=mongodb+srv://your-username:your-password@cluster0.mongodb.net/blogging?retryWrites=true&w=majority
SECRET_KEY=your-super-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. Run the Application

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 4. API Documentation

- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login user (sets refresh token cookie)
- `POST /api/v1/auth/refresh` - Refresh access token using cookie
- `POST /api/v1/auth/logout` - Logout user (clears refresh token cookie)
- `GET /api/v1/auth/me` - Get current user profile

### Blogs

- `POST /api/v1/blogs/` - Create a new blog post
- `GET /api/v1/blogs/` - Get all published blogs (with pagination)
- `GET /api/v1/blogs/my-blogs` - Get current user's blogs
- `GET /api/v1/blogs/{blog_id}` - Get specific blog post
- `PUT /api/v1/blogs/{blog_id}` - Update blog post
- `DELETE /api/v1/blogs/{blog_id}` - Delete blog post
- `GET /api/v1/blogs/search/{query}` - Search blogs

### Comments

- `POST /api/v1/comments/blogs/{blog_id}` - Add comment to blog
- `GET /api/v1/comments/blogs/{blog_id}` - Get blog comments
- `GET /api/v1/comments/my-comments` - Get user's comments
- `DELETE /api/v1/comments/{comment_id}` - Delete comment

### Likes

- `POST /api/v1/likes/blogs/{blog_id}` - Like/dislike a blog
- `GET /api/v1/likes/blogs/{blog_id}/count` - Get like/dislike counts
- `GET /api/v1/likes/blogs/{blog_id}/my-like` - Get user's like status
- `DELETE /api/v1/likes/blogs/{blog_id}` - Remove like/dislike
- `GET /api/v1/likes/my-likes` - Get user's likes

### Tags

- `POST /api/v1/tags/` - Create a new tag
- `GET /api/v1/tags/` - Get all tags
- `GET /api/v1/tags/search/{query}` - Search tags
- `GET /api/v1/tags/{tag_id}` - Get specific tag
- `DELETE /api/v1/tags/{tag_id}` - Delete tag
- `GET /api/v1/tags/popular/` - Get popular tags

### Images

- `POST /api/v1/images/blogs/{blog_id}` - Add images to blog
- `GET /api/v1/images/blogs/{blog_id}` - Get blog images
- `PUT /api/v1/images/blogs/{blog_id}` - Update blog images
- `DELETE /api/v1/images/blogs/{blog_id}` - Delete blog images
- `GET /api/v1/images/my-images` - Get user's images

## Authentication Flow

1. **Register/Login**: User registers or logs in
2. **Token Generation**: Server generates access token and refresh token
3. **Cookie Storage**: Refresh token is stored in HTTP-only cookie
4. **API Access**: Use access token in Authorization header: `Bearer <access_token>`
5. **Token Refresh**: When access token expires, use `/auth/refresh` endpoint
6. **Logout**: Clear refresh token cookie

## Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "username": "string",
  "email": "string",
  "password_hash": "string",
  "refresh_token": "string",
  "created_at": "datetime"
}
```

### Blogs Collection
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "title": "string",
  "content": "string",
  "tag_ids": ["ObjectId"],
  "main_image_url": "string",
  "published": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Comments Collection
```json
{
  "_id": "ObjectId",
  "blog_id": "ObjectId",
  "text": "string",
  "created_at": "datetime"
}
```

### Likes Collection
```json
{
  "_id": "ObjectId",
  "blog_id": "ObjectId",
  "user_id": "ObjectId",
  "isLiked": "boolean"
}
```

### Tags Collection
```json
{
  "_id": "ObjectId",
  "name": "string"
}
```

### Images Collection
```json
{
  "_id": "ObjectId",
  "blog_id": "ObjectId",
  "image_url": ["string"],
  "uploaded_at": "datetime"
}
```

## Security Features

- **Password Hashing**: Bcrypt for secure password storage
- **JWT Tokens**: Secure access token with expiration
- **HTTP-only Cookies**: Refresh tokens stored securely
- **CORS Configuration**: Configurable cross-origin requests
- **Input Validation**: Pydantic models for request validation

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload
```

### Testing the API

Use the interactive documentation at `http://localhost:8000/docs` to test all endpoints.

## Production Deployment

1. Set `secure=True` for cookies in production (HTTPS)
2. Update CORS origins to specific domains
3. Use a strong SECRET_KEY
4. Configure proper MongoDB security
5. Set up proper logging and monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

