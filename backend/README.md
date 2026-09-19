# Installation

We are using the [uv package manager](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer).

Just run `uv add` to install everything needed :)

To run the server, run `uv run --env-file .env backend` if you want to use ENV variables.
Otherwise, `uv run backend` should work.

# Test

To run the test client, run `uv run src/backend/test_client.py`.

# Routes we need

We'll need to send lots of data over a socket UDP connection.

We should format the data as json, which we encode with `json.dumps(data).encode('utf-8')`.

- Recieve audio and track:
  - Current number of speakers at a given time
  - Segments of audio

- Audio playback route
