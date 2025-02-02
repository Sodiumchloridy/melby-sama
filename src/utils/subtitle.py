def generate_subtitle(filename, text):
    """
    Generate subtitle file from text.
    filename: str - name of the file to write to (e.g. output.txt)
    text: str - text to write to the
    """
    with open(filename, "w", encoding="utf-8") as outfile:
        try:
            words = text.split()
            lines = [words[i:i+10] for i in range(0, len(words), 10)]
            for line in lines:
                outfile.write(" ".join(line) + "\n")
        except:
            print(f"Error writing to {filename}")