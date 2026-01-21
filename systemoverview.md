# Event Hub Backend - Complete Architecture & Request Flow Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture Layers](#architecture-layers)
4. [Data Models & Relationships](#data-models--relationships)
5. [Request Flow Analysis](#request-flow-analysis)
6. [Security & Authentication](#security--authentication)
7. [API Endpoints](#api-endpoints)
8. [Service Layer Logic](#service-layer-logic)
9. [Database Layer](#database-layer)
10. [Exception Handling](#exception-handling)
11. [Configuration & Setup](#configuration--setup)

---

## System Overview

**Event Hub** is a Spring Boot-based REST API application that enables users to:
- Register and authenticate as either PARTICIPANT or ORGANIZER
- Create, read, update, and delete events
- Browse events by category
- Register/unregister for events
- Manage event categories

The application follows a **layered architecture pattern** with clear separation of concerns:
```
Frontend (Static Files) → Controller Layer → Service Layer → Repository Layer → Database (MySQL)
                              ↑
                         Security/JWT Layer
```

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | Spring Boot | 4.0.1 |
| **Language** | Java | 25 |
| **Database** | MySQL | Latest |
| **ORM** | Spring Data JPA (Hibernate) | Included in Spring Boot |
| **Security** | Spring Security | 4.0.1 |
| **JWT** | JJWT (JSON Web Token) | 0.12.6 |
| **Validation** | Jakarta Bean Validation | 4.0.1 |
| **Build Tool** | Maven | Bundled |
| **Server Port** | 8080 | Default |

**Key Dependencies:**
- `spring-boot-starter-data-jpa` - Database abstraction
- `spring-boot-starter-security` - Authentication & Authorization
- `spring-boot-starter-webmvc` - REST controller support
- `jjwt-api/impl/jackson` - JWT token generation and validation
- `mysql-connector-j` - MySQL JDBC driver

---

## Architecture Layers

### Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    1. PRESENTATION LAYER                     │
│                      (Controller Layer)                       │
│  AuthController | EventController | CategoryController       │
│  RegistrationController | UserController                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   2. SECURITY LAYER                          │
│  JwtFilter | JwtUtil | SecurityConfig                        │
│  AppUserDetailsService                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   3. SERVICE LAYER                           │
│  AuthService | EventService | RegistrationService           │
│  CategoryService | UserService                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   4. DATA ACCESS LAYER                       │
│              (Repository/DAO Layer)                           │
│  UserRepository | EventRepository | RegistrationRepository   │
│  CategoryRepository                                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   5. DATABASE LAYER                          │
│                    MySQL Database                            │
│  users | events | categories | registrations                 │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

**1. Controller Layer (Presentation)**
- Receives HTTP requests from frontend
- Validates request format via DTOs
- Delegates business logic to service layer
- Returns JSON responses

**2. Security Layer**
- Authenticates users via JWT tokens
- Extracts and validates bearer tokens
- Loads user details for authorization
- Enforces role-based access control

**3. Service Layer (Business Logic)**
- Implements core business rules
- Orchestrates database operations
- Performs data validation
- Manages transactions
- Converts entities to DTOs

**4. Data Access Layer (Repository)**
- Provides abstraction over database
- Executes CRUD operations
- Implements custom queries
- Manages entity relationships

**5. Database Layer**
- Stores persistent data
- Manages relationships via foreign keys
- Enforces constraints
- Provides query support

---

## Data Models & Relationships

### 1. User Entity
**Table:** `users`

```java
@Entity
@Table(name = "users")
public class User {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true, length = 100)
    private String username;
    
    @Column(nullable = false, unique = true, length = 150)
    private String email;
    
    @Column(nullable = false)
    private String password;  // BCrypt encrypted
    
    @Column(nullable = false, length = 200)
    private String fullName;
    
    @Column(nullable = false, length = 30)
    private String role = "PARTICIPANT";  // PARTICIPANT or ORGANIZER
}
```

**Purpose:** Stores user account information and authentication credentials
**Fields:**
- `id` - Primary key, auto-increment
- `username` - Unique identifier for login (3-100 chars)
- `email` - Unique email address (required for registration)
- `password` - BCrypt-hashed password
- `fullName` - User's display name
- `role` - User type (PARTICIPANT/ORGANIZER), defaults to PARTICIPANT

---

### 2. Category Entity
**Table:** `categories`

```java
@Entity
@Table(name = "categories")
public class Category {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String name;
}
```

**Purpose:** Categorizes events for easier browsing/filtering
**Fields:**
- `id` - Primary key
- `name` - Unique category name (e.g., "Technology", "Sports", "Music")

---

### 3. Event Entity
**Table:** `events`

```java
@Entity
@Table(name = "events")
public class Event {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, length = 200)
    private String title;
    
    @Column(nullable = false, length = 2000)
    private String description;
    
    @Column(nullable = false)
    private LocalDateTime date;  // Event date/time
    
    @Column(nullable = false, length = 255)
    private String location;
    
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "category_id", nullable = false)
    private Category category;  // Foreign key to categories
    
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "organizer_id", nullable = false)
    private User organizer;  // Foreign key to users
}
```

**Purpose:** Represents events that can be created and attended
**Fields:**
- `id` - Primary key
- `title` - Event name (max 200 chars)
- `description` - Detailed event information (max 2000 chars)
- `date` - When the event occurs (must be in future)
- `location` - Physical or virtual location
- `category` - Reference to category entity
- `organizer` - Reference to user who created the event

**Relationships:**
- **ManyToOne with Category**: Each event belongs to one category
- **ManyToOne with User**: Each event has one organizer
- **OneToMany with Registration**: One event can have multiple registrations

---

### 4. Registration Entity
**Table:** `registrations`

```java
@Entity
@Table(name = "registrations",
    uniqueConstraints = @UniqueConstraint(
        name = "uk_registration_user_event", 
        columnNames = {"user_id", "event_id"}
    )
)
public class Registration {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private User participant;
    
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "event_id", nullable = false)
    private Event event;
}
```

**Purpose:** Join table tracking which users are registered for which events
**Fields:**
- `id` - Primary key
- `participant` - Reference to user attending the event
- `event` - Reference to event being attended

**Constraints:**
- Composite unique constraint on (user_id, event_id) - prevents duplicate registrations

**Relationships:**
- **ManyToOne with User**: Multiple registrations can reference same user
- **ManyToOne with Event**: Multiple registrations can reference same event

---

### Entity Relationship Diagram (ERD)

```
┌─────────────┐
│   users     │
├─────────────┤
│ id (PK)     │
│ username    │
│ email       │
│ password    │
│ fullName    │
│ role        │
└──────┬──────┘
       │
       │ (1:N) organizer_id
       │
       ├────────────────────────┬──────────────────┐
       │                        │                  │
       ▼                        ▼                  │
┌──────────────┐       ┌──────────────┐          │
│   events     │       │registrations │          │
├──────────────┤       ├──────────────┤          │
│ id (PK)      │       │ id (PK)      │          │
│ title        │       │ user_id (FK) ├──────┐   │
│ description  │       │ event_id(FK) ├──┐   │   │
│ date         │       └──────────────┘  │   │   │
│ location     │                          │   │   │
│ category_id  │◄──────────────┐          │   │   │
│ organizer_id │◄──────────────┼──────────┘   │   │
└──────────────┘               │              │   │
       ▲                       │              │   │
       │                       │              └───┘
       │ (1:N) category_id     │
       │                       └───────────────┘
┌──────────────┐
│  categories  │
├──────────────┤
│ id (PK)      │
│ name         │
└──────────────┘
```

---

## Request Flow Analysis

### Request Processing Pipeline

Each HTTP request passes through the following sequence:

```
1. HTTP Request arrives → Spring DispatcherServlet
                              ↓
2. SecurityFilterChain (JwtFilter) - Authentication
                              ↓
3. URL Mapping → Appropriate Controller Method
                              ↓
4. Request Validation (JSR-303 annotations on DTOs)
                              ↓
5. Controller extracts Authentication object
                              ↓
6. Controller calls Service Method
                              ↓
7. Service executes Business Logic
   └─ Queries/Updates via Repository
   └─ Calls Database (MySQL)
                              ↓
8. Service returns Data/DTO
                              ↓
9. Controller wraps in ResponseEntity
                              ↓
10. Response serialized to JSON
                              ↓
11. HTTP Response sent to Frontend
```

---

### Authentication Flow (Detailed)

#### Registration Flow: `POST /api/v1/auth/register`

```
Frontend sends:
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "fullName": "John Doe",
    "role": "ORGANIZER"
}
        ↓
AuthController.register() receives RegisterRequest
        ↓
RequestValidation:
├─ @NotBlank - username, email, password, fullName required
├─ @Email - email format validation
├─ @Size - username (3-100), password (6-100), fullName (2-200)
└─ Returns 400 Bad Request if validation fails
        ↓
AuthServiceImpl.register() executes:
├─ Check: userRepository.existsByUsername("john_doe")
│         └─ If TRUE → throw IllegalArgumentException "Username already taken"
│
├─ Check: userRepository.existsByEmail("john@example.com")
│         └─ If TRUE → throw IllegalArgumentException "Email already registered"
│
├─ Create new User entity:
│   ├─ user.setUsername("john_doe")
│   ├─ user.setEmail("john@example.com")
│   ├─ user.setFullName("John Doe")
│   ├─ user.setPassword(passwordEncoder.encode("SecurePass123"))
│   │   └─ BCryptPasswordEncoder with strength 10
│   └─ user.setRole("ORGANIZER")
│       └─ Validation: Only "PARTICIPANT" or "ORGANIZER" allowed
│
├─ userRepository.save(user)
│   └─ Persists to database, generates ID
│
└─ jwtUtil.generateToken("john_doe")
   ├─ Creates JWT with claims:
   │   ├─ subject: "john_doe"
   │   ├─ issuedAt: current timestamp
   │   └─ expiration: current time + 86400000ms (24 hours)
   └─ Signs token with HMAC-SHA algorithm using secret key

Response:
{
    "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqb2huX2RvZSIsImlhdCI6MTcwMTI4NDgwMCwiZXhwIjoxNzAxMzcxMjAwfQ.xxxxx"
}
```

#### Login Flow: `POST /api/v1/auth/login`

```
Frontend sends:
{
    "username": "john_doe",
    "password": "SecurePass123"
}
        ↓
AuthController.login() receives LoginRequest
        ↓
RequestValidation:
├─ @NotBlank - username and password required
└─ Returns 400 Bad Request if validation fails
        ↓
AuthServiceImpl.login() executes:
├─ authenticationManager.authenticate(
│   new UsernamePasswordAuthenticationToken(
│       username: "john_doe",
│       password: "SecurePass123"
│   )
│ )
│
│ Authentication Process:
│ ├─ DaoAuthenticationProvider retrieves user details
│ ├─ AppUserDetailsService.loadUserByUsername("john_doe")
│ │  ├─ userRepository.findByUsername("john_doe")
│ │  ├─ Load password hash from database
│ │  ├─ Map role to Spring authority:
│ │  │  ├─ "ORGANIZER" → "ROLE_ORGANIZER"
│ │  │  └─ "PARTICIPANT" → "ROLE_USER"
│ │  └─ Return UserDetails object
│ │
│ ├─ PasswordEncoder.matches("SecurePass123", stored_hash)
│ │  └─ If FALSE → throw BadCredentialsException
│ │
│ └─ If authentication succeeds → return Authentication object
│
├─ If authentication fails → throw BadCredentialsException
│  └─ Returns 401 Unauthorized
│
└─ jwtUtil.generateToken("john_doe")
   └─ Create JWT token (same as registration)

Response:
{
    "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqb2huX2RvZSIsImlhdCI6MTcwMTI4NDgwMCwiZXhwIjoxNzAxMzcxMjAwfQ.xxxxx"
}
```

---

### Event Creation Flow: `POST /api/v1/events`

```
Frontend sends (with Authorization header):
Authorization: Bearer <jwt_token>
{
    "title": "Tech Conference 2024",
    "description": "Annual technology conference...",
    "date": "2024-12-15T10:00:00",
    "location": "San Francisco Convention Center",
    "categoryId": 1
}
        ↓
JwtFilter (Security Layer):
├─ Extract "Authorization" header
├─ Check if value starts with "Bearer "
├─ Extract token: substring(7)
├─ jwtUtil.isTokenValid(token)
│  ├─ Parse JWT using HMAC-SHA key
│  ├─ Verify signature
│  └─ If invalid → continue without authentication
│
├─ jwtUtil.extractUsername(token)
│  └─ Extract subject claim: "john_doe"
│
├─ AppUserDetailsService.loadUserByUsername("john_doe")
│  └─ Load user authorities from database
│
├─ Create UsernamePasswordAuthenticationToken
│  ├─ principal: UserDetails object
│  ├─ credentials: null (not needed for JWT)
│  ├─ authorities: [ROLE_ORGANIZER]
│  └─ details: WebAuthenticationDetails (IP, session ID)
│
└─ SecurityContextHolder.getContext().setAuthentication(token)
   └─ Stores in ThreadLocal for this request
        ↓
EventController.create() receives:
├─ Authentication object (extracted from SecurityContext)
├─ EventRequest DTO (validated)
│  ├─ @NotBlank - title, description, location
│  ├─ @NotNull - date, categoryId
│  ├─ @Future - date must be in future
│  ├─ @Size - title (max 200), description (max 2000), location (max 255)
│  └─ Returns 400 if validation fails
│
└─ Calls: eventService.create(
    authentication.getName(),  // "john_doe"
    eventRequest
  )
        ↓
EventServiceImpl.create() executes (Transactional):
├─ Get organizer user:
│  ├─ userRepository.findByUsername("john_doe")
│  └─ If not found → throw RuntimeException "User not found"
│
├─ Get category:
│  ├─ categoryRepository.findById(1L)
│  └─ If not found → throw RuntimeException "Category not found"
│
├─ Create Event entity:
│  ├─ event.setTitle("Tech Conference 2024")
│  ├─ event.setDescription("Annual technology conference...")
│  ├─ event.setDate(LocalDateTime.parse("2024-12-15T10:00:00"))
│  ├─ event.setLocation("San Francisco Convention Center")
│  ├─ event.setCategory(categoryObject)
│  └─ event.setOrganizer(userObject)
│
├─ eventRepository.save(event)
│  └─ INSERT into events table, generates event ID
│
└─ Convert to EventResponse:
   ├─ response.setId(1L)
   ├─ response.setTitle("Tech Conference 2024")
   ├─ response.setOrganizerId(user.getId())
   ├─ response.setOrganizerUsername("john_doe")
   ├─ response.setCategoryId(1L)
   ├─ response.setCategoryName("Technology")
   └─ ... other fields
        ↓
EventController returns ResponseEntity<EventResponse>:
├─ HTTP Status: 200 OK
└─ Response Body (JSON):
{
    "id": 1,
    "title": "Tech Conference 2024",
    "description": "Annual technology conference...",
    "date": "2024-12-15T10:00:00",
    "location": "San Francisco Convention Center",
    "categoryId": 1,
    "categoryName": "Technology",
    "organizerId": 10,
    "organizerUsername": "john_doe"
}
```

---

### Event Update Flow: `PUT /api/v1/events/{id}`

```
Frontend sends (with Authorization header):
Authorization: Bearer <jwt_token>
PUT /api/v1/events/1
{
    "title": "Tech Conference 2024 - Updated",
    "description": "Updated description...",
    "date": "2024-12-16T10:00:00",
    "location": "San Francisco Marriott",
    "categoryId": 2
}
        ↓
JwtFilter & Authentication (same as creation)
        ↓
EventController.update() receives:
├─ Authentication object
├─ pathVariable id = 1L
└─ EventRequest DTO (validated)
        ↓
EventServiceImpl.update() executes (Transactional):
├─ Fetch event:
│  ├─ eventRepository.findById(1L)
│  └─ If not found → throw RuntimeException "Event not found"
│
├─ Enforce ownership:
│  ├─ Check: event.getOrganizer().getUsername() == "john_doe"
│  └─ If not equal → throw AccessDeniedException
│       "You are not the organizer of this event"
│
├─ Get new category:
│  ├─ categoryRepository.findById(2L)
│  └─ If not found → throw RuntimeException "Category not found"
│
├─ Update event fields:
│  ├─ event.setTitle("Tech Conference 2024 - Updated")
│  ├─ event.setDescription("Updated description...")
│  ├─ event.setDate(LocalDateTime.parse("2024-12-16T10:00:00"))
│  ├─ event.setLocation("San Francisco Marriott")
│  ├─ event.setCategory(categoryObject)
│  └─ Note: organizer CANNOT be changed
│
├─ eventRepository.save(event)
│  └─ UPDATE events table where id = 1
│
└─ Return EventResponse (converted)
        ↓
Response: 200 OK with updated event details
```

---

### Event Listing Flow: `GET /api/v1/events?category=Technology`

```
Frontend sends (with optional Authorization):
GET /api/v1/events?category=Technology
        ↓
JwtFilter (optional - no authentication required)
        ↓
EventController.list() receives:
├─ category parameter: "Technology"
│  └─ Optional parameter (required = false)
│
└─ Calls: eventService.list("Technology")
        ↓
EventServiceImpl.list() executes (Transactional, readOnly):
├─ Check if category is null or blank:
│  ├─ If YES → eventRepository.findAll()
│  │           └─ SELECT * FROM events (no filtering)
│  └─ If NO  → eventRepository.findByCategoryName("Technology")
│              └─ Custom @Query:
│                 SELECT e FROM Event e 
│                 WHERE LOWER(e.category.name) = LOWER('Technology')
│
├─ Stream result → map each Event to EventResponse
└─ Collect into List<EventResponse>
        ↓
Response: 200 OK with JSON array
[
    {
        "id": 1,
        "title": "Tech Conference 2024",
        ...
    },
    {
        "id": 2,
        "title": "Web Development Workshop",
        ...
    }
]
```

---

### Event Registration Flow: `POST /api/v1/registrations/events/{eventId}`

```
Frontend sends (with Authorization):
Authorization: Bearer <jwt_token>
POST /api/v1/registrations/events/5
        ↓
JwtFilter & Authentication
        ↓
RegistrationController.register() receives:
├─ Authentication object (participant: "jane_doe")
└─ pathVariable eventId = 5L
        ↓
RegistrationServiceImpl.register() executes (Transactional):
├─ Get participant user:
│  ├─ userRepository.findByUsername("jane_doe")
│  └─ If not found → throw RuntimeException "User not found"
│
├─ Get event:
│  ├─ eventRepository.findById(5L)
│  └─ If not found → throw RuntimeException "Event not found"
│
├─ Check for duplicate registration:
│  ├─ registrationRepository.existsByParticipantIdAndEventId(
│      user.getId(), event.getId()
│    )
│  └─ If TRUE → throw AlreadyRegisteredException
│       "You have already registered for this event."
│       └─ Returns 409 Conflict HTTP status
│
├─ Create Registration entity:
│  ├─ registration.setParticipant(userObject)
│  └─ registration.setEvent(eventObject)
│
├─ registrationRepository.save(registration)
│  └─ INSERT into registrations table
│      (Creates link between user_id=jane_doe and event_id=5)
│
└─ Transaction commits
        ↓
Response: 204 No Content
(Empty response body, just HTTP status)
```

---

### Event Unregistration Flow: `DELETE /api/v1/registrations/events/{eventId}`

```
Frontend sends (with Authorization):
Authorization: Bearer <jwt_token>
DELETE /api/v1/registrations/events/5
        ↓
JwtFilter & Authentication
        ↓
RegistrationController.unregister() receives:
├─ Authentication object (participant: "jane_doe")
└─ pathVariable eventId = 5L
        ↓
RegistrationServiceImpl.unregister() executes (Transactional):
├─ Get participant user:
│  ├─ userRepository.findByUsername("jane_doe")
│  └─ If not found → throw RuntimeException "User not found"
│
├─ Find registration:
│  ├─ registrationRepository.findByParticipantIdAndEventId(
│      user.getId(), event.getId()
│    )
│  └─ Result is Optional<Registration>
│
├─ If registration exists:
│  ├─ registrationRepository.delete(registrationObject)
│  └─ DELETE FROM registrations WHERE user_id=jane_doe AND event_id=5
│
└─ If registration doesn't exist:
   └─ Do nothing (idempotent operation)
        ↓
Response: 204 No Content
```

---

### Get Event Participants Flow: `GET /api/v1/events/{id}/participants`

```
Frontend sends (with Authorization):
Authorization: Bearer <jwt_token>
GET /api/v1/events/5/participants
        ↓
JwtFilter & Authentication
        ↓
EventController.participants() receives:
├─ Authentication object (organizer: "john_doe")
└─ pathVariable id = 5L
        ↓
EventServiceImpl.participantsUsernames() executes (Transactional, readOnly):
├─ Get event:
│  ├─ eventRepository.findById(5L)
│  └─ If not found → throw RuntimeException "Event not found"
│
├─ Enforce ownership:
│  ├─ Check: event.getOrganizer().getUsername() == "john_doe"
│  └─ If not equal → throw AccessDeniedException
│       "You are not the organizer of this event"
│
├─ Get all registrations for event:
│  ├─ registrationRepository.findByEventId(5L)
│  └─ Returns List<Registration> (all participants)
│
├─ Stream and map:
│  ├─ For each registration → extract participant.getUsername()
│  └─ Collect into List<String>
│
└─ Return list of usernames
        ↓
Response: 200 OK
[
    "jane_doe",
    "alice_smith",
    "bob_johnson"
]
```

---

### Get Events by Organizer: `GET /api/v1/events/mine`

```
Frontend sends (with Authorization):
Authorization: Bearer <jwt_token>
GET /api/v1/events/mine
        ↓
JwtFilter & Authentication
        ↓
EventController.mine() receives:
├─ Authentication object (organizer: "john_doe")
│
└─ Calls: eventService.listMine("john_doe")
        ↓
EventServiceImpl.listMine() executes (Transactional, readOnly):
├─ Get user:
│  ├─ userRepository.findByUsername("john_doe")
│  └─ If not found → throw RuntimeException "User not found"
│
├─ Query events by organizer:
│  ├─ eventRepository.findByOrganizerId(user.getId())
│  └─ Returns List<Event> where organizer_id matches
│
├─ Stream and convert:
│  └─ Each Event → EventResponse DTO
│
└─ Return list of organizer's events
        ↓
Response: 200 OK
[
    { "id": 1, "title": "Tech Conference 2024", ... },
    { "id": 3, "title": "Python Workshop", ... }
]
```

---

### Category List Flow: `GET /api/v1/categories`

```
Frontend sends:
GET /api/v1/categories
(No authentication required - public endpoint)
        ↓
CategoryController.list() receives:
└─ No parameters
        ↓
CategoryServiceImpl.listAll() executes (Transactional, readOnly):
├─ categoryRepository.findAll()
│  └─ SELECT * FROM categories
│
└─ Return List<Category>
        ↓
Response: 200 OK
[
    { "id": 1, "name": "Technology" },
    { "id": 2, "name": "Sports" },
    { "id": 3, "name": "Music" },
    { "id": 4, "name": "Food & Beverage" }
]
```

---

### Create Category Flow: `POST /api/v1/categories`

```
Frontend sends (with Authorization):
Authorization: Bearer <jwt_token>
POST /api/v1/categories
{
    "name": "Art & Culture"
}
        ↓
JwtFilter & Authentication
        ↓
CategoryController.create() receives:
├─ Category object
├─ @PreAuthorize("hasRole('ORGANIZER')")
│  ├─ Check if user has ROLE_ORGANIZER
│  └─ If FALSE → throw AccessDeniedException (403 Forbidden)
│
└─ Calls: categoryService.create("Art & Culture")
        ↓
CategoryServiceImpl.create() executes (Transactional):
├─ Create Category entity:
│  └─ category.setName("Art & Culture")
│
├─ categoryRepository.save(category)
│  └─ INSERT into categories table, generates ID
│
└─ Return Category (with generated ID)
        ↓
Response: 200 OK
{
    "id": 5,
    "name": "Art & Culture"
}
```

---

## Security & Authentication

### JWT (JSON Web Token) Architecture

#### Token Structure
```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqb2huX2RvZSIsImlhdCI6MTcwMTI4NDgwMCwiZXhwIjoxNzAxMzcxMjAwfQ.xxxxx

Three parts separated by dots:
├─ Header: eyJhbGciOiJIUzI1NiJ9
│  Decoded: {"alg":"HS256"}
│  └─ Algorithm: HMAC with SHA-256
│
├─ Payload: eyJzdWIiOiJqb2huX2RvZSIsImlhdCI6MTcwMTI4NDgwMCwiZXhwIjoxNzAxMzcxMjAwfQ
│  Decoded: {
│      "sub": "john_doe",           # Subject (username)
│      "iat": 1701284800,           # Issued At (timestamp)
│      "exp": 1701371200            # Expiration (timestamp)
│  }
│
└─ Signature: xxxxx
   └─ HMAC-SHA256(header + payload, SECRET_KEY)
```

#### Configuration
```properties
# In application.properties
app.jwt.secret=change-me-in-prod-change-me-in-prod-change-me-in-prod
app.jwt.expiration-ms=86400000  # 24 hours in milliseconds
```

#### JwtUtil Component (Token Generation & Validation)

**Token Generation:**
```java
public String generateToken(String username) {
    Date now = new Date();
    Date expiry = new Date(now.getTime() + expirationMs);
    return Jwts.builder()
            .subject(username)                    // Payload: sub claim
            .issuedAt(now)                        // Payload: iat claim
            .expiration(expiry)                   // Payload: exp claim
            .signWith(key)                        // Sign with HMAC-SHA256
            .compact();                           // Serialize to string
}
```

**Token Validation:**
```java
public boolean isTokenValid(String token) {
    try {
        Jwts.parser()
            .verifyWith((javax.crypto.SecretKey) key)  // Verify signature
            .build()
            .parseSignedClaims(token)                   // Parse and verify
            .getPayload();
        return true;
    } catch (Exception e) {
        return false;  // Invalid token (expired, tampered, etc.)
    }
}
```

**Username Extraction:**
```java
public String extractUsername(String token) {
    return extractAllClaims(token).getSubject();  // Get "sub" claim
}
```

---

### Security Filter Chain

#### JwtFilter (OncePerRequestFilter)
**Purpose:** Intercepts every HTTP request to validate JWT tokens

```
HTTP Request
    ↓
JwtFilter.doFilterInternal()
    ├─ Step 1: Extract Authorization header
    │  ├─ Check if header exists
    │  ├─ Check if starts with "Bearer "
    │  └─ Extract token (skip "Bearer " prefix)
    │
    ├─ Step 2: Validate token
    │  ├─ Call jwtUtil.isTokenValid(token)
    │  ├─ If FALSE → continue without authentication
    │  └─ If TRUE → proceed to step 3
    │
    ├─ Step 3: Extract username
    │  ├─ jwtUtil.extractUsername(token)
    │  └─ Result: authenticated username
    │
    ├─ Step 4: Load user details
    │  ├─ AppUserDetailsService.loadUserByUsername(username)
    │  ├─ Queries: userRepository.findByUsername(username)
    │  ├─ Maps role to Spring authority
    │  │  ├─ "ORGANIZER" → "ROLE_ORGANIZER"
    │  │  └─ "PARTICIPANT" → "ROLE_USER"
    │  └─ Returns UserDetails object
    │
    ├─ Step 5: Create Authentication token
    │  ├─ new UsernamePasswordAuthenticationToken(
    │  │     userDetails,
    │  │     null,           // credentials
    │  │     authorities     // [ROLE_ORGANIZER]
    │  │ )
    │  └─ setDetails(webAuthDetailsSource.buildDetails(request))
    │
    ├─ Step 6: Set authentication in SecurityContext
    │  ├─ SecurityContextHolder.getContext().setAuthentication(auth)
    │  └─ Available throughout request processing
    │
    └─ Step 7: Continue filter chain
       └─ filterChain.doFilter(request, response)
    ↓
    Controller receives Authentication object
    (with username, role, credentials)
```

---

### Authentication Manager Setup

```java
@Bean
public AuthenticationManager authenticationManager() {
    DaoAuthenticationProvider authProvider = new DaoAuthenticationProvider();
    authProvider.setUserDetailsService(userDetailsService);
    authProvider.setPasswordEncoder(passwordEncoder());
    return new ProviderManager(authProvider);
}
```

**Flow during login:**
1. User provides username & password
2. AuthenticationManager passes to DaoAuthenticationProvider
3. DaoAuthenticationProvider:
   - Calls AppUserDetailsService.loadUserByUsername()
   - Gets UserDetails (username, password hash, authorities)
   - Calls PasswordEncoder.matches(plain_password, hash)
   - If match → authentication successful
   - If no match → throw BadCredentialsException

---

### Security Configuration (SecurityConfig)

```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http
        // Disable CSRF (not needed for stateless REST API)
        .csrf(csrf -> csrf.disable())
        
        // Enable CORS (allow frontend requests)
        .cors(Customizer.withDefaults())
        
        // Stateless session (no cookies, only JWT)
        .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        
        // URL Authorization
        .authorizeHttpRequests(auth -> auth
            // Public endpoints (no auth required)
            .requestMatchers(
                "/",
                "/index.html",
                "/favicon.ico",
                "/error",
                "/static/**",      // CSS, JS files
                "/**/*.css",
                "/**/*.js"
            ).permitAll()
            
            // Auth endpoints (public)
            .requestMatchers("/api/v1/auth/**").permitAll()
            
            // Actuator & H2 Console (for development)
            .requestMatchers("/h2-console/**", "/actuator/**").permitAll()
            
            // All other endpoints require authentication
            .anyRequest().authenticated()
        )
        
        // Disable frame options (for H2 console)
        .headers(headers -> headers.frameOptions(frame -> frame.disable()))
    
    // Add JWT filter before Spring Security's UsernamePasswordAuthenticationFilter
    http.addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
    
    return http.build();
}
```

---

### Authorization & Role-Based Access Control

#### Role Mapping
```java
// In AppUserDetailsService
String authority = "ROLE_" + ("ORGANIZER".equals(role) ? "ORGANIZER" : "USER");
// ORGANIZER → ROLE_ORGANIZER
// PARTICIPANT → ROLE_USER
```

#### Method-Level Authorization
```java
@PreAuthorize("hasRole('ORGANIZER')")
public ResponseEntity<Category> create(@RequestBody Category category) {
    // Only users with ROLE_ORGANIZER can call this
    // Returns 403 Forbidden if authorization fails
}
```

#### Service-Level Authorization (Example in EventServiceImpl)
```java
private void enforceOwnership(String organizerUsername, Event event) {
    String actualOrganizer = event.getOrganizer().getUsername();
    if (!actualOrganizer.equals(organizerUsername)) {
        throw new AccessDeniedException(
            "You are not the organizer of this event"
        );
    }
}
// Called in update() and delete() to ensure only organizer can modify
```

---

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Auth | Description | Request Body |
|--------|----------|------|-------------|--------------|
| POST | `/api/v1/auth/register` | ❌ | Register new user | `RegisterRequest` |
| POST | `/api/v1/auth/login` | ❌ | Login user | `LoginRequest` |

**RegisterRequest DTO:**
```json
{
    "username": "john_doe",       // 3-100 chars
    "email": "john@example.com",  // Valid email
    "password": "SecurePass123",  // 6-100 chars
    "fullName": "John Doe",       // 2-200 chars
    "role": "ORGANIZER"           // Optional: PARTICIPANT (default) or ORGANIZER
}
```

**LoginRequest DTO:**
```json
{
    "username": "john_doe",
    "password": "SecurePass123"
}
```

**AuthResponse DTO:**
```json
{
    "token": "eyJhbGciOiJIUzI1NiJ9..."
}
```

---

### Event Endpoints

| Method | Endpoint | Auth | Description | Permission |
|--------|----------|------|-------------|-----------|
| GET | `/api/v1/events` | ❌ | List all events (optionally filter by category) | Public |
| GET | `/api/v1/events/{id}` | ❌ | Get single event | Public |
| GET | `/api/v1/events/mine` | ✅ | List user's events | Organizer only |
| POST | `/api/v1/events` | ✅ | Create event | Authenticated user |
| PUT | `/api/v1/events/{id}` | ✅ | Update event | Event organizer only |
| DELETE | `/api/v1/events/{id}` | ✅ | Delete event | Event organizer only |
| GET | `/api/v1/events/{id}/participants` | ✅ | Get event participants | Event organizer only |

**EventRequest DTO (Create/Update):**
```json
{
    "title": "Tech Conference",           // 1-200 chars, required
    "description": "Annual tech event",  // 1-2000 chars, required
    "date": "2024-12-15T10:00:00",       // ISO 8601, future date, required
    "location": "San Francisco",          // 1-255 chars, required
    "categoryId": 1                       // Valid category ID, required
}
```

**EventResponse DTO:**
```json
{
    "id": 1,
    "title": "Tech Conference",
    "description": "Annual tech event",
    "date": "2024-12-15T10:00:00",
    "location": "San Francisco",
    "categoryId": 1,
    "categoryName": "Technology",
    "organizerId": 10,
    "organizerUsername": "john_doe"
}
```

---

### Registration Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/registrations/events/{eventId}` | ✅ | Register for event |
| DELETE | `/api/v1/registrations/events/{eventId}` | ✅ | Unregister from event |

**Response:** 204 No Content (success) or 409 Conflict (already registered)

---

### Category Endpoints

| Method | Endpoint | Auth | Description | Permission |
|--------|----------|------|-------------|-----------|
| GET | `/api/v1/categories` | ❌ | List all categories | Public |
| POST | `/api/v1/categories` | ✅ | Create category | ORGANIZER role only |

**Category Request/Response:**
```json
{
    "id": 1,
    "name": "Technology"
}
```

---

## Service Layer Logic

### AuthServiceImpl

**Responsibilities:**
- User registration with validation
- User authentication
- JWT token generation

**Key Methods:**

1. **register(RegisterRequest)**
   - Validates username/email uniqueness
   - Validates role (PARTICIPANT or ORGANIZER)
   - Encodes password using BCrypt
   - Saves user to database
   - Returns JWT token

2. **login(LoginRequest)**
   - Uses AuthenticationManager to authenticate credentials
   - If authentication succeeds, generates JWT token
   - Returns token

---

### EventServiceImpl

**Responsibilities:**
- Event CRUD operations
- Event filtering and querying
- Authorization (ownership checks)
- Organizer-specific operations

**Key Methods:**

1. **create(organizerUsername, EventRequest)**
   - Fetches organizer user
   - Validates category exists
   - Creates Event entity
   - Sets relationships (organizer, category)
   - Saves and returns EventResponse

2. **update(organizerUsername, eventId, EventRequest)**
   - Fetches event
   - Enforces organizer ownership
   - Updates event fields
   - Saves updated entity

3. **delete(organizerUsername, eventId)**
   - Fetches event
   - Enforces organizer ownership
   - Deletes event from database

4. **list(categoryName)**
   - If categoryName null → fetch all events
   - Else → fetch events filtered by category (case-insensitive)
   - Converts all to EventResponse DTOs

5. **listMine(organizerUsername)**
   - Fetches user by username
   - Queries events where organizer_id = user.id
   - Returns list of user's events

6. **participantsUsernames(organizerUsername, eventId)**
   - Fetches event
   - Enforces organizer ownership
   - Queries all registrations for event
   - Extracts participant usernames
   - Returns list

7. **getById(eventId)**
   - Fetches event by ID
   - Returns EventResponse
   - Returns 404 if not found

---

### RegistrationServiceImpl

**Responsibilities:**
- Event registration/unregistration
- Duplicate registration prevention

**Key Methods:**

1. **register(participantUsername, eventId)**
   - Fetches participant user
   - Fetches event
   - Checks for existing registration (duplicate prevention)
   - Creates Registration entity
   - Saves to database

2. **unregister(participantUsername, eventId)**
   - Fetches participant user
   - Finds registration by user_id and event_id
   - Deletes if found (idempotent)

---

### CategoryServiceImpl

**Responsibilities:**
- Category management

**Key Methods:**

1. **listAll()**
   - Fetches all categories
   - Returns List<Category>

2. **create(name)**
   - Creates Category entity
   - Sets name
   - Saves to database

---

## Database Layer

### Repository Pattern (Data Access Abstraction)

All repositories extend `JpaRepository<Entity, Long>` which provides:
- `save(entity)` - INSERT/UPDATE
- `findById(id)` - SELECT by primary key
- `findAll()` - SELECT all
- `delete(entity)` - DELETE
- Plus many more...

### Custom Repository Methods

**UserRepository:**
```java
Optional<User> findByUsername(String username);
boolean existsByUsername(String username);
boolean existsByEmail(String email);
```

**EventRepository:**
```java
// Custom @Query with JPQL (HQL)
@Query("select e from Event e where lower(e.category.name) = lower(:categoryName)")
List<Event> findByCategoryName(@Param("categoryName") String categoryName);

// Derived query method
List<Event> findByOrganizerId(Long organizerId);
```

**RegistrationRepository:**
```java
boolean existsByParticipantIdAndEventId(Long participantId, Long eventId);
Optional<Registration> findByParticipantIdAndEventId(Long participantId, Long eventId);
List<Registration> findByEventId(Long eventId);
```

**CategoryRepository:**
```java
Optional<Category> findByNameIgnoreCase(String name);
```

---

### Transaction Management

**@Transactional Annotation:**

```java
// Read-only transaction
@Transactional(readOnly = true)
public List<EventResponse> list(String categoryName) {
    // Optimized for reads
    // Session doesn't track changes
}

// Write transaction (default)
@Transactional
public EventResponse create(String organizerUsername, EventRequest request) {
    // Tracks entity changes
    // Auto-commits on success
    // Rolls back on exception
}
```

**Transaction Lifecycle:**
1. Spring opens database transaction
2. Method executes
3. If no exception → transaction commits automatically
4. If exception thrown → transaction rolls back (no partial updates)

---

### Database Schema

**Table: users**
```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'PARTICIPANT'
);
```

**Table: categories**
```sql
CREATE TABLE categories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);
```

**Table: events**
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

**Table: registrations**
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

## Exception Handling

### Exception Types & HTTP Status Codes

| Exception | HTTP Status | Thrown When |
|-----------|-------------|------------|
| `RuntimeException` | 500 Internal Server Error | User/Event/Category not found |
| `IllegalArgumentException` | 400 Bad Request | Invalid input (during registration) |
| `AccessDeniedException` | 403 Forbidden | Unauthorized access (not organizer) |
| `AlreadyRegisteredException` | 409 Conflict | Duplicate event registration |
| `BadCredentialsException` | 401 Unauthorized | Invalid login credentials |
| `UsernameNotFoundException` | 401 Unauthorized | User doesn't exist (during login) |
| `MethodArgumentNotValidException` | 400 Bad Request | DTO validation fails (@Valid) |

### Exception Throwing Points

**Registration:**
```java
if (userRepository.existsByUsername(request.getUsername())) {
    throw new IllegalArgumentException("Username already taken");
    // → 400 Bad Request
}

if (userRepository.existsByEmail(request.getEmail())) {
    throw new IllegalArgumentException("Email already registered");
    // → 400 Bad Request
}

if (!role.equals("PARTICIPANT") && !role.equals("ORGANIZER")) {
    throw new IllegalArgumentException("Invalid role");
    // → 400 Bad Request
}
```

**Event Operations:**
```java
User organizer = userRepository.findByUsername(organizerUsername)
    .orElseThrow(() -> new RuntimeException("User not found"));
    // → 500 Internal Server Error

Category category = categoryRepository.findById(request.getCategoryId())
    .orElseThrow(() -> new RuntimeException("Category not found"));
    // → 500 Internal Server Error

Event event = eventRepository.findById(eventId)
    .orElseThrow(() -> new RuntimeException("Event not found"));
    // → 500 Internal Server Error

enforceOwnership(organizerUsername, event);
// → AccessDeniedException if not organizer
// → 403 Forbidden
```

**Registration Operations:**
```java
if (registrationRepository.existsByParticipantIdAndEventId(user.getId(), event.getId())) {
    throw new AlreadyRegisteredException("Already registered");
    // → 409 Conflict
}
```

---

## Configuration & Setup

### Application Properties

```properties
# Server Configuration
spring.application.name=eventhub
server.port=8080

# Database Configuration
spring.datasource.url=jdbc:mysql://localhost:3306/event_db
spring.datasource.username=event_user
spring.datasource.password=Event@123
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

# JPA/Hibernate Configuration
spring.jpa.hibernate.ddl-auto=update          # Auto-create/update tables
spring.jpa.show-sql=true                      # Log SQL queries
spring.sql.init.mode=always                   # Initialize data

# JWT Configuration
app.jwt.secret=change-me-in-prod-...         # HMAC key
app.jwt.expiration-ms=86400000                # 24 hours

# Actuator Configuration
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Spring Boot Application Entry Point

```java
@SpringBootApplication
public class EventHubApplication {
    public static void main(String[] args) {
        SpringApplication.run(EventHubApplication.class, args);
    }
}
```

**@SpringBootApplication includes:**
- `@Configuration` - Class is a Spring config source
- `@ComponentScan` - Scans for @Component, @Service, @Repository, etc.
- `@EnableAutoConfiguration` - Configures Spring Boot based on classpath JARs

**Initialization Flow:**
1. Classpath scanning discovers all components
2. Dependency injection creates bean instances
3. SecurityConfig bean creates security filter chain
4. JwtFilter bean created
5. All repositories created (backed by JPA)
6. All services created
7. All controllers created
8. Embedded Tomcat starts on port 8080

---

## Request-Response Flow Summary

```
┌────────────────────────────────────────────────────────────────────┐
│                         COMPLETE REQUEST CYCLE                      │
└────────────────────────────────────────────────────────────────────┘

1. FRONTEND sends HTTP request
   ├─ URL: /api/v1/events
   ├─ Method: POST
   ├─ Headers: { Authorization: Bearer <JWT> }
   └─ Body: JSON payload

2. SPRING DISPATCHERSERVLET receives request
   └─ Route to appropriate handler

3. SECURITY FILTER CHAIN
   ├─ JwtFilter intercepts request
   ├─ Extract, validate, and parse JWT
   ├─ Load user details from database
   ├─ Set Authentication in SecurityContext
   └─ Continue filter chain

4. CONTROLLER LAYER (@RestController)
   ├─ Receive request
   ├─ Extract path variables, query params
   ├─ Get Authentication object from SecurityContext
   ├─ Validate DTO with @Valid annotations
   │  └─ If validation fails → return 400 Bad Request
   └─ Call appropriate service method

5. SERVICE LAYER (@Service, @Transactional)
   ├─ Receive parameters from controller
   ├─ Execute business logic
   ├─ Perform authorization checks
   ├─ Query/modify database via repositories
   ├─ Convert entity to DTO
   └─ Return result

6. REPOSITORY LAYER (JpaRepository)
   ├─ Receive method call
   ├─ Generate SQL query
   ├─ Execute against database
   └─ Return entity/list

7. DATABASE
   ├─ Execute SQL
   ├─ Return results
   └─ Handle transactions

8. EXCEPTION HANDLING (if needed)
   ├─ Spring catches exceptions
   ├─ Maps to HTTP status code
   └─ Returns error response

9. RESPONSE CONVERSION
   ├─ Service returns data
   ├─ Controller wraps in ResponseEntity
   ├─ Object serialized to JSON
   └─ HTTP headers set

10. RESPONSE sent to FRONTEND
    ├─ HTTP Status Code (200, 400, 401, 403, 409, 500, etc.)
    ├─ Headers (Content-Type: application/json)
    └─ Body (JSON)
```

---

## Summary of Key Concepts

### Dependency Injection (IoC)
Spring manages object creation and injection:
```java
@Service
public class EventServiceImpl implements EventService {
    // Spring automatically provides repositories
    public EventServiceImpl(
        EventRepository eventRepository,      // Injected
        UserRepository userRepository         // Injected
    ) {
        this.eventRepository = eventRepository;
        this.userRepository = userRepository;
    }
}
```

### Aspect-Oriented Programming (AOP)
`@Transactional` is implemented as AOP aspect:
```java
@Transactional
public EventResponse create(...) {
    // Intercepted by Spring TransactionAspect
    // Begins transaction before method
    // Commits after method completes
    // Rolls back on exception
}
```

### Stateless Authentication
JWT enables stateless requests (no sessions):
- No session stored on server
- Token contains all auth info
- Each request is independent
- Scalable across multiple servers

### Lazy Loading
```java
@ManyToOne(fetch = FetchType.LAZY)
private User organizer;
// Organizer not fetched until accessed
// Reduces database queries
```

### Query Derivation
```java
List<Event> findByOrganizerId(Long organizerId);
// Spring generates SQL automatically:
// SELECT * FROM events WHERE organizer_id = ?
```

---

## Performance Considerations

1. **Lazy Loading** - Related entities loaded on-demand, not eagerly
2. **Read-Only Transactions** - `readOnly = true` optimizes read operations
3. **Custom Queries** - @Query allows optimized JPQL instead of SQL
4. **JWT Stateless** - No server-side session storage needed
5. **Database Indexes** - Primary/unique keys automatically indexed
6. **Connection Pooling** - HikariCP manages database connections

---

## Security Best Practices Implemented

1. ✅ **Password Hashing** - BCrypt with strength 10
2. ✅ **JWT Expiration** - Tokens expire after 24 hours
3. ✅ **CSRF Disabled** - Appropriate for stateless API
4. ✅ **Stateless Sessions** - No session fixation vulnerabilities
5. ✅ **Ownership Checks** - Users can only modify their own resources
6. ✅ **Role-Based Access** - @PreAuthorize enforces permissions
7. ✅ **Input Validation** - JSR-303 annotations validate all inputs
8. ✅ **Prepared Statements** - JPA prevents SQL injection

---

**Document Version:** 1.0  
**Last Updated:** January 21, 2025  
**Technology Stack:** Spring Boot 4.0.1, Java 25, MySQL
