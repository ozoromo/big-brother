from moviepy.video.io.VideoFileClip import VideoFileClip
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
from faster_whisper import WhisperModel


class HelperFN:
    """
    This class contains helper functions .
    """

    def combine_sentences(self, sentences, value, limit):
        """
        Combines separate sentences into one array element within the token limit.

        Arguments:
        sentences - array with separate sentences to be merged into element.
        value - array with token values, which are summed up until limit is reached.
        limit - token limit setting.

        Return:
        Returns a list which elements are sets of sentences within the token limit.
        """
        result = []
        current_sentence = ""
        temp_sum = 0

        for sent, val in zip(sentences, value):
            temp_sum += val
            if temp_sum <= limit:
                current_sentence += sent
            else:
                result.append(current_sentence)
                current_sentence = sent
                temp_sum = 0

        if current_sentence:
            result.append(current_sentence)

        return result

    def count_tokens(self, chunks, tokenizer):
        """
        Counts how many tokens are used for each sentence. values are stored in array.

        Arguments:
        chunks - array with separate sentences. Each element of this array will corespond to returned array elem.
        tokenizer - hugging face model param.

        Return:
        Returns an array which elements are number of tokens used for each sentence. Returned array lenght = lenght of chunks param.
        """
        self.tokenizer = tokenizer
        sentence_token_counts = []
        for elem in chunks:
            sentences = elem.split(".")
            for sentence in sentences:
                sentence_tokens = self.tokenizer.encode(
                    sentence, add_special_tokens=False
                )
                sentence_token_count = len(sentence_tokens) + 1
                sentence_token_counts.append(sentence_token_count)
        return sentence_token_counts[::2]

    def merge_overlapping_segments(segments):
        """
        Merges overlapping segments (ex. array - [(13.0, 26.0), (26.0, 39.0)] can be merged into [(13.0, 39.0)]).

        Arguments:
        segments - array with timestamps (ex form of elem - (13.0, 26.0))

        Return:
        Returns an array which elements are ready timestamps (after merging)
        """
        if not segments:
            return []

        segments.sort(key=lambda x: x[0])
        merged_segments = [segments[0]]

        for segment in segments[1:]:
            if segment[0] <= merged_segments[-1][1]:
                merged_segments[-1] = (
                    merged_segments[-1][0],
                    max(merged_segments[-1][1], segment[1]),
                )
            else:
                merged_segments.append(segment)

        return merged_segments

    def find_matching_segments(tag_array, answer):
        """
        Searches for matching segments, if at least 2 words of param answer are overlapping one by one with text (3rd pos) from tag_array elem - append it to new list.

        Arguments:
        tag_array - array with which elements have such a form (timestamp when text starts, -||- ends, text).
        answer - list of words.

        Return:
        Returns a list with timestamps of segments (text) which correspond to given answer, so you can know when given answer is said.
        """
        matching_segments = []
        answer_words = answer.split()
        answer_pairs = [" ".join(pair) for pair in zip(answer_words, answer_words[1:])]

        for segment in tag_array:
            segment_words = segment[2].split()
            segment_pairs = [
                " ".join(pair) for pair in zip(segment_words, segment_words[1:])
            ]

            for pair in answer_pairs:
                if pair in segment_pairs:
                    matching_segments.append((segment[0], segment[1]))
                    break

        return matching_segments

    def extract_audio_from_mp4(self, input_file, output_file, start_time, end_time):
        """
        Extracts .wav file from .mp4

        Arguments:
        input_file - .mp4 file path
        output_file - path where .wav file will be saved
        """
        try:
            with VideoFileClip(input_file) as video_clip:
                with video_clip.subclip(start_time, end_time).audio as audio_clip:
                    audio_clip.write_audiofile(output_file, codec="pcm_s16le")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


class SpeechRecog:
    """
    This class performs speech recognition (s2t algorithm)
    """

    def __init__(self, audio_source):
        self.model = WhisperModel("base", compute_type="float32")
        self.segments, self.info = self.model.transcribe(audio_source)

    def transcribe(self):
        transcription_list = []
        tag_array = []
        for self.segment in self.segments:
            transcription_list.append(self.segment.text)
            tag_array.append([self.segment.start, self.segment.end, self.segment.text])
        script = "".join(transcription_list)

        return script, tag_array


class QAAlgo:
    """
    This class performs question answering algorithm
    """

    # define the maximum number of tokens per chunk (model limitations - 512)
    def __init__(self, model_name, max_tokens_per_chunk=512):
        # settings for hugging face model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_name)
        self.max_tokens_per_chunk = max_tokens_per_chunk

    def answer_question(self, context, question):
        """
        Answer given question using question answering algorithm.

        Arguments:
        context - string, here list with strings (due to model limitation) on which qa algo relays
        question

        Return:
        Returns answer for given question which bases on given context
        """
        # encode the full context to count the tokens
        context_tokens = self.tokenizer.encode(context, add_special_tokens=False)

        helper = HelperFN()
        start_idx = 0
        chunks = []

        # split entire context into separate sentences
        while start_idx < len(context_tokens):
            next_period_idx = (
                context_tokens[start_idx:].index(
                    self.tokenizer.convert_tokens_to_ids(".")
                )
                + start_idx
            )
            if next_period_idx - start_idx <= self.max_tokens_per_chunk:
                # if the next sentence fits within the chunk, include it
                end_idx = next_period_idx + 1
            else:
                # if the next sentence doesn't fit, use the max_tokens_per_chunk limit
                end_idx = start_idx + self.max_tokens_per_chunk

            chunk_tokens = context_tokens[start_idx:end_idx]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
            start_idx = end_idx

        tok_val_list = helper.count_tokens(chunks, self.tokenizer)
        ready_chunks = helper.combine_sentences(
            chunks, tok_val_list, self.max_tokens_per_chunk
        )

        final_answer_tokens = []
        for chunk in ready_chunks:
            encoding = self.tokenizer.encode_plus(
                question, chunk, max_length=512, truncation=True, return_tensors="pt"
            )
            input_ids, attention_mask = (
                encoding["input_ids"],
                encoding["attention_mask"],
            )
            start_scores, end_scores = self.model(
                input_ids, attention_mask=attention_mask, return_dict=False
            )
            # determine the answer tokens based on the highest start and end scores
            ans_tokens = input_ids[
                0, torch.argmax(start_scores) : torch.argmax(end_scores) + 1
            ]
            answer_tokens = self.tokenizer.convert_ids_to_tokens(
                ans_tokens, skip_special_tokens=True
            )
            final_answer_tokens += answer_tokens

        answer = self.tokenizer.convert_tokens_to_string(final_answer_tokens)
        return answer
