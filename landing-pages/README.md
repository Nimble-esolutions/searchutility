# Landing Pages - CC & RCS Maharashtra

Beautiful, responsive landing pages for the Maharashtra Cooperative Societies AI-powered document search system.

## 📁 Files Structure

```
landing-pages/
├── coming-soon.html      # Coming Soon page
├── maintenance.html      # Maintenance page
├── assets/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── main.js       # Interactive JavaScript
│   └── images/
│       ├── banner-opt-2-wotxt.png  # Maharashtra banner
│       └── MahaIT_Logo.png         # Maharashtra IT logo
└── README.md            # This file
```

## 🎨 Features

### Coming Soon Page (`coming-soon.html`)
- **Modern Design**: Glassmorphism effects with gradient backgrounds
- **Progress Indicator**: Visual progress bar showing development status
- **Feature Preview**: Showcase of upcoming AI features
- **Responsive Layout**: Works perfectly on all devices
- **Interactive Elements**: Hover effects and animations
- **Contact Information**: Easy access to support details

### Maintenance Page (`maintenance.html`)
- **Live Countdown**: Real-time countdown timer for maintenance completion
- **Status Updates**: Current maintenance activities with progress indicators
- **What's Being Improved**: Visual showcase of improvements being made
- **Emergency Contact**: 24/7 support information
- **Real-time Updates**: Dynamic status updates with timestamps

### Shared Features
- **Branded Header**: Official Maharashtra government banner
- **Professional Styling**: Clean, modern design with government branding
- **Accessibility**: Keyboard navigation and screen reader friendly
- **Performance Optimized**: Fast loading with optimized assets
- **Mobile First**: Responsive design for all screen sizes
- **SEO Friendly**: Proper meta tags and semantic HTML

## 🚀 Deployment Instructions

### Option 1: Simple Web Server Deployment

1. **Upload Files**: Copy the entire `landing-pages` folder to your web server
2. **Set Document Root**: Point your domain to the `landing-pages` directory
3. **Configure Web Server**: Ensure static file serving is enabled

**Example for Apache (.htaccess):**
```apache
# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>

# Cache static assets
<IfModule mod_expires.c>
    ExpiresActive on
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
</IfModule>
```

**Example for Nginx:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/landing-pages;
    index coming-soon.html maintenance.html;

    # Gzip compression
    gzip on;
    gzip_types text/css application/javascript image/png image/jpeg;

    # Cache static assets
    location ~* \.(css|js|png|jpg|jpeg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Fallback to coming-soon page
    location / {
        try_files $uri $uri/ /coming-soon.html;
    }
}
```

### Option 2: CDN Deployment (Recommended)

1. **Upload to CDN**: Upload files to your CDN (CloudFlare, AWS CloudFront, etc.)
2. **Configure Caching**: Set appropriate cache headers for static assets
3. **Enable Compression**: Enable Gzip/Brotli compression
4. **Set Custom Domain**: Point your domain to the CDN

### Option 3: Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Deploy with Docker:
```bash
docker build -t cc-rcs-landing .
docker run -d -p 80:80 cc-rcs-landing
```

## 🔧 Customization

### Updating Content

1. **Edit HTML Files**: Modify `coming-soon.html` or `maintenance.html`
2. **Update Progress**: Change progress percentage in coming-soon page
3. **Modify Countdown**: Adjust maintenance duration in maintenance page
4. **Update Contact Info**: Change email, phone, and address details

### Styling Changes

1. **Colors**: Modify CSS variables in `assets/css/style.css`
2. **Fonts**: Update Google Fonts imports in HTML files
3. **Layout**: Adjust grid layouts and spacing in CSS
4. **Animations**: Customize animations and transitions

### Adding New Features

1. **JavaScript**: Add new functionality in `assets/js/main.js`
2. **Icons**: Use Font Awesome icons (already included)
3. **Images**: Add new images to `assets/images/` directory

## 📱 Browser Support

- **Modern Browsers**: Chrome 60+, Firefox 60+, Safari 12+, Edge 79+
- **Mobile Browsers**: iOS Safari 12+, Chrome Mobile 60+
- **Features Used**: CSS Grid, Flexbox, CSS Variables, ES6 JavaScript

## 🔒 Security Considerations

- **No Server-Side Code**: Pure static files, no security vulnerabilities
- **Content Security Policy**: Consider adding CSP headers
- **HTTPS**: Always serve over HTTPS in production
- **Regular Updates**: Keep external dependencies (Font Awesome, Google Fonts) updated

## 📊 Performance

- **Optimized Images**: Compressed PNG images
- **Minified CSS**: Production-ready stylesheets
- **Lazy Loading**: Images load as needed
- **Caching**: Proper cache headers for static assets

## 🎯 Usage Scenarios

### Coming Soon Page
- **Pre-launch**: Use when the system is under development
- **Marketing**: Showcase upcoming features to stakeholders
- **User Engagement**: Collect user interest and feedback

### Maintenance Page
- **Scheduled Maintenance**: During planned system updates
- **Emergency Maintenance**: During unexpected downtime
- **System Upgrades**: When deploying major updates

## 📞 Support

For technical support or customization requests:
- **Email**: support@ccrs.maharashtra.gov.in
- **Phone**: +91-20-XXXX-XXXX
- **Address**: Pune, Maharashtra, India

## 📄 License

© 2025 Commissioner for Cooperation and Registrar, Cooperative Societies, Maharashtra State. All rights reserved.

---

**Note**: Remember to update contact information, countdown timers, and progress indicators according to your actual deployment schedule and requirements.
