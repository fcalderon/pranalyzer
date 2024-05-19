import logging
from datetime import datetime

# from anal.models import APICache

from services.fetch_pr_data import get_pull_request_details, get_reviewers, get_comments, get_review_comments, \
    get_commits, get_pull_requests
from services.write_pr_data import calculate_additional_metrics, write_to_csv
from views import should_include, is_dependency

# Replace with your GitHub personal access token
GITHUB_TOKEN = "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"
# Replace with your GitHub repository owner and name
REPO_OWNER = "compt"
REPO_NAME = "compt"
CACHE_DIR = "pr_stats_cache"


logging.basicConfig(filename='pull_requests.log', level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}


def pull_data():
    current_year = datetime.now().year
    since = f'{current_year}-01-01T00:00:00Z'
    print("Fetching pull requests...")
    prs = get_pull_requests(since)

    total_prs = len(prs)
    print(f"Total pull requests to process: {total_prs}")

    filtered_prs = [pr for pr in prs if should_include(pr) and not is_dependency(pr)]
    total_filtered_prs = len(filtered_prs)
    print(f"Pull requests after filtering dependencies: {total_filtered_prs}")

    data = []
    for i, pr in enumerate(filtered_prs, start=1):
        print(f"Processing PR {i}/{total_filtered_prs}")
        pr_number = pr['number']
        pr_details = get_pull_request_details(pr_number)
        if not pr_details:
            continue
        reviewers = get_reviewers(pr_number)
        comments = get_comments(pr_number)
        review_comments = get_review_comments(pr_number)
        comment_count = len(comments) + len(review_comments)
        commit_count = get_commits(pr_number)

        created_at = datetime.strptime(pr['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        merged_at = datetime.strptime(pr['merged_at'], '%Y-%m-%dT%H:%M:%SZ') if pr['merged_at'] else None
        time_to_merge = (merged_at - created_at).total_seconds() / 3600 if merged_at else None

        additional_metrics = calculate_additional_metrics(pr_details, review_comments, comments)

        data.append({
            'PR Number': pr_number,
            'Author': pr['user']['login'],
            'Reviewers': ', '.join(reviewers),
            'Comment Count': comment_count,
            'Commit Count': commit_count,
            'Created At': pr['created_at'],
            'Merged At': pr['merged_at'],
            'Time to Merge (hours)': time_to_merge,
            'First Review At': additional_metrics['First Review At'],
            'Time to First Review (hours)': additional_metrics['Time to First Review (hours)']
        })

        if i % 50 == 0 or i == total_filtered_prs:
            write_to_csv(data, header=(i <= 50))
            data = []

    print('Data saved to pull_requests.csv')
