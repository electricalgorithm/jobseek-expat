"""Helper functions for generating job search alerts."""

COUNTRY_LANGUAGES = {
    "Germany": "German",
    "Netherlands": "Dutch",
    "Sweden": "Swedish",
    "Denmark": "Danish",
    "Norway": "Norwegian",
    "Finland": "Finnish",
    "Poland": "Polish",
    "Austria": "German",
    "Switzerland": "German",
    "Belgium": "Dutch",
    "France": "French",
    "Spain": "Spanish",
    "Italy": "Italian",
    "Portugal": "Portuguese",
    "Ireland": "English",
    "UK": "English",
    "Czech Republic": "Czech",
}


def generate_job_alerts(
    job_titles: list[str],
    exclude_keywords: list[str],
    countries: list[str],
    locations: list[str],
    hours_old: int = 72,
    results_wanted: int = 20,
) -> list[dict]:
    """
    Generate job search alert configurations by combining job titles with locations.

    Args:
        job_titles: List of 3 job titles from CV analysis
        exclude_keywords: Keywords to exclude (from CV analysis)
        countries: User-specified countries
        locations: User-specified locations (cities or "Remote")
        hours_old: Hours filter
        results_wanted: Max results per search

    Returns:
        List of alert dictionaries
    """
    alerts = []
    exclude_str = ", ".join(exclude_keywords)

    # Strategy: Create one alert per job title per country
    # Combine all locations into single search for better coverage
    location_str = ", ".join(locations) if locations else "Remote"

    for job_title in job_titles:
        for country in countries:
            local_language = COUNTRY_LANGUAGES.get(country, "")

            alerts.append(
                {
                    "keyword": job_title,
                    "country": country,
                    "location": location_str,
                    "local_language": local_language,
                    "exclude": exclude_str,
                    "hours_old": hours_old,
                    "results_wanted": results_wanted,
                }
            )

    return alerts
