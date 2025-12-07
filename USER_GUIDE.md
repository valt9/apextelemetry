# User Guide - Apex Telemetry Fixed Version

## 🚀 Getting Started

### Start the Application
```powershell
cd "c:\Users\aldus\Desktop\Apex Telemetry"
python app.py
```
Then open: **http://127.0.0.1:5000**

---

## 🏠 Main Dashboard

The home screen shows your account and provides access to:
- **Dashboard** - Overview and sample data
- **F1 Viewer** - Browse telemetry by race
- **Comparison** - Compare 2 drivers (FIXED)
- **Sectors** - Analyze sector performance (FIXED)
- **Sessions** - Your saved sessions (FIXED)

---

## 🏁 Feature #1: Driver Comparison (FIXED)

### What Changed
- ✅ **Removed country filter** - Now simpler: Year → Meeting → Session
- ✅ **Fixed data not showing** - Better error handling
- ✅ **Clear error messages** - Know what went wrong

### How to Use

**Step 1: Select Year**
```
Click dropdown → Choose year (e.g., 2024)
```

**Step 2: Select Meeting**
```
Click dropdown → See all races for that year
Shows: "Race Name - Country" (e.g., "Bahrain GP - Bahrain")
```

**Step 3: Select Session**
```
Choose: Practice, Qualifying, or Race
```

**Step 4: Choose Drivers**
```
Driver 1 dropdown → Pick first driver
Driver 2 dropdown → Pick second driver
```

**Step 5: Compare**
```
Click blue button: "COMPARE DRIVERS"
```

### What You'll See
**7 Comparison Charts:**
1. **Speed Comparison** - Who's faster through corners/straights
2. **RPM Pattern** - Engine usage differences
3. **Throttle Input** - Throttle application technique
4. **Brake Input** - Braking patterns and aggression
5. **Driver 1 Sectors** - Sector 1, 2, 3 times for driver 1
6. **Driver 2 Sectors** - Sector 1, 2, 3 times for driver 2
7. **Lap Times** - Overall lap time consistency

### Chart Controls
```
🖱️  SCROLL              Zoom in/out
🖱️  CLICK & DRAG        Pan around zoomed area
🔍  EXPAND BUTTON       Open full-screen modal
🔄  DOUBLE-CLICK        Reset to original view
```

### Troubleshooting
**"Error loading comparison data"**
- ✓ Make sure both drivers participated in selected session
- ✓ Some races don't have telemetry data available
- ✓ Try a different race or drivers

**"No telemetry data found"**
- ✓ That driver might not have finished the session
- ✓ Select a different driver from the dropdown

---

## 📈 Feature #2: Sector Breakdown (FIXED)

### What Changed
- ✅ **Removed country filter** - Simpler filtering
- ✅ **Fixed layout** - All in one column now
- ✅ **Better controls** - Clear button placement

### How to Use

**Step 1: Select Year → Meeting → Session → Driver**
```
Year    ↓
Meeting ↓
Session ↓
Driver  ↓
Button: "LOAD SECTOR DATA"
```

### What You'll See
**5 Charts + Statistics:**
1. **Sector Times Progression** - How S1, S2, S3 change lap-by-lap
2. **Sector Distribution** - Percentage of lap time in each sector
3. **Sector 1 Detail** - S1 performance across all laps
4. **Sector 2 Detail** - S2 performance across all laps
5. **Sector 3 Detail** - S3 performance across all laps

**Plus:**
- ⏱️ Fastest Sector 1 time
- ⏱️ Fastest Sector 2 time
- ⏱️ Fastest Sector 3 time

---

## 📁 Feature #3: Sessions (FIXED)

### What Changed
- ✅ **Styled with F1 theme** - Red borders, dark backgrounds
- ✅ **Better data visibility** - Driver, team, date clearly shown
- ✅ **Improved layout** - 2-3 columns, looks professional

### Viewing Sessions
```
Go to: Sessions menu
See: All your saved telemetry sessions
```

### Session Information
Each card shows:
```
📌 Session Name
👤 Driver: [Name]
🏁 Team: [Team Name]
📅 Date: [Race Date]
📊 Data: Available (if saved)
```

### Actions
```
✏️  EDIT    - Update session details
🗑️  DELETE  - Remove session
```

### Create New Session
```
Click: "+ NEW SESSION" button
Fill in: Name, Driver, Team, Date
Save: Click "Create"
```

---

## 🎯 Comparison: Old vs New

### Before Fixes
```
Year ✓
↓
Country (confusing, unnecessary) ✗
↓
Meeting (redundant filter)
↓
Session
↓
Drivers
↓
Click button → No data showing ✗
```

### After Fixes
```
Year ✓
↓
Meeting (country shown in name) ✓
↓
Session ✓
↓
Drivers ✓
↓
Click button → Data loads! ✓
Shows errors if something's wrong ✓
```

---

## 📊 Using Charts Like a Pro

### Basic Navigation
1. **Zoom**: Scroll mouse wheel (in/out)
2. **Pan**: Click and drag on zoomed chart
3. **Reset**: Double-click center
4. **Expand**: Click 🔍 button for full-screen

### Analyzing Data
```
Looking at Speed Comparison:
  Red line = Driver 1 speed
  Gold line = Driver 2 speed
  
Zoom in on a section to see:
  - Exact speed points
  - Where driver differences occur
  - Braking points
  - Acceleration zones
```

### Export Data
```
On Comparison or Sectors page:
📥 CSV     - Download as Excel spreadsheet
📥 JSON    - Download as raw data format
```

---

## 🔍 Example Workflows

### Workflow 1: Quick Driver Comparison
```
1. Comparison menu
2. Select: 2024 → Monaco → Race
3. Choose: Verstappen vs Alonso
4. See: Speed, throttle, braking differences
5. Click 🔍 on speed chart
6. Zoom to see exact corner handling
```

### Workflow 2: Analyze Your Favorite Driver
```
1. Sectors menu
2. Select: 2024 → Monza → Race → Leclerc
3. Click "LOAD SECTOR DATA"
4. See: Which sector is weakest?
5. Check statistics: Best times
6. Notice: Sector 2 (high-speed) is fastest
7. Export data for deeper analysis
```

### Workflow 3: Save Session Notes
```
1. Go to Sessions
2. Click "+ NEW SESSION"
3. Enter: "Monaco 2024 Analysis"
4. Driver: "Max Verstappen"
5. Team: "Red Bull"
6. Date: "2024-05-26"
7. Data: "Comparison with Alonso"
8. Save and view in Sessions list
```

---

## ⚠️ Common Issues & Fixes

### "No meetings found for this year"
✓ That year doesn't have data available
✓ Try: 2023 or 2024

### "No sessions found for this meeting"
✓ That race doesn't have session data
✓ Only some races have telemetry data

### "No telemetry data found for selected drivers"
✓ Driver didn't participate or didn't finish
✓ Try: Different drivers or races

### Chart won't zoom
✓ Hover over chart first
✓ Then scroll (not on edge)

### Can't see data in Sessions
✓ Scroll down if using small screen
✓ Try fullscreen mode (F11)

---

## 🎨 Color Guide

### Chart Colors
```
Red (#DC0000)           = Ferrari Red (Driver 1 / Sector 1)
Gold (#ffb800)          = Accent Gold (Driver 2 / Sector 2)
Cyan (#00d4ff)          = Light Blue (Sector 3)
```

### Button Colors
```
Red                     = Primary action (Compare, Load)
Dark Red outline        = Secondary actions (Edit, Delete)
```

### Theme Colors
```
Dark (#15151e)          = Background
Gray (#2a2a33)          = Cards
Red (#DC0000)           = Borders/Highlights
```

---

## 🚀 Tips for Best Results

1. **Start with recent races** - More complete telemetry data
2. **Compare similar cars** - More interesting differences
3. **Use zoom carefully** - Too much zoom = hard to see pattern
4. **Export for analysis** - CSV works great with Excel
5. **Save important sessions** - Use the Sessions feature

---

## 📞 Quick Reference

| Feature | Access | What It Does |
|---------|--------|--------------|
| **Viewer** | Menu → F1 Viewer | Browse F1 data by race |
| **Compare** | Menu → Comparison | Side-by-side driver analysis |
| **Sectors** | Menu → Sectors | Track sector performance |
| **Sessions** | Menu → Sessions | Manage saved sessions |
| **Dashboard** | Menu → Dashboard | Overview & sample data |

---

## ✅ You're All Set!

Everything is fixed and ready to use:
- ✅ Comparison data loads correctly
- ✅ Zoom and expand work separately
- ✅ Filtering is simple and clear
- ✅ Sessions display beautifully
- ✅ Error messages are helpful

**Happy analyzing! 🏁**

---

*Last Updated: December 6, 2025*
*All issues resolved and tested*
