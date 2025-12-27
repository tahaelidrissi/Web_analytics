# System Design – Basic Web Scraping Application

## 1. Goal
Build a simple web application that allows a user to:
- Provide a website URL
- Define what content to extract
- Set a limit on extracted data

---

## 2. Architecture Overview

User  
→ Web Interface  
→ Backend API  
→ Scraping Module  
→ Response to User

---

## 3. Components

### 3.1 Web Interface
**Purpose**
- Collect user inputs

**Inputs**
- URL
- Content selector (CSS)
- Data limit

---

### 3.2 Backend API
**Purpose**
- Handle requests
- Validate inputs

**Responsibilities**
- Check URL format
- Apply max limit
- Return results

---

### 3.3 Scraping Module
**Purpose**
- Extract data from the website

**Tools**
- Requests + BeautifulSoup

**Tasks**
- Fetch page
- Apply selector
- Limit results

---

## 4. Data Flow

1. User submits form
2. Backend receives request
3. Scraper extracts data
4. Results are limited
5. Data is returned to user

---

## 5. Output
- JSON response

---

## 6. Constraints
- Maximum extraction limit
- Basic error handling
- Respect robots.txt

---

## 7. Possible Improvements
- Dynamic website support
- Data export (CSV)
- User authentication
