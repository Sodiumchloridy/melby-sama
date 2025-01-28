<div align="center">
  <div>
    <h1 style="display: inline-block;">Nero-sama</h1>
  </div>
  <p align='center'>the Neuro-sama clone from Temu</p>

  [![forthebadge](https://forthebadge.com/images/featured/featured-built-with-love.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/featured/featured-powered-by-electricity.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/featured/featured-gluten-free.svg)](https://forthebadge.com)
  
  [![forthebadge](https://forthebadge.com/images/badges/ctrl-c-ctrl-v.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/works-on-my-machine.svg)](https://forthebadge.com)
</div>


## 1. Install Dependencies (Recommended)
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

For the YouTube API's `client_secret.json`, you can get it at [https://console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials). Create a `OAuth 2.0 client ID` following this [YouTube example](https://www.youtube.com/watch?v=Q49gGXCCY_4), adding `Youtube Data APIv3` scopes below under `OAuth consent screen`:  
- `https://www.googleapis.com/auth/youtube.force-ssl` 
- `https://www.googleapis.com/auth/youtube.readonly`  

After that, download the `client_secret.json`. Then, place it inside the [/src/utils](/src/utils) folder.

### 3. Run the project
At the root of the project, run:
```bash
poetry run python src/main.py
```