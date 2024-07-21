# Imports
from openai import OpenAI
import streamlit as st
from context import context
from PIL import Image, ImageEnhance
import base64
from cards import travel_packages_tab
from chatbot_test import run_chatbot
from home import home
from aboutme import test
from chatbot import run_bot


def show():
    run_bot()
