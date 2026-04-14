import argparse
import sys
from config.settings import Settings
from pipeline.orchestrator import PipelineOrchestrator

def main():
    parser = argparse.ArgumentParser(
        description="GitHub Pipeline Analysis - MSc Project"
    )
    parser.add_argument(
        "--mode",
        choices=["full", "collect", "analyze"],
        default="full",
        help="Pipeline execution mode (default: full)"
    )
    parser.add_argument(
        "--repos",
        nargs="*",
        help="Optional: specific repos to analyze (e.g., pytorch/pytorch)"
    )
    args = parser.parse_args()

    settings = Settings()
    logger = settings.get_logger("main")
    logger.info("GitHub Pipeline Analysis starting in '%s' mode", args.mode)

    orchestrator = PipelineOrchestrator(settings)

    try:
        if args.mode == "full":
            results = orchestrator.run_full_pipeline(args.repos)
        elif args.mode == "collect":
            dataset = orchestrator.run_collection(args.repos)
            if dataset:
                orchestrator.run_storage(dataset)
                logger.info("Collection complete: %d repos stored", len(dataset))
            return
        elif args.mode == "analyze":
            results = orchestrator.run_analysis_only()
        else:
            logger.error("Unknown mode: %s", args.mode)
            sys.exit(1)

        if results:
            _print_summary(results, logger)
        else:
            logger.warning("No results produced. Check if data exists in MongoDB.")

    except Exception as e:
        logger.error("Pipeline failed: %s", str(e), exc_info=True)
        sys.exit(1)

def _print_summary(results: dict, logger):
    "Print a summary of the analysis results to console."
    df = results.get("df")
    if df is None:
        return
    logger.info("\n" + "=" * 60)
    logger.info("ANALYSIS SUMMARY")
    logger.info("=" * 60)

    # Score summary
    score_summary = results.get("score_summary")
    if score_summary is not None and not score_summary.empty:
        logger.info("\nRepository Scores (ranked by overall):")
        print(score_summary.to_string(index=False))

    # Dimension leaders
    leaders = results.get("dimension_leaders", {})
    if leaders:
        logger.info("\nDimension Leaders:")
        for dim, repo in leaders.items():
            logger.info("  %s: %s", dim, repo)

    # Community grades
    community = results.get("community_summary")
    if community is not None and not community.empty:
        logger.info("\nCommunity Health Grades:")
        print(community[["name", "community_grade", "community_total_score"]].to_string(index=False))

    # Community insights
    insights = results.get("community_insights", [])
    if insights:
        logger.info("\nCommunity Insights:")
        for insight in insights:
            logger.info("  [%s] %s", insight["type"].upper(), insight["message"])

    # Top contributors
    top_contribs = results.get("top_contributors")
    if top_contribs is not None and not top_contribs.empty:
        logger.info("\nTop 10 Contributors:")
        print(top_contribs.head(10)[["login", "total_contributions", "repo_count"]].to_string(index=False))
    logger.info("\n" + "=" * 60)

if __name__ == "__main__":
    main()
