from app import db
from models import User, Stand, StandImage, BlogPost, GalleryImage, SiteSetting, Testimonial, Download
from datetime import datetime, date
import os

def seed_initial_data():
    """Seed the database with initial data if it's empty"""

    # Create admin user if it doesn't exist
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            email='admin@hiddekel.org',
            is_admin=True
        )
        admin_user.set_password('admin123')  # Change this in production
        db.session.add(admin_user)
        print("Created admin user: admin/admin123")

    # Create site settings if they don't exist
    default_settings = {
        'site_title': 'Hiddekel Investments',
        'site_tagline': 'We are the land developers of choice.',
        'contact_email': 'info@hiddekel.org',
        'contact_phone': '+263 716 236 518',
        'contact_address': 'Suite 13, 1st Floor, Merchant House, 43 Robson Manyika Ave, Harare',
        'google_maps_embed': '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3798.4722043194744!2d31.035800915074856!3d-17.829771987793706!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x1931a4de8d0e2a37%3A0x8f0c0e0f8e0e0e0e!2sHarare%2C%20Zimbabwe!5e0!3m2!1sen!2sus!4v1609459200000!5m2!1sen!2sus" width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe>',
        'facebook_url': 'https://facebook.com/hiddekel',
        'twitter_url': 'https://twitter.com/hiddekel',
        'instagram_url': 'https://instagram.com/hiddekel',
        'linkedin_url': 'https://linkedin.com/company/hiddekel',
        'whatsapp_number': '+263716236518',
        'footer_text': '© 2024 Hiddekel Investments. All rights reserved. We are the land developers of choice.',
    }

    for key, value in default_settings.items():
        if not SiteSetting.query.filter_by(key=key).first():
            setting = SiteSetting(key=key, value=value)
            db.session.add(setting)

    # Create featured stands if they don't exist
    if Stand.query.count() == 0:
        stands_data = [
            {
                'title': 'Premium Residential Stand - Borrowdale',
                'description': 'A premium 2000 sqm residential stand located in the prestigious Borrowdale area. Perfect for building your dream home with excellent infrastructure and utilities.',
                'price': 125000.00,
                'location': 'Borrowdale, Harare',
                'size': '2000 sqm',
                'status': 'Available',
                'featured': True,
                'map_embed': '<iframe src="https://www.google.com/maps/embed" width="100%" height="300"></iframe>'
            },
            {
                'title': 'Commercial Plot - CBD',
                'description': 'Strategic commercial plot in Harare CBD, ideal for office development or retail space. High foot traffic area with excellent visibility.',
                'price': 250000.00,
                'location': 'Harare CBD',
                'size': '1500 sqm',
                'status': 'Available',
                'featured': True
            },
            {
                'title': 'Residential Stand - Mt Pleasant',
                'description': 'Beautiful residential stand in Mt Pleasant with mountain views. Quiet neighborhood with good security and proximity to schools.',
                'price': 95000.00,
                'location': 'Mt Pleasant, Harare',
                'size': '1800 sqm',
                'status': 'Available',
                'featured': True
            },
            {
                'title': 'Industrial Plot - Msasa',
                'description': 'Large industrial plot suitable for manufacturing or warehousing. Good road access and proximity to transport links.',
                'price': 180000.00,
                'location': 'Msasa, Harare',
                'size': '5000 sqm',
                'status': 'Available',
                'featured': True
            },
            {
                'title': 'Luxury Stand - Chisipite',
                'description': 'Exclusive luxury stand in Chisipite with panoramic city views. Premium location for upmarket residential development.',
                'price': 350000.00,
                'location': 'Chisipite, Harare',
                'size': '3000 sqm',
                'status': 'Reserved',
                'featured': True
            },
            {
                'title': 'Development Land - Ruwa',
                'description': 'Large development land suitable for subdivision or commercial development. Growing area with excellent potential.',
                'price': 75000.00,
                'location': 'Ruwa',
                'size': '10000 sqm',
                'status': 'Available',
                'featured': True
            }
        ]

        for stand_data in stands_data:
            stand = Stand(**stand_data)
            db.session.add(stand)

    # Create blog posts if they don't exist
    if BlogPost.query.count() == 0:
        blog_posts = [
            {
                'title': 'Real Estate Investment Trends in Zimbabwe 2024',
                'slug': 'real-estate-investment-trends-zimbabwe-2024',
                'content': '''<p>The real estate market in Zimbabwe continues to show promising growth patterns as we move through 2024. With increasing foreign investment and infrastructure development, property values in key areas have shown steady appreciation.</p>

<h3>Key Market Indicators</h3>
<p>Our analysis shows that residential properties in Harare's northern suburbs have experienced an average growth of 12% year-on-year. Commercial properties, particularly in the CBD and surrounding areas, have also shown strong performance.</p>

<h3>Investment Opportunities</h3>
<p>For investors looking to enter the Zimbabwe real estate market, now presents an excellent opportunity. With the government's commitment to infrastructure development and economic stability measures, the property market is positioned for continued growth.</p>

<h3>Location Spotlight</h3>
<p>Areas like Borrowdale, Mt Pleasant, and Chisipite continue to be prime locations for residential investment, while the CBD and industrial areas like Msasa offer excellent commercial opportunities.</p>''',
                'excerpt': 'Explore the latest trends and opportunities in Zimbabwe\'s real estate market for 2024.',
                'status': 'Published'
            },
            {
                'title': 'Guide to Buying Land in Harare',
                'slug': 'guide-to-buying-land-harare',
                'content': '''<p>Purchasing land in Harare requires careful consideration of several factors. This comprehensive guide will walk you through the essential steps and considerations for a successful land purchase.</p>

<h3>Legal Requirements</h3>
<p>Before purchasing any land in Zimbabwe, it's crucial to understand the legal framework. Ensure all documentation is in order and consider engaging a qualified legal professional to guide you through the process.</p>

<h3>Location Considerations</h3>
<p>The location of your land purchase will significantly impact both its current value and future appreciation potential. Consider factors such as proximity to amenities, infrastructure development plans, and neighborhood growth patterns.</p>

<h3>Due Diligence</h3>
<p>Always conduct thorough due diligence, including title deed verification, land survey, and checking for any encumbrances or restrictions on the property.</p>''',
                'excerpt': 'Everything you need to know about purchasing land in Harare, from legal requirements to location considerations.',
                'status': 'Published'
            },
            {
                'title': 'Why Choose Hiddekel Investments',
                'slug': 'why-choose-hiddekel-investments',
                'content': '''<p>At Hiddekel Investments, we pride ourselves on being the land developers of choice. With years of experience in the Zimbabwe real estate market, we offer unparalleled expertise and service.</p>

<h3>Our Commitment</h3>
<p>We are committed to providing our clients with the best possible service, from initial consultation through to final transfer. Our team of experienced professionals ensures that every transaction is handled with the utmost care and attention to detail.</p>

<h3>Track Record</h3>
<p>Our track record speaks for itself. We have successfully facilitated hundreds of property transactions, helping individuals and businesses find the perfect land for their needs.</p>

<h3>Customer Service</h3>
<p>What sets us apart is our commitment to excellent customer service. We believe in building long-term relationships with our clients and providing ongoing support even after the transaction is complete.</p>''',
                'excerpt': 'Discover what makes Hiddekel Investments the preferred choice for land development in Zimbabwe.',
                'status': 'Featured'
            },
            {
                'title': 'Commercial Property Investment Opportunities',
                'slug': 'commercial-property-investment-opportunities',
                'content': '''<p>Commercial property investment in Zimbabwe offers excellent opportunities for both local and international investors. With a growing economy and increasing business activity, demand for quality commercial space continues to rise.</p>

<h3>Market Overview</h3>
<p>The commercial property market in Harare has shown remarkable resilience and growth. Key sectors driving demand include retail, office space, and industrial facilities.</p>

<h3>Investment Benefits</h3>
<p>Commercial property investment offers several advantages including steady rental income, capital appreciation potential, and portfolio diversification benefits.</p>

<h3>Location Analysis</h3>
<p>Prime commercial locations in Harare continue to command premium rents and show strong capital growth potential. Areas such as the CBD, Avondale, and Msasa industrial area are particularly attractive to investors.</p>''',
                'excerpt': 'Explore the lucrative opportunities in Zimbabwe\'s commercial property market.',
                'status': 'Published'
            },
            {
                'title': 'Residential Development Trends',
                'slug': 'residential-development-trends',
                'content': '''<p>The residential development sector in Zimbabwe is experiencing significant transformation, with new trends emerging in design, sustainability, and community planning.</p>

<h3>Modern Design Trends</h3>
<p>Contemporary residential developments are incorporating modern architectural elements while respecting local cultural preferences. Open-plan designs, natural lighting, and outdoor living spaces are becoming increasingly popular.</p>

<h3>Sustainability Focus</h3>
<p>Environmental consciousness is driving demand for sustainable building practices. Solar power, rainwater harvesting, and energy-efficient designs are becoming standard features in new developments.</p>

<h3>Community-Centered Development</h3>
<p>Modern residential developments are focusing on creating complete communities with integrated amenities including schools, shopping centers, and recreational facilities.</p>''',
                'excerpt': 'Discover the latest trends shaping residential development in Zimbabwe.',
                'status': 'Published'
            },
            {
                'title': 'Investment Financing Options',
                'slug': 'investment-financing-options',
                'content': '''<p>Understanding the various financing options available for real estate investment is crucial for making informed decisions. This guide explores the different financing methods available in Zimbabwe.</p>

<h3>Traditional Bank Financing</h3>
<p>Local banks offer various mortgage and development finance products for both residential and commercial properties. Terms and conditions vary significantly between institutions.</p>

<h3>Developer Financing</h3>
<p>Many developers, including Hiddekel Investments, offer flexible financing arrangements to help clients secure their desired properties. These arrangements often provide more favorable terms than traditional banking.</p>

<h3>International Finance</h3>
<p>For larger investments, international financing options may be available through foreign banks or investment funds specializing in emerging markets.</p>''',
                'excerpt': 'Navigate the various financing options available for real estate investment in Zimbabwe.',
                'status': 'Published'
            }
        ]

        for post_data in blog_posts:
            post = BlogPost(**post_data)
            db.session.add(post)

    # Create testimonials if they don't exist
    if Testimonial.query.count() == 0:
        testimonials_data = [
            {
                'name': 'John Mukamuri',
                'position': 'Business Owner',
                'company': 'Mukamuri Enterprises',
                'content': 'Hiddekel Investments helped me find the perfect commercial plot for my business. Their professional service and attention to detail made the entire process smooth and stress-free.',
                'rating': 5
            },
            {
                'name': 'Sarah Chigumba',
                'position': 'Homeowner',
                'company': '',
                'content': 'I couldn\'t be happier with my residential stand purchase through Hiddekel. The location is perfect and the value for money is excellent. Highly recommended!',
                'rating': 5
            },
            {
                'name': 'Michael Zvobgo',
                'position': 'Property Developer',
                'company': 'Zvobgo Properties',
                'content': 'As a fellow developer, I appreciate Hiddekel\'s professionalism and market knowledge. They consistently deliver quality properties and excellent service.',
                'rating': 5
            }
        ]

        for testimonial_data in testimonials_data:
            testimonial = Testimonial(**testimonial_data)
            db.session.add(testimonial)

    # Create sample downloads if they don't exist
    if Download.query.count() == 0:
        downloads_data = [
            {
                'title': 'Hiddekel Investments Brochure',
                'filename': 'hiddekel_brochure.pdf',
                'category': 'Brochure',
                'description': 'Complete overview of our services and available properties'
            },
            {
                'title': 'Property Investment Guide',
                'filename': 'property_investment_guide.pdf',
                'category': 'Guide',
                'description': 'Comprehensive guide to property investment in Zimbabwe'
            },
            {
                'title': 'Financing Options Overview',
                'filename': 'financing_options.pdf',
                'category': 'Information',
                'description': 'Overview of available financing options for property purchases'
            }
        ]

        for download_data in downloads_data:
            download = Download(**download_data)
            db.session.add(download)

    try:
        db.session.commit()
        print("Initial data seeded successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding data: {e}")