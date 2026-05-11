# E-Commerce Monitoring System

A Flask-based e-commerce monitoring dashboard with role-based access, inventory tracking, sales analytics, customer storefront, and real-time notifications.

## Features

- Role-based authentication for `admin`, `cashier`, and `customer`
- JSON-backed database stored in `ecommerce_database.json`
- Admin dashboard with store metrics and analytics
- Sales and inventory management APIs
- Customer storefront, cart, wishlist, orders, checkout, and reviews
- Real-time updates via Socket.IO
- Sample data seeded automatically on first run

## Built With

- Python 3.11+ (recommended)
- Flask
- Flask-SocketIO
- Flask-CORS
- SQLAlchemy
- pandas, numpy, plotly, dash
- bcrypt
- PyJWT
- python-dotenv

## Getting Started

### Prerequisites

- Python 3.11 or newer
- `pip` package manager

### Installation

1. Clone or download the repository
2. Create a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. (Optional) Create a `.env` file in the project root to override defaults:

```env
SECRET_KEY=your-secret-key
```

### Run the App

```powershell
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Default Sample Accounts

- Admin: `admin` / `admin123`
- Cashier: `cashier` / `cashier123`

> Customer accounts are created through the registration page.

## Project Structure

- `app.py` – main Flask application and API backend
- `ecommerce_database.json` – local JSON data store
- `templates/` – HTML pages for login, dashboard, store, admin, analytics, and customer views
- `static/` – static assets used by the web UI

## Notes

- The app initializes sample products, categories, customers, and sales data on first launch.
- Database changes are persisted to `ecommerce_database.json`.
- Socket.IO is configured with `async_mode='threading'` for local development.

## Builder

- Mayuri Santosh Futane
- Roll No: `BT24F05F021`
