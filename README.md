# Gamezawy

Gamezawy is a game store website built using Flask and SQLite as part of our summer training at **Cyberus Stud**. The primary focus of this project was to learn and apply **secure web coding** practices, ensuring that the website is free from common web vulnerabilities while delivering essential e-commerce functionality for users to browse and purchase games.

## Features
- **User Authentication**: Secure login and registration system with password encryption.
- **Game Listings**: A collection of games that users can browse, view details, and add to their cart.
- **Shopping Cart**: Users can add games to their cart and proceed with checkout.
- **Secure Web Coding**: Best practices for secure web development are integrated, including protection against SQL injection, Cross-Site Scripting (XSS), and Cross-Site Request Forgery (CSRF).

## Technologies Used
- **Backend**: Flask (Python web framework)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript (Jinja2 templating engine)
- **Security**: Implementation of secure coding techniques learned during training

## Installation

1. Clone the repository:
      ```bash
      git clone https://github.com/yourusername/Gamezawy.git
      ```
2. Navigate to the project directory:
      ```bash
      cd Gamezawy
      ```
3. Create and activate a virtual environment:
     ```bash
     python3 -m venv venv
     source venv/bin/activate  # On Windows use `venv\Scripts\activate`
     ```
4. Install the required dependencies:
     ```bash
     pip install -r requirements.txt
     ```
5. Run the application:
   ```bash
   flask --app app.py run
   ```

