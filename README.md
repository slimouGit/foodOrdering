# Voice Based Food Order Processing System

This Flask application demonstrates a simple voice order processing system. It utilizes the OpenAI API to convert text to speech and speech to text, simulating a customer ordering system. The app showcases how to integrate OpenAI's powerful models into a web application for practical use cases.

## Features

- Flask web server setup for handling voice order requests.
- Integration with OpenAI API for text-to-speech and speech-to-text functionalities.
- Simple UI for initiating voice orders and displaying the order text.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.8 or above installed on your system.
- An active OpenAI API key. You can obtain one by signing up at [OpenAI](https://openai.com/api/).

## Installation

1. **Clone the repository**

   Start by cloning the project repository to your local machine:

   ```sh
   git clone https://yourrepositorylink.git
   ```

2. **Create and activate a Conda environment**

   Replace `foodordering` with your preferred environment name:

   ```sh
   conda create --name foodordering python=3.10
   conda activate foodordering
   ```

3. **Install dependencies**

   Navigate to the project directory and install the required dependencies:

   ```sh
   pip install -r requirements.txt
   ```

4. **Configure API Key**

   Ensure your `config.py` contains the OpenAI API key:

   ```python
   API_KEY = 'your_openai_api_key'
   ```

## Running the Application

With the setup complete, you can run the Flask application using:

```sh
python app.py
```

Navigate to `http://127.0.0.1:5000/` in your web browser to view the application.

## Usage

- Access the main page to initiate a voice order.
- Follow the on-screen instructions to complete your order.
- Review the converted text of your order before finalizing.

## Contributing

Contributions to enhance this project are welcome. Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`
