from watson_nlu import get_full_transcript
from happytransformer import HappyTextToText, TTSettings


# https://www.vennify.ai/summarize-text-with-transformer-models/

def summarize_text(transcript_filename):
    happy_tt = HappyTextToText("DISTILBART", "sshleifer/distilbart-cnn-12-6")
    top_k_sampling_settings = TTSettings(do_sample=True, top_k=50,
                                         temperature=0.7, max_length=50)
    summary = happy_tt.generate_text(get_full_transcript(transcript_filename),
                                     args=top_k_sampling_settings).text

    return summary.replace(" .", ".")


print(summarize_text("1.json"))
