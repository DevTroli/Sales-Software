# 🚀 Sales Software

![GitHub repo size](https://img.shields.io/github/repo-size/DevTroli/Sales-Software)
[![Status do Projeto][status-shield]][status-url]
[![Versão][version-shield]][version-url]
[![Licença][license-shield]][license-url]

## 📖 About
Sales Software is a modern business solution that transforms sales and inventory management into an efficient, intuitive experience. Developed to meet the specific needs of the retail and food service markets, our system automates critical processes, reduces operational errors, and provides valuable insights for decision-making.

Combining a robust POS (Point of Sale) system with advanced inventory management, it enables businesses of any size to modernize their operations without complexity. Our solution eliminates time-consuming manual processes, allowing your team to focus on what truly matters: providing excellent customer service.

### 🌟 Motivation
This project was born from observing the challenges faced by small and medium-sized businesses in managing their daily operations. Many companies still rely on manual processes or use disconnected tools, leading to inefficiencies and errors.

Our mission is to democratize access to management technology by providing an integrated solution that is both powerful and easy to use. We believe every business deserves access to tools that drive growth.

### 🎯 Goals
- Simplify operational management for retail and food service companies
- Reduce errors and time spent on manual processes
- Provide real-time insights for decision-making
- Enhance customer experience through faster service
- Facilitate inventory control and management
- Offer an accessible and scalable solution

## ✨ Highlights
- 🔥 Advanced Reports: Automatic generation of inventory and sales reports in Excel for detailed business analysis

- 💳 Complete POS: Intuitive point of sale system supporting multiple payment methods

- 🎯 Order Management: Efficient order and ticket management with real-time status tracking

- 📦 Inventory Control: Automated inventory management with low-level alerts and restocking suggestions

- 🌐 Custom Hot Site: Responsive, customizable web interface for an improved user experience

-  🔐 Access Control: Flexible authentication system with custom access levels per employee or store

- 📱 Responsive Design: Adaptable interface that works seamlessly on any device, from desktop to smartphone

- 🔄 Full Integration: All features integrated into a single platform, eliminating the need for multiple systems

## 🛠️ Built With

### 🎨 Frontend
* [TailwindCSS](https://tailwindcss.com/) - Utility-first CSS framework for rapidly building custom designs
* [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript) - Client-side scripting for dynamic web features
* [HTML5](https://developer.mozilla.org/en-US/docs/Web/HTML) - Standard markup language for web pages

### ⚙️ Backend
* [Django 5.0.6](https://www.djangoproject.com/) - High-level Python web framework
* [Python](https://www.python.org/) - Programming language for backend logic
* [Gunicorn 22.0.0](https://gunicorn.org/) - Python WSGI HTTP Server for UNIX
* [WhiteNoise 6.7.0](http://whitenoise.evans.io/en/stable/) - Static file serving for Python web apps

### 🗄️ Database
* [PostgreSQL](https://www.postgresql.org/) - Advanced open source relational database
* [psycopg2-binary 2.9.9](https://pypi.org/project/psycopg2-binary/) - PostgreSQL adapter for Python

### 📊 Data Processing
* [NumPy 2.0.1](https://numpy.org/) - Library for numerical computing in Python
* [Pandas 2.2.2](https://pandas.pydata.org/) - Data manipulation and analysis library
* [python-dateutil 2.9.0](https://pypi.org/project/python-dateutil/) - Extensions to the standard Python datetime module

### 🔧 Development Tools
* [django-extensions 3.2.3](https://django-extensions.readthedocs.io/) - Collection of custom extensions for Django
* [django-widget-tweaks 1.5.0](https://pypi.org/project/django-widget-tweaks/) - Tweak form field rendering in templates
* [black 24.4.2](https://black.readthedocs.io/) - Python code formatter
* [python-decouple 3.8](https://pypi.org/project/python-decouple/) - Separates settings from code

### 📋 Additional Libraries
* [openpyxl 3.1.5](https://openpyxl.readthedocs.io/) - Library for reading/writing Excel 2010 xlsx/xlsm files
* [cryptography 43.0.0](https://cryptography.io/) - Library for secure communication and data protection

## 🎯 Requirements
```text
Python >= 3.8
PostgreSQL >= 12.0
Node.js >= 14.0 (for TailwindCSS)
```

## ⚙️ Installation
<details>
<summary>📋 Step by Step</summary>

1. Clone the repository
```bash
git clone https://github.com/DevTroli/Sales-Software.git
```

2. Enter the directory
```bash
cd Sales-Software
```

3. Install dependencies
```bash
python -m venv .venv --clear
source .venv/bin/activate
pip -r install requirements.txt
```

4. Configure environment variables
```bash
python contrib/envGen.py
# Don't forget to add your database access to .env
```

5. Start the project
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
</details>

## 📚 Documentation
<details>
<summary>📖 Complete Guide</summary>

### 🏗️ Project Structure
```
sales_software/                    
├── manage.py                     # Django's command-line utility for administrative tasks
├── requirements.txt              # List of Python dependencies for the project
├── .env                          # Environment variables configuration
├── .gitignore                    # Specifies which files Git should ignore
├── LICENSE                       # Project license details
├── railway.json                  # Railway.app deployment configuration
├── write_xlsx.py                 # Utility script for Excel file operations
│
├── setup/                       # Project configuration directory
│   ├── __init__.py              
│   ├── asgi.py                  # ASGI configuration for async web servers
│   ├── settings.py              # Main Django settings
│   ├── staging.py               # Staging environment specific settings
│   ├── urls.py                  # Main URL configuration
│   └── wsgi.py                  # WSGI configuration for web servers
│
├── comandas/                   # Orders/Tabs management application
│   ├── migrations/             # Database migrations for orders
│   ├── __init__.py             
│   ├── admin.py                
│   ├── apps.py                 
│   ├── models.py               # Data models for orders/tabs
│   ├── urls.py                 # URL patterns for orders/tabs
│   └── views.py                # View logic for orders/tabs
│
├── core/                      # Core functionality application
│   ├── migrations/            # Database migrations for core features
│   ├── __init__.py            
│   ├── admin.py               
│   ├── apps.py                
│   ├── models.py              # Core data models
│   ├── urls.py                # URL patterns for core features
│   └── views.py               # Core view logic
│
├── pdv/                      # Point of Sale (POS) application
│   ├── migrations/           # Database migrations for POS
│   ├── __init__.py           
│   ├── admin.py              
│   ├── apps.py               
│   ├── models.py             # POS data models
│   ├── urls.py               # URL patterns for POS
│   └── views.py              # POS view logic
│
├── produto/                  # Product management application
│   ├── migrations/           
│   ├── __init__.py           
│   ├── admin.py             
│   ├── apps.py               
│   ├── models.py             # Product data models
│   ├── urls.py               # URL patterns for products
│   └── views.py              # Product view logic
│
├── contrib/                  # Additional utilities and scripts
│   └── envGen.py             # Script to generate .env file with secure defaults
│
├── docs/                     # Project documentation files
│
├── static/                   # Static files (CSS, JavaScript, admin and etc...)
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript files
│   └── admin/                # Admin interface static files
│
├── staticfiles/              # Collected static files for production
│
├── templates/                 # HTML templates
│   ├── base.html              # Base template for inheritance
│   ├── includes/              # Reusable template parts
│   ├── registration/          # User authentication templates
│   ├── core/                  # Core feature templates
│   ├── produto/               # Product management templates
│   ├── pdv/                   # Point of Sale templates
│   └── comandas/              # Orders/Tabs templates
│
└── backups/                    # Database backup files
    ├── backup_file.dump       # PostgreSQL dump file
    └── backup_file.sql        # SQL backup file
```

</details>


## 📊 Roadmap
- [x] MVP
- [x] Basic Documentation
- [ ] Automated Tests
- [ ] Continuous Integration
- [ ] Feature X
- [ ] Feature Y

## 🤝 How to Contribute
<details>
<summary>👩‍💻 Contribution Guide</summary>

1. Fork or clone the project
2. Create your Feature Branch
```bash
git checkout -b feature/MyFeature
```

3. Commit your changes
```bash
git commit -m 'Add: MyFeature'
```

4. Push to the Branch
```bash
git push origin feature/MyFeature
```

5. Open a Pull Request

### 📝 Commit Conventions
- `Add:` New functionality
- `Update:` Functionality update
- `Fix:` Bug fix
- `Doc:` Documentation
- `Style:` Formatting
- `Refactor:` Code refactoring
- `Test:` Tests
</details>

## ✍️ Authors
* **[Troli]** - *Initial Work*

See also the list of [contributors](https://github.com/DevTroli/Sales-Software/contributors) who participated in this project.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact
[Troli] - [@DevTroli]() - pablotroli@outlook.com

---

<p align="center">
  <sub>⭐ Made with ❤️ by <strong>@DevTroli</strong> ⭐</sub>
</p>

<!-- MARKDOWN LINKS & IMAGES -->
[status-shield]: https://img.shields.io/badge/status-ativo-success.svg
[status-url]: #
[version-shield]: https://img.shields.io/badge/version-1.0.0-blue.svg
[version-url]: #
[license-shield]: https://img.shields.io/badge/license-MIT-green.svg
[license-url]: #
