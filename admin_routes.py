from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import User, Stand, StandImage, BlogPost, GalleryImage, Contact, SiteVisit, Download, SiteSetting, Testimonial, TeamMember
from app import db
from werkzeug.utils import secure_filename
from PIL import Image
import os
import re
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'admin_user_id' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def create_slug(title):
    """Create a URL-friendly slug from title"""
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.is_admin:
            session['admin_user_id'] = user.id
            session['admin_username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('admin_user_id', None)
    session.pop('admin_username', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@login_required
def dashboard():
    stats = {
        'total_stands': Stand.query.count(),
        'available_stands': Stand.query.filter_by(status='Available').count(),
        'sold_stands': Stand.query.filter_by(status='Sold').count(),
        'reserved_stands': Stand.query.filter_by(status='Reserved').count(),
        'total_blogs': BlogPost.query.count(),
        'published_blogs': BlogPost.query.filter_by(status='Published').count(),
        'unread_messages': Contact.query.filter_by(is_read=False).count(),
        'pending_visits': SiteVisit.query.filter_by(status='Pending').count(),
        'total_downloads': db.session.query(db.func.sum(Download.download_count)).scalar() or 0,
        'gallery_images': GalleryImage.query.filter_by(is_active=True).count(),
    }
    
    recent_contacts = Contact.query.order_by(Contact.created_at.desc()).limit(5).all()
    recent_visits = SiteVisit.query.order_by(SiteVisit.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', stats=stats, 
                         recent_contacts=recent_contacts, recent_visits=recent_visits)

# Stands Management
@admin_bp.route('/stands')
@login_required
def stands():
    stands = Stand.query.order_by(Stand.created_at.desc()).all()
    return render_template('admin/stands.html', stands=stands)

@admin_bp.route('/stands/add', methods=['GET', 'POST'])
@login_required
def add_stand():
    if request.method == 'POST':
        stand = Stand(
            title=request.form['title'],
            description=request.form['description'],
            price=float(request.form['price']) if request.form['price'] else None,
            location=request.form['location'],
            size=request.form['size'],
            status=request.form['status'],
            map_embed=request.form.get('map_embed', ''),
            featured=bool(request.form.get('featured'))
        )
        db.session.add(stand)
        db.session.flush()  # Get the ID
        
        # Handle image uploads
        for file in request.files.getlist('images'):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"stand_{stand.id}_{filename}"
                file.save(os.path.join('uploads', filename))
                
                # Create thumbnail
                try:
                    with Image.open(os.path.join('uploads', filename)) as img:
                        img.thumbnail((300, 300))
                        thumb_filename = f"thumb_{filename}"
                        img.save(os.path.join('uploads', thumb_filename))
                except Exception as e:
                    print(f"Error creating thumbnail: {e}")
                
                stand_image = StandImage(
                    stand_id=stand.id,
                    filename=filename,
                    caption=request.form.get(f'caption_{file.filename}', ''),
                    is_primary=len(stand.images) == 0  # First image is primary
                )
                db.session.add(stand_image)
        
        db.session.commit()
        flash('Stand added successfully!', 'success')
        return redirect(url_for('admin.stands'))
    
    return render_template('admin/stand_form.html', stand=None)

@admin_bp.route('/stands/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_stand(id):
    stand = Stand.query.get_or_404(id)
    
    if request.method == 'POST':
        stand.title = request.form['title']
        stand.description = request.form['description']
        stand.price = float(request.form['price']) if request.form['price'] else None
        stand.location = request.form['location']
        stand.size = request.form['size']
        stand.status = request.form['status']
        stand.map_embed = request.form.get('map_embed', '')
        stand.featured = bool(request.form.get('featured'))
        stand.updated_at = datetime.utcnow()
        
        # Handle new image uploads
        for file in request.files.getlist('images'):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"stand_{stand.id}_{filename}"
                file.save(os.path.join('uploads', filename))
                
                stand_image = StandImage(
                    stand_id=stand.id,
                    filename=filename,
                    caption=request.form.get(f'caption_{file.filename}', '')
                )
                db.session.add(stand_image)
        
        db.session.commit()
        flash('Stand updated successfully!', 'success')
        return redirect(url_for('admin.stands'))
    
    return render_template('admin/stand_form.html', stand=stand)

@admin_bp.route('/stands/delete/<int:id>')
@login_required
def delete_stand(id):
    stand = Stand.query.get_or_404(id)
    
    # Delete associated images
    for image in stand.images:
        try:
            os.remove(os.path.join('uploads', image.filename))
            os.remove(os.path.join('uploads', f"thumb_{image.filename}"))
        except:
            pass
    
    db.session.delete(stand)
    db.session.commit()
    flash('Stand deleted successfully!', 'success')
    return redirect(url_for('admin.stands'))

# Blog Management
@admin_bp.route('/blog')
@login_required
def blog():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/blog.html', posts=posts)

@admin_bp.route('/blog/add', methods=['GET', 'POST'])
@login_required
def add_blog():
    if request.method == 'POST':
        title = request.form['title']
        slug = create_slug(title)
        
        # Ensure unique slug
        counter = 1
        original_slug = slug
        while BlogPost.query.filter_by(slug=slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        post = BlogPost(
            title=title,
            slug=slug,
            content=request.form['content'],
            excerpt=request.form['excerpt'],
            status=request.form['status']
        )
        
        # Handle featured image upload
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join('uploads', filename))
                post.featured_image = filename
        
        db.session.add(post)
        db.session.commit()
        flash('Blog post added successfully!', 'success')
        return redirect(url_for('admin.blog'))
    
    return render_template('admin/blog_form.html', post=None)

@admin_bp.route('/blog/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_blog(id):
    post = BlogPost.query.get_or_404(id)
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.excerpt = request.form['excerpt']
        post.status = request.form['status']
        post.updated_at = datetime.utcnow()
        
        # Handle featured image upload
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and allowed_file(file.filename) and file.filename != '':
                # Delete old image
                if post.featured_image:
                    try:
                        os.remove(os.path.join('uploads', post.featured_image))
                    except:
                        pass
                
                filename = secure_filename(file.filename)
                filename = f"blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join('uploads', filename))
                post.featured_image = filename
        
        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin.blog'))
    
    return render_template('admin/blog_form.html', post=post)

@admin_bp.route('/blog/delete/<int:id>')
@login_required
def delete_blog(id):
    post = BlogPost.query.get_or_404(id)
    
    # Delete featured image
    if post.featured_image:
        try:
            os.remove(os.path.join('uploads', post.featured_image))
        except:
            pass
    
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('admin.blog'))

# Gallery Management
@admin_bp.route('/gallery')
@login_required
def gallery():
    images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
    return render_template('admin/gallery.html', images=images)

@admin_bp.route('/gallery/upload', methods=['POST'])
@login_required
def upload_gallery():
    category = request.form['category']
    
    for file in request.files.getlist('images'):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = f"gallery_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            file.save(os.path.join('uploads', filename))
            
            # Create thumbnail
            try:
                with Image.open(os.path.join('uploads', filename)) as img:
                    img.thumbnail((300, 300))
                    thumb_filename = f"thumb_{filename}"
                    img.save(os.path.join('uploads', thumb_filename))
            except Exception as e:
                print(f"Error creating thumbnail: {e}")
            
            image = GalleryImage(
                filename=filename,
                caption=request.form.get('caption', ''),
                category=category
            )
            db.session.add(image)
    
    db.session.commit()
    flash('Images uploaded successfully!', 'success')
    return redirect(url_for('admin.gallery'))

@admin_bp.route('/gallery/delete/<int:id>')
@login_required
def delete_gallery_image(id):
    image = GalleryImage.query.get_or_404(id)
    
    # Delete files
    try:
        os.remove(os.path.join('uploads', image.filename))
        os.remove(os.path.join('uploads', f"thumb_{image.filename}"))
    except:
        pass
    
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('admin.gallery'))

# Contact Management
@admin_bp.route('/contacts')
@login_required
def contacts():
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    visits = SiteVisit.query.order_by(SiteVisit.created_at.desc()).all()
    return render_template('admin/contacts.html', contacts=contacts, visits=visits)

@admin_bp.route('/contacts/mark-read/<int:id>')
@login_required
def mark_contact_read(id):
    contact = Contact.query.get_or_404(id)
    contact.is_read = True
    db.session.commit()
    return redirect(url_for('admin.contacts'))

# Site Settings
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Handle logo upload
        if 'site_logo' in request.files:
            file = request.files['site_logo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"logo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join('uploads', filename))
                
                # Update logo setting
                logo_setting = SiteSetting.query.filter_by(key='site_logo').first()
                if logo_setting:
                    # Delete old logo file
                    if logo_setting.value:
                        try:
                            os.remove(os.path.join('uploads', logo_setting.value))
                        except:
                            pass
                    logo_setting.value = filename
                    logo_setting.updated_at = datetime.utcnow()
                else:
                    logo_setting = SiteSetting(key='site_logo', value=filename)
                    db.session.add(logo_setting)
        
        settings_data = {
            'site_title': request.form.get('site_title', ''),
            'site_tagline': request.form.get('site_tagline', ''),
            'contact_email': request.form.get('contact_email', ''),
            'contact_phone': request.form.get('contact_phone', ''),
            'contact_address': request.form.get('contact_address', ''),
            'google_maps_embed': request.form.get('google_maps_embed', ''),
            'facebook_url': request.form.get('facebook_url', ''),
            'twitter_url': request.form.get('twitter_url', ''),
            'instagram_url': request.form.get('instagram_url', ''),
            'linkedin_url': request.form.get('linkedin_url', ''),
            'whatsapp_number': request.form.get('whatsapp_number', ''),
            'footer_text': request.form.get('footer_text', ''),
        }
        
        for key, value in settings_data.items():
            setting = SiteSetting.query.filter_by(key=key).first()
            if setting:
                setting.value = value
                setting.updated_at = datetime.utcnow()
            else:
                setting = SiteSetting(key=key, value=value)
                db.session.add(setting)
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.settings'))
    
    # Get current settings
    settings = {}
    for setting in SiteSetting.query.all():
        settings[setting.key] = setting.value
    
    return render_template('admin/settings.html', settings=settings)

# Downloads Management
@admin_bp.route('/downloads')
@login_required
def downloads():
    downloads = Download.query.order_by(Download.created_at.desc()).all()
    return render_template('admin/downloads.html', downloads=downloads)

@admin_bp.route('/downloads/upload', methods=['POST'])
@login_required
def upload_download():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('admin.downloads'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('admin.downloads'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        file.save(os.path.join('uploads', filename))
        
        download = Download(
            title=request.form['title'],
            filename=filename,
            category=request.form['category'],
            description=request.form.get('description', '')
        )
        db.session.add(download)
        db.session.commit()
        flash('File uploaded successfully!', 'success')
    else:
        flash('Invalid file type', 'error')
    
    return redirect(url_for('admin.downloads'))

@admin_bp.route('/downloads/delete/<int:id>')
@login_required
def delete_download(id):
    download = Download.query.get_or_404(id)
    
    # Delete file
    try:
        os.remove(os.path.join('uploads', download.filename))
    except:
        pass
    
    db.session.delete(download)
    db.session.commit()
    flash('Download deleted successfully!', 'success')
    return redirect(url_for('admin.downloads'))

# Team Management
@admin_bp.route('/team')
@login_required
def team():
    team_members = TeamMember.query.order_by(TeamMember.display_order.asc(), TeamMember.created_at.desc()).all()
    return render_template('admin/team.html', team_members=team_members)

@admin_bp.route('/team/add', methods=['GET', 'POST'])
@login_required
def add_team_member():
    if request.method == 'POST':
        member = TeamMember(
            name=request.form['name'],
            position=request.form['position'],
            bio=request.form.get('bio', ''),
            linkedin_url=request.form.get('linkedin_url', ''),
            email=request.form.get('email', ''),
            phone=request.form.get('phone', ''),
            years_experience=int(request.form['years_experience']) if request.form.get('years_experience') else None,
            specialization=request.form.get('specialization', ''),
            display_order=int(request.form.get('display_order', 0))
        )
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"team_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join('uploads', filename))
                member.image = filename
        
        db.session.add(member)
        db.session.commit()
        flash('Team member added successfully!', 'success')
        return redirect(url_for('admin.team'))
    
    return render_template('admin/team_form.html', member=None)

@admin_bp.route('/team/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_team_member(id):
    member = TeamMember.query.get_or_404(id)
    
    if request.method == 'POST':
        member.name = request.form['name']
        member.position = request.form['position']
        member.bio = request.form.get('bio', '')
        member.linkedin_url = request.form.get('linkedin_url', '')
        member.email = request.form.get('email', '')
        member.phone = request.form.get('phone', '')
        member.years_experience = int(request.form['years_experience']) if request.form.get('years_experience') else None
        member.specialization = request.form.get('specialization', '')
        member.display_order = int(request.form.get('display_order', 0))
        member.updated_at = datetime.utcnow()
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Delete old image
                if member.image:
                    try:
                        os.remove(os.path.join('uploads', member.image))
                    except:
                        pass
                
                filename = secure_filename(file.filename)
                filename = f"team_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join('uploads', filename))
                member.image = filename
        
        db.session.commit()
        flash('Team member updated successfully!', 'success')
        return redirect(url_for('admin.team'))
    
    return render_template('admin/team_form.html', member=member)

@admin_bp.route('/team/delete/<int:id>')
@login_required
def delete_team_member(id):
    member = TeamMember.query.get_or_404(id)
    
    # Delete image
    if member.image:
        try:
            os.remove(os.path.join('uploads', member.image))
        except:
            pass
    
    db.session.delete(member)
    db.session.commit()
    flash('Team member deleted successfully!', 'success')
    return redirect(url_for('admin.team'))
