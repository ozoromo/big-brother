# Educational Video Training

## Motivation & Overview

The concept of the project is to greatly facilitate the learning process by effectively extracting information to be later presented in an optimal and accessible form to the student. The solution will make learning new material less overwhelming and more effective - students will be able to benefit more.

- Step 1: Students will know in advance what content the selected recording contains - they will be able to prepare better and it will not be a surprise to them.
- Step 2: Then they can watch the videos attentively, purposefully.
- Step 3: After the studies have had a look at the relevant section, they can try to get a few steps further in the task. Back-and-forth between theory and practice, so learning is efficient and stress-free.

## Ideas:
- *A way to produce tutorial videos and lecture videos.*
- *Take recordings autoregressively guess what is said afterwards.*
- *Identify segments in audio and group them together or index them with keywords so that you can access relevant segments by demand.*
- *Video to text but from text to video: if we could get to relevant sections using natural language (or diagrams).*
- *Remember topic changes from sound and image.*

## TODO:
- Hyperlink to the video at each slide change. Train the **visual** model to notice that there was a slide change (later more advanced topic changes).
- Indexing - create a list of key time points each with a title and people can click on them to get to the segments.

# Planned development
- Script extraction from video (using the s2t algorithm)
- Script summarization using AI
- Extraction of keywords from the received notes, which will point to particular topics
- Recognizing the change of presentation slides and recognizing the content on them using OCR
- If the keywords from the OCR and the script overlap, it can be assumed that the topic has changed
- Sections between topic changes will be indexed and described by keywords

### Subteam members

- **miloSK1 (Milosz)**
- maxworm (Max)
