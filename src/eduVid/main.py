import os
import sys
import whisper
import zipfile

sys.path.append(os.path.join(os.path.dirname(__file__), 'processes'))
from slides_extractor import SlideExtractor
from slides_ocr import SlideOCR
from summarization import TextSummarizer
from keyword_extractor import KeywordExtractor
from speech2text import VideoScript

# define function which wipes folder content
def wipe_folder(folder_path):
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            os.remove(file_path)
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            os.rmdir(dir_path)

def zip_output_files(main_directory, output_path, zip_path):
    # Name of the zip file to be created
    zip_filename = "output_files.zip"

    #  path of the zip file
    zip_file_path = os.path.join(zip_path, zip_filename)

    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for folder_path, _, file_names in os.walk(output_path):
            for file_name in file_names:
                file_path = os.path.join(folder_path, file_name)
                zipf.write(file_path, os.path.relpath(file_path, output_path))

# Usage example:
if __name__ == "__main__":

    # ---------------------------------------------------------------------------------------------
    # ---PATHS-------------------------------------------------------------------------------------

        # define main dir path
    main_directory = os.path.dirname(os.path.abspath(__file__))
        # define folder in which output files should be saved
    output_path = os.path.join(main_directory, "output")
        # path were zip dir will land
    zip_path = os.path.join(main_directory, "zipf")

    # TODO: implement functionality to enable user to upload his mp4 file

        # path for video with presentation    # TODO : VVVVVVVVVVVVVVVV
    video_path = os.path.join(main_directory, "input", "dateisysteme.mp4")
        # folder where slides are extracted and saved
    slides_folder = os.path.join(main_directory, "output", "slides")

    # TODO: install Tesseract on server and link it

        # path for tesseract
    tesseract_path = '/tesseract'
        # set where OCR txt file should be saved
    ocr_file = os.path.join(main_directory, "output", 'OCR_output.txt')
        # set where summary txt file should be saved
    summary_file = os.path.join(main_directory, "output", "summary.txt")
        # set where keywords should be saved
    keywords_file = os.path.join(main_directory, "output", 'keywords.txt')

    # ---------------------------------------------------------------------------------------------

    # clean output folder before starting
    wipe_folder(output_path)

    # ---------------------------------------------------------------------------------------------
    # ---SPEECH2TEXT-------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------

    # whisper settings
    model = whisper.load_model("base")
    fp16 = False

    # execute s2t
    transcriber = VideoScript(model)
    transcriber.transcribe_video(video_path, output_path)

    # ---------------------------------------------------------------------------------------------
    # ---SLIDE EXTRACTOR---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------

    # execute Slide extractor
    slide_extractor_ = SlideExtractor(video_path, slides_folder)
    slide_extractor_.extract_slides_from_video()


    # ---------------------------------------------------------------------------------------------
    # ---OCR---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    
    # execute OCR
    slide_ocr_ = SlideOCR(tesseract_path, slides_folder, ocr_file)
    slide_ocr_.ocr_text_from_slides()

    # ---------------------------------------------------------------------------------------------
    # ---SUMMARIZER--------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------

    # execute summarizer
    summarizer = TextSummarizer()
    summarizer.summarize_file(ocr_file, summary_file)

    # ---------------------------------------------------------------------------------------------
    # ---KEYWORD EXTRACTOR ------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------

    # execute keyword extractor
    keyword_extractor = KeywordExtractor()
    extracted_keywords = keyword_extractor.extract_keywords(summary_file)
    keyword_extractor.save_keywords(extracted_keywords, keywords_file)

    # zip results
    wipe_folder(zip_path)
    zip_output_files(main_directory, output_path, zip_path)
