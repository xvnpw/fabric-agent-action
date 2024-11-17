import os


fabric_patterns_included = "clean_text,create_stride_threat_model,create_design_document,review_design,refine_design_document,create_threat_scenarios,improve_writing,create_quiz,create_summary"


def helper_file_path(file_name, mode="r"):
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    file_path = os.path.join(data_dir, file_name)

    return open(file_path, mode=mode, encoding="utf-8")
