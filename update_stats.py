import os
import requests

USERNAME = "ViniciosTorres-Dev"
TOKEN = os.getenv("GITHUB_TOKEN") 

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_github_stats():
    """Busca as estatísticas usando as APIs REST e GraphQL do GitHub"""
    print(f"Buscando dados de {USERNAME}...")
    
    # Busca PRs e Issues (REST API)
    prs_url = f"https://api.github.com/search/issues?q=author:{USERNAME}+type:pr"
    issues_url = f"https://api.github.com/search/issues?q=author:{USERNAME}+type:issue"
    
    prs_count = requests.get(prs_url, headers=headers).json().get("total_count", 0)
    issues_count = requests.get(issues_url, headers=headers).json().get("total_count", 0)

    repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner"
    repos_data = requests.get(repos_url, headers=headers).json()
    
    repos_count = len(repos_data) if isinstance(repos_data, list) else 0
    stars_count = sum(repo.get("stargazers_count", 0) for repo in repos_data) if isinstance(repos_data, list) else 0

    graphql_url = "https://api.github.com/graphql"
    query = """
    query {
      user(login: "%s") {
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """ % USERNAME
    
    graphql_response = requests.post(graphql_url, json={'query': query}, headers=headers)
    
    commits_count = 0
    if graphql_response.status_code == 200:
        data = graphql_response.json()
        commits_count = data.get("data", {}).get("user", {}).get("contributionsCollection", {}).get("contributionCalendar", {}).get("totalContributions", 0)
    else:
        print(f"Erro no GraphQL: {graphql_response.status_code}")

    return {
        "{COMMITS}": str(commits_count),
        "{STARS}": str(stars_count),
        "{PRS}": str(prs_count),
        "{ISSUES}": str(issues_count),
        "{REPOS}": str(repos_count)
    }

def update_svg(stats):
    caminho_template = "assets/generated/stats-card.template.svg"
    caminho_final = "assets/generated/stats-card.svg"
    
    try:
        with open(caminho_template, "r", encoding="utf-8") as file:
            svg_content = file.read()
            
        for key, value in stats.items():
            svg_content = svg_content.replace(key, value)
            
        with open(caminho_final, "w", encoding="utf-8") as file:
            file.write(svg_content)
            
        print(f"Sucesso: {stats['{COMMITS}']} commits aplicados ao card.")
    except Exception as e:
        print(f"Erro ao atualizar SVG: {e}")

if __name__ == "__main__":
    estatisticas = get_github_stats()
    update_svg(estatisticas)
