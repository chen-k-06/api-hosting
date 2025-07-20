from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins = ["https://chen-k-06.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

#------------------------------------------------
#------------------------------------------------
# WORDLE
#------------------------------------------------
#------------------------------------------------

from scipy.stats import entropy
from typing import Dict
import os
import pickle
from fastapi.middleware.cors import CORSMiddleware
from Wordle.wordle_helper_functions import get_all_patterns

#------------------------------------------------
# Get feedback dict cache functions
#------------------------------------------------
def get_feedback_dict():
    feedback_dict = None

    if os.path.exists("Wordle/pattern_cache.pkl"):
        try:
            with open("Wordle/pattern_cache.pkl", "rb") as file:
                feedback_dict = pickle.load(file)
        except Exception as e:
            print("Error loading pattern_cache.pkl:", e)
    
    if feedback_dict is None:
        print("Feedback pickle not included")

    return feedback_dict

#------------------------------------------------
# Reduce guess list functions
#------------------------------------------------
def get_remaining_guesses(guesses: list[str], feedback: list[str], current_possible_answers: list[str]):
    '''Reduces the list of possible answers based on the most recent feedback. Returns a new list of 
       possible answers that is a subset of current_possible_answers
        
        Args:
         guesses (list): A list of string guesses, which could be empty
         feedback (list): A list of feedback strings, which could be empty
         current_possible_answers (list): a list of possible words that could be the secret word, 
            not yet updated based on most recent feedback. Cannot be empty.

        Returns:
         possible_answers (list): a list of remaining possible words that could be the secret word
    '''
    if (guesses[0] == ""):  # current guess is the first guess -> valid guesses is the list of all valid guesses
        return current_possible_answers
    
    feedback_dict = get_feedback_dict()
    possible_answers = set()
    current_possible_answers = set(current_possible_answers)
    last_guess = guesses[len(feedback) - 1]
    last_feedback = feedback[len(feedback) - 1]

    words = feedback_dict[last_guess][last_feedback]
    possible_answers = current_possible_answers.intersection(words)

    return list(possible_answers)

class GetRemainingGuesses(BaseModel):
    guesses: list[str]
    feedback: list[str]
    current_possible_answers: list[str]

@app.post("/wordle_get_remaining_guesses")
def handle_get_remaining_guesses(request: GetRemainingGuesses) -> list[str]: 
    result = get_remaining_guesses(request.guesses, request.feedback, request.current_possible_answers)
    return result

#------------------------------------------------
# Entropy functions
#------------------------------------------------
def calculate_entropies(possible_guesses: list[str], possible_answers: list[str]) -> Dict[str, float]:
    '''
    Calculates the entropy for every guess in possible guesses, taking into account 
    the remaining possible answers. 
        Args:
            possible_guesses (list): a list of all valid guesses. Will not be empty
            possible_answers (list): a list of all words that could be the secret word. Will not be empty

        Returns:
            entropies (list): a list of entropies that correspond to each guess in possible_guesses
    '''
    entropies = {}
    feedback_dict = get_feedback_dict()
    all_patterns = get_all_patterns()
    possible_answers = set(possible_answers)
    if len(possible_answers) <= 2:
        return {answer: 1.0 for answer in possible_answers}
    
    for guess in possible_guesses: # ~2,500 words
        counts = []
        for pattern in all_patterns: # 243 patterns
            if ((guess not in feedback_dict) or (pattern not in feedback_dict[guess])):
                continue
            answers = (set(feedback_dict[guess][pattern])).intersection(possible_answers)
            counts.append(len(answers))
        total = sum(counts)
        if total > 0: 
            counts = [c / total for c in counts if c > 0]
            entropies[guess] = entropy(counts, base = 2)
        else: 
            entropies[guess] = 0.0
    sorted_entropies = dict(sorted(entropies.items(), key=lambda item: item[1], reverse=True))
    return sorted_entropies

class GetEntropies(BaseModel):
    possible_guesses: list[str]
    possible_answers: list[str]

@app.post("/wordle_get_entropies")
def get_entropies(request: GetEntropies) -> dict: 
    result = calculate_entropies(request.possible_guesses, request.possible_answers)
    return result

#------------------------------------------------
#------------------------------------------------
# ANAGAME 
#------------------------------------------------
#------------------------------------------------

from Anagame.AnagramExplorer import AnagramExplorer
from Anagame.valid_anagame_words import get_valid_word_list
from Anagame.anagame import calc_stats, generate_letters
from typing import List, Tuple, Any

#------------------------------------------------
# Calculate end of game statistics functions
#------------------------------------------------
class GetLetters(BaseModel):
    fun_factor: int
    distribution: str
    
@app.post("/anagame_get_letters")
def handle_get_letters(request: GetLetters) -> list[str]: 
    explorer = AnagramExplorer(get_valid_word_list())
    result = generate_letters(request.fun_factor, request.distribution, explorer)
    return result

#------------------------------------------------
# Calculate end of game statistics functions 
#------------------------------------------------
class CalcStats(BaseModel):
    guesses: list[list[str]]
    letters: list[str]

class StatsResponse(BaseModel):
    valid_guesses: List[str]
    invalid_guesses: List[Tuple[str, str]]
    score: int
    accuracy: float
    skill: float
    guessed_words: list[str]
    not_guessed_words: list[str]

@app.post("/anagame_calc_stats", response_model=StatsResponse)
def handle_calc_stats(request: CalcStats) -> StatsResponse: 
    explorer = AnagramExplorer(get_valid_word_list())
    result = calc_stats(request.guesses, request.letters, explorer) #guesses needs to be tuples
        
    return StatsResponse(
        valid_guesses=result[0],
        invalid_guesses=result[1],
        score=result[2],
        accuracy=result[3],
        skill=result[4],
        guessed_words=result[5],
        not_guessed_words=result[6]
    )

#------------------------------------------------
# Get all anagrams (for hint)
#------------------------------------------------

#------------------------------------------------
#------------------------------------------------
# REAL TIME STOCK INDICATOR
#------------------------------------------------
#------------------------------------------------
