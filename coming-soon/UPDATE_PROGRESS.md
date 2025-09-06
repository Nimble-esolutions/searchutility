# How to Update Progress - Simple Instructions

## 🎯 **Quick Methods to Change Progress**

### **Method 1: Browser Console (Easiest)**
1. **Open your website** in browser
2. **Press F12** to open Developer Tools
3. **Go to Console tab**
4. **Type:** `updateProgress(50)` (replace 50 with your desired percentage)
5. **Press Enter** - Progress updates instantly!

**Examples:**
```javascript
updateProgress(25)  // Set to 25%
updateProgress(50)  // Set to 50%
updateProgress(75)  // Set to 75%
updateProgress(90)  // Set to 90%
```

### **Method 2: URL Parameters (Testing)**
Add `?progress=X` to your URL:
```
https://your-domain.com/coming-soon/?progress=30
https://your-domain.com/coming-soon/?progress=60
https://your-domain.com/coming-soon/?progress=85
```

### **Method 3: Edit config.js File**
1. **Edit the file:** `coming-soon/config.js`
2. **Change this line:**
   ```javascript
   window.PROGRESS_PERCENTAGE = 25; // Change 25 to your desired percentage
   ```
3. **Save the file** - Changes take effect on next page load

### **Method 4: Dokploy File Manager**
1. **Go to Dokploy dashboard**
2. **Open your application**
3. **Go to File Manager**
4. **Edit `coming-soon/config.js`**
5. **Change the progress value**
6. **Save** - Updates immediately!

## 🔧 **Current Default Settings**

- **Default Progress:** 25%
- **Status Message:** "Under Development"
- **Valid Range:** 0-100%
- **Auto-validation:** Yes (invalid values are corrected)

## 📊 **Progress Examples**

| Value | Display | Meaning |
|-------|---------|---------|
| 0% | 0% Complete | Just started |
| 25% | 25% Complete | Early development |
| 50% | 50% Complete | Half way |
| 75% | 75% Complete | Almost done |
| 90% | 90% Complete | Nearly ready |
| 100% | 100% Complete | Complete! |

## 🚀 **Why This Works Better**

### **Problem with Dokploy Static:**
- Dokploy Static build type doesn't inject environment variables
- Static files can't access server-side environment variables
- Need client-side solution

### **Our Solution:**
- ✅ **Browser Console**: Instant updates via JavaScript
- ✅ **URL Parameters**: Easy testing
- ✅ **Config File**: Simple file editing
- ✅ **Local Storage**: Persistent changes
- ✅ **Multiple Fallbacks**: Always works

## 🎉 **Quick Start**

1. **Deploy your application** normally
2. **Open the website** in browser
3. **Press F12** → Console tab
4. **Type:** `updateProgress(50)`
5. **See the progress bar update!**

That's it! No code changes, no redeployment needed! 🚀
