import pytest
from unittest.mock import patch, MagicMock
from scraper import get_jobs_work_ua  
from models import JobPosting


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
    
    mock_requests_get.assert_called_once()
    
    mock_job_query.filter_by.assert_called_once_with(url="https://work.ua/job/123")
    
    assert mock_db_session.add.called
    
    assert mock_db_session.commit.called
