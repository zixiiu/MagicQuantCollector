import logging
import json
import time
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine, func
from datetime import date

import Notification
import SQLEngine
from Model import History, Comment
from analysis.ollama_api import generate_completion  # Assuming you have a module for this


# Function to configure console logging
def configure_logging():
    logger = logging.getLogger("tagging_process")
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console_handler)

    return logger


def query_stock_comments(session, filter_type="filtered"):
    """
    Query stock comments based on the specified filter type.
    :param session: SQLAlchemy session
    :param filter_type: Type of filtering; "filtered" or "all"
    :return: List of histories with comments
    """
    today = date.today()

    if filter_type == "filtered":
        # Filter histories with more than 100 comments
        histories_with_comments = (
            session.query(History)
            .join(Comment)
            .options(joinedload(History.comments))  # Ensure comments are eagerly loaded
            .filter(History.date == today)
            .group_by(History.id)
            .having(func.count(Comment.id) > 10)
            .all()
        )
    elif filter_type == "all":
        # Retrieve all histories and their comments
        histories_with_comments = (
            session.query(History)
            .join(Comment)
            .options(joinedload(History.comments))
            .all()
        )
    else:
        raise ValueError(f"Unknown filter type: {filter_type}")

    logging.info('queried: %i' % (len(histories_with_comments)))
    return histories_with_comments


def process_comments(session, histories_with_comments, logger):
    """
    Process comments and tag them using an external API.
    :param session: SQLAlchemy session
    :param histories_with_comments: List of histories with comments
    :param logger: Logger instance
    """
    tstart_time = time.time()
    processed_comments = 0
    tagged_comments = 0

    total_comments = sum(len(history.comments) for history in histories_with_comments)
    logger.info(f"Total comments to process: {total_comments}")

    for history in histories_with_comments:
        stock = history.stock

        # Read system prompt from the file
        with open("analysis/prompt_tagging.txt", "r", encoding='utf-8') as f:
            system_prompt = f.read().replace("{stock_name}", f"{stock.code} ({stock.name})")

        for comment in history.comments:
            start_time = time.time()  # Start timing
            prompt = comment.text

            # Generate completion using the API
            response = generate_completion(system_prompt, prompt)
            try:
                result = json.loads(response)  # Ensure it's valid JSON
                if isinstance(result, dict):
                    comment.encoding = response  # Save JSON-encoded string
                    session.add(comment)
                    session.commit()
                    tagged_comments += 1
            except Exception as e:
                logger.error(f"Error processing comment {comment.id}: {e}")

            # Measure time consumed
            time_consumed = time.time() - start_time

            # Log progress with time consumed
            elapsed_time = time.time() - tstart_time
            hours, remainder = divmod(int(elapsed_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            elapsed_time_formatted = f"{hours:02}h{minutes:02}m{seconds:02}s"

            processed_comments += 1
            logger.info(
                f" {comment.id} | {processed_comments}/{total_comments} | {elapsed_time_formatted} | {time_consumed:.2f}s |"
                f" {stock.code} ({stock.name}) || "
                f" {response} "
            )

        # Commit changes for the processed history
        session.commit()

    logger.info("All comments processed successfully.")
    return processed_comments, tagged_comments


def process_stock_comments(engine=SQLEngine.engine().engine):
    """Process stock comments with filtering."""
    logger = logging.getLogger("tagging_process")
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Query filtered comments
        histories_with_comments = query_stock_comments(session, filter_type="filtered")
        processed_comments, tagged_comments = process_comments(session, histories_with_comments, logger)
        Notification.send_notification(f'Tagging Complete: {tagged_comments}/{processed_comments} Tagged.')

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        session.close()
        logger.info("Process completed.")


def process_all_stock_comments(engine=SQLEngine.engine().engine):
    logging.info('start tagging all comments.')
    """Process all stock comments without filtering."""
    logger = logging.getLogger("tagging_process")
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Query all comments
        histories_with_comments = query_stock_comments(session, filter_type="all")
        processed_comments, tagged_comments = process_comments(session, histories_with_comments, logger)
        Notification.send_notification(f'Tagging Complete: {tagged_comments}/{processed_comments} Tagged.')

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        session.close()
        logger.info("Process completed.")


if __name__ == "__main__":
    # Set up console logging
    logger = configure_logging()

    # Replace with your database engine configuration
    engine = SQLEngine.engine().engine

    # Call the processing function
    # process_stock_comments(engine)
    # Uncomment to process all comments
    process_all_stock_comments(engine)

