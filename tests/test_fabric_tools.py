import pytest
from langchain_core.language_models.fake_chat_models import ParrotFakeChatModel

from fabric_agent_action.fabric_tools import FabricTools


@pytest.fixture(scope="module")
def llm():
    return ParrotFakeChatModel()


@pytest.mark.parametrize(
    "pattern_name",
    [
        "agility_story",
        "ai",
        "analyze_answers",
        "analyze_candidates",
        "analyze_cfp_submission",
        "analyze_claims",
        "analyze_comments",
        "analyze_debate",
        "analyze_email_headers",
        "analyze_incident",
        "analyze_interviewer_techniques",
        "analyze_logs",
        "analyze_malware",
        "analyze_military_strategy",
        "analyze_paper",
        "analyze_patent",
        "analyze_personality",
        "analyze_presentation",
        "analyze_product_feedback",
        "analyze_proposition",
        "analyze_prose",
        "analyze_prose_json",
        "analyze_prose_pinker",
        "analyze_sales_call",
        "analyze_spiritual_text",
        "analyze_tech_impact",
        "analyze_threat_report",
        "analyze_threat_report_trends",
        "answer_interview_question",
        "ask_secure_by_design_questions",
        "ask_uncle_duke",
        "capture_thinkers_work",
        "check_agreement",
        "clean_text",
        "coding_master",
        "compare_and_contrast",
        "create_5_sentence_summary",
        "create_academic_paper",
        "create_ai_jobs_analysis",
        "create_aphorisms",
        "create_art_prompt",
        "create_better_frame",
        "create_coding_project",
        "create_command",
        "create_cyber_summary",
        "create_design_document",
        "create_diy",
        "create_formal_email",
        "create_git_diff_commit",
        "create_graph_from_input",
        "create_hormozi_offer",
        "create_idea_compass",
        "create_investigation_visualization",
        "create_keynote",
        "create_logo",
        "create_markmap_visualization",
        "create_mermaid_visualization",
        "create_mermaid_visualization_for_github",
        "create_micro_summary",
        "create_network_threat_landscape",
        "create_npc",
        "create_pattern",
        "create_quiz",
        "create_reading_plan",
        "create_recursive_outline",
        "create_report_finding",
        "create_rpg_summary",
        "create_security_update",
        "create_show_intro",
        "create_sigma_rules",
        "create_story_explanation",
        "create_stride_threat_model",
        "create_summary",
        "create_tags",
        "create_threat_scenarios",
        "create_ttrc_graph",
        "create_ttrc_narrative",
        "create_upgrade_pack",
        "create_user_story",
        "create_video_chapters",
        "create_visualization",
        "dialog_with_socrates",
        "explain_code",
        "explain_docs",
        "explain_math",
        "explain_project",
        "explain_terms",
        "export_data_as_csv",
        "extract_algorithm_update_recommendations",
        "extract_article_wisdom",
        "extract_book_ideas",
        "extract_book_recommendations",
        "extract_business_ideas",
        "extract_controversial_ideas",
        "extract_core_message",
        "extract_ctf_writeup",
        "extract_extraordinary_claims",
        "extract_ideas",
        "extract_insights",
        "extract_insights_dm",
        "extract_instructions",
        "extract_jokes",
        "extract_latest_video",
        "extract_main_idea",
        "extract_most_redeeming_thing",
        "extract_patterns",
        "extract_poc",
        "extract_predictions",
        "extract_primary_problem",
        "extract_primary_solution",
        "extract_product_features",
        "extract_questions",
        "extract_recommendations",
        "extract_references",
        "extract_skills",
        "extract_song_meaning",
        "extract_sponsors",
        "extract_videoid",
        "extract_wisdom",
        "extract_wisdom_agents",
        "extract_wisdom_dm",
        "extract_wisdom_nometa",
        "find_hidden_message",
        "get_wow_per_minute",
        "get_youtube_rss",
        "identify_dsrp_distinctions",
        "identify_dsrp_perspectives",
        "identify_dsrp_relationships",
        "identify_dsrp_systems",
        "identify_job_stories",
        "improve_academic_writing",
        "improve_prompt",
        "improve_report_finding",
        "improve_writing",
        "label_and_rate",
        "md_callout",
        "official_pattern_template",
        "prepare_7s_strategy",
        "provide_guidance",
        "rate_ai_response",
        "rate_ai_result",
        "rate_content",
        "rate_value",
        "raw_query",
        "recommend_artists",
        "recommend_pipeline_upgrades",
        "recommend_talkpanel_topics",
        "refine_design_document",
        "review_design",
        "show_fabric_options_markmap",
        "solve_with_cot",
        "suggest_pattern",
        "summarize",
        "summarize_debate",
        "summarize_git_changes",
        "summarize_git_diff",
        "summarize_lecture",
        "summarize_legislation",
        "summarize_micro",
        "summarize_newsletter",
        "summarize_paper",
        "summarize_prompt",
        "summarize_pull-requests",
        "summarize_rpg_session",
        "to_flashcards",
        "transcribe_minutes",
        "translate",
        "tweet",
        "write_essay",
        "write_hackerone_report",
        "write_latex",
        "write_micro_essay",
        "write_nuclei_template_rule",
        "write_pull-request",
        "write_semgrep_rule",
        "find_logical_fallacies",
        "analyze_mistakes",
        "summarize_meeting",
        "extract_recipe",
        "create_newsletter_entry",
        "analyze_risk",
        "convert_to_markdown",
    ],
)
def test_read_fabric_patterns(llm, pattern_name):
    fabric_tools = FabricTools(llm)
    pattern = fabric_tools.read_fabric_pattern(pattern_name)
    assert len(pattern) > 0


def test_read_fabric_pattern_on_not_exist(llm):
    fabric_tools = FabricTools(llm)
    with pytest.raises(OSError):
        fabric_tools.read_fabric_pattern("not_exists")


def test_invoke_llm(llm):
    fabric_tools = FabricTools(llm)
    fabric_output = fabric_tools.invoke_llm("create quiz for me about hammer", "create_quiz")
    assert "create quiz for me about hammer" in fabric_output


@pytest.mark.parametrize(
    "included,excluded,tools_count",
    [
        ("create_stride_threat_model", "", 1),
        ("", "", 182),
        ("", "create_stride_threat_model", 181),
    ],
)
def test_fabric_tools_filter(llm, included, excluded, tools_count):
    fabric_tools = FabricTools(llm, max_number_of_tools=1000, included_tools=included, excluded_tools=excluded)
    tools = fabric_tools.get_fabric_tools()
    assert len(tools) == tools_count


def test_fabric_tools_max_number_of_tools(llm):
    fabric_tools = FabricTools(llm)
    tools = fabric_tools.get_fabric_tools()
    assert len(tools) == 182


def test_fabric_tools_max_number_of_tools_on_error(llm):
    fabric_tools = FabricTools(llm, max_number_of_tools=1)
    with pytest.raises(ValueError, match="Model supporting only 1 tools, but got 182"):
        fabric_tools.get_fabric_tools()
