# Event Hub Backend - Quick Reference Guide

## API Quick Reference

### Authentication Endpoints

#### 1. Register User
```
POST /api/v1/auth/register
Content-Type: application/json

Request:
{
    "username": "john_doe",       # Required: 3-100 chars
    "email": "john@example.com",  # Required: valid email
    "password": "SecurePass123",  # Required: 6-100 chars
    "fullName": "John Doe",       # Required: 2-200 chars
    "role": "ORGANIZER"           # Optional: ORGANIZER or PARTICIPANT (default)
}

Response (200 OK):
{
    "token": "eyJhbGciOiJIUzI1NiJ9..."
}

Error Responses:
- 400 Bad Request: Validation failed or username/email already taken
- 400 Bad Request: Invalid role (only PARTICIPANT/ORGANIZER allowed)
```

#### 2. Login User
```
POST /api/v1/auth/login
Content-Type: application/json

Request:
{
    "username": "john_doe",      # Required
    "password": "SecurePass123"  # Required
}

Response (200 OK):
{
    "token": "eyJhbGciOiJIUzI1NiJ9..."
}

Error Responses:
- 400 Bad Request: Username or password not provided
- 401 Unauthorized: Invalid credentials
```

---

### Event Endpoints

#### 1. List All Events (Public)
```
GET /api/v1/events
Authorization: (optional)

Query Parameters:
- category: Optional, filters by category name (case-insensitive)

Response (200 OK):
[
    {
        "id": 1,
        "title": "Tech Conference",
        "description": "...",
        "date": "2024-12-15T10:00:00",
        "location": "San Francisco",
        "categoryId": 1,
        "categoryName": "Technology",
        "organizerId": 10,
        "organizerUsername": "john_doe"
    },
    ...
]

Examples:
- GET /api/v1/events → All events
- GET /api/v1/events?category=Technology → Events in Technology category
```

#### 2. Get Single Event (Public)
```
GET /api/v1/events/{id}
Authorization: (optional)

Response (200 OK):
{
    "id": 1,
    "title": "Tech Conference",
    ...
}

Error Responses:
- 500 Internal Server Error: Event not found
```

#### 3. List My Events (Authenticated)
```
GET /api/v1/events/mine
Authorization: Bearer <JWT_TOKEN>

Response (200 OK):
[
    {
        "id": 1,
        "title": "Event organized by me",
        ...
    },
    ...
]

Error Responses:
- 401 Unauthorized: Missing or invalid JWT token
```

#### 4. Create Event (Authenticated)
```
POST /api/v1/events
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

Request:
{
    "title": "Tech Conference 2024",              # Required: 1-200 chars
    "description": "Annual technology event",    # Required: 1-2000 chars
    "date": "2024-12-15T10:00:00",              # Required: ISO 8601 format, future date
    "location": "San Francisco Convention",     # Required: 1-255 chars
    "categoryId": 1                             # Required: valid category ID
}

Response (200 OK):
{
    "id": 5,
    "title": "Tech Conference 2024",
    ...
}

Error Responses:
- 400 Bad Request: Validation failed
- 401 Unauthorized: Invalid JWT
- 500 Internal Server Error: User not found, Category not found
```

#### 5. Update Event (Authenticated, Owner Only)
```
PUT /api/v1/events/{id}
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

Request: Same as Create Event

Response (200 OK): Updated event

Error Responses:
- 400 Bad Request: Validation failed
- 401 Unauthorized: Invalid JWT
- 403 Forbidden: You are not the organizer
- 500 Internal Server Error: Event/category not found
```

#### 6. Delete Event (Authenticated, Owner Only)
```
DELETE /api/v1/events/{id}
Authorization: Bearer <JWT_TOKEN>

Response: 204 No Content

Error Responses:
- 401 Unauthorized: Invalid JWT
- 403 Forbidden: You are not the organizer
- 500 Internal Server Error: Event not found
```

#### 7. Get Event Participants (Authenticated, Owner Only)
```
GET /api/v1/events/{id}/participants
Authorization: Bearer <JWT_TOKEN>

Response (200 OK):
[
    "jane_doe",
    "alice_smith",
    "bob_johnson"
]

Error Responses:
- 401 Unauthorized: Invalid JWT
- 403 Forbidden: You are not the organizer
- 500 Internal Server Error: Event not found
```

---

### Registration Endpoints

#### 1. Register for Event (Authenticated)
```
POST /api/v1/registrations/events/{eventId}
Authorization: Bearer <JWT_TOKEN>

Response: 204 No Content

Error Responses:
- 401 Unauthorized: Invalid JWT
- 409 Conflict: Already registered for this event
- 500 Internal Server Error: User or event not found
```

#### 2. Unregister from Event (Authenticated)
```
DELETE /api/v1/registrations/events/{eventId}
Authorization: Bearer <JWT_TOKEN>

Response: 204 No Content

Error Responses:
- 401 Unauthorized: Invalid JWT

Note: Idempotent - no error if not registered
```

---

### Category Endpoints

#### 1. List All Categories (Public)
```
GET /api/v1/categories
Authorization: (not required)

Response (200 OK):
[
    { "id": 1, "name": "Technology" },
    { "id": 2, "name": "Sports" },
    { "id": 3, "name": "Music" },
    ...
]
```

#### 2. Create Category (Authenticated, ORGANIZER Only)
```
POST /api/v1/categories
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

Request:
{
    "name": "Art & Culture"
}

Response (200 OK):
{
    "id": 5,
    "name": "Art & Culture"
}

Error Responses:
- 400 Bad Request: Category name not provided
- 401 Unauthorized: Invalid JWT
- 403 Forbidden: You don't have ORGANIZER role
```

---

## Database Schema

### users table
```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- BCrypt hashed
    full_name VARCHAR(200) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'PARTICIPANT'  -- ORGANIZER or PARTICIPANT
);
```

### categories table
```sql
CREATE TABLE categories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);
```

### events table
```sql
CREATE TABLE events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(2000) NOT NULL,
    date DATETIME NOT NULL,
    location VARCHAR(255) NOT NULL,
    category_id BIGINT NOT NULL,
    organizer_id BIGINT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (organizer_id) REFERENCES users(id)
);
```

### registrations table
```sql
CREATE TABLE registrations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL,
    UNIQUE KEY uk_registration_user_event (user_id, event_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);
```

---

## HTTP Status Codes Used

| Status | Meaning | When Used |
|--------|---------|-----------|
| 200 | OK | Successful GET, POST, PUT requests |
| 204 | No Content | Successful DELETE, registration/unregistration |
| 400 | Bad Request | Validation errors, invalid input |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Authorized but insufficient permissions (not organizer) |
| 409 | Conflict | Duplicate registration for event |
| 500 | Internal Server Error | Unexpected errors (user/event/category not found) |

---

## Authentication Flow

### Step 1: Register
```
POST /api/v1/auth/register
{
    "username": "john_doe",
    "password": "SecurePass123",
    "role": "ORGANIZER"
}
↓
Response: JWT token (valid for 24 hours)
```

### Step 2: Use Token in Requests
```
GET /api/v1/events/mine
Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
↓
Server:
1. Extract token from Authorization header
2. Validate signature using secret key
3. Check expiration
4. Extract username from token payload
5. Load user from database
6. Set authentication in Spring SecurityContext
7. Process request
```

### JWT Token Structure
```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqb2huX2RvZSIsImlhdCI6MTcwMTI4NDgwMCwiZXhwIjoxNzAxMzcxMjAwfQ.xxxxx
│                 │                                                                                           │
└─ Header ────────┘ └─ Payload ──────────────────────────────────────────────────────────────────────────────┘ └─ Signature
   Algorithm: HS256    {
   (HMAC-SHA256)          "sub": "john_doe",          // Subject (username)
                          "iat": 1701284800,          // Issued At (timestamp)
                          "exp": 1701371200           // Expiration (timestamp)
                       }

Expiration: 24 hours (86400000 milliseconds)
```

---

## Key Classes & Their Roles

### Controllers
- **AuthController** - Handles registration and login
- **EventController** - Handles event CRUD operations
- **RegistrationController** - Handles event registration/unregistration
- **CategoryController** - Handles category listing and creation

### Services
- **AuthServiceImpl** - Registration, login, JWT token generation
- **EventServiceImpl** - Event CRUD, filtering, ownership validation
- **RegistrationServiceImpl** - Event registration, duplicate prevention
- **CategoryServiceImpl** - Category CRUD

### Security
- **JwtUtil** - JWT token generation and validation
- **JwtFilter** - Intercepts requests, validates JWT, sets authentication
- **AppUserDetailsService** - Loads user details from database
- **SecurityConfig** - Configures Spring Security, defines security rules

### Data Models
- **User** - User account (id, username, email, password, role)
- **Event** - Event information (id, title, date, organizer, category)
- **Category** - Event category (id, name)
- **Registration** - Event registration link (user + event)

### DTOs (Data Transfer Objects)
- **RegisterRequest** - Incoming registration data
- **LoginRequest** - Incoming login credentials
- **EventRequest** - Incoming event data
- **EventResponse** - Outgoing event data
- **AuthResponse** - JWT token response

### Repositories
- **UserRepository** - Database access for users
- **EventRepository** - Database access for events
- **CategoryRepository** - Database access for categories
- **RegistrationRepository** - Database access for registrations

---

## Common Workflows

### Workflow 1: User Registration & Login
```
1. Frontend: POST /api/v1/auth/register with user details
2. Backend:
   - Validate input
   - Check username/email not taken
   - Hash password with BCrypt
   - Save user to database
   - Generate JWT token
3. Response: JWT token
4. Frontend: Store token (localStorage/session)
5. Frontend: Include token in all future requests
```

### Workflow 2: Create & List Events
```
1. Frontend: POST /api/v1/events with JWT
2. Backend:
   - Validate JWT
   - Extract username from token
   - Fetch user from database
   - Validate event data
   - Fetch category from database
   - Save event to database
3. Response: Created event

4. Frontend: GET /api/v1/events?category=Technology
5. Backend:
   - Query events filtered by category
   - Convert to EventResponse DTOs
6. Response: List of events
```

### Workflow 3: Event Registration
```
1. Frontend: POST /api/v1/registrations/events/5 with JWT
2. Backend:
   - Validate JWT
   - Extract participant username
   - Fetch user from database
   - Fetch event from database
   - Check if already registered
   - Create registration record
   - Save to database
3. Response: 204 No Content

4. Frontend: DELETE /api/v1/registrations/events/5 with JWT
5. Backend:
   - Validate JWT
   - Extract participant username
   - Find and delete registration
6. Response: 204 No Content
```

---

## Configuration

### application.properties
```properties
# Server
server.port=8080
spring.application.name=eventhub

# Database
spring.datasource.url=jdbc:mysql://localhost:3306/event_db
spring.datasource.username=event_user
spring.datasource.password=Event@123
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

# JPA/Hibernate
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.sql.init.mode=always

# JWT
app.jwt.secret=change-me-in-prod-change-me-in-prod-change-me-in-prod
app.jwt.expiration-ms=86400000

# Actuator
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

---

## Error Handling Summary

### Validation Errors (400)
- Username/email/password too short/long
- Email format invalid
- Event date not in future
- Missing required fields

### Authentication Errors (401)
- Missing JWT token
- Invalid JWT token
- Expired JWT token
- Corrupted JWT token
- Invalid login credentials

### Authorization Errors (403)
- User is not the organizer of the event
- User doesn't have ORGANIZER role

### Conflict Errors (409)
- Duplicate event registration
- Username already taken
- Email already registered

### Resource Not Found (500)
- User not found
- Event not found
- Category not found

---

## Security Features

✅ **Password Hashing** - BCrypt with 10 strength rounds
✅ **JWT Authentication** - Stateless token-based auth
✅ **Token Expiration** - 24 hours
✅ **CSRF Protection** - Disabled (not needed for stateless API)
✅ **Ownership Validation** - Users can only modify their own resources
✅ **Role-Based Access** - ORGANIZER vs PARTICIPANT roles
✅ **Input Validation** - JSR-303 annotations on all DTOs
✅ **Prepared Statements** - JPA prevents SQL injection

---

## Performance Tips

1. **Use JWT tokens** - No server-side session storage
2. **Enable lazy loading** - Related entities loaded on-demand
3. **Filter by category** - Avoid loading all events every time
4. **Use custom queries** - @Query allows optimized JPQL
5. **Keep token expiration reasonable** - 24 hours is good
6. **Index database columns** - Primary keys automatically indexed

---

## Development Commands

### Build Project
```bash
./mvnw clean install
```

### Run Application
```bash
./mvnw spring-boot:run
```

### Run Tests
```bash
./mvnw test
```

### Build JAR
```bash
./mvnw clean package
```

### Access H2 Console (Development)
```
http://localhost:8080/h2-console
JDBC URL: jdbc:h2:mem:testdb
```

### View API Documentation (if added)
```
http://localhost:8080/swagger-ui.html (requires Springdoc dependency)
```

---

## Troubleshooting

### Issue: 401 Unauthorized
**Solution:** Check if JWT token is:
- Present in Authorization header
- Starts with "Bearer "
- Not expired
- Not corrupted

### Issue: 403 Forbidden (Event Update)
**Solution:** Verify you are the event organizer:
- Check the event's organizerId matches your user ID
- Only event organizers can modify

### Issue: 409 Conflict (Registration)
**Solution:** You're already registered for this event
- Unregister first if you want to re-register

### Issue: 400 Bad Request
**Solution:** Check request validation:
- All required fields provided
- Field lengths within limits
- Email format valid
- Date is in future

### Issue: Database Connection Error
**Solution:** Verify MySQL is running:
```bash
# Check MySQL service
sudo systemctl status mysql

# Start MySQL
sudo systemctl start mysql
```

---

**For detailed architecture documentation, see: BACKEND_ARCHITECTURE_DOCUMENTATION.md**

**For visual request flows, see: REQUEST_FLOW_DIAGRAMS.md**
