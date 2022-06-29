from watson_nlu import get_full_transcript
from happytransformer import HappyTextToText, TTSettings


def summarize_text(transcript_filename):
    happy_t5 = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
    input = "summarize: " + get_full_transcript(transcript_filename)
    summary = happy_t5.generate_text(input).text

    beam_settings = TTSettings(num_beams=5, min_length=1, max_length=100)
    result = happy_t5.generate_text("grammar: " + summary,
                                    args=beam_settings).text
    return result
