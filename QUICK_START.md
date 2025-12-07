# Apex Telemetry - Quick Feature Guide

## 🎯 What's New

Three powerful new tools have been added to Apex Telemetry for advanced F1 data analysis:

---

## 1️⃣ DRIVER COMPARISON 🏁

**What it does**: Compare two drivers side-by-side across multiple metrics

### How to Use
1. Click **Comparison** in the top menu
2. Select Year → Country → Meeting → Session
3. Pick Driver 1 and Driver 2
4. Click **COMPARE DRIVERS**

### What You'll See
- **Speed Comparison** - Who goes faster through which sections
- **RPM Patterns** - Engine usage differences
- **Throttle vs Brake** - Driving technique comparison
- **Sector Times** - Individual performance per track section
- **Lap Times** - Consistency across the race

### Pro Tips
- 🔍 Click the zoom icon to expand any chart to full-screen
- 🖱️ Scroll to zoom in/out, drag to pan around
- 🔄 Double-click to reset zoom level
- 📥 Export data for external analysis in CSV or JSON

---

## 2️⃣ SECTOR BREAKDOWN 📊

**What it does**: Analyze performance broken down by track sectors

### How to Use
1. Click **Sectors** in the top menu
2. Select Year → Country → Meeting → Session → Driver
3. Click **LOAD SECTOR DATA**

### What You'll See
- **Sector Times Progression** - How sector times changed lap-by-lap
- **Sector Distribution** - How much time spent in each sector
- **Individual Sector Charts** - Detailed performance per sector
- **Statistics** - Fastest times for Sector 1, 2, and 3
- **Export Options** - Download all data

### Pro Tips
- Compare sectors to identify strengths/weaknesses
- Look for patterns in sector consistency
- Export and analyze in Excel or Python
- Use for setup tuning analysis

---

## 3️⃣ DATA EXPORT 📥

**What it does**: Download F1 telemetry data for analysis

### Available Exports

#### Telemetry Data
- Speed (km/h)
- RPM (engine revolutions)
- Throttle (0-100%)
- Brake (0-100%)
- Gear selection
- Timestamps

#### Lap Data
- Lap times (minutes)
- Sector 1, 2, 3 times
- Intermediate speeds
- Lap numbers

### Export Formats

**CSV** - Best for Excel/Spreadsheets
```
date,speed,rpm,throttle,brake,n_gear
2024-01-01T12:00:00,280,12500,0,0,8
2024-01-01T12:00:02,285,12600,100,0,8
...
```

**JSON** - Best for Programming
```json
[
  {
    "date": "2024-01-01T12:00:00",
    "speed": 280,
    "rpm": 12500,
    "throttle": 0,
    "brake": 0,
    "n_gear": 8
  },
  ...
]
```

### Use Cases
- Statistical analysis
- Machine learning training
- Performance modeling
- Custom reporting
- Data visualization tools

---

## 🎮 Chart Controls

### All Charts Support

| Action | Effect |
|--------|--------|
| 🖱️ Scroll | Zoom in/out |
| 👆 Pinch | Zoom (touch devices) |
| 🖐️ Drag | Pan around chart |
| 🔍 Click Button | Open full-screen modal |
| 🔄 Double-click | Reset zoom |

### Chart Types
- **Line Charts** - Speed, RPM, positions over time
- **Bar Charts** - Lap times, sector times
- **Stacked Bars** - Sector distribution

---

## 📊 Sample Analysis Workflow

### Comparing Two Drivers
```
1. Go to Comparison
2. Select your race and both drivers
3. Look at Speed Comparison - who has better top speed?
4. Check Throttle/Brake - who drives more aggressively?
5. Compare Sector Times - where does one driver excel?
6. Export data for deeper statistical analysis
```

### Analyzing Your Driver's Performance
```
1. Go to Sectors
2. Load sector data for your race
3. Identify which sector is fastest/slowest
4. Look for consistency patterns
5. Export to Excel for performance tracking
```

### Building Analysis Dataset
```
1. Select Comparison or Sectors
2. Click export buttons (CSV or JSON)
3. Collect data from multiple races
4. Combine into single spreadsheet
5. Perform statistical analysis
```

---

## 🚀 Pro Features

### Zoom & Pan Deep Dive
- **Zoom In**: Scroll up to focus on specific lap segment
- **Zoom Out**: Scroll down to see full race
- **Pan**: Click and drag to move around large dataset
- **Reset**: Double-click center of chart to go back to full view

### Multi-Metric Comparison
- See up to 7 different metrics side-by-side
- Identify correlation between metrics (e.g., high throttle → high speed)
- Spot anomalies (unusual braking patterns, etc.)

### Statistics
- Fastest times calculated automatically
- Min/max values highlighted
- Lap-by-lap consistency tracked
- Sector distribution analysis

---

## 💡 Use Cases

### For Engineers
- Analyze setup impact on telemetry
- Compare engineer strategies
- Identify optimization areas
- Track improvements over season

### For Analysts
- Statistical performance metrics
- Trend analysis across races
- Driver comparison reports
- Export for machine learning models

### For Fans
- Understand driving styles
- Compare favorite drivers
- Discover performance patterns
- Download data for analysis

### For Teams
- Multi-driver performance comparison
- Team strategy optimization
- Development direction analysis
- Historical performance tracking

---

## ❓ FAQ

**Q: Can I compare more than 2 drivers?**
A: Currently supports 1-on-1 comparison. Export multiple datasets to combine.

**Q: What data format works best?**
A: CSV for Excel, JSON for programming languages (Python, JavaScript, etc.)

**Q: How far back can I go?**
A: OpenF1 API has recent seasons. Check available meetings to see historical coverage.

**Q: Can I export a full race?**
A: Yes! Each driver's complete telemetry for a race session can be exported.

**Q: Is the data real-time?**
A: Currently historical races. Real-time support coming in future updates.

**Q: Can I modify exported data?**
A: Yes! CSV and JSON are standard formats - modify as needed for analysis.

---

## 🛠️ Keyboard Shortcuts

- **On Charts**:
  - Scroll: Zoom
  - Drag: Pan
  - Double-click: Reset zoom

- **Navigation**:
  - Click navbar links to switch between tools
  - Use browser back button to go back
  - F5 to refresh if needed

---

## 📞 Support

If something isn't working:
1. Refresh the page (F5)
2. Check browser console (F12) for errors
3. Verify you have internet connection
4. Ensure you're logged in
5. Try a different race/driver

---

## 🎉 You're Ready!

Start exploring F1 telemetry data like never before. Happy analyzing! 🏁
