# Indiana District Lookup Tool 🏛️

A simple, fast web tool for looking up Indiana legislative districts by county or finding counties by district number.

**[🚀 Live Demo](https://YOUR_USERNAME.github.io/indiana-district-lookup/)**

[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue)](https://pages.github.com/)
[![No Backend](https://img.shields.io/badge/Backend-None-green)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- **Lookup by County** - Enter any Indiana county to see all House, Senate, and Congressional districts
- **Lookup by District(s)** - Enter 1-3 district numbers to find counties and overlapping districts
- **Find Overlaps** - See where multiple districts intersect
- **Autocomplete** - County names auto-suggest as you type
- **Mobile Friendly** - Works perfectly on phones and tablets
- **100% Static** - No server required, runs entirely in your browser
- **Fast** - Instant results with client-side lookups

## 🎯 Quick Start

### For Users

Just visit the live site:
**https://YOUR_USERNAME.github.io/indiana-district-lookup/**

### For Developers

1. **Clone this repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/indiana-district-lookup.git
   cd indiana-district-lookup
   ```

2. **Open in browser**
   ```bash
   # Just open index.html in any web browser
   open index.html
   # Or on Windows: start index.html
   # Or on Linux: xdg-open index.html
   ```

That's it! No installation, no dependencies, no build process.

## 📁 Repository Structure

```
indiana-district-lookup/
├── index.html              # Main application (all-in-one)
├── district_data.json      # District and county data
├── convert_to_json.py      # Excel to JSON converter
└── README.md              # This file
```

## 🔄 Updating Data

When your district data changes:

1. **Get the Excel file** (`Indiana House Districts by County.xlsx`)

2. **Convert to JSON**
   ```bash
   python convert_to_json.py "Indiana House Districts by County.xlsx"
   ```

3. **Upload to GitHub**
   - Go to your repository on GitHub
   - Click "Upload files"
   - Drag `district_data.json`
   - Commit changes

4. **Done!** Changes appear instantly (may need browser refresh)

## 🌐 Hosting on GitHub Pages

This project is designed for **GitHub Pages** - free static hosting by GitHub.

### Deploy Your Own Copy

1. **Fork this repository** (click "Fork" button on GitHub)
2. **Go to Settings** → **Pages**
3. **Source**: Select `main` branch and `/ (root)`
4. **Save**
5. **Wait 1-2 minutes**
6. **Access your site** at `https://YOUR_USERNAME.github.io/indiana-district-lookup/`

See [GITHUB_PAGES_DEPLOY.md](GITHUB_PAGES_DEPLOY.md) for detailed instructions.

## 💻 How It Works

This is a **pure client-side application**:

```
User visits page
    ↓
Browser loads index.html
    ↓
JavaScript fetches district_data.json
    ↓
User searches → JavaScript finds matches
    ↓
Results displayed instantly
```

**No server, no API calls, no backend.**

Everything runs in your browser using vanilla JavaScript.

## 📊 Data Structure

The `district_data.json` contains:

```json
{
  "hd_to_counties": {
    "1": ["Adams", "Wells"],
    "2": ["Allen", "Wells"],
    ...
  },
  "sd_to_counties": {
    "1": ["DeKalb", "LaGrange", "Noble", "Steuben"],
    ...
  },
  "cd_to_counties": {
    "1": ["Lake", "Porter", "LaPorte"],
    ...
  },
  "county_to_hds": {
    "Marion": [86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100],
    ...
  },
  "county_to_sds": {...},
  "county_to_cds": {...},
  "all_counties": ["Adams", "Allen", "Bartholomew", ...]
}
```

## 🎨 Customization

### Change Colors

Edit the gradient in `index.html` (line ~15):

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

Try gradients from [uiGradients](https://uigradients.com/)

### Change Title

Edit line ~70 in `index.html`:

```html
<h1>🏛️ Indiana District Lookup</h1>
```

### Add Your Logo

Add before the `<h1>` tag:

```html
<img src="logo.png" alt="Logo" style="width: 100px; margin-bottom: 20px;">
```

Then upload `logo.png` to your repo.

## 📱 Mobile Support

The app is fully responsive and works great on:
- 📱 iOS (iPhone, iPad)
- 🤖 Android phones and tablets
- 💻 Desktop browsers (Chrome, Firefox, Safari, Edge)
- 🖥️ Tablets

## 🔧 Technical Details

- **Framework**: None (vanilla JavaScript)
- **Libraries**: None
- **Build Process**: None
- **Backend**: None
- **Database**: None
- **Size**: < 50KB total
- **Load Time**: < 1 second
- **Dependencies**: Zero

## 🚀 Performance

- ⚡ **Instant lookups** - all data loaded in memory
- 📦 **Tiny size** - entire app + data < 100KB
- 🌐 **CDN hosted** - served by GitHub's Fastly CDN
- 🔒 **HTTPS** - secure by default on GitHub Pages
- 💾 **Cached** - browsers cache the files

## 🐛 Known Issues

None! 🎉

If you find a bug, please [open an issue](https://github.com/YOUR_USERNAME/indiana-district-lookup/issues).

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with vanilla HTML, CSS, and JavaScript
- Hosted on GitHub Pages
- Data from Indiana legislative district mappings

## 📧 Contact

Questions? [Open an issue](https://github.com/YOUR_USERNAME/indiana-district-lookup/issues) on GitHub.

## ⭐ Star This Repo

If you find this tool useful, please consider giving it a star! ⭐

---

**Made with ❤️ for Indiana**
