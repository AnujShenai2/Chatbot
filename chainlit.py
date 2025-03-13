import chainlit as cl

# Chainlit configuration
cl.configure(
    # General settings
    title="Car Parts Chatbot",
    description="A chatbot for finding car parts information",
    # Theme settings
    theme_name="default",
    # Page settings
    page_title="Car Parts Chatbot",
    # UI settings
    hide_cot=False,
    show_thinking=True,
    avatar="🚗",
)