def diagnose(summary):
    return {"facts": ["positive_negative_offset"] if summary["positive_difference"] > 0 and summary["negative_difference"] < 0 else [],
            "root_cause": "not_established",
            "hypotheses": [{"status": "not_testable", "candidate": "timing_or_definition_or_processing",
                            "required_evidence": "Independent system logs, approved definitions and cutoff history."}]}
