# /quotes_storage.py
import random

STOIC_QUOTES = {
    1: "You have power over your mind - not outside events. Realize this, and you will find strength. - Marcus Aurelius",
    2: "The happiness of your life depends upon the quality of your thoughts. - Marcus Aurelius",
    3: "What need is there to weep over parts of life? The whole of it calls for tears. - Seneca",
    4: "We suffer more often in imagination than in reality. - Seneca",
    5: "If it is not right, do not do it; if it is not true, do not say it. - Marcus Aurelius",
    6: "Difficulties strengthen the mind, as labor does the body. - Seneca",
    7: "Waste no more time arguing about what a good man should be. Be one. - Marcus Aurelius",
    8: "Luck is what happens when preparation meets opportunity. - Seneca",
    9: "The best revenge is to be unlike him who performed the injury. - Marcus Aurelius",
    10: "There is only one way to happiness and that is to cease worrying about things which are beyond the power of our will. - Epictetus",
    11: "He who fears death will never do anything worth of a man who is alive. - Seneca",
    12: "Very little is needed to make a happy life; it is all within yourself in your way of thinking. - Marcus Aurelius",
    13: "No man is free who is not master of himself. - Epictetus",
    14: "Life is very short and anxious for those who forget the past, neglect the present, and fear the future. - Seneca",
    15: "It is not the man who has too little, but the man who craves more, that is poor. - Seneca",
    16: "First say to yourself what you would be; and then do what you have to do. - Epictetus",
    17: "Accept the things to which fate binds you, and love the people with whom fate brings you together, but do so with all your heart. - Marcus Aurelius",
    18: "While we are postponing, life speeds by. - Seneca",
    19: "It's not what happens to you, but how you react to it that matters. - Epictetus",
    20: "If you want to improve, be content to be thought foolish and stupid. - Epictetus"
}

def get_random_quote():
    """Returns a random quote from the dictionary"""
    quote_id = random.choice(list(STOIC_QUOTES.keys()))
    return {
        'id': quote_id,
        'text': STOIC_QUOTES[quote_id].split(' - ')[0],
        'author': STOIC_QUOTES[quote_id].split(' - ')[1] if ' - ' in STOIC_QUOTES[quote_id] else None
    }