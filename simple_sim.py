import io
import pandas as pd
import numpy as np
import re


######################
## Helper functions ##
######################

# Fixing random seed for reproduceability
rng = np.random.default_rng(5321463312)

# Strips out the parenthetical in some block size entries
# Example: clean_block_size('120(r38243)') returns '120'
def clean_block_size(size_string):
  return re.sub(r"\([^()]*\)", "", size_string)

# CDF of Age-Sex distribution from Ruggles (http://users.hist.umn.edu/~ruggles/censim.html)
# A pair Age-Sex is represented by a number X fom 0 to 191
# X = 0,...,95 represents an X year old male.
# X = 96,...,192 represents an X-96 year old female.
AGE_SEX = [0.00,0.006338392,0.012912896,0.019739577,0.026636939,0.033374605,0.040123997,0.046849289,0.05351731,0.060238034,0.067117257,0.074013323,0.080860639,0.087675626,0.094488119,0.101353801,0.108403345,0.115546147,0.122869863,0.130283825,0.137848543,0.145356704,0.152600053,0.159670134,0.166606173,0.173587238,0.180563445,0.187349635,0.194298501,0.201148473,0.207988014,0.214994378,0.221445497,0.227920004,0.234212561,0.240423326,0.246824495,0.252953144,0.259315119,0.265941094,0.272954131,0.280057447,0.286675907,0.293262622,0.299871754,0.306635787,0.313879331,0.321092879,0.328326446,0.335571415,0.342898727,0.350345147,0.357445255,0.364608109,0.371518979,0.378310481,0.385015819,0.391358876,0.397542075,0.403501407,0.40916726,0.414840402,0.420266484,0.425829102,0.431261177,0.435367318,0.439489688,0.443517633,0.447545286,0.451085914,0.454318649,0.457394182,0.460311022,0.463087763,0.46565081,0.468089565,0.470425862,0.47253136,0.47457379,0.476524159,0.478400835,0.480169027,0.481759674,0.483245499,0.484611275,0.485810748,0.486897785,0.48784861,0.488662446,0.489357628,0.489866162,0.490076099,0.490123749,0.49036663,0.491082413,0.491590106,0.491605168,0.497702072,0.504005902,0.510547105,0.517132719,0.523615972,0.530073862,0.536526244,0.542929746,0.549363406,0.555926442,0.562529192,0.569062233,0.575562945,0.582066346,0.588571205,0.595264234,0.602076695,0.608984196,0.616014174,0.623245571,0.630431747,0.637369859,0.644130718,0.65081756,0.657571357,0.664365484,0.671027901,0.677863263,0.684624738,0.691470369,0.69837625,0.704794005,0.711247003,0.717543382,0.723782329,0.730191629,0.736389501,0.742820958,0.749540808,0.7566564,0.763744265,0.770426474,0.777057956,0.783771489,0.790648315,0.798000763,0.805416053,0.812847249,0.820301961,0.827875069,0.835522065,0.842899585,0.850359513,0.857616565,0.864715215,0.871778202,0.878537215,0.885129469,0.891482924,0.897588672,0.903656584,0.909514203,0.915493846,0.92134288,0.925835079,0.930395367,0.934887694,0.939421355,0.943436505,0.9471585,0.950697444,0.954096969,0.957372754,0.960449744,0.963446368,0.966352097,0.969015788,0.971673615,0.974261021,0.976823258,0.979301791,0.98163987,0.983897128,0.986020378,0.988003755,0.989867312,0.991561519,0.993056446,0.994413088,0.99544334,0.995911027,0.996014101,0.996634876,0.998513042,0.999948884,1.000000000]

# Samples an index in 1,...,len(AGE_SEX) according to the AGE_SEX CDF
def sample_age_sex():
  r = rng.random()
  sample = np.argmax([(a_s if a_s <= r else 0) for a_s in AGE_SEX])
  return sample

# Sample a block size from the list
def sample_block_size(block_size_list):
  return rng.choice(block_size_list)

# Sample a block's worth of Age-Sex values
def sample_block(block_size):
  block = []
  for i in range(block_size):
    block.append(sample_age_sex())
  return block

#################################
## Reading in the Alabama data ##
#################################

# df = pd.read_csv(io.BytesIO('Alabama-non-empty-blocks-2010.csv'), header = None)
df = pd.read_csv('Alabama-non-empty-blocks-2010.csv', header = None)
arr = df.to_numpy().flatten()
arr = [(x if len(x)<5 else clean_block_size(x)) for x in arr]
arr = [int(x) for x in arr]

AL_BLOCKS_NON_EMPTY_2010 = arr
AL_BLOCKS_1_TO_9_2010 = list(filter(lambda x: (x>=1 and x<=9), AL_BLOCKS_NON_EMPTY_2010))
AL_BLOCKS_10_TO_49_2010 = list(filter(lambda x: (x>=10 and x<=49), AL_BLOCKS_NON_EMPTY_2010))

## Calculate fraction of AL population living in small blocks.
percent_1_9 = 100*sum(AL_BLOCKS_1_TO_9_2010)/sum(AL_BLOCKS_NON_EMPTY_2010)
percent_10_49 = 100*sum(AL_BLOCKS_10_TO_49_2010)/sum(AL_BLOCKS_NON_EMPTY_2010)

print(f"In 2010, {percent_1_9:.1f}% of AL's population lived in blocks with 1 to 9 people.")
print(f"In 2010, {percent_10_49:.1f}% of AL's population lived in blocks with 10 to 49 people.")


##################################
## Main simple simulation logic ##
##################################
NUM_BLOCKS = 1000

def count_matches(sampled_block, guessed_block):
  num_matches = 0
  for value in set(sampled_block + guessed_block):
    num_value_sampled = sum([sample==value for sample in sampled_block])
    num_value_guessed = sum([guess==value for guess in guessed_block])
    num_value_match = np.min([num_value_sampled,num_value_guessed])
    num_matches += num_value_match
  return num_matches

def run_simple_simulation(block_size_list):
  # Sampling blocks and guesses
  sampled_blocks = []
  guessed_blocks = []
  for block in range(NUM_BLOCKS):
    size = sample_block_size(block_size_list)
    sampled_blocks.append(sample_block(size))
    guessed_blocks.append(sample_block(size))
  # Counting matches
  num_matches = 0
  for block in range(NUM_BLOCKS):
    num_matches += count_matches(sampled_blocks[block],guessed_blocks[block])
  # Computing the fraction of correct guesses
  num_guesses = sum([len(g) for g in guessed_blocks])
  match_rate = num_matches / num_guesses
  return match_rate

print(f'Starting simple simulation for blocks with population 1 to 9. This may take a few seconds.')
match_rate_1_9 = 100*run_simple_simulation(AL_BLOCKS_1_TO_9_2010)
print(f'Starting simple simulation for blocks with population 10 to 49. This may take a few seconds.')
match_rate_10_49 = 100*run_simple_simulation(AL_BLOCKS_10_TO_49_2010)

print(f'The match rate for blocks with 1 to 9 people is {match_rate_1_9:.1f}')
print(f'The match rate for blocks with 10 to 49 people is {match_rate_10_49:.1f}')
