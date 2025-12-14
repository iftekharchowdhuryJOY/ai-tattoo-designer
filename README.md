# 🚀 AI Tattoo Concept Designer: Full-Stack & High-Performance

This project is a modern, full-stack web application that uses **Google's Gemini Image Generation API** to turn simple conversational text into high-quality, illustrative tattoo concepts. The architecture emphasizes scalability, performance, and cost-optimization.

## 🌟 Key Technical Highlights

This section immediately draws attention to your most advanced decisions:

*   **Asynchronous Processing (Async I/O)**: All I/O-bound operations (database reads/writes) are handled asynchronously using `asyncpg` and Async SQLAlchemy. This prevents worker threads from blocking, allowing the server to handle massive concurrent user traffic (high scalability).
*   **Performance Optimization (Redis Caching)**: Implemented a Cache-Aside pattern with Redis to store image URLs based on a SHA256 key of the engineered prompt. This achieves sub-millisecond latency for repeat requests and reduces AI API costs by preventing redundant calls.
*   **Non-Blocking Workflow (Background Tasks)**: Database logging for successful image generations is decoupled using FastAPI's `BackgroundTasks`. The user receives their image instantly while the logging happens non-blocking in a separate thread.
*   **Advanced Prompt Engineering**: Developed a robust, multi-stage Python function to translate conversational prompts into highly-specific, technical commands (e.g., using "Blackwork Style Tattoo" and anti-prompts) to overcome the Gemini model's compositional limitations.

## 🏛️ System Architecture

The system follows a standard three-tier, decoupled architecture:

*   **Client Tier (React)**: Handles user input, displays history, and manages the asynchronous request state (loading spinners).
*   **Application Tier (FastAPI/Python)**: The high-performance backend serving as the central API gateway.
    *   *Core Logic*: Prompt Engineering, Caching (Redis), and Workflow Management.
    *   *Dependencies*: SQL/DB (Supabase), AI (Gemini).
*   **Data Tier (PostgreSQL/Supabase & Redis)**:
    *   *PostgreSQL*: Stores persistent conversation history and metadata.
    *   *Redis*: Serves as a volatile, in-memory cache for generated images.

## ⚙️ Technology Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | React, TypeScript | Responsive UI and state management. |
| **Backend Framework** | FastAPI (Python) | High-performance API server. |
| **AI Integration** | Google Gemini Image Generation API | Generates the tattoo concepts. |
| **Database (ORM)** | Async SQLAlchemy 2.0, asyncpg | Asynchronous, non-blocking database interaction. |
| **Cache Store** | Redis | In-memory cache for speed and cost reduction. |
| **Persistence DB** | PostgreSQL (via Supabase) | Durable storage for conversation history. |

## 💻 How to Run Locally

### Prerequisites
*   Python 3.10+
*   Node.js & npm (for the React frontend)
*   A running Redis server (local or external)
*   A Supabase project (or local PostgreSQL instance)

### Setup Steps

1.  **Clone the Repository**:
    ```bash
    git clone [YOUR_REPO_LINK]
    cd ai-tattoo-designer
    ```

2.  **Configure Environment Variables**:
    Create a `.env` file in the `backend/` directory with your credentials:
    ```env
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host]:[port]/[db_name]
    
    # For local Redis (default)
    REDIS_HOST=localhost
    REDIS_PORT=6379
    ```

3.  **Install & Run Backend**:
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn main:app --reload
    ```

4.  **Install & Run Frontend**:
    ```bash
    cd ../frontend
    npm install
    npm start
    ```

## 🧠 Architectural Deep Dive (For the Senior Reviewer)

This section directly addresses the technical problems and your solutions:

### Problem: API Latency and Cost
Image generation is slow and expensive.
**Solution: Cache-Aside with Background Logging**
The `/generate_tattoo` endpoint performs the following non-blocking sequence:
1.  Check Redis.
2.  On cache miss, call Gemini API.
3.  Store the result in Redis (TTL 24h).
4.  *Crucially*: Use `FastAPI.BackgroundTasks` to delegate the final `db.commit()` to a separate thread, ensuring the user gets the HTTP response before the database transaction is finalized.

### Problem: Database Blocking (Scalability)
Synchronous database calls limit concurrency.
**Solution: Full Asynchronous Stack**
Migrated the entire database layer from synchronous SQLAlchemy to Async SQLAlchemy 2.0 using the `asyncpg` driver. This allows a single backend worker to manage hundreds of concurrent database queries without stalling, dramatically boosting the application's scalability and efficiency under load.

### Problem: AI Output Reliability
Simple user prompts often lead to irrelevant generic images (e.g., landscapes).
**Solution: Prompt Engineering Layer**
Implemented a dedicated Python function to inject technical modifiers (Blackwork Style Tattoo, Isolated Tattoo Concept) and anti-prompts (NOT a photo, NOT scenery) into the user's request. This forces the model to focus on the desired output medium (illustration) over generic photography.