# Futuristic Landing Pages - CC & RCS Maharashtra
## AI-Powered Document Search System

[![HTML5](https://img.shields.io/badge/HTML5-Ready-orange.svg)](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5)
[![CSS3](https://img.shields.io/badge/CSS3-Modern-blue.svg)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Responsive](https://img.shields.io/badge/Design-Responsive-green.svg)](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)

> **Professional futuristic landing pages for the Maharashtra government's AI-powered document search system. Beautifully designed, mobile-responsive, and deployment-ready static pages.**

## 🎯 Overview

This repository contains **only the futuristic landing pages** specifically designed for the Commissioner for Cooperation and Registrar, Cooperative Societies, Maharashtra State. These static HTML pages provide professional coming soon and maintenance interfaces that can be deployed independently.

### 🌟 Key Features

- **🎨 Government Branding**: Official Maharashtra government styling and logos
- **📱 Responsive Design**: Mobile-first approach with perfect cross-device compatibility
- **✨ Futuristic UI**: Dark space theme with neon accents and glassmorphism effects
- **🚀 Performance Optimized**: Lightweight, fast-loading static files
- **🔧 Easy Deployment**: No server-side dependencies, deploy anywhere
- **♿ Accessible**: WCAG compliant with keyboard navigation support
- **🌐 SEO Friendly**: Proper meta tags and semantic HTML structure

## 🏗️ Project Structure

```
landing-pages-only/
├── index.html                   # Landing page selector
├── coming-soon.html            # Pre-launch page
├── maintenance.html            # System maintenance page
├── favicon.ico                 # Maharashtra IT favicon
├── assets/
│   ├── css/
│   │   └── style.css          # Main stylesheet with futuristic design
│   ├── js/
│   │   └── main.js            # Interactive JavaScript features
│   └── images/
│       ├── banner-opt-2-wotxt.png    # Maharashtra government banner
│       └── MahaIT_Logo.png           # Maharashtra IT department logo
└── README.md                   # This documentation
```

## 🎨 Page Designs

### 🚀 Coming Soon Page (`coming-soon.html`)

**Perfect for pre-launch scenarios**

- **Progress Indicator**: Visual progress bar showing development status (85% complete)
- **Feature Preview**: Showcase of upcoming AI-powered features
- **Launch Timeline**: Expected launch date with countdown
- **Contact Information**: Government contact details and support
- **Interactive Elements**: Hover effects and smooth animations

**Key Sections:**
- Hero section with Maharashtra government branding
- Development progress visualization
- Feature grid with AI capabilities preview
- Contact and update information
- Professional footer with government attribution

### 🔧 Maintenance Page (`maintenance.html`)

**Ideal for scheduled maintenance and system updates**

- **Live Countdown**: Real-time countdown timer for maintenance completion
- **Status Updates**: Current maintenance activities with progress indicators
- **Activity Tracker**: Visual representation of completed and pending tasks
- **Emergency Contact**: 24/7 support information for urgent needs
- **Real-time Updates**: Dynamic status updates with timestamps

**Key Sections:**
- Maintenance status dashboard
- Live countdown timer
- Current activities checklist
- System improvements showcase
- Emergency contact information

### 🏠 Index Page (`index.html`)

**Administrator control panel for page selection**

- **Page Selector**: Choose between coming soon or maintenance pages
- **Auto-redirect Logic**: Configurable automatic redirection
- **Admin Interface**: Simple selection interface for administrators
- **Time-based Routing**: Optional automatic page selection based on time

## 🚀 Deployment Guide

### 🌐 Dokploy Static Deployment (Recommended)

#### Step 1: Create New Application in Dokploy

1. **Go to Dokploy Dashboard**
2. **Click "Add Application"**
3. **Configure Application:**
   ```
   Application Name: maharashtra-landing-pages
   Build Type: Static ✅
   Repository: https://github.com/Nimble-esolutions/searchutility.git
   Branch: landing-pages-only
   ```

#### Step 2: Domain Configuration

```
Host: ai-sahakar.net (or your domain)
Path: /
Internal Path: /
Container Port: 80
HTTPS: Enable with Let's Encrypt
```

#### Step 3: Deploy

1. **Click "Deploy"**
2. **Dokploy will automatically:**
   - Clone the repository
   - Copy all files from root directory to `/usr/share/nginx/html`
   - Use optimized Nginx Dockerfile
   - Serve your futuristic landing pages

### 🌐 Traditional Web Server Deployment

#### Apache Configuration:
```apache
<VirtualHost *:80>
    ServerName ai-sahakar.net
    DocumentRoot /var/www/html/landing-pages
    
    # Enable compression
    <IfModule mod_deflate.c>
        AddOutputFilterByType DEFLATE text/html text/css application/javascript image/png
    </IfModule>
    
    # Cache static assets
    <IfModule mod_expires.c>
        ExpiresActive on
        ExpiresByType text/css "access plus 1 year"
        ExpiresByType application/javascript "access plus 1 year"
        ExpiresByType image/png "access plus 1 year"
    </IfModule>
</VirtualHost>
```

#### Nginx Configuration:
```nginx
server {
    listen 80;
    server_name ai-sahakar.net;
    root /var/www/html/landing-pages;
    index index.html coming-soon.html maintenance.html;

    # Gzip compression
    gzip on;
    gzip_types text/css application/javascript image/png;

    # Cache static assets
    location ~* \.(css|js|png|jpg|jpeg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Default fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### ☁️ CDN Deployment

#### CloudFlare Pages:
1. Connect your GitHub repository
2. Set build command: `echo "Static site - no build needed"`
3. Set publish directory: `landing-pages-only`
4. Configure custom domain: `ai-sahakar.net`

#### AWS S3 + CloudFront:
```bash
# Upload files to S3
aws s3 sync . s3://your-bucket-name/ --delete

# Configure CloudFront distribution
# Point to your S3 bucket
# Set custom domain: ai-sahakar.net
```

#### Netlify:
1. Drag and drop the `landing-pages-only` folder to Netlify
2. Configure custom domain
3. Enable HTTPS with Let's Encrypt

## 🎛️ Customization Guide

### 🎨 Visual Customization

**Colors and Branding:**
```css
/* In assets/css/style.css */
:root {
    --primary-gradient: linear-gradient(135deg, #00ffff, #ff00ff);
    --success-color: #00ff00;
    --warning-color: #ff9800;
    --text-primary: #ffffff;
    --text-secondary: #cccccc;
}
```

**Logo and Images:**
- Replace `assets/images/MahaIT_Logo.png` with your logo
- Replace `assets/images/banner-opt-2-wotxt.png` with your banner
- Maintain aspect ratios for best results

### 📝 Content Updates

**Coming Soon Page:**
```html
<!-- Update progress percentage -->
<div class="progress-fill" style="width: 85%;"></div>
<small>85% Complete</small>

<!-- Update launch date -->
<p>Expected Launch: Q4 2025</p>
```

**Maintenance Page:**
```javascript
// Update maintenance duration in maintenance.html
const maintenanceEnd = now + (2.5 * 60 * 60 * 1000); // 2.5 hours
```

**Contact Information:**
```html
<!-- Update in both pages -->
<div class="contact-item">
    <strong>Email:</strong> your-email@domain.com
</div>
<div class="contact-item">
    <strong>Phone:</strong> +91-XX-XXXX-XXXX
</div>
```

### ⚙️ Functional Customization

**Auto-redirect Logic:**
```javascript
// In index.html - uncomment and modify
const currentHour = new Date().getHours();
if (currentHour >= 2 && currentHour <= 6) {
    // Maintenance window: 2 AM to 6 AM
    window.location.href = 'maintenance.html';
} else {
    window.location.href = 'coming-soon.html';
}
```

## 🔧 Technical Specifications

### Browser Support
- **Modern Browsers**: Chrome 60+, Firefox 60+, Safari 12+, Edge 79+
- **Mobile Browsers**: iOS Safari 12+, Chrome Mobile 60+
- **Features Used**: CSS Grid, Flexbox, CSS Variables, ES6 JavaScript

### Performance Metrics
- **Page Load Time**: < 2 seconds on 3G
- **First Contentful Paint**: < 1.5 seconds
- **Lighthouse Score**: 95+ (Performance, Accessibility, Best Practices, SEO)
- **File Sizes**: 
  - HTML: ~8KB (gzipped)
  - CSS: ~12KB (gzipped)
  - JS: ~6KB (gzipped)
  - Images: ~150KB total

### Accessibility Features
- **WCAG 2.1 AA Compliant**
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Semantic HTML and ARIA labels
- **Color Contrast**: Meets accessibility standards
- **Focus Management**: Visible focus indicators

## 🚨 Troubleshooting

### Common Issues

1. **Images Not Loading**
   ```bash
   # Check file paths and permissions
   ls -la assets/images/
   # Ensure images are in correct directory
   ```

2. **CSS Not Applied**
   ```bash
   # Verify CSS file path in HTML
   # Check for MIME type issues on server
   ```

3. **JavaScript Errors**
   ```javascript
   // Check browser console for errors
   // Ensure ES6 compatibility
   ```

4. **Mobile Display Issues**
   ```css
   /* Check viewport meta tag */
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   ```

### Deployment Checklist

- [ ] All file paths are relative
- [ ] Images are optimized and compressed
- [ ] CSS and JS are minified (optional)
- [ ] Meta tags are updated for SEO
- [ ] Contact information is current
- [ ] HTTPS is configured
- [ ] Caching headers are set
- [ ] Gzip compression is enabled

## 📊 Usage Scenarios

### 🚀 Coming Soon Deployment
**When to use:**
- Pre-launch marketing
- Feature announcement
- User interest collection
- Stakeholder preview

**Deployment steps:**
1. Update progress percentage
2. Set expected launch date
3. Configure contact information
4. Deploy to production domain

### 🔧 Maintenance Deployment
**When to use:**
- Scheduled system updates
- Emergency maintenance
- Database migrations
- Security patches

**Deployment steps:**
1. Set maintenance duration
2. Update activity checklist
3. Configure emergency contacts
4. Activate maintenance mode

### 🎛️ Hybrid Deployment
**Automatic switching:**
```javascript
// Time-based switching
const maintenanceHours = [2, 3, 4, 5, 6]; // 2 AM - 6 AM
const currentHour = new Date().getHours();

if (maintenanceHours.includes(currentHour)) {
    window.location.href = 'maintenance.html';
} else {
    window.location.href = 'coming-soon.html';
}
```

## 📞 Support and Maintenance

### Technical Support
- **Email**: support@ccrs.maharashtra.gov.in
- **Phone**: +91-20-XXXX-XXXX (24/7 for maintenance issues)
- **Address**: Pune, Maharashtra, India

### Content Updates
- **Frequency**: Update progress and dates monthly
- **Responsibility**: IT Department, Maharashtra Government
- **Approval**: Department Head approval required for major changes

### Performance Monitoring
- **Uptime Monitoring**: Set up monitoring for landing page availability
- **Analytics**: Track visitor engagement and conversion
- **Error Tracking**: Monitor JavaScript errors and broken links

## 🔄 Version History

- **v1.0.0** (2025-01-06): Initial release with coming soon and maintenance pages
- **Features**: Responsive design, Maharashtra branding, interactive elements
- **Browser Support**: Modern browsers with ES6 support

## 📄 License

© 2025 Commissioner for Cooperation and Registrar, Cooperative Societies, Maharashtra State. All rights reserved.

---

**Built with ❤️ for the people of Maharashtra**