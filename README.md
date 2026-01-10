# JobSeek Expat 🌍

**JobSeek Expat** is a powerful, open-source CLI tool designed to help expats and international job seekers find **English-speaking jobs** in non-English speaking countries (like Germany, France, Netherlands, etc.).

It scrapes major job boards, filters out local-language requirements, and presents you with a clean, curated list of opportunities.

## 🚀 Features

- **Multi-Platform Scraping**: Search **LinkedIn**, **Indeed**, and **Glassdoor** simultaneously.
- **Smart Filtering**: 
  - **English Only**: Automatically detects job description language.
  - **No "Local Language" Required**: Filters out jobs requiring C1/Fluent local language skills (customizable).
  - **Experience Level**: Filter by Seniority (Entry, Mid-Senior, etc. - *Best on LinkedIn*).
- **Flexible Locations**: Search multiple cities or "Remote" in your target country.
- **Advanced Search**:
  - **Multiple Keywords**: Search for "Developer, Designer" in one go.
  - **Exclusion Lists**: Hates specific terms? `--exclude "intern, thesis"`.
- **Output Options**:
  - **Beautiful CLI Tables**: Clickable links, color-coded output.
  - **JSON**: Machine-readable format for automation.

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install jobseek-expat
```

### From Source

```bash
git clone https://github.com/electricalgorithm/jobseek-expat.git
cd jobseek-expat
pip install .
```

## 🛠️ Usage

Once installed, the `jobseek-expat` command (and its short alias `je`) is available globally.

Generic syntax:
```bash
jobseek-expat "KEYWORD" --country "COUNTRY_NAME" [OPTIONS]
# or simply:
je "KEYWORD" --country "COUNTRY_NAME" [OPTIONS]
```

### Examples

**1. The Classic Expat Search (Berlin)**
Find "Software Engineer" jobs in **Germany** (Berlin) that likely don't require German.
```bash
jobseek-expat "Software Engineer" --location "Berlin"
```

**2. Multi-City & Remote Search**
Search for "Product Manager" in **Amsterdam** and **Remote** within the **Netherlands**.
```bash
jobseek-expat "Product Manager" \
  --country "Netherlands" \
  --location "Amsterdam, Remote" \
  --local-language "Dutch"
```
*Note: We specify `--local-language "Dutch"` so it filters out "Dutch required" jobs.*

**3. The "Broad Net" Strategy**
Search for **Developer** OR **Data Scientist** roles in **France**, specifically **Paris**, excluding internships.
```bash
jobseek-expat "Developer, Data Scientist" \
  --country "France" \
  --location "Paris" \
  --local-language "French" \
  --exclude "intern, stage, internship" \
  --results-wanted 50
```

### Command Line Options

| Option | Alias | Description | Default |
|--------|-------|-------------|---------|
| `KEYWORD` | | Job title(s) or keywords (comma-separated). **Required**. | |
| `--country` | | Target Country (e.g. Germany, France). | `Germany` |
| `--location` | | Specific City/Region (comma-separated). Use "Remote" for country-wide remote. | Whole Country |
| `--local-language` | | Language to filter out if required (e.g. German, Dutch). | `German` |
| `--hours-old` | | Max age of job postings in hours. | `24` |
| `--results-wanted` | | Jobs to fetch per keyword/location. | `20` |
| `--exclude` | | Keywords to exclude (title/description). | `None` |
| `--site` | | Sites: `linkedin`, `indeed`, `glassdoor`. | All 3 |
| `--output` | `-o` | Format: `table` or `json`. | `table` |
| `--verbose` | `-v` | Show scraper debug logs. | `False` |

## 🤝 Contributing

We welcome contributions! Whether it's adding a new filter, improving the language detection, or supporting more job boards.

1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---
*Built with ❤️ for the global expat community.*
