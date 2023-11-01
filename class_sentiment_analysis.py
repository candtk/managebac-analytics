from managebac import ManageBac
from sentiment import sentiment_analysis
from os import system
from matplotlib import pyplot as plt

# Class discussion IDs to analyse — add or remove as needed
discussions = [
    {"name": "Physics",  "id": "11981921"},
    {"name": "Hidden 1", "id": "11981919"},
    {"name": "Hidden 2", "id": "11981899"},
    {"name": "Hidden 3", "id": "11981911"},
    {"name": "Hidden 4", "id": "11981893"},
    {"name": "Hidden 5", "id": "11981915"},
    {"name": "Hidden 6", "id": "11981902"},
    {"name": "Coding",   "id": "11982115"},
]

ManagebacSession = ManageBac(Email=input("enter email"), Password=input("enter pass"))

system('clear')

scores = {}

for discussion in discussions:
    print(discussion["name"])
    discussion["positives"] = 0
    discussion["negatives"] = 0
    discussion["neutrals"] = 0
    discussion["score"] = 0
    messages = ManagebacSession.get_class_messages(discussionid=discussion["id"])

    for message in messages:
        analysis, polarity = sentiment_analysis(message)
        if analysis == "positive":
            discussion["positives"] += 1
            discussion["score"] += polarity
        elif analysis == "negative":
            discussion["negatives"] += 1
            discussion["score"] += polarity
        else:
            discussion["neutrals"] += 1

    discussion["score"] = discussion["score"] / len(messages)
    scores[discussion["name"]] = discussion["score"]

keys = scores.keys()
values = scores.values()

plt.bar(keys, values)
plt.title("Average Sentiment Score of ManageBac Class Discussions")
plt.xlabel("Class")
plt.ylabel("Average Polarity Score")
plt.show()
