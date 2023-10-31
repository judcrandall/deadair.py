#!/usr/bin/python

# Quick script for batch silence removal from mp3s. Useful for processing lots and lots of Broadcastify archives, for example.
# github.com/judcrandall/deadair.py/

import os
import sys
from pydub import AudioSegment, silence
import concurrent.futures

def process_file(file_path, silence_thresh, min_silence_len):
    print(f"Processing {file_path}...")
    audio = AudioSegment.from_mp3(file_path)
    non_silent_chunks = silence.detect_nonsilent(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    return [audio[start_i:end_i] for start_i, end_i in non_silent_chunks]

def remove_dead_noise(input_path, output_path, silence_thresh=-40, min_silence_len=5000): # You can adjust the silence threshold and minimum silence length (in milliseconds) to detect here.
    print("Working now-- this may take a while.")

    mp3_files = sorted([f for f in os.listdir(input_path) if f.endswith('.mp3')])
    audio_segments = []

    with concurrent.futures.ProcessPoolExecutor() as executor: # This is where we say "not today, Satan" to the Global Interpreter Lock.
        future_to_file = {executor.submit(process_file, os.path.join(input_path, mp3_file), silence_thresh, min_silence_len): mp3_file for mp3_file in mp3_files}
        for future in concurrent.futures.as_completed(future_to_file):
            mp3_file = future_to_file[future]
            try:
                data = future.result()
                audio_segments.extend(data)
            except Exception as exc:
                print(f"{mp3_file} generated an exception: {exc}")
            else:
                print(f"{mp3_file} processed successfully.")

    final_audio = sum(audio_segments, AudioSegment.empty())
    final_audio.export(output_path, format="mp3")
    print("Process completed. The output is saved in", output_path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python deadair.py <input_directory> <output_file>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_file = sys.argv[2]

    remove_dead_noise(input_directory, output_file)
