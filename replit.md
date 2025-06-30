# Hiddekel Investments Web Application

## Overview

This is a Flask-based web application for Hiddekel Investments, a land development company in Zimbabwe. The application serves as both a public-facing website and an administrative content management system. It features property listings, blog management, contact forms, and gallery functionality.

## System Architecture

The application follows a traditional Flask MVC pattern with the following architectural decisions:

- **Backend Framework**: Flask with SQLAlchemy for database operations
- **Database**: SQLite for development (configured to support PostgreSQL via DATABASE_URL environment variable)
- **Frontend**: Server-side rendered templates using Jinja2 with Bootstrap 5 for responsive design
- **File Storage**: Local file system for uploads with image optimization
- **Email**: Flask-Mail for contact form submissions
- **Authentication**: Session-based admin authentication

## Key Components

### 1. Models (`models.py`)
- **User**: Admin user management with password hashing
- **Stand**: Property listings with images, pricing, and location data
- **StandImage**: Property image management with captions
- **BlogPost**: Blog/news articles with slug-based URLs
- **GalleryImage**: Site gallery management
- **Contact**: Contact form submissions
- **SiteVisit**: Site visit booking requests
- **Download**: Downloadable files/brochures
- **SiteSetting**: Configurable site settings
- **Testimonial**: Customer testimonials

### 2. Routes
- **Main Routes** (`routes.py`): Public website functionality
- **Admin Routes** (`admin_routes.py`): Administrative interface
- Blueprint-based route organization for modularity

### 3. Forms (`forms.py`)
- WTForms integration for form validation
- Contact, Stand, and Blog forms with file upload support

### 4. Utilities (`utils.py`)
- Image processing with PIL for resizing and thumbnail generation
- Unique filename generation to prevent conflicts
- File validation helpers

### 5. Frontend
- **Templates**: Jinja2 templates with base template inheritance
- **Styling**: Bootstrap 5 with custom CSS using CSS variables
- **JavaScript**: Vanilla JS for interactivity and admin dashboard functionality
- **Icons**: Font Awesome for consistent iconography

## Data Flow

1. **Public Website**: Users browse properties, read blog posts, submit contact forms
2. **Admin Panel**: Authenticated administrators manage content through CRUD operations
3. **File Uploads**: Images are processed, resized, and stored in the uploads directory
4. **Email Notifications**: Contact form submissions trigger email notifications
5. **Database**: All data persisted in SQLite/PostgreSQL with proper relationships

## External Dependencies

- **Flask Ecosystem**: Core framework, SQLAlchemy ORM, WTForms, Flask-Mail
- **Image Processing**: Pillow (PIL) for image manipulation
- **Frontend Libraries**: Bootstrap 5, Font Awesome, AOS animations
- **Admin Interface**: TinyMCE for rich text editing
- **Email Service**: Configurable SMTP (defaults to Gmail)

## Deployment Strategy

The application is configured for flexible deployment:

- **Development**: SQLite database, local file storage
- **Production**: Environment-based configuration for PostgreSQL, external file storage
- **Session Management**: Secure session handling with configurable secret keys
- **File Uploads**: Organized in uploads directory with size limits (16MB)
- **Error Handling**: Comprehensive error handling and logging

## Changelog

- June 30, 2025: Initial setup and ultra-premium design implementation
- June 30, 2025: Added luxury features, glassmorphism effects, animated gold particles
- June 30, 2025: Implemented comprehensive admin dashboard with all missing templates
- June 30, 2025: Added real property images and blog thumbnails
- June 30, 2025: Background images added to landing page, then rolled back per user request

## User Preferences

Preferred communication style: Simple, everyday language.