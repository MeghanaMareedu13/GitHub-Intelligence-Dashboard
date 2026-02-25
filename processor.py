import pandas as pd
import datetime

class GitHubDataProcessor:
    """
    Transforms raw GitHub API data into visualizable insights.
    """
    
    @staticmethod
    def process_languages(language_counts):
        """
        Aggregates multiple repo language results into a single summary.
        Ex: {'Python': 500, 'JavaScript': 200}
        """
        # language_counts is a list of dicts: [{'Python': 100}, {'Python': 50, 'JS': 20}]
        combined = {}
        for repo_lang in language_counts:
            for lang, count in repo_lang.items():
                combined[lang] = combined.get(lang, 0) + count
        
        if not combined:
            return pd.DataFrame(columns=['Language', 'Bytes'])
            
        df = pd.DataFrame(list(combined.items()), columns=['Language', 'Bytes'])
        return df.sort_values(by='Bytes', ascending=False)

    @staticmethod
    def calculate_health_score(repo):
        """
        Calculates a 'Project Health' score (0-100) based on repository metadata.
        """
        score = 0
        
        # 1. Documentation (README presence) - assumed true if repo exists for now, 
        # but we can check if description exists
        if repo.get('description'):
            score += 20
            
        # 2. Popularity (Stars/Forks)
        stars = repo.get('stargazers_count', 0)
        score += min(stars * 5, 30) # Max 30 points for stars
        
        # 3. Maintenance (Recent updates)
        updated_at = repo.get('updated_at')
        if updated_at:
            last_update = datetime.datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ")
            days_since_update = (datetime.datetime.now() - last_update).days
            if days_since_update < 30:
                score += 30
            elif days_since_update < 90:
                score += 15
        
        # 4. Community (License)
        if repo.get('license'):
            score += 20
            
        return score

    @staticmethod
    def process_repo_metrics(repos):
        """
        Creates a DataFrame of key metrics across multiple repositories.
        """
        data = []
        for r in repos:
            data.append({
                'Name': r['name'],
                'Stars': r['stargazers_count'],
                'Forks': r['forks_count'],
                'Health Score': GitHubDataProcessor.calculate_health_score(r),
                'Primary Language': r['language'],
                'Open Issues': r['open_issues_count']
            })
        return pd.DataFrame(data)
