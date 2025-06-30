from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from models import Stand, BlogPost, GalleryImage, Contact, SiteVisit, Download, SiteSetting, TeamMember, Testimonial
from app import db, mail
from flask_mail import Message
from datetime import datetime
import os
from werkzeug.utils import secure_filename

main_bp = Blueprint('main', __name__)

def get_setting(key, default=''):
    setting = SiteSetting.query.filter_by(key=key).first()
    return setting.value if setting else default

@main_bp.route('/')
def index():
    featured_stands = Stand.query.filter_by(featured=True).limit(6).all()
    latest_blogs = BlogPost.query.filter_by(status='Published').order_by(BlogPost.created_at.desc()).limit(6).all()
    testimonials = Testimonial.query.filter_by(is_active=True).all()

    return render_template('index.html', 
                         featured_stands=featured_stands,
                         latest_blogs=latest_blogs,
                         testimonials=testimonials)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/stands')
def stands():
    page = request.args.get('page', 1, type=int)
    location_filter = request.args.get('location', '')
    status_filter = request.args.get('status', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    query = Stand.query

    if location_filter:
        query = query.filter(Stand.location.contains(location_filter))
    if status_filter:
        query = query.filter_by(status=status_filter)
    if min_price:
        query = query.filter(Stand.price >= min_price)
    if max_price:
        query = query.filter(Stand.price <= max_price)

    stands = query.order_by(Stand.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )

    locations = db.session.query(Stand.location).distinct().all()
    locations = [loc[0] for loc in locations if loc[0]]

    return render_template('stands.html', stands=stands, locations=locations)

@main_bp.route('/stands/<int:id>')
def stand_detail(id):
    stand = Stand.query.get_or_404(id)
    related_stands = Stand.query.filter(Stand.id != id).limit(3).all()
    return render_template('stand_detail.html', stand=stand, related_stands=related_stands)

@main_bp.route('/gallery')
def gallery():
    category_filter = request.args.get('category', '')

    query = GalleryImage.query.filter_by(is_active=True)
    if category_filter:
        query = query.filter_by(category=category_filter)

    images = query.order_by(GalleryImage.created_at.desc()).all()
    categories = db.session.query(GalleryImage.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]

    return render_template('gallery.html', images=images, categories=categories)

@main_bp.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(status='Published').order_by(
        BlogPost.created_at.desc()
    ).paginate(page=page, per_page=9, error_out=False)

    return render_template('blog.html', posts=posts)

@main_bp.route('/blog/<slug>')
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, status='Published').first_or_404()
    # Increment view count
    post.views += 1
    db.session.commit()

    recent_posts = BlogPost.query.filter(
        BlogPost.id != post.id,
        BlogPost.status == 'Published'
    ).order_by(BlogPost.created_at.desc()).limit(3).all()

    return render_template('blog_post.html', post=post, recent_posts=recent_posts)

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        contact = Contact(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form.get('phone', ''),
            subject=request.form.get('subject', ''),
            message=request.form['message']
        )
        db.session.add(contact)
        db.session.commit()

        # Send email notification
        try:
            msg = Message(
                subject=f"New Contact Form Submission: {contact.subject}",
                recipients=[get_setting('contact_email', 'info@hiddekel.org')],
                body=f"""
New contact form submission:

Name: {contact.name}
Email: {contact.email}
Phone: {contact.phone}
Subject: {contact.subject}

Message:
{contact.message}
                """
            )
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")

        flash('Thank you for your message. We will get back to you soon!', 'success')
        return redirect(url_for('main.contact'))

    return render_template('contact.html')

@main_bp.route('/book-visit', methods=['POST'])
def book_visit():
    site_visit = SiteVisit(
        name=request.form['name'],
        email=request.form['email'],
        phone=request.form['phone'],
        preferred_date=datetime.strptime(request.form['preferred_date'], '%Y-%m-%d').date(),
        preferred_time=request.form['preferred_time'],
        message=request.form.get('message', '')
    )
    db.session.add(site_visit)
    db.session.commit()

    flash('Site visit request submitted successfully! We will contact you soon.', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/download/<int:id>')
def download_file(id):
    download = Download.query.get_or_404(id)
    if not download.is_active:
        flash('File not available for download.', 'error')
        return redirect(url_for('main.index'))

    download.download_count += 1
    db.session.commit()

    return send_from_directory('uploads', download.filename, as_attachment=True)

@main_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)