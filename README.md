## IT Ticket Tracker — Milestone 3 Project

I have created  a simple full-stack web app designed to manage IT support tickets. Users can register, log in, and raise new support requests. Admins can view, edit, assign, and close tickets in real-time. The app is styled for usability, fully responsive, and built with accessibility and CRUD in mind.

---

### Live Site

**Hosted on Heroku**: [CraigAust.in](https://milestone-support-tickets-67fbfa276455.herokuapp.com)

---

## Project Overview


The goal was to build a fully functional **full-stack application** with a real-world use case. I chose to build an **IT Support Ticket Tracker**, a tool that could be used by companies to log internal technical issues, assign support staff, and track the status of tickets.  This is something missing at my current workplace and this is what inspired me to do the project.

---

## Target Audience

- Small to mid-sized companies with internal IT teams.
- Admins managing IT support workloads.
- End users needing to report problems/ get help/ help their business grow.  This allows them to also track responses from the admins.

---

##  UX / Design

###  Wireframes
All wireframes were created using adobe illustrator and can be found 

![Desktop Login/ Register](static/images/desktopwire.png)
![Non User Authentication](static/images/mobilewire.png)


###  Key UX Goals
- Minimal, clean layout for both users and admins.
- Clear call-to-actions for creating and updating tickets.
- Responsive design across mobile, tablet, and desktop.
![Device Layout](static/images/SupportMockup.png)
![Mobile Layout](static/images/mobile.png)
![Tablet Layout](static/images/tablet.png)
![Desktop Layout](static/images/desktop.png)
![Mobile Nav Layout](static/images/nav.png)


## Database Schema

The application uses SQLAlchemy ORM to manage a relational database. It includes three primary models:

- **User**: Stores login credentials, roles, and links to submitted tickets.
- **Ticket**: Represents a support request created by a user.
- **Status**: Tracks the current state of each ticket (e.g. Submitted, In Progress, Done).

### Rationale & Design Considerations

The schema was designed based on real-world user stories. Regular users need to raise support tickets and track progress by logging in. Admins require access to all tickets, along with the ability to update statuses and manage workload. By separating ticket `Status` into its own table, the design allows for future scalability, including analytics, filters, and workflow automation.

The database schema supports full Create, Read, Update, and Delete operations using SQLAlchemy. Field types have been chosen for flexibility and performance (e.g., `Text` for descriptions, `DateTime` for timestamps). This structure also allows for future enhancements like assigning tickets to support staff or adding threaded comments.


### Entity Relationships

User
 └── id (PK)
 └── email
 └── password_hash
 └── is_admin (Boolean)
 └── tickets (1-to-many relationship to Ticket)
 └── activity_logs (1-to-many relationship to ActivityLog)

Ticket
 └── id (PK)
 └── user_id (FK → User)
 └── category
 └── description
 └── status (default: 'Submitted')
 └── created_at (timestamp)
 └── logs (1-to-many relationship to ActivityLog)

ActivityLog
 └── id (PK)
 └── ticket_id (FK → Ticket)
 └── user_id (FK → User)
 └── action (e.g., "Created", "Updated", "Closed")
 └── message (details of the action)
 └── timestamp (timestamp)
 
### Visual ERD

 [Database Schema](static/images/database_schema.png)

 ## Accessibility

Accessibility was a core consideration throughout the design and development of this project to ensure that it is usable by as many people as possible, including users with disabilities.

The following steps were taken to improve accessibility:

- **Semantic HTML:** All pages use semantic HTML5 elements (e.g., `<header>`, `<main>`, `<nav>`, `<section>`, `<footer>`) to ensure content is structured logically for screen readers and assistive technologies.

![Semantic](static/images/semantic.png)
  
- **ARIA Labels:** ARIA (Accessible Rich Internet Applications) attributes were added to key interactive elements where additional context was needed, improving the navigation experience for users relying on screen readers.

  ![Aria Labels](static/images/aria.png)


- **Keyboard Navigation:**
  - All interactive elements (buttons, links, forms) are fully accessible via keyboard alone.
  - Focus indicators (`:focus-visible`) are clearly visible, helping users understand where they are on the page.
  ![Keyboard Navigations](static/images/keyboard.png)
  
- **CSS for Accessibility:**
  - Accessible `line-height` and `text-wrap` properties have been applied for better readability.
  - Form controls inherit fonts correctly to maintain consistency across different devices and user settings.
  - Media elements (images, videos, etc.) have responsive defaults and are styled to avoid overflow issues.

- **Alt Text for Images:** All images include appropriate `alt` text to describe content where necessary.

- **Color Contrast:** I made a conscious effort to ensure good color contrast between background and foreground elements, adhering to WCAG 2.1 guidelines wherever possible.

- **Responsive Design:**
  - The layout adapts effectively across screen sizes.
  - Text size and element spacing are designed to remain legible without requiring zoom.

- **Accessability via browsers:**

![WAVE Test](static/images/wave.png)
- For Chrome devtools accessability tests goto [TESTING.md](TESTING.md)

This ensures that the application is inclusive and provides a usable experience for a wider audience.

## Features

### MVP Features
- User registration and login/logout (Flask & SQLAlchemy)
- Raise a new IT support ticket
- View ticket details
- Edit/update ticket status (admin only)
- Delete ticket (admin only)
- Responsive layout (Bootstrap + custom CSS)

### User Roles
- **Regular Users**: Can log in and create/view their own tickets.
- **Admins**: Can view all tickets, assign users, change statuses, and delete tickets.

## Data Model Justification

- The data model was designed to reflect real-world technical support workflows. Users can submit tickets and view updates, while admins can update statuses and add notes. Each update is stored in a log to ensure transparency and accountability.

- A User can submit multiple Tickets.
- A Ticket tracks its status, description, and is linked to a User.
- All ticket updates (like status changes, admin responses) are stored in ActivityLogs.
- This structure ensures full CRUD capability, supports real-time feedback, and provides a scalable foundation for future features (e.g., ticket assignment, priority levels, threaded comments).

 [Database Schema](static/images/database_schema.png)


## Usable Relational Database

The data model was developed into a fully usable relational database using **SQLAlchemy ORM** with **PostgreSQL** as the production database and **SQLite** for local development.

### Technologies Used
- **SQLAlchemy**: Object Relational Mapper (ORM) to handle database models and operations.
- **SQLite**: Lightweight relational database used during local development.
- **PostgreSQL**: Production-grade relational database used on Heroku.
- **Flask-SQLAlchemy**: Flask extension that integrates SQLAlchemy smoothly with the Flask application.

### Database Setup and Configuration
- In local development, the database defaults to SQLite (`sqlite:///instance/support_db.db`).
- In production (deployed on Heroku), environment variables configure a PostgreSQL database connection securely using `psycopg2-binary`.
- `python-dotenv` is used to manage sensitive credentials (e.g., database URLs) via a `.env` file during local development.

### Table Structure
The database contains three primary tables:

- **User Table**: Stores user authentication details and roles (admin/user).
- **Ticket Table**: Stores ticket submissions, categories, status, and user references.
- **ActivityLog Table**: Stores action logs related to ticket updates and user activity.

Each table was designed to:
- Ensure **data integrity** through primary keys and foreign keys.
- Support **1-to-many relationships** (e.g., a user can have multiple tickets).
- Allow **consistent and structured data storage**.
- Provide **full CRUD (Create, Read, Update, Delete)** operations with minimal redundancy.

### Data Consistency and Organisation
- Fields use appropriate data types (e.g., `String`, `Text`, `DateTime`).
- Default values are used where applicable (e.g., `created_at` timestamps).
- Relationships are clearly defined to maintain data consistency (e.g., ticket status linked to users and tickets).
- Cascading rules (e.g., `delete-orphan`) are used in relationships to maintain referential integrity.

### Scalability Considerations
The database was structured to allow for future expansion, including:
- Ticket assignment to staff members.
- Ticket prioritisation and categorisation.
- Additional activity types in the `ActivityLog`.
- User role management (admin vs. regular users).

[Database](static/images/database.png)

## Database Configuration Management

All database configuration settings are maintained in a single `config.py` file. The application dynamically loads the database URI and related credentials from environment variables, ensuring no hardcoded values are present and allowing easy switching between local (SQLite) and production (PostgreSQL) databases.


## Testing

Testing was a mix of **manual** and **automated** methods:
**Go to TESTING →** [TESTING.md](TESTING.md)

### Manual Tests
- Form validation for all inputs (ticket submission, login, etc.)
- Role-based access controls
- Navigation via keyboard (Tab, Shift+Tab)
- Screen reader check using VoiceOver (Mac)
- Responsive layout on different screen sizes

### Automated Tests
- Lighthouse Accessibility audit (Chrome DevTools)  
  - Score: 97/100
- WAVE accessibility checker
- PEP8 validation using flake8
- HTML validation with W3C validator

### Bugs & Fixes
-  **Issue**: Tickets could be submitted without a subject line.  
   **Fix**: Added Flask-WTF form validation with required fields.
-  **Issue**: Admin-only routes were accessible without login.  
   **Fix**: Added `@login_required` and role-based checks.
-  **Issue**:Mailgun API's were pushed to github because of bad formatting in the gitignore  
   **Fix**: quickly replaced the API's
   **Todo**: Remove any old API's from github

- All other known bugs have been addressed.

**Go to TESTING →** [TESTING.md](TESTING.md)
---

## Technologies Used

### Back End
- Python  
- Flask  
- Jinja2 (template engine)  
- SQLAlchemy  
- Flask-WTF (form validation)  
- Flask-Mail (email functionality)  
- SQLite (dev), MySQL (production)  
- dotenv (for managing environment variables)  
- PEP8 via flake8  
- Code formatting with Black
- Routes
- gunicorn
**For all requirements go to →** [Requirements](requirements.txt)


### Front End

- Bootstrap
- HTML/CSS

###  Other Tools
- Heroku (deployment)
- GitHub (version control)
- Mailgun (for email confirmations)

 
### Configuration

All sensitive settings are stored in environment variables and loaded through a central `config.py` file using Python's `os.getenv()` and `python-dotenv`.

This ensures secure, flexible, and environment-specific configuration for both development and production environments.


### PEP8 Compliance

Code quality and style were maintained throughout the project using two industry-standard tools: **Flake8** and **Black**.

- **Linting** was performed using `flake8`, with a configuration file (`.flake8`) specifying the following:
  - `exclude = venv` – to ignore third-party packages and focus only on project code.
  - `max-line-length = 102` – slightly extended from the PEP8 default to accommodate readable lines without unnecessary wrapping but still left my code readable.
- All Python files were scanned and verified to be compliant with [PEP8](https://peps.python.org/pep-0008/) standards, including rules for:
  - Spacing and indentation  
  - Function and variable naming conventions  
  - Import ordering and blank lines  
  - Docstring usage
- Any `E501` warnings for long lines within the `venv/` directory were ignored as they do not pertain to the submitted codebase.
- All remaining issues within the project files (`app.py`, `routes.py`, etc.) were resolved, with no critical errors after final linting.
- **Black** was used to automatically format all Python code, ensuring consistent spacing, quoting, and line wrapping.


- [Black Formatter](static/images/black_formatter.png)  
- [Flake8 Formatted](static/images/black8a.png)  
- [Flake8 Pass](static/images/black8b.png)


#### Environment Variables Used:

- `SECRET_KEY` – Flask app security
- `DATABASE_URL` – PostgreSQL URL from Heroku (fallbacks to SQLite locally)
- `FLASK_ENV` – Toggles debug mode (`production` disables it)
- `MAILGUN_API_KEY`, `MAILGUN_DOMAIN`, `MAILGUN_SENDER`, `MAILGUN_WEBHOOK_SECRET`, `MAILGUN_PUBLIC_KEY` – Used for Mailgun email integration

#### Key Features in `config.py`:

- Single point of truth for all configuration settings
- Loads `.env` file locally for development using `python-dotenv`
- Automatically fixes Heroku's `postgres://` to `postgresql://`
- Disables `DEBUG` mode automatically in production


## Deployment

Deployed via **Heroku** using the following process:

1. Set up PostgreSQL database on Heroku
2. Configure `Procfile`, `requirements.txt`, `runtime.txt`
3. Set environment variables using Heroku dashboard
4. Pushed code via GitHub → connected Heroku app
5. Verified deployed version matches development version

**For all go to →** [Deployment](static/images/deploy.png)


##  Security Considerations

- All secret keys and credentials are stored as environment variables.
- No working API keys or passwords are committed to the repo.
- Admin-only routes are protected via decorators.
- CSRF protection is enabled on all forms.
- Minimum 8 characters for the password.

##  File Structure (simplified)
```
milestone-project-three/

│
├── app.py
├── config.py
├── routes.py
├── run.py
├── requirements.txt
├── Procfile
├── README.md
├── TESTING.md
├── templates/
├── static/
│   ├── styles.css
│   └── images/
│      
├── instance/
│   └── (database or environment-related files)
├── venv/
├── .env (in .gitignore)
└── .vscode/

```
## Credits

- Design inspiration from various helpdesk UIs that I found on google.
- Some Bootstrap snippets sourced from [getbootstrap.com](https://getbootstrap.com).
- Accessibility tested with [WAVE](https://wave.webaim.org/) and Chrome Lighthouse.
- CSS reset [Josh Comeau](https://www.joshwcomeau.com/css/custom-css-reset/).
- Envato for my graphics [Evato](https://www.envato).
- Help from W3 schools [W3 Schools]( http://w3schools.com/). 
- https://www.udemy.com/course/python-flask-beginners/.
- https://www.youtube.com/watch?v=G1FBSYJ45Ww
---

## Future Improvements

- Assign tickets to specific support staff
- Add comments to each ticket
- Implement search and filters for tickets
- Add automated email notifications on ticket 
