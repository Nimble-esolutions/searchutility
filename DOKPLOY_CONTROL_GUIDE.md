# Dokploy Control Guide - Dynamic Progress Control
## Control Development Progress Without Code Changes

### 🎯 **Smart Solution Overview**

You can now control the Development Progress percentage directly from Dokploy's environment variables or by simply editing a single configuration file, without needing to change any code or redeploy.

### 🚀 **Method 1: Environment Variables (Recommended)**

#### **In Dokploy Application Settings:**

1. **Go to your application settings in Dokploy**
2. **Navigate to Environment Variables section**
3. **Add these variables:**

```bash
# Primary environment variable
PROGRESS_PERCENTAGE=75

# Alternative variable name
DEVELOPMENT_PROGRESS=75

# Optional: Status message
STATUS_MESSAGE="Under Development"

# Optional: Maintenance mode flag
MAINTENANCE_MODE=false
```

4. **Save and redeploy** - The progress will update automatically!

#### **Progress Values:**
- **0-100**: Any number between 0 and 100
- **Auto-validation**: Values are automatically clamped to 0-100 range
- **Real-time**: Changes take effect on next page load

### 🔧 **Method 2: Configuration File (Quick Edit)**

#### **Edit the config.js file:**

1. **Navigate to your deployed application files**
2. **Edit `coming-soon/config.js`**
3. **Change the progress value:**

```javascript
// Change this line
window.PROGRESS_PERCENTAGE = 75; // Your desired percentage

// Or this line
window.DEVELOPMENT_PROGRESS = 75; // Alternative variable
```

4. **Save the file** - Changes take effect immediately!

### 📊 **Method 3: URL Parameters (Testing)**

#### **For testing purposes, you can use URL parameters:**

```
https://your-domain.com/coming-soon/?progress=60
https://your-domain.com/coming-soon/?progress=90
```

This is useful for testing different progress values without changing files.

### 🎨 **Visual Progress Updates**

#### **What Updates Automatically:**
- ✅ **Progress Bar Width**: Smoothly animates to new percentage
- ✅ **Progress Text**: Updates to show new percentage
- ✅ **Animation**: Smooth transition with shimmer effect
- ✅ **Validation**: Automatically clamps values to 0-100%

#### **Example Progress Values:**
- **25%**: Early development phase
- **50%**: Mid-development phase
- **75%**: Near completion
- **90%**: Almost ready
- **100%**: Complete (shows completion message)

### 🔄 **How It Works**

#### **JavaScript Logic:**
1. **Checks environment variables** first (Dokploy injected)
2. **Falls back to config.js** file values
3. **Checks URL parameters** for testing
4. **Uses default value** (85%) if none found
5. **Validates and clamps** values to 0-100 range
6. **Updates UI** with smooth animation

#### **Priority Order:**
1. `window.PROGRESS_PERCENTAGE` (Environment variable)
2. `window.DEVELOPMENT_PROGRESS` (Alternative environment variable)
3. URL parameter `?progress=X`
4. Default value (85%)

### 🛠️ **Dokploy Setup Instructions**

#### **For Environment Variables:**

1. **Create/Edit Application in Dokploy:**
   ```
   Application Name: maharashtra-coming-soon
   Build Type: Static
   Repository: Nimble-esolutions/searchutility
   Branch: landing-pages-only
   Root Directory: coming-soon/
   ```

2. **Add Environment Variables:**
   - Go to Environment Variables section
   - Add: `PROGRESS_PERCENTAGE` = `75`
   - Add: `DEVELOPMENT_PROGRESS` = `75` (backup)
   - Add: `STATUS_MESSAGE` = `"Under Development"`

3. **Deploy** - Progress will be controlled by environment variables!

#### **For File Editing:**

1. **Deploy the application normally**
2. **Access file manager** in Dokploy
3. **Edit `config.js`** file
4. **Change progress value**
5. **Save** - Changes take effect immediately!

### 📱 **Testing Different Values**

#### **Quick Test URLs:**
```
https://your-domain.com/?progress=25
https://your-domain.com/?progress=50
https://your-domain.com/?progress=75
https://your-domain.com/?progress=90
https://your-domain.com/?progress=100
```

### 🎉 **Benefits**

#### **No Code Changes Required:**
- ✅ **Environment Variables**: Control from Dokploy UI
- ✅ **Config File**: Simple file edit
- ✅ **URL Parameters**: Instant testing
- ✅ **Real-time Updates**: No redeployment needed

#### **Professional Management:**
- ✅ **Easy Updates**: Change progress in seconds
- ✅ **Multiple Methods**: Choose what works best
- ✅ **Validation**: Automatic value checking
- ✅ **Smooth Animation**: Professional appearance

### 🔧 **Advanced Configuration**

#### **Additional Customizable Values:**

```javascript
// In config.js or environment variables
window.PROGRESS_PERCENTAGE = 75;        // Progress percentage (0-100)
window.STATUS_MESSAGE = "Under Development"; // Status badge text
window.MAINTENANCE_MODE = false;        // Maintenance mode flag
window.COMPLETION_MESSAGE = "Development Complete!"; // 100% message
```

### 📞 **Support**

If you need help setting up environment variables or have questions about the configuration, the system is designed to be simple and intuitive. The progress will always show a valid value between 0-100% regardless of what you input.

---

**Built with ❤️ for easy management and professional deployment**
