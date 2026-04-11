from match_pipe.benchmark import build_benchmark_suite
from match_pipe.matcher import MatchEngine


def test_benchmark_suite_has_standard_and_hard_cases():
    engine = MatchEngine.from_project_data(include_scraped=True, include_portfolio=True)
    suite = build_benchmark_suite(engine.index.jobs)
    assert len(suite.standard_cases) >= 150
    assert len(suite.hard_cases) >= 30
