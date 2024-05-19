import requests
import logging
from datetime import datetime

from django.db.utils import IntegrityError
from django.conf import settings

from PRAnalyzer.models import APICache

GITHUB_TOKEN = settings.GITHUB_TOKEN
# Replace with your GitHub repository owner and name
REPO_OWNER = settings.REPO_OWNER
REPO_NAME = settings.REPO_NAME
CACHE_DIR = settings.CACHE_DIR

logging.basicConfig(filename='pull_requests.log', level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}


def cache_data(endpoint, params, data):
    try:
        APICache.objects.create(endpoint=endpoint, params=params, data=data)
    except IntegrityError:
        cache_entry = APICache.objects.get(endpoint=endpoint, params=params)
        cache_entry.data = data
        cache_entry.save()


def get_cached_data(endpoint, params):
    try:
        cache_entry = APICache.objects.get(endpoint=endpoint, params=params)
        return cache_entry.data
    except APICache.DoesNotExist:
        return None


def get_pull_requests(since, owner=REPO_OWNER, repo=REPO_NAME):
    prs = []
    page = 1

    while True:
        try:
            params = f"state=all&since={since}&page={page}&per_page=100"
            cached_data = get_cached_data('pulls', params)
            if cached_data:
                batch = cached_data
            else:
                url = f'https://api.github.com/repos/{owner}/{repo}/pulls?{params}'
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                batch = response.json()
                cache_data('pulls', params, batch)

            if not batch:
                break
            prs.extend(batch)
            page += 1
        except Exception as e:
            logging.error(f"Error fetching pull requests: {e}")
            break

    return prs


def get_pull_request_details(pr_number, owner=REPO_OWNER, repo=REPO_NAME):
    try:
        params = f"{pr_number}"
        cached_data = get_cached_data('pull_details', params)
        if cached_data:
            return cached_data
        else:
            url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}'
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            cache_data('pull_details', params, data)
            return data
    except Exception as e:
        logging.error(f"Error fetching pull request details for PR {pr_number}: {e}")
        return None


def get_reviewers(pr_number, owner=REPO_OWNER, repo=REPO_NAME):
    try:
        params = f"{pr_number}_reviews"
        cached_data = get_cached_data('pull_reviews', params)
        if cached_data:
            reviews = cached_data
        else:
            url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews'
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            reviews = response.json()
            cache_data('pull_reviews', params, reviews)

        reviewers = {review['user']['login'] for review in reviews}
        return list(reviewers)
    except Exception as e:
        logging.error(f"Error fetching reviewers for PR {pr_number}: {e}")
        return []


def get_comments(pr_number, owner=REPO_OWNER, repo=REPO_NAME):
    try:
        params = f"{pr_number}_comments"
        cached_data = get_cached_data('pull_comments', params)
        if cached_data:
            comments = cached_data
        else:
            url = f'https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments'
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            comments = response.json()
            cache_data('pull_comments', params, comments)
        return comments
    except Exception as e:
        logging.error(f"Error fetching comments for PR {pr_number}: {e}")
        return []


def get_review_comments(pr_number, owner=REPO_OWNER, repo=REPO_NAME):
    try:
        params = f"{pr_number}_review_comments"
        cached_data = get_cached_data('pull_review_comments', params)
        if cached_data:
            review_comments = cached_data
        else:
            url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments'
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            review_comments = response.json()
            cache_data('pull_review_comments', params, review_comments)
        return review_comments
    except Exception as e:
        logging.error(f"Error fetching review comments for PR {pr_number}: {e}")
        return []


def get_commits(pr_number, owner=REPO_OWNER, repo=REPO_NAME):
    try:
        params = f"{pr_number}_commits"
        cached_data = get_cached_data('pull_commits', params)
        if cached_data:
            commits = cached_data
        else:
            url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits'
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            commits = response.json()
            cache_data('pull_commits', params, commits)
        return len(commits)
    except Exception as e:
        logging.error(f"Error fetching commits for PR {pr_number}: {e}")
        return 0
