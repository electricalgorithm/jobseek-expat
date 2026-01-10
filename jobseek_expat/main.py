import pandas as pd
from jobspy import scrape_jobs
import typer
from langdetect import detect, LangDetectException
import logging

# Suppress some logging derived from libraries if needed
logging.getLogger("jobspy").setLevel(logging.WARNING)

app = typer.Typer()

def is_english(text: str) -> bool:
    """
    Detect if the given text is in English.

    Uses the 'langdetect' library. Returns False if text is too short (<10 chars)
    or if detection fails.
    """
    if not text or len(text) < 10:
        return False
    try:
        # Detect language
        lang = detect(text)
        return lang == 'en'
    except LangDetectException:
        # If detection fails, assume not English or unsure
        return False

def has_language_requirement(text: str, language: str) -> bool:
    """
    Returns True if the text seems to explicitly require the local language.
    """
    text_lower = text.lower()
    lang = language.lower()
    
    # Phrases implying Language is mandatory
    # We dynamically insert the language name
    required_phrases = [
        f"{lang} is required",
        f"requires {lang}",
        f"{lang} language skills are required",
        f"fluent in {lang}",
        f"fluency in {lang}",
        f"native {lang}",
        f"{lang} native",
        f"c1 level {lang}",
        f"c2 level {lang}",
        f"c1 in {lang}",
        f"c2 in {lang}",
        f"{lang}: c1",
        f"{lang}: c2",
        f"excellent command of {lang}",
        f"good knowledge of {lang}",
        f"proficient in {lang}",
        f"business fluent {lang}",
        f"{lang} is mandatory",
        f"{lang} language is a must",
        "local language of the country",
        f"{lang} skills"
    ]
    
    # Check for these phrases
    for phrase in required_phrases:
        if phrase in text_lower:
            return True
            
    return False

@app.command()
def search(
    keyword: str = typer.Argument(..., help="Job search keyword(s), separated by comma"),
    country: str = typer.Option("Germany", help="Country to search in (e.g. Germany, France, USA)"),
    location: str = typer.Option(None, help="Specific location(s) (e.g. Berlin). If omitted, searches the whole country."),
    local_language: str = typer.Option("German", help="Local language to filter out if required (e.g. German, French)"),
    hours_old: int = typer.Option(24, help="Filter jobs posted in the last N hours"),
    results_wanted: int = typer.Option(20, help="Number of results to fetch per keyword/location"),
    description_length: int = typer.Option(50, help="Minimum description length to process"),
    experience_level: str = typer.Option(None, help="Filter by experience level (e.g. mid_senior, entry, associate)"),
    exclude_keywords: str = typer.Option(None, "--exclude", help="Keywords to exclude from title/description (comma separated)"),
    sites: list[str] = typer.Option(None, "--site", help="Site(s) to scrape (linkedin, indeed, glassdoor). Default: All"),
    output_format: str = typer.Option("table", "--output", "-o", help="Output format: table (human-readable) or json"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed scraper logs")
):
    """
    Search for jobs matching KEYWORD in COUNTRY, filtering for English-speaking jobs only.
    """
    
    # Configure logging
    log_level = logging.INFO if verbose else logging.WARNING
    logging.getLogger("jobspy").setLevel(log_level)

    # Determine sites
    search_sites = sites if sites else ["linkedin", "indeed", "glassdoor"]
    
    # Process inputs
    search_keywords = [k.strip() for k in keyword.split(",") if k.strip()]
    
    if location:
        search_locations = [loc_str.strip() for loc_str in location.split(",") if loc_str.strip()]
    else:
        search_locations = [country] # Default to country level search
    
    exclusions = []
    if exclude_keywords:
        exclusions = [e.strip().lower() for e in exclude_keywords.split(",") if e.strip()]

    # Warn about Experience Level limitations
    if experience_level and any(s in search_sites for s in ["indeed", "glassdoor"]):
        typer.secho("WARNING: You specified an 'experience_level' filter.", fg=typer.colors.YELLOW, err=True)
        typer.secho("         This is fully supported only on LinkedIn.", fg=typer.colors.YELLOW, err=True)
        typer.secho("         Jobs from Indeed or Glassdoor might be skipped because they often lack this data.", fg=typer.colors.YELLOW, err=True)
    
    if output_format == "table":
        typer.echo(f"Starting search for: {', '.join(search_keywords)}")
        typer.echo(f"Country: {country}")
        typer.echo(f"Locations: {', '.join(search_locations)}")
        typer.echo(f"Looking for {results_wanted} results per search, posted in last {hours_old}h...")
        
    all_jobs_list = []

    for loc in search_locations:
        # Determine specific location params
        current_loc = loc
        is_remote_flag = False
        if current_loc.lower() == "remote":
            is_remote_flag = True
            current_loc = country # Search in Country if remote
            
        loc_display = f"Remote, {country}" if is_remote_flag else current_loc

        for kw in search_keywords:
            if output_format == "table":
                typer.echo(f"Fetching for '{kw}' in '{loc_display}'...")

            try:
                # scrape_jobs returns a pandas DataFrame
                jobs: pd.DataFrame = scrape_jobs(
                    site_name=search_sites,
                    search_term=kw,
                    location=current_loc,
                    results_wanted=results_wanted,
                    hours_old=hours_old,
                    is_remote=is_remote_flag,
                    country_utcnow=False,
                    country_indeed=country.lower(), # Use the country argument
                    linkedin_fetch_description=True, # Explicitly requesting descriptions if supported by this version
                    verbose=2 if verbose else 0
                )
                if not jobs.empty:
                    all_jobs_list.append(jobs)
            except Exception as e:
                typer.echo(f"Error scraping jobs for '{kw}': {e}", err=True)
                # Continue to next keyword instead of returning
                continue

    if not all_jobs_list:
        if output_format == "json":
             print("[]")
        else:
             typer.echo("No jobs found from the scraper.")
        return

    # Combine all results
    jobs = pd.concat(all_jobs_list, ignore_index=True)
    
    # Deduplicate (sometimes different keywords find same job)
    # Use 'job_url' as primary key if available, else 'id'
    jobs = jobs.drop_duplicates(subset=['job_url'])

    if output_format == "table":
        typer.echo(f"Total scraped (deduplicated): {len(jobs)}. Analysis beginning...")

    valid_jobs = []
    skipped_count = 0
    language_skipped = 0
    requirement_skipped = 0
    exclusion_skipped = 0
    
    for idx, row in jobs.iterrows():
        desc = str(row.get('description', ''))
        title = str(row.get('title', '')).lower()
        desc_lower = desc.lower()
        
        if len(desc) < description_length:
            skipped_count += 1
            continue

        # Exclusion Check
        # Check against title and description
        excluded_found = False
        for exc in exclusions:
            if exc in title or exc in desc_lower:
                exclusion_skipped += 1
                skipped_count += 1
                excluded_found = True
                break
        
        if excluded_found:
            continue
            
        # Experience Level Check
        if experience_level:
            job_lvl = str(row.get('job_level', '')).lower()
            if not job_lvl or job_lvl == 'nan':
                skipped_count += 1
                continue
            
            norm_req = experience_level.lower().replace("_", "-").replace(" ", "-")
            if norm_req not in job_lvl.replace(" ", "-"):
                 if experience_level.lower() not in job_lvl:
                    skipped_count += 1
                    continue

        # 1. Language Check
        if not is_english(desc):
            language_skipped += 1
            skipped_count += 1
            continue
            
        # 2. Check for explicit Language requirements in English text
        if has_language_requirement(desc, local_language):
            requirement_skipped += 1
            skipped_count += 1
            continue
            
        valid_jobs.append(row)

    if output_format == "table":
        typer.echo("Filtering Report:")
        typer.echo(f"  Total Scraped: {len(jobs)}")
        typer.echo(f"  Non-English/Too Short: {language_skipped}")
        typer.echo(f"  {local_language} Required: {requirement_skipped}")
        typer.echo(f"  Excluded Keywords: {exclusion_skipped}")
        typer.echo(f"  Valid Jobs: {len(valid_jobs)}")
    
    if not valid_jobs:
        if output_format == "json":
            print("[]")
        else:
            typer.echo("No jobs met the criteria.")
        return

    # Create DF
    valid_df = pd.DataFrame(valid_jobs)
    
    # --- OUTPUT ---
    
    if output_format == "json":
        # Convert date objects to string for JSON serialization
        import json
        
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            from datetime import date, datetime
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()
            return str(obj)

        records = valid_df.to_dict(orient="records")
        # Clean up NaNs
        clean_records = []
        for r in records:
            clean_r = {k: v for k, v in r.items() if pd.notna(v)}
            clean_records.append(clean_r)
            
        print(json.dumps(clean_records, default=json_serial, indent=2))
        
    else:
        # HUMAN READABLE (RICH TABLE)
        from rich.console import Console
        from rich.table import Table
        from rich import box

        console = Console()
        table = Table(title=f"Job Search Results ({len(valid_df)})", box=box.ROUNDED, show_lines=True)

        table.add_column("Site", style="cyan", no_wrap=True)
        table.add_column("Title", style="bold white")
        table.add_column("Company", style="magenta")
        table.add_column("Location", style="green")
        table.add_column("Level", style="yellow")
        table.add_column("Posted", style="blue", no_wrap=True)
        table.add_column("Link", style="blue underline", justify="center")

        for idx, job in valid_df.iterrows():
            title = str(job.get('title', 'N/A'))
            company = str(job.get('company', 'N/A'))
            job_loc = str(job.get('location', 'N/A'))
            date_posted = str(job.get('date_posted', 'N/A'))
            url = str(job.get('job_url', 'N/A'))
            job_lvl = str(job.get('job_level', 'N/A'))
            site = str(job.get('site', 'N/A'))
            
            if job_lvl == "nan":
                job_lvl = "-"
            if date_posted == "nan":
                date_posted = "-"
            
            # Create a clickable link text using Rich markup
            # This keeps the table clean. The URL is embedded.
            link_text = f"[link={url}]Open[/link]"
            
            table.add_row(site, title, company, job_loc, job_lvl, date_posted, link_text)

        console.print(table)

if __name__ == "__main__":
    app()
