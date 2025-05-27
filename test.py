import pytest
from unittest.mock import patch, MagicMock
from scraper import get_jobs_work_ua  # replace with your actual import
from models import JobPosting

# Sample minimal HTML to simulate the real page structure
SAMPLE_HTML = """
<div id="pjax-jobs-list">
    <div class="job-link">
        <h2 class="my-0"><a href="/job/123">Junior Python Developer</a></h2>
        <span class="strong-600">$1,000</span>
        <span class="mt-xs">Remote</span>
        <span class="mt-xs">Full-time</span>
        <p class="ellipsis ellipsis-line ellipsis-line-3 text-default-7 mb-0">Exciting job for juniors!</p>
    </div>
</div>
"""

@pytest.fixture
def mock_requests_get():
    with patch("your_module.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = SAMPLE_HTML.encode("utf-8")
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_db_session():
    with patch("your_module.db.session") as mock_session:
        yield mock_session

@pytest.fixture
def mock_job_query():
    with patch("your_module.JobPosting.query") as mock_query:
        # filter_by(url=...) returns mock_query again for chaining .first()
        mock_query.filter_by.return_value.first.return_value = None
        yield mock_query

@pytest.fixture
def mock_app_context():
    with patch("your_module.app.app_context") as mock_context:
        mock_context.return_value.__enter__.return_value = None
        mock_context.return_value.__exit__.return_value = None
        yield mock_context

def test_get_jobs_work_ua(mock_requests_get, mock_db_session, mock_job_query, mock_app_context):
    get_jobs_work_ua()
    
    # It should call requests.get with the expected URL and headers
    mock_requests_get.assert_called_once()
    
    # It should query the database for the job URL
    mock_job_query.filter_by.assert_called_once_with(url="https://work.ua/job/123")
    
    # It should add the new job to the session
    assert mock_db_session.add.called
    
    # It should commit the session
    assert mock_db_session.commit.called
