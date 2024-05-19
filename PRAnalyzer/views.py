from datetime import datetime

# Create your views here.
import io
from django.shortcuts import render
from django.http import HttpResponse

from PRAnalyzer.forms import DateForm
from services.fetch_pr_data import get_pull_requests, get_pull_request_details, get_reviewers, get_comments, \
    get_review_comments, get_commits
from services.write_pr_data import write_to_csv, calculate_additional_metrics

GITHUB_TOKEN = "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"
# Replace with your GitHub repository owner and name


def generate_csv(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            print("Getting pull requests...")
            date = form.cleaned_data['date']
            prs = get_pull_requests(f'{date}T00:00:00Z')
            filtered_prs = [pr for pr in prs if should_include(pr) and not is_dependency(pr)]
            data = []
            for pr in filtered_prs:
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

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="pull_requests_{date}.csv"'
            writer = io.StringIO()
            write_to_csv(data, writer, header=True)
            response.write(writer.getvalue())
            return response
    else:
        form = DateForm()
    return render(request, 'generate_csv.html', {'form': form})


def is_dependency(pr):
    return any(label['name'].lower() == 'dependency' for label in pr['labels'])


def should_include(pr):
    created_at = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    return created_at.year >= datetime.now().year
