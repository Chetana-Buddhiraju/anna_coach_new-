# Anna AI Coach - Conversational AI for Entrepreneurs

Anna is an AI-powered conversational coach designed to support first-time entrepreneurs by answering business-related questions, providing motivational guidance, and helping users take actionable steps forward in their entrepreneurial journey.

This repository contains both a deployment-ready version (`src/main.py`) and local development scripts (`local_dev/app.py` and `local_dev/simple_app.py`) for testing and experimentation.

## Features

- **Conversational AI Interface**: Chat naturally with Anna, an AI coach specialized in entrepreneurship.

- **Knowledge Base Integration**: Uses a curated Markdown-based knowledge base (`knowledge_base.md`) covering essential entrepreneurship topics.

- **Goal-Oriented Coaching**: Asks follow-up questions and provides actionable advice to help users move forward.

- **Interaction Logging**: Records conversations with basic reasoning analysis for transparency.

- **Responsive Web Interface**: Modern, mobile-friendly chat interface with quick suggestion buttons.

- **Real-time Responses**: Powered by OpenAI’s GPT-4o or configured compatible model for intelligent, contextual answers.

## What Anna Can Help With

- **Idea Validation**: Steps to test and prove business idea viability.

- **Target Audience**: Defining and understanding your ideal customers.

- **MVP Planning**: Scoping your Minimum Viable Product effectively.

- **Funding Options**: Understanding different startup funding sources.

- **Marketing Strategy**: Basic marketing concepts and digital strategies.

- **Business Model**: Using frameworks like Business Model Canvas.

- **Team Building**: Co-founder selection and hiring strategies.

- **Financial Management**: Budgeting, cash flow, and pricing basics.

- **Sales Strategy**: Lead generation and conversion techniques.

- **Entrepreneurial Mindset**: Building resilience and managing stress.

## Technology Stack

- **Backend**: Flask (Python)

- **Frontend**: HTML, CSS, JavaScript

- **AI Model**: OpenAI GPT / gpt-4

- **Knowledge Base**: Markdown-based curated content (`knowledge_base.md`)

- **Deployment**: Flask web application

## Project Structure

```
local_dev/
├── app.py             # Light Flask application for local development
├── simple_app.py      # Simplified version for testing
├── src/               # Deployment-ready source code
│ ├── main.py          # Entry point for deployment
│ ├── templates/
│ │ └── index.html     # Web interface template
│ └── static/
│ └── style.css        # Styling for the web interface
├── .gitignore         # Git ignore rules
├── Procfile           # For deployment on platforms like Render
├── README.md          # Project documentation
├── knowledge_base.md  # Curated entrepreneurship content
└── requirements.txt   # Python dependencies
└── write_up.pdf       # Architecture, design, improvemnt ideas 
```

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

1. Clone the repository:

```bash
git clone <https://github.com/Chetana-Buddhiraju/anna_coach_new-.git>
cd anna-ai-coach
```
2. (Optional but recommended) Create and activate a virtual environment:

```bash
python -m venv venv
# On macOS/Linux
source venv/bin/activate
# On Windows
venv\Scripts\activate
```
3. Install dependencies:

```bash
pip install -r requirements.txt
```
4. Set up your OpenAI API key:
   
```bash
export OPENAI_API_KEY="your-api-key-here"
# On Windows Command Prompt
set OPENAI_API_KEY="your-api-key-here"
```
5. Run the application for local development:

```bash
python app.py
```
6. Open your browser and navigate to http://localhost:5000

## Usage

1. **Start a Conversation**: Open the web interface and begin chatting with Anna.

2. **Use Quick Suggestions**: Click on the suggested topics for common entrepreneurship questions.

3. **Ask Follow-up Questions**: Anna will guide you with relevant follow-up questions.

4. **Get Actionable Advice**: Receive specific steps you can take to move forward.

5. **Reset Conversation**: Use the "New Conversation" button to start fresh.

### Example Interactions

**User**: "How do I validate my business idea?"

**Anna**: "Great question! Idea validation is crucial before investing time and resources. Here are the key steps: First, identify your core assumptions about your idea, target customers, and the problem you're solving. Then, conduct customer interviews with potential users to understand their real needs and pain points. I'm asking about your specific idea because the validation approach can vary depending on your target market. What type of business idea are you looking to validate?"

## Architecture

Anna follows a modular architecture with the following components:

1. **User Interface**: Web-based chat interface located in `src/templates` and styled with `src/static/style.css`.

2. **Backend / API Gateway**: Flask application (`app.py` for local dev, `src/main.py` for deployment) handling HTTP requests and responses.

3. **AI Engine**: OpenAI GPT (currently using `gpt-4`) integrated via the OpenAI Python SDK, with custom system prompts.

4. **Knowledge Base**: Markdown file (`knowledge_base.md`) providing curated entrepreneurship content for contextual responses.

5. **Logging System**: Interaction tracking in `interaction_log.txt` with reasoning analysis for transparency.

### Prompt Engineering Strategy

- Defines Anna's personality as a supportive, goal-oriented coach.
- Instructs Anna to provide actionable advice and ask goal-oriented follow-up questions.
- Incorporates knowledge base content for informed responses.
- Explains reasoning behind follow-up questions for transparency.
- Keeps responses concise, encouraging, and actionable.

## Knowledge Base

The knowledge base (`knowledge_base.md`) covers key entrepreneurship topics to guide Anna's responses. Current topics include:

1. Idea Validation
2. Defining Target Audience
3. MVP Scoping
4. Business Model Canvas
5. Funding Options
6. Marketing Fundamentals
7. Legal Considerations
8. Team Building
9. Financial Management
10. Sales Strategy
11. Product Development
12. Networking & Mentorship
13. Time Management
14. Resilience & Mindset

You can expand the knowledge base by adding new sections in the same Markdown format. Anna will automatically incorporate new content after a restart.

## Development

### Running in Development Mode

To run the application locally for development:

```bash
python app.py
```
This starts the Flask server. Open your browser and navigate to:

http://localhost:5000

### Testing Endpoints

- `/health` - Health check endpoint to verify the server is running.  
- `/reset` - Reset the chat history.  
- `/chat` - Main chat API endpoint to send and receive messages.  

### Adding or Updating Knowledge

1. Edit `knowledge_base.md` to add new topics or update existing content.  
2. Restart the Flask application to load the updated knowledge base.

## Deployment

The application is structured to support deployment on various platforms. The `src/` directory contains deployment-ready code.

### Local Deployment

```bash
python src/main.py
```

## Production Considerations

- Set `debug=False` in production.
- Use a production WSGI server like Gunicorn.
- Implement proper error handling and logging.
- Set up environment variables for API keys.
- Consider rate limiting for the OpenAI API to avoid excessive usage.
  
### Deployment on Render

The Anna AI Coach is deployed on [Render](https://render.com), a cloud platform for hosting web applications. This allows the app to be publicly accessible via a stable URL, without needing your local machine to be running.

### How It Works

- The deployment uses the `src/main.py` file as the entry point.
- A `Procfile` specifies the command for starting the Flask app with Gunicorn:
- The `requirements.txt` file lists all Python dependencies, which Render installs in a virtual environment during build.
- Environment variables, such as `OPENAI_API_KEY`, are configured in the Render dashboard to keep sensitive information secure.

### Accessing the App

Once deployed, Anna is accessible via a Render-provided URL (e.g., `https://anna-ai-coach.onrender.com`). Users can interact with the chat interface directly through their web browser.

### Constraints of Free Deployment

- **Instance Sleep**: Free instances spin down after periods of inactivity. If Anna is not used for ~25 minutes, the first request after inactivity may take up to 50 seconds to respond while the instance starts.
- **Compute Limitations**: Free Render instances have limited memory and CPU, which can affect response speed for complex queries.
- **API Rate Limits**: OpenAI API usage is subject to rate limits; extensive usage may be throttled or require paid API access.
- **No Persistent Local Storage**: Logs and uploaded files are not persisted beyond the instance's lifecycle unless explicitly stored externally.

This deployment ensures that Anna is available publicly for demonstration and testing without requiring a local setup, while highlighting considerations for performance and uptime.

## Future Improvements

- **Personalization**: Tailored advice based on the user's business stage and industry.
- **External Integrations**: Connect with CRM, project management, or market research APIs.
- **Voice Interface**: Add speech-to-text and text-to-speech capabilities for a more interactive experience.
- **Multi-language Support**: Expand to support multiple languages.
- **Enhanced Knowledge Base**: Integrate external sources or dynamic retrieval to keep content up-to-date.
