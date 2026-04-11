from match_pipe.frozen_teacher import frozen_teacher_manifest


def test_frozen_teacher_manifest_is_pure_semantic():
    manifest = frozen_teacher_manifest()
    config = manifest.feature_config
    assert manifest.version == "teacher_b_semantic_v1"
    assert config.enable_same_company_recall is False
    assert config.enable_duplicate_score is False
    assert config.allow_duplicate_override is False
    assert "taxonomy expansion" in manifest.allowed_mutations
