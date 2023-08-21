<a id="qa_algo_core"></a>

# qa\_algo\_core

<a id="qa_algo_core.HelperFN"></a>

## HelperFN Objects

```python
class HelperFN()
```

This class contains helper functions .

<a id="qa_algo_core.HelperFN.combine_sentences"></a>

#### combine\_sentences

```python
def combine_sentences(sentences, value, limit)
```

Combines separate sentences into one array element within the token limit.

**Arguments**:

  sentences - array with separate sentences to be merged into element.
  value - array with token values, which are summed up until limit is reached.
  limit - token limit setting.
  

**Returns**:

  Returns a list which elements are sets of sentences within the token limit.

<a id="qa_algo_core.HelperFN.count_tokens"></a>

#### count\_tokens

```python
def count_tokens(chunks, tokenizer)
```

Counts how many tokens are used for each sentence. values are stored in array.

**Arguments**:

  chunks - array with separate sentences. Each element of this array will corespond to returned array elem.
  tokenizer - hugging face model param.
  

**Returns**:

  Returns an array which elements are number of tokens used for each sentence. Returned array lenght = lenght of chunks param.

<a id="qa_algo_core.HelperFN.merge_overlapping_segments"></a>

#### merge\_overlapping\_segments

```python
def merge_overlapping_segments(segments)
```

Merges overlapping segments (ex. array - [(13.0, 26.0), (26.0, 39.0)] can be merged into [(13.0, 39.0)]).

**Arguments**:

  segments - array with timestamps (ex form of elem - (13.0, 26.0))
  

**Returns**:

  Returns an array which elements are ready timestamps (after merging)

<a id="qa_algo_core.HelperFN.find_matching_segments"></a>

#### find\_matching\_segments

```python
def find_matching_segments(tag_array, answer)
```

Searches for matching segments, if at least 2 words of param answer are overlapping one by one with text (3rd pos) from tag_array elem - append it to new list.

**Arguments**:

  tag_array - array with which elements have such a form (timestamp when text starts, -||- ends, text).
  answer - list of words.
  

**Returns**:

  Returns a list with timestamps of segments (text) which correspond to given answer, so you can know when given answer is said.

<a id="qa_algo_core.HelperFN.extract_audio_from_mp4"></a>

#### extract\_audio\_from\_mp4

```python
def extract_audio_from_mp4(input_file, output_file)
```

Extracts .wav file from .mp4

**Arguments**:

  input_file - .mp4 file path
  output_file - path where .wav file will be saved

<a id="qa_algo_core.SpeechRecog"></a>

## SpeechRecog Objects

```python
class SpeechRecog()
```

This class performs speech recognition (s2t algorithm)

<a id="qa_algo_core.SpeechRecog.__init__"></a>

#### \_\_init\_\_

```python
def __init__(audio_source)
```

<a id="qa_algo_core.SpeechRecog.transcribe"></a>

#### transcribe

```python
def transcribe()
```

<a id="qa_algo_core.QAAlgo"></a>

## QAAlgo Objects

```python
class QAAlgo()
```

This class performs question answering algorithm

<a id="qa_algo_core.QAAlgo.__init__"></a>

#### \_\_init\_\_

```python
def __init__(model_name, max_tokens_per_chunk=512)
```

<a id="qa_algo_core.QAAlgo.answer_question"></a>

#### answer\_question

```python
def answer_question(context, question)
```

Answer given question using question answering algorithm.

**Arguments**:

  context - string, here list with strings (due to model limitation) on which qa algo relays
  question
  

**Returns**:

  Returns answer for given question which bases on given context

