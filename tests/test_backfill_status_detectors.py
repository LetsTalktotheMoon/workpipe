import requests

import pytest

from backfill_status.detectors import _extract_text, detect_job_status, evaluate_fetched_page
from backfill_status.models import FetchedPage, JobAvailability, JobRecord


def make_job(host: str = "boards.greenhouse.io", title: str = "Software Engineer") -> JobRecord:
    return JobRecord(
        job_id="job-1",
        company_name="Acme",
        title=title,
        apply_url=f"https://{host}/embed/job_app?token=123",
        host=host,
    )


def make_page(raw_html: str, *, status_code: int = 200, final_url: str = "", title: str = "Software Engineer") -> FetchedPage:
    return FetchedPage(
        requested_url="https://example.com/job",
        final_url=final_url or "https://example.com/job",
        status_code=status_code,
        title=title,
        raw_html=raw_html,
        text=_extract_text(raw_html),
    )


def test_detects_closed_via_http_status() -> None:
    result = evaluate_fetched_page(make_job(), make_page("missing", status_code=404))
    assert result.status == JobAvailability.CLOSED
    assert result.http_status == 404


def test_detects_greenhouse_open_marker() -> None:
    page = make_page("Apply for this job Questions Location Software Engineer")
    result = evaluate_fetched_page(make_job(), page)
    assert result.status == JobAvailability.OPEN


@pytest.mark.parametrize(
    ("host", "job_title", "page_title", "raw_html", "final_url"),
    [
        (
            "boards.greenhouse.io",
            "Data Analyst, Payments Platform",
            "Job Application for Data Analyst, Payments Platform at Current",
            """
            <script>
            window.__GH_JOB = {"questions":[{"label":"Resume"}],"metadata":{"team":"Payments"}};
            </script>
            <div>Apply for this job</div>
            <div>Responsibilities</div>
            <div>Qualifications</div>
            <script src="https://www.recaptcha.net/recaptcha/enterprise.js"></script>
            """,
            "https://job-boards.greenhouse.io/embed/job_app?for=current81&token=7506171",
        ),
        (
            "jobs.ashbyhq.com",
            "Software Engineer",
            "Software Engineer @ Comulate",
            """
            <script type="application/ld+json">
            {"@type":"JobPosting","title":"Software Engineer","hiringOrganization":{"name":"Comulate"},"datePosted":"2026-04-01"}
            </script>
            <style>.grecaptcha-badge { visibility: hidden; }</style>
            <div id="root"></div>
            """,
            "https://jobs.ashbyhq.com/comulate/4d5a3632-2812-4ab0-b3ad-ca6cf6083348/application",
        ),
        (
            "jobs.lever.co",
            "Full Stack Software Engineer",
            "Cyngn - Full Stack Software Engineer",
            """
            <meta property="og:title" content="Cyngn - Full Stack Software Engineer" />
            <meta property="og:description" content="Build web services and submit application." />
            <div>Resume/CV</div>
            <div>Submit application</div>
            <script>let captchaId; let hCaptchaTokenExpired;</script>
            """,
            "https://jobs.lever.co/cyngn/ee7518e1-7f77-4655-b07d-ea968ec82127/apply",
        ),
        (
            "apply.careers.microsoft.com",
            "Senior Software Engineer",
            "Senior Software Engineer | Microsoft Careers",
            """
            <script type="application/ld+json">
            {"@type":"JobPosting","title":"Senior Software Engineer","hiringOrganization":{"name":"Microsoft"}}
            </script>
            <div>Job number 1970393556769530</div>
            <div>Job description</div>
            <script defer src="https://www.recaptcha.net/recaptcha/api.js?render=test"></script>
            """,
            "https://apply.careers.microsoft.com/careers/job/1970393556769530",
        ),
    ],
)
def test_captcha_marker_does_not_override_strong_open_signals(
    host: str,
    job_title: str,
    page_title: str,
    raw_html: str,
    final_url: str,
) -> None:
    job = make_job(host=host, title=job_title)
    page = make_page(raw_html, title=page_title, final_url=final_url)
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.OPEN


def test_detects_closed_marker_text() -> None:
    page = make_page("This job post is no longer active and has been removed.")
    result = evaluate_fetched_page(make_job(), page)
    assert result.status == JobAvailability.CLOSED


def test_unknown_when_evidence_is_weak() -> None:
    page = make_page("Welcome to careers. Search all jobs here.")
    result = evaluate_fetched_page(make_job(host="www.linkedin.com"), page)
    assert result.status == JobAvailability.UNKNOWN


def test_detects_capital_one_open_from_title_page() -> None:
    job = make_job(host="www.capitalonecareers.com", title="Senior Associate, Data Scientist")
    page = make_page(
        "Senior Associate, Data Scientist at Capital One Returning Applicant Posted 04/10/2026",
        final_url="https://www.capitalonecareers.com/job/-/-/234/93806318624",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.OPEN


def test_detects_oracle_closed_404_redirect() -> None:
    job = make_job(host="jpmc.fa.oraclecloud.com", title="Data Scientist")
    page = make_page(
        "Page not found. The page was moved or no longer exists.",
        final_url="https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/errors/404",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.CLOSED


def test_uses_final_redirect_host_rule_for_oracle_candidate_page() -> None:
    job = make_job(host="jpmorganchase.contacthr.com", title="Software Engineer III")
    page = make_page(
        'JPMC Candidate Experience page "JOB_DETAILS" "apiBaseUrl"',
        final_url="https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/210729713",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.OPEN


def test_detects_workday_open_from_og_metadata() -> None:
    job = make_job(host="arlo.wd12.myworkdayjobs.com", title="Sr Data Engineer")
    page = make_page(
        "og:title: Sr. Data Engineer og:description: About Arlo locations apply",
        final_url="https://arlo.wd12.myworkdayjobs.com/External_Careers/job/Milpitas-CA/Sr-Data-Engineer_JR100321",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.OPEN


def test_detects_workable_not_found_as_closed() -> None:
    job = make_job(host="apply.workable.com", title="Drupal Developer")
    page = make_page(
        "Valsoft Corporation - Current Openings",
        final_url="https://apply.workable.com/valsoft-corp/?not_found=true",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.CLOSED


def test_detects_breezy_title_page_as_open() -> None:
    job = make_job(host="accrete-ai.breezy.hr", title="Software Engineer")
    page = make_page(
        "Software Engineer at Accrete",
        final_url="https://accrete-ai.breezy.hr/p/0d80ab81b533-software-engineer",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.OPEN


def test_detects_open_from_structured_json_script() -> None:
    job = make_job(host="company.wd5.myworkdayjobs.com", title="Software Engineer")
    page = make_page(
        """
        <html><head></head><body>
        <script>
        window.__INITIAL_STATE__ = {
          "jobPostingInfo":{"title":"Software Engineer","jobReqId":"R-12345"},
          "externalPath":"/job/ABC",
          "hiringOrganization":"Acme"
        };
        </script>
        Careers
        </body></html>
        """,
        final_url="https://company.wd5.myworkdayjobs.com/en-US/careers/job/ABC",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.OPEN


def test_detects_phenom_closed_phrase() -> None:
    job = make_job(host="careers.qualcomm.com", title="ML Engineer")
    page = make_page("The job you are trying to apply for has been filled.")
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.CLOSED


def test_detects_jobvite_closed_phrase() -> None:
    job = make_job(host="jobs.jobvite.com", title="Backend Engineer")
    page = make_page("The job listing no longer exists.")
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.CLOSED


def test_oracle_open_from_og_metadata_and_deep_link() -> None:
    job = make_job(host="jpmorganchase.contacthr.com", title="Software Engineer III")
    page = make_page(
        """
        <html><head>
        <meta property="og:title" content="Software Engineer III"/>
        <meta property="og:description" content="Responsibilities, qualifications and apply now."/>
        </head><body>Candidate Experience</body></html>
        """,
        final_url="https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/job/151740427",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.OPEN


def test_jometer_406_defaults_unknown_when_no_signal() -> None:
    job = make_job(host="tnl2.jometer.com", title="Software Engineer")
    page = make_page("Not Acceptable", status_code=406, final_url="https://tnl2.jometer.com/jobs/123")
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.UNKNOWN


class _FakeResponse:
    def __init__(self, *, text: str, url: str, status_code: int, headers: dict[str, str] | None = None) -> None:
        self.text = text
        self.url = url
        self.status_code = status_code
        self.headers = headers or {"content-type": "text/html"}


class _FakeSession:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def get(self, url: str, **_: object) -> _FakeResponse:
        self.calls.append(url)
        if "jobs-guest/jobs/api/jobPosting/123456" in url:
            return _FakeResponse(
                text="<html><body>Easy Apply Responsibilities Qualifications</body></html>",
                url=url,
                status_code=200,
            )
        return _FakeResponse(text="fallback", url=url, status_code=429)


def test_linkedin_uses_guest_endpoint_before_fallback() -> None:
    job = JobRecord(
        job_id="li-1",
        company_name="LinkedIn Co",
        title="Software Engineer",
        apply_url="https://www.linkedin.com/jobs/view/software-engineer-123456",
        host="www.linkedin.com",
    )
    session = _FakeSession()
    result = detect_job_status(job, session=session)
    assert result.status == JobAvailability.OPEN
    assert any("jobs-guest/jobs/api/jobPosting/123456" in url for url in session.calls)


def test_linkedin_guest_top_card_page_classifies_open() -> None:
    job = make_job(host="www.linkedin.com", title="Software Engineer")
    page = make_page(
        """
        <div class="top-card-layout"></div>
        <div class="jobs-unified-top-card">Software Engineer</div>
        <div class="description__text">Responsibilities and qualifications listed below.</div>
        <button>Apply</button>
        """,
        final_url="https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/123456",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.OPEN


def test_linkedin_direct_job_page_with_captcha_script_still_classifies_open() -> None:
    job = make_job(host="www.linkedin.com", title="Software Engineer")
    page = make_page(
        """
        <meta name="pageKey" content="d_jobs_guest_details" />
        <section class="top-card-layout"></section>
        <div class="jobs-unified-top-card">Software Engineer</div>
        <div class="description__text">Responsibilities and qualifications listed below.</div>
        <script src="https://www.recaptcha.net/recaptcha/api.js"></script>
        """,
        final_url="https://www.linkedin.com/jobs/view/4401029223",
        title="Company hiring Software Engineer in Seattle, WA | LinkedIn",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.OPEN


class _RetryingLinkedInGuestSession:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.guest_attempts = 0

    def get(self, url: str, **_: object) -> _FakeResponse:
        self.calls.append(url)
        if "jobs-guest/jobs/api/jobPosting/123456" in url:
            self.guest_attempts += 1
            if self.guest_attempts == 1:
                return _FakeResponse(text="rate limited", url=url, status_code=429)
            return _FakeResponse(
                text="""
                <section class="top-card-layout"></section>
                <div class="jobs-unified-top-card">Software Engineer</div>
                <div class="description__text">Responsibilities and qualifications listed below.</div>
                """,
                url=url,
                status_code=200,
            )
        return _FakeResponse(text="fallback", url=url, status_code=429)


def test_linkedin_guest_retries_before_fallback(monkeypatch) -> None:
    monkeypatch.setattr("backfill_status.detectors.time.sleep", lambda _: None)
    job = JobRecord(
        job_id="li-1",
        company_name="LinkedIn Co",
        title="Software Engineer",
        apply_url="https://www.linkedin.com/jobs/view/software-engineer-123456",
        host="www.linkedin.com",
    )
    session = _RetryingLinkedInGuestSession()
    result = detect_job_status(job, session=session)
    assert result.status == JobAvailability.OPEN
    assert session.guest_attempts == 2
    assert len(session.calls) == 2


class _GuestErrorDirectSuccessSession:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def get(self, url: str, **_: object) -> _FakeResponse:
        self.calls.append(url)
        if "jobs-guest/jobs/api/jobPosting/123456" in url:
            raise requests.RequestException("guest endpoint timeout")
        return _FakeResponse(
            text="""
            <meta name="pageKey" content="d_jobs_guest_details" />
            <section class="top-card-layout"></section>
            <div class="jobs-unified-top-card">Software Engineer</div>
            <div class="description__text">Responsibilities and qualifications listed below.</div>
            <script src="https://www.recaptcha.net/recaptcha/api.js"></script>
            """,
            url=url,
            status_code=200,
        )


def test_linkedin_guest_request_error_falls_back_to_direct_page(monkeypatch) -> None:
    monkeypatch.setattr("backfill_status.detectors.time.sleep", lambda _: None)
    job = JobRecord(
        job_id="li-1",
        company_name="LinkedIn Co",
        title="Software Engineer",
        apply_url="https://www.linkedin.com/jobs/view/software-engineer-123456",
        host="www.linkedin.com",
    )
    session = _GuestErrorDirectSuccessSession()
    result = detect_job_status(job, session=session)
    assert result.status == JobAvailability.OPEN
    assert any("jobs-guest/jobs/api/jobPosting/123456" in url for url in session.calls)
    assert any("/jobs/view/software-engineer-123456" in url for url in session.calls)


def test_ashby_null_payload_jobs_title_is_closed() -> None:
    job = make_job(host="jobs.ashbyhq.com", title="Software Engineer")
    page = make_page(
        """
        <script>
        window.__appData = {"organization":null,"posting":null,"jobBoard":null};
        </script>
        """,
        title="Jobs",
        final_url="https://jobs.ashbyhq.com/company/role",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.CLOSED


def test_gem_org_root_metadata_for_job_path_is_closed() -> None:
    job = make_job(host="jobs.gem.com", title="Backend Engineer")
    page = make_page(
        """
        <meta property="og:url" content="https://jobs.gem.com/auger" />
        <meta property="og:title" content="Auger Careers" />
        <div>Open positions at Auger Careers</div>
        """,
        final_url="https://jobs.gem.com/auger/jobs/backend-engineer",
        title="Auger Careers",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.CLOSED


def test_gem_encoded_job_token_path_org_page_is_closed() -> None:
    job = make_job(host="jobs.gem.com", title="Quality Assurance Engineer")
    page = make_page(
        """
        <meta property="og:url" content="https://jobs.gem.com/auger" />
        <meta property="og:title" content="Auger Careers" />
        <div>Open positions at Auger Careers</div>
        """,
        final_url="https://jobs.gem.com/auger/am9icG9zdDrg-r5dGbMDQyuZzGWzVspj",
        title="Auger Careers",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.CLOSED


def test_indeed_security_check_stays_unknown() -> None:
    job = make_job(host="www.indeed.com", title="Data Scientist")
    page = make_page(
        """
        Security Check
        Please verify that you're not a robot.
        """,
        status_code=403,
        final_url="https://www.indeed.com/viewjob?jk=abcdef",
        title="Security Check - Indeed.com",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.UNKNOWN
    assert "anti_bot" in result.detector


def test_avature_js_robot_challenge_stays_unknown() -> None:
    job = make_job(host="ibmglobal.avature.net", title="Software Engineer")
    page = make_page(
        """
        JavaScript is disabled.
        In order to continue, we need to verify that you're not a robot.
        Enable JavaScript and then reload the page.
        """,
        status_code=202,
        final_url="https://careers.ibm.com/en_US/careers/JobDetail?jobId=96261",
        title="",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.UNKNOWN
    assert "anti_bot" in result.detector


def test_workday_posting_available_false_is_closed() -> None:
    job = make_job(host="cisco.wd5.myworkdayjobs.com", title="Software Engineer")
    page = make_page(
        """
        <script>
        window.__INITIAL_STATE__ = {"postingAvailable": false, "jobPostingInfo": {"title":"Software Engineer"}};
        </script>
        """,
        final_url="https://cisco.wd5.myworkdayjobs.com/External/job/ABC",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.CLOSED


def test_ultipro_opportunitydetail_rich_content_is_open_with_empty_title() -> None:
    job = make_job(host="recruiting2.ultipro.com", title="Data Analyst")
    page = make_page(
        """
        <div>Qualifications: 3+ years experience</div>
        <div>Description: Build dashboards and analytics workflows</div>
        <div>Benefits: medical, dental, 401k</div>
        """,
        final_url="https://recruiting2.ultipro.com/ABC1000/JobBoard/OpportunityDetail?opportunityId=123",
        title="",
    )
    result = evaluate_fetched_page(job, page)
    assert result.status == JobAvailability.OPEN
