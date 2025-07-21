import random
from Anagame.valid_anagame_words import get_valid_word_list
from Anagame.AnagramExplorer import AnagramExplorer

def generate_letters(fun_factor: int, distribution: str, explorer:AnagramExplorer) -> list:
    '''Generates a list of 7 randomly-chosen lowercase letters which can form at least 
      fun_factor unique anagramable words.


         Args:
          fun_factor (int): minimum number of unique anagram words offered by the chosen letters
          distribution (str): The type of distribution to use in order to choose letters
                "uniform" - chooses letters based on a uniform distribution, with replacement
                "scrabble" - chooses letters based on a scrabble distribution, without replacement
          explorer (AnagramExplorer): helper object used to facilitate computing anagrams based on specific letters.
         
         Returns:
             set: A set of 7 lowercase letters

         Example
         -------
         >>> explorer = AnagramExplorer(get_valid_word_list())
         >>> generate_letters(75, "scrabble", explorer)
         ["p", "o", "t", "s", "r", "i", "a"] 
    '''   
    letters = ["p", "o", "t", "s", "r", "i", "a"] 
    fun_factor_achieved = False
    distribution = distribution.lower()

    while (fun_factor_achieved == False):
        if distribution == "uniform":
            uniform_distribution = "abcdiefghjklmnopqrstuvwxyz"
            uniform_distribution = list(uniform_distribution)
            for i in range(7):
                letters[i] = uniform_distribution[int(random.random()*25)]

        elif distribution == "scrabble":
            scrabble_distribution = "aaaaaaaaabbccddddeeeeeeeeeeeeffggghhiiiiiiiiijkllllmmnnnnnnooooooooppqrrrrrrssssttttttuuuuvvwwxyyz"
            scrabble_distribution = list(scrabble_distribution)
            for i in range(7):
                index = int(random.random()*len(scrabble_distribution) - 1)
                letters[i] = scrabble_distribution[index]
                scrabble_distribution.remove(scrabble_distribution[index])
        print(letters)
        if (fun_factor <= (len(explorer.get_all_anagrams(letters)))):
            fun_factor_achieved = True

    # print(type(explorer.get_all_anagrams(letters)))
    # print(len(explorer.get_all_anagrams(letters)))
    # print(fun_factor <= (len(explorer.get_all_anagrams(letters))))
    return letters


def parse_guess(guess:str) -> tuple:
   '''Splits an entered guess into a two word tuple with all white space removed

        Args:
            guess (str): A single string reprsenting the player guess

        Returns:
            tuple: A tuple of two words. ("", "") in case of invalid input.

        Examples
        --------
        >>> parse_guess("eat, tea")
        ("eat", "tea")

        >>> parse_guess("eat , tea")
        ("eat", "tea")

        >>> parse_guess("eat,tea")
        ("eat", "tea")

        >>> parse_guess("eat tea")
        ("", "")
   '''
   print("parse guess: ", guess)
   guess = list(guess)

   for i in range(len(guess)): 
      guess[i] = guess[i].replace(",", "")
      guess[i] = guess[i].replace(" ", "")

   return tuple(guess)
   
def calc_stats(guesses: list, letters: list, explorer) -> dict:
    '''Aggregates several statistics into a single dictionary with the following key-value pairs:
        "valid" - list of valid guesses
        "invalid" - list of invalid/duplicate guesses
        "score" - per the rules of the game
        "accuracy" -  truncated int percentage representing valid player guesses out of all player guesses
                      3 valid and 5 invalid guesses would result in an accuracy of 37 --> 3/8 = .375
        "guessed" - set of unique words guessed from valid guesses
        "not guessed" - set of unique words not guessed
        "skill" - truncated int percentage representing the total number of unique anagram words guessed out of all possible unique anagram words
                  Guessing 66 out of 99 unique words would result in a skill of 66 --> 66/99 = .66666666
     Args:
      guesses (list): A list of tuples representing all word pairs guesses by the user
      letters (list): The list of valid letters from which user should create anagrams
      explorer (AnagramExplorer): helper object used to compute anagrams of letters.

     Returns:
      dict: Returns a dictionary with seven keys: "valid", "invalid", "score", "accuracy", "guessed", "not guessed", "skill"
    
     Example
     -------
     >>> letters = ["p", "o", "t", "s", "r", "i", "a"]
     >>> guesses = [("star","tarts"),("far","rat"),("rat","art"),("rat","art"),("art","rat")]
     >>> explorer = AnagramExplorer(get_valid_word_list())
     >>> calc_stats(guesses, letters, explorer)
     {
        "valid":[("rat","art")],
        "invalid":[("star","tarts"),("far","rat"),("rat","art"),("art","rat")],
        "score": 1,
        "accuracy": 20,
        "guessed": { "rat", "art" },
        "not_guessed": { ...73 other unique },
        "skill": 2
     }
    '''
    stats = [[], [], [], [], [], [], []]
    stats[0] = []   #list of tuples: "valid"
    stats[1] = [] #list of tuples: "invalid"
    stats[2] = 0    #total score per the rules of the game: "score"
    stats[3] = 0 # truncated int percentage representing valid player guesses out of all player guesses
                 # "accuracy"
    stats[4] = 0    #truncated int percentage representing unique guessed words out of all possible unique anagram words
                 # "skill"
    stats[5] = set() #unique valid guessed words: "guessed"
    stats[6] = set() #unique words the player could have guessed, but didn’t: "not guessed"

    guesses_copy = []
    for guess in guesses: 
        print("guess: ", guess)
        temp = parse_guess(tuple(guess))
        guesses_copy.append(temp)
        print("guesses copy: ", guesses_copy)

    guesses = guesses_copy

    for guess in guesses: 
       if len(guess) == 2 and explorer.is_valid_anagram_pair((guess[0], guess[1]), letters) and sorted(guess) not in stats["valid"]:
            stats[0].append(sorted(guess))
            print(stats[0])

       else: 
          stats[1].append(guess)

    if len(guesses) == 0: 
       stats[3] = 0
    
    else:
        stats[3] = int ((len(stats[0]) / len(guesses)) * 100)

    for pair in stats[0]:
       for word in pair: 
          stats[5].add(word)

    stats[6] = explorer.get_all_anagrams(letters)

    guessed_words = set()

    for word in stats[6]:
       if word in stats[5]:
          guessed_words.add(word)

    for word in guessed_words: 
       stats[6].remove(word)
       
    stats[6] = list(filter(lambda item: item is not None, stats[6]))
    stats[6] =  set(stats[6])

    if len(explorer.get_all_anagrams(letters)) == 0:
       stats[4] = 0

    else: 
        stats[4] = int((len(stats[5]) / len(explorer.get_all_anagrams(letters))) * 100)

    for pair in stats[0]: 
       if len(pair[0]) == 3:
            stats[2] += 1
        
       elif len(pair[0]) == 4:
            stats[2] += 2

       elif len(pair[0]) == 5:
            stats[2] += 3    

       elif len(pair[0]) == 6:
            stats[2] += 3

       elif len(pair[0]) == 7:
            stats[2] += 5

    stats[5] = list(stats[5])
    stats[6] = list(stats[6])

    return stats

  
  