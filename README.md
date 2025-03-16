![banner](https://github.com/user-attachments/assets/18014e27-a881-4ea0-924e-a7b0a3a944aa)
> This project is built for the [Google Cloud x MLB™ Hackathon – Building with Gemini Models](https://next2025challenge.devpost.com/)

> This project may also serve as my backup plan to become a Twitch streamer if the CS job market goes south.
> Inspired by the AI VTuber [Neuro-sama](https://www.youtube.com/@Neurosama).

<div align="center">
  <div>
    <h1 style="display: inline-block;">Melby-sama</h1>
  </div>
  <p align='center'>
  Melby-sama (MLB... Melby... get it?), an AI MLB VTuber and streamer powered by Google's Multimodal AI — the segue to our sponsor: the Google Cloud x MLB Hackathon, powered by Gemini!
  </p>
  
  [![forthebadge](https://forthebadge.com/images/badges/ctrl-c-ctrl-v.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/works-on-my-machine.svg)](https://forthebadge.com)
</div>

### 👀 Demo

| [![](https://img.youtube.com/vi/Zxxj-QVYgow/maxresdefault.jpg)](https://www.youtube.com/watch?v=Zxxj-QVYgow) | ![](https://github.com/user-attachments/assets/1dd93eed-c3aa-4c42-9ee9-ac6e8c5dc1d9) |
|:---:|:---:|
| [Video Demo](https://www.youtube.com/watch?v=Zxxj-QVYgow) | Melby-sama chilling |
| ![](https://github.com/user-attachments/assets/9314104e-375f-49a0-b862-aa9a1bbbf8f5) | [![](https://img.youtube.com/vi/L639zifZP0U/maxresdefault.jpg)](https://youtube.com/live/L639zifZP0U) |
| Melby-sama reacts to YouTube live chat | [Live Stream Demo](https://youtube.com/live/L639zifZP0U) |



## 1. Setup

### 1. Install Poetry

You can install Poetry by following the official [installation guide](https://python-poetry.org/docs/#installation).

```bash
pip install poetry
poetry config virtualenvs.in-project true # to create the virtual environment in the project directory
```

### 2. Setup the environment variables

Create a `.env` file at the root of the project with the following variables:

```env
GEMINI_API_KEY=
SPEECH_KEY=
SPEECH_REGION=
```

You can get your own `GEMINI_API_KEY` at [Google AI Studio](https://aistudio.google.com/app/apikey).

You can get the `SPEECH_KEY` and `SPEECH_REGION` by following the steps below:

1. Sign up for an Azure free account at [https://azure.microsoft.com/free/cognitive-services](https://azure.microsoft.com/free/cognitive-services).
2. [Create a Speech Services resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices) in the Azure Portal.
3. Get the `SPEECH_KEY` and `SPEECH_REGION` from the resource.

### 3. Run the project
At the root of the project, run:

```bash
poetry run python src/main.py
```

### 4. Set up VTube Studio
1. Downlaod and launch [VTube Studio](https://store.steampowered.com/app/1325860/VTube_Studio/).
2. Optional (Advanced) : Port the model's output audio into microphone input of Vtube Studio via [Voicemeeter Banana](https://vb-audio.com/Voicemeeter/banana.htm) and [VB Cable](https://vb-audio.com/Cable/).

### 5. Set up OBS Studio
1. Add VTube Studio as Game Capture to source.
2. Add `src/temp/subtitles.txt` as Text to source.
3. If you previously set up Voicemeeter and VB Cable in Step 4.2, you'll need to configure it here too.
