from __future__ import annotations

from dataclasses import dataclass


GENERIC_CLOSED_MARKERS = (
    "job is no longer available",
    "this job is no longer available",
    "this opportunity is no longer available",
    "the job you are looking for is no longer available",
    "job posting is no longer available",
    "no longer accepting applications",
    "this job is closed",
    "position has been filled",
    "position has been closed",
    "requisition has been closed",
    "job requisition has been closed",
    "job has expired",
    "posting has expired",
    "the page you requested could not be found",
    "page not found",
    "job not found",
    "we couldn't find that job",
    "couldn't find the job",
    "this job has been removed",
    "this posting is no longer active",
    "this job post is no longer active",
    "this role is no longer open",
    "the requested job is no longer available",
    "this vacancy is no longer available",
    "this posting has been filled",
    "position is no longer available",
    "the position you are trying to view is no longer available",
    "the job you are trying to apply for has been filled",
    "the job listing no longer exists",
    "postingavailable: false",
    "error 404",
    "not found",
)

GENERIC_OPEN_MARKERS = (
    "apply for this job",
    "apply now",
    "submit application",
    "job description",
    "responsibilities",
    "qualifications",
    "preferred qualifications",
    "basic qualifications",
    "about the role",
    "about the job",
    "what you'll do",
    "what you will do",
    "about this role",
    "minimum qualifications",
    "basic qualifications",
    "preferred qualifications",
    "job posting",
    "job id",
    "job requisition id",
    "schema.org/jobposting",
    "\"@type\":\"jobposting\"",
    "\"@type\": \"jobposting\"",
)

HOST_ALIASES = {
    "boards.greenhouse.io": "greenhouse",
    "grnh.se": "greenhouse",
    "jobs.ashbyhq.com": "ashby",
    "jobs.lever.co": "lever",
    "www.amazon.jobs": "amazon",
    "www.linkedin.com": "linkedin",
    "apply.careers.microsoft.com": "microsoft",
    "careers.google.com": "google",
    "www.capitalonecareers.com": "capitalone",
    "careers.adobe.com": "phenom",
    "careers.qualcomm.com": "phenom",
    "careers.mastercard.com": "phenom",
    "jobs.jobvite.com": "jobvite",
    "jobs.gem.com": "gem",
}

HOST_SUFFIX_ALIASES = {
    ".greenhouse.io": "greenhouse",
    ".ashbyhq.com": "ashby",
    ".lever.co": "lever",
    ".amazon.jobs": "amazon",
    ".linkedin.com": "linkedin",
    ".careers.microsoft.com": "microsoft",
    ".google.com": "google",
    ".myworkdayjobs.com": "workday",
    ".oraclecloud.com": "oracle",
    ".icims.com": "icims",
    ".jobvite.com": "jobvite",
    ".gem.com": "gem",
    ".ultipro.com": "ultipro",
}


@dataclass(frozen=True)
class HostRule:
    name: str
    open_markers: tuple[str, ...]
    closed_markers: tuple[str, ...]
    strong_open_markers: tuple[str, ...] = ()
    strong_closed_markers: tuple[str, ...] = ()


HOST_RULES = {
    "greenhouse": HostRule(
        name="greenhouse",
        open_markers=(
            "apply for this job",
            "application submitted",
            "greenhouse.io",
            "\"job_board_name\"",
            "\"questions\"",
            "\"metadata\"",
            "\"absolute_url\"",
            "\"data_compliance\"",
            "\"location\"",
        ),
        closed_markers=(
            "job post is no longer active",
            "job you are trying to view has either expired or been removed",
            "this job is archived",
            "this job has been removed from our website",
        ),
        strong_open_markers=("apply for this job", "\"questions\"", "\"absolute_url\""),
    ),
    "ashby": HostRule(
        name="ashby",
        open_markers=(
            "apply for this job",
            "applicationformdefinition",
            "job posting",
            "ashbyhq",
            "\"jobposting\"",
            "\"employmenttype\"",
            "\"dateposted\"",
            "\"hiringorganization\"",
        ),
        closed_markers=(
            "job not found",
            "role is no longer available",
            "this job post has expired",
            "posting has been removed",
            "this posting is no longer accepting applications",
            "the job post is no longer available",
            "window.__appdata",
            "\"organization\":null",
            "\"posting\":null",
            "\"jobboard\":null",
        ),
        strong_closed_markers=(
            "\"organization\":null",
            "\"posting\":null",
            "\"jobboard\":null",
        ),
        strong_open_markers=("apply for this job", "applicationformdefinition", "\"hiringorganization\""),
    ),
    "lever": HostRule(
        name="lever",
        open_markers=(
            "apply for this job",
            "apply to this job",
            "lever",
            "commitment to diversity",
            "\"lever-via\"",
            "refer a friend",
            "resume/cv",
        ),
        closed_markers=(
            "this job has been filled",
            "this posting is no longer available",
            "job not found",
            "the posting you are looking for has expired",
        ),
        strong_open_markers=("apply for this job", "apply to this job", "resume/cv"),
    ),
    "amazon": HostRule(
        name="amazon",
        open_markers=(
            "job details",
            "basic qualifications",
            "preferred qualifications",
            "amazon is committed",
            "description",
            "job id:",
            "inclusive team culture",
        ),
        closed_markers=(
            "job details are no longer available",
            "the job you are trying to apply for is no longer available",
            "job has expired",
            "this job has been filled",
            "sorry, this job is no longer available",
        ),
        strong_open_markers=("basic qualifications", "preferred qualifications", "job details"),
        strong_closed_markers=("job details are no longer available",),
    ),
    "linkedin": HostRule(
        name="linkedin",
        open_markers=(
            "easy apply",
            "meet the hiring team",
            "see who",
            "applicants",
            "actively recruiting",
            "continue to apply",
            "jobs-guest/jobs/api/jobposting",
            "top-card-layout",
            "jobs-unified-top-card",
            "topcard",
            "description__text",
        ),
        closed_markers=(
            "no longer accepting applications",
            "job is closed",
            "this job is no longer accepting applications",
            "we couldn’t find a match",
            "page not found",
            "this job is no longer available",
            "the job you were looking for no longer exists",
        ),
        strong_open_markers=("easy apply", "continue to apply", "top-card-layout"),
        strong_closed_markers=("no longer accepting applications", "job is closed"),
    ),
    "microsoft": HostRule(
        name="microsoft",
        open_markers=(
            "apply",
            "professionals",
            "job number",
            "responsibilities",
            "qualifications",
            "share job",
            "similar jobs",
            "\"jobid\"",
            "\"jobtitle\"",
        ),
        closed_markers=(
            "job is no longer available",
            "this posting is no longer available",
            "the job you were looking for does not exist",
            "this job has expired",
        ),
        strong_open_markers=("job number", "share job", "\"jobid\""),
    ),
    "google": HostRule(
        name="google",
        open_markers=(
            "minimum qualifications",
            "preferred qualifications",
            "about the job",
            "apply",
            "share this job",
            "job responsibilities",
        ),
        closed_markers=(
            "the job posting you are looking for is no longer available",
            "job not found",
            "page not found",
            "no jobs found matching",
        ),
        strong_open_markers=("minimum qualifications", "preferred qualifications", "about the job"),
    ),
    "capitalone": HostRule(
        name="capitalone",
        open_markers=(
            "at capital one",
            "returning applicant",
            "posted",
            "find jobs here",
        ),
        closed_markers=(
            "custom job error",
            "oops! let’s fix this.",
            "oops! let's fix this.",
        ),
        strong_open_markers=("at capital one",),
        strong_closed_markers=("custom job error",),
    ),
    "workday": HostRule(
        name="workday",
        open_markers=(
            "apply",
            "posted date",
            "locations",
            "job requisition id",
            "career area",
            "\"jobpostinginfo\"",
            "\"externalpath\"",
            "\"bulletfields\"",
        ),
        closed_markers=(
            "job requisition has been closed",
            "job has expired",
            "the job posting is no longer available",
            "the job posting you requested is no longer available",
            "this job is no longer accepting applications",
            "postingavailable: false",
            "\"postingavailable\":false",
            "\"postingavailable\": false",
        ),
        strong_closed_markers=("postingavailable: false", "\"postingavailable\":false"),
        strong_open_markers=("job requisition id", "posted date", "\"jobpostinginfo\""),
    ),
    "oracle": HostRule(
        name="oracle",
        open_markers=(
            "apply now",
            "job description",
            "organization",
            "locations",
            "candidate experience page",
            "job_details",
            "apibaseurl",
            "\"jobid\"",
            "\"jobtitle\"",
            "\"jobdescription\"",
        ),
        closed_markers=(
            "job could not be loaded",
            "job posting is expired",
            "job is no longer available",
            "page not found",
            "404 - page not found",
            "we can’t find the job",
        ),
        strong_open_markers=("job_details", "candidate experience page", "\"jobtitle\""),
    ),
    "icims": HostRule(
        name="icims",
        open_markers=(
            "apply for this job online",
            "share with a friend",
            "job description",
            "options",
            "iCIMS",
            "job details",
            "posted date",
        ),
        closed_markers=(
            "this opportunity is no longer available",
            "job not found",
            "page not found",
            "this job is no longer available",
            "position has been filled",
        ),
        strong_open_markers=("apply for this job online", "job details"),
    ),
    "phenom": HostRule(
        name="phenom",
        open_markers=(
            "job details",
            "responsibilities",
            "qualifications",
            "share job",
            "og:title",
            "og:description",
            "apply",
        ),
        closed_markers=(
            "the job you are trying to apply for has been filled",
            "this job is no longer available",
            "job posting is no longer available",
            "page not found",
        ),
        strong_open_markers=("og:title", "og:description", "job details"),
        strong_closed_markers=("the job you are trying to apply for has been filled",),
    ),
    "jobvite": HostRule(
        name="jobvite",
        open_markers=(
            "apply now",
            "job description",
            "job id",
            "jobvite",
            "share this job",
        ),
        closed_markers=(
            "the job listing no longer exists",
            "this job is no longer available",
            "job not found",
        ),
        strong_open_markers=("job description", "jobvite"),
        strong_closed_markers=("the job listing no longer exists",),
    ),
    "gem": HostRule(
        name="gem",
        open_markers=(
            "apply for this job",
            "job description",
            "responsibilities",
            "qualifications",
        ),
        closed_markers=(
            "careers",
            "open positions",
            "we're hiring",
            "og:url",
            "job not found",
        ),
        strong_closed_markers=("og:url",),
    ),
    "ultipro": HostRule(
        name="ultipro",
        open_markers=(
            "opportunitydetail",
            "qualifications",
            "benefits",
            "responsibilities",
            "description",
            "apply",
        ),
        closed_markers=(
            "opportunity not found",
            "requisition not found",
            "this position is no longer available",
            "job not found",
        ),
        strong_open_markers=("opportunitydetail", "qualifications", "benefits"),
    ),
}


def canonical_host(host: str) -> str:
    lowered = str(host or "").strip().lower()
    if lowered in HOST_ALIASES:
        return HOST_ALIASES[lowered]
    for suffix, alias in HOST_SUFFIX_ALIASES.items():
        if lowered.endswith(suffix) or suffix in lowered:
            return alias
    return lowered


def host_rule(host: str) -> HostRule | None:
    return HOST_RULES.get(canonical_host(host))
