'''
from langchain_openai import ChatOpenAI
from config import config
from logger import get_logger

logger = get_logger(__name__)

def get_llm():
    logger.info("Initializing LLM")

    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=config.OPENAI_API_KEY
    )
'''

from langchain_google_genai import ChatGoogleGenerativeAI
from config import config
from logger import get_logger

logger = get_logger(__name__)

def get_llm():
    logger.info("Initializing Gemini LLM")

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",   # or "gemini-1.5-pro"
        temperature=0,
        google_api_key=config.GOOGLE_API_KEY
    )