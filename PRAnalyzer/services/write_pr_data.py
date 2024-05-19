import csv
from datetime import datetime


def write_to_csv(data, file_obj, header=False):
    writer = csv.DictWriter(file_obj, fieldnames=['PR Number', 'Author', 'Reviewers', 'Comment Count', 'Commit Count', 'Created At', 'Merged At', 'Time to Merge (hours)', 'First Review At', 'Time to First Review (hours)'])
    if header:
        writer.writeheader()
    for row in data:
        writer.writerow(row)


def calculate_additional_metrics(pr_details, review_comments, comments):
    first_review_at = None
    if review_comments:
        first_review_at = min(comment['created_at'] for comment in review_comments)
    elif comments:
        first_review_at = min(comment['created_at'] for comment in comments)

    created_at = datetime.strptime(pr_details['created_at'], '%Y-%m-%dT%H:%M:%SZ')
    first_review_datetime = datetime.strptime(first_review_at, '%Y-%m-%dT%H:%M:%SZ') if first_review_at else None
    time_to_first_review = (first_review_datetime - created_at).total_seconds() / 3600 if first_review_datetime else None

    return {
        'First Review At': first_review_at,
        'Time to First Review (hours)': time_to_first_review
    }
