# Course Platform Prototype

This is a prototype of a web-based course platform developed using Flask. The application is intended for university environments and includes basic functionalities for professors and students, such as course creation, enrollment, chat, file upload, and video conferencing.

> **Note**: The interface and all content of the application are in Romanian, as it was built in the context of a Romanian university project.

## Features

- User authentication (student/professor roles)
- Course management (create, join, view)
- Real-time chat using WebSockets
- File upload and download for course materials
- Video conferencing functionality
- Email notifications to students upon material upload
- Designed with a responsive and modern Bootstrap-based UI

## Technologies Used

- Python + Flask
- Flask-SocketIO
- Flask-Login
- Flask-Mail
- SQLAlchemy (with MySQL backend)
- Bootstrap 5
- JavaScript (for client-side updates)

## Installation

> This project requires Python 3.10+ and a local MySQL server.

1. Clone the repository:
->   git clone https://github.com/VladoiuGabriel/course-platform-prototype cd course-platform-prototype
2. Create and activate a virtual environment (optional but recommended):
->   python -m venv venv venv\Scripts\activate # for Windows
3. Install dependencies:
->   pip install -r requirements.txt
4. Configure your `.env` or `config.py` file with the appropriate database and email credentials.
5. Initialize the database:
->  flask db init flask db migrate flask db upgrade
6. Run the app:
->  flask run
   
## Notes
- The project is meant as a prototype and learning project, not for production use.
- To enable email notifications, make sure your email provider supports "App Passwords" and SMTP.
