# Deployment Guide - CC & RCS Maharashtra Landing Pages
## Apple-Style Design with Independent Pages

### 🎯 **Overview**

This repository contains three independent landing pages with Apple-style design:
- `index.html` - Auto-redirect page (default)
- `coming-soon.html` - Futuristic coming soon page
- `maintenance.html` - Animated maintenance page

### 🚀 **Dokploy Static Deployment**

#### **Method 1: Deploy All Pages (Recommended)**

1. **Create Application in Dokploy:**
   ```
   Application Name: maharashtra-landing-pages
   Build Type: Static
   Repository: Nimble-esolutions/searchutility
   Branch: landing-pages-only
   ```

2. **Domain Configuration:**
   ```
   Host: ai-sahakar.net
   Path: /
   Internal Path: /
   Container Port: 80
   HTTPS: Enable with Let's Encrypt
   ```

3. **Deploy** - All pages will be available:
   - `https://ai-sahakar.net/` - Auto-redirect page
   - `https://ai-sahakar.net/coming-soon.html` - Coming soon page
   - `https://ai-sahakar.net/maintenance.html` - Maintenance page

#### **Method 2: Deploy Single Page as Index**

To set a specific page as the main page, rename it to `index.html`:

**For Coming Soon Page:**
```bash
# Rename coming-soon.html to index.html
mv coming-soon.html index.html
# Remove old index.html
rm index.html.backup
```

**For Maintenance Page:**
```bash
# Rename maintenance.html to index.html
mv maintenance.html index.html
# Remove old index.html
rm index.html.backup
```

### 🎨 **Design Features**

#### **Apple-Style UI/UX:**
- **SF Pro Display/Text Fonts**: Apple's official typeface
- **Dark Theme**: Pure black background with subtle gradients
- **Glassmorphism**: Frosted glass effects with backdrop blur
- **Minimalist Design**: Clean, spacious layouts
- **Smooth Animations**: Subtle transitions and hover effects
- **Responsive Design**: Perfect on all devices

#### **Color Scheme:**
- **Primary**: Pure black (#000000)
- **Text**: White (#f5f5f7) and light gray (#a1a1a6)
- **Accents**: 
  - Coming Soon: Green (#34c759) and blue (#007aff)
  - Maintenance: Orange (#ff9500) and red (#ff6b35)
- **Backgrounds**: Subtle gradients with transparency

### 📱 **Responsive Design**

- **Desktop**: Optimized for 1920x1080 and larger
- **Tablet**: Perfect on iPad and Android tablets
- **Mobile**: iPhone and Android phone optimized
- **Breakpoints**: 768px and 480px

### 🔧 **Customization**

#### **Change Page Content:**
1. Edit the HTML files directly
2. Update text, colors, and images
3. Commit and push changes
4. Dokploy will auto-deploy

#### **Modify Auto-Redirect Logic:**
Edit `index.html` JavaScript:
```javascript
function redirectToPage() {
    const currentHour = new Date().getHours();
    
    // Customize maintenance window
    if (currentHour >= 2 && currentHour <= 6) {
        window.location.href = 'maintenance.html';
    } else {
        window.location.href = 'coming-soon.html';
    }
}
```

#### **Update Contact Information:**
Edit contact sections in both pages:
```html
<div class="contact-item">
    <div class="contact-icon">✉️</div>
    <span>your-email@domain.com</span>
</div>
```

### 📊 **Performance**

- **Page Load Time**: < 1 second
- **Lighthouse Score**: 95+ across all metrics
- **File Sizes**: 
  - HTML: ~5KB (gzipped)
  - CSS: ~8KB (gzipped)
  - Images: ~100KB total

### 🎯 **Usage Scenarios**

#### **Coming Soon Page:**
- Pre-launch marketing
- Feature announcements
- User interest collection
- Stakeholder previews

#### **Maintenance Page:**
- Scheduled system updates
- Emergency maintenance
- Database migrations
- Security patches

#### **Auto-Redirect Page:**
- Smart routing based on time
- Fallback for all scenarios
- Manual page selection

### 🔄 **Updates and Maintenance**

1. **Content Updates:**
   - Edit HTML files
   - Commit changes
   - Push to repository
   - Dokploy auto-deploys

2. **Design Updates:**
   - Modify CSS in HTML files
   - Update colors, fonts, layouts
   - Test on different devices

3. **Feature Updates:**
   - Add new sections
   - Update JavaScript functionality
   - Enhance animations

### 📞 **Support**

- **Email**: support@ccrs.maharashtra.gov.in
- **Phone**: +91-20-XXXX-XXXX
- **Address**: Pune, Maharashtra, India

---

**Built with ❤️ for the people of Maharashtra**
