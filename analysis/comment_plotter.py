import json
from datetime import date, datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from matplotlib import pyplot as plt
from matplotlib import rcParams
import numpy as np
import SQLEngine
from Model import Stock, History, Comment

# Initialize SQLAlchemy engine and session
engine = SQLEngine.engine().engine  # Use the provided engine setup
Session = sessionmaker(bind=engine)
session = Session()

# Define the colors for the categories
colors = {
    "狂热": (139 / 255, 0, 0, 1),  # Dark Red
    "乐观": (255 / 255, 105 / 255, 97 / 255, 1),  # Light Red
    "平静": (192 / 255, 192 / 255, 192 / 255, 0.5),  # Gray
    "悲观": (144 / 255, 238 / 255, 144 / 255, 1),  # Light Green
    "恐慌": (0, 100 / 255, 0, 1),  # Dark Green
}

# Configure Matplotlib to render Chinese characters
rcParams['font.sans-serif'] = ['SimHei']  # Replace 'SimHei' with a valid font supporting Chinese if necessary
rcParams['axes.unicode_minus'] = False


def get_top_histories_with_comments():
    today = date.today()

    # Query histories with today's date and count comments
    histories = (
        session.query(
            History,
            func.count(Comment.id).label("comment_count"),
            Stock.code,
            Stock.name
        )
        .join(Comment, History.id == Comment.history_id)
        .join(Stock, History.stock_code == Stock.code)
        .filter(History.date == today)
        .group_by(History.id, Stock.code, Stock.name)
        .order_by(func.count(Comment.id).desc())
        .limit(20)
        .all()
    )

    return histories


def analyze_emotions(comments):
    emotion_counts = {"狂热": 0, "乐观": 0, "平静": 0, "悲观": 0, "恐慌": 0}

    for comment in comments:
        try:
            encoding = json.loads(comment.encoding)
            emotion = encoding.get("情绪强度")
            if emotion in emotion_counts:
                emotion_counts[emotion] += 1
        except (json.JSONDecodeError, TypeError, AttributeError):
            # Ignore comments with invalid JSON or missing "情绪强度"
            continue

    return emotion_counts


def plot_histories(histories_with_emotions):
    # Prepare data for plotting
    history_labels = []
    emotion_data = {key: [] for key in colors.keys()}
    comment_counts = []
    changes = []

    for (history, stock_code, stock_name, comment_count), emotions in histories_with_emotions:
        label = f"{stock_code} {stock_name} ({comment_count})"
        history_labels.append(label)
        comment_counts.append(comment_count)
        changes.append(history.change)  # Collect the change value

        total_comments = sum(emotions.values())
        for emotion in colors.keys():
            percentage = (emotions[emotion] / total_comments) * 100 if total_comments > 0 else 0
            emotion_data[emotion].append(percentage)

    # Create horizontal stacked bar chart
    bar_width = 0.8
    y_positions = np.arange(len(history_labels))

    fig, ax = plt.subplots(figsize=(12, 10))

    # Initialize bottom values for stacking
    bottom = np.zeros(len(history_labels))

    for emotion, color in colors.items():
        ax.barh(y_positions, emotion_data[emotion], color=color, label=emotion, left=bottom)
        bottom += emotion_data[emotion]

    # Add gold vertical lines for changes and annotate the values
    for i, change in enumerate(changes):
        # Scale change value to fit the range [-20, 20]
        scaled_change = 50 - (change / 10) * 50


        # Draw a vertical line
        # ymin = (i - bar_width / 2) / len(y_positions)
        # ymax = (i + bar_width / 2) / len(y_positions)
        # ax.axvline(scaled_change, ymin=ymin, ymax=ymax, color="black", linewidth=2, linestyle="-")

        # Annotate with the change value
        ax.text(scaled_change, i, f"{change:.2f}%", va='center', ha='left',
                fontsize=10, color="black", weight="bold")

    ax.axvline(50, 0, 1, color=(0, 0, 0, 0.2), linewidth=2)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(history_labels, fontsize=10)
    ax.set_title("Sentiment Report @ %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fontsize=14)

    # Remove axis labels
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.legend(title="Emotions", loc="upper right")

    plt.tight_layout()
    plt.show()


# Main logic
if __name__ == "__main__":
    histories = get_top_histories_with_comments()
    histories_with_emotions = []

    for history, comment_count, stock_code, stock_name in histories:
        comments = session.query(Comment).filter(Comment.history_id == history.id).all()
        emotion_counts = analyze_emotions(comments)
        histories_with_emotions.append(((history, stock_code, stock_name, comment_count), emotion_counts))

    histories_with_emotions.sort(key=lambda x: x[0][3], reverse=False)
    plot_histories(histories_with_emotions)
