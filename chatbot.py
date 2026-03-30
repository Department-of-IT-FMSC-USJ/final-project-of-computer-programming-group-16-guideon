import streamlit as st
import json
from storage import load_json

def chatbot_response(user_input):
    """Core logic for keyword detection and recommendations."""
    user_input = user_input.lower()
    
    # 1. FAQ responses
    if "how to book" in user_input or "booking" in user_input:
        return "To book a jewelry set, navigate to the 'Browse Jewelry' page, select a set, and fill out the reservation form."
    
    if "price" in user_input or "cost" in user_input:
        return "Our bridal collections cater to various budgets. Use the price slider in the gallery to find options within your range."
    
    # 2. Smart Recommendations
    if "gold" in user_input or "temple" in user_input or "modern" in user_input:
        jewelry_data = load_json('jewelry.json')
        matching_items = []
        
        style_filter = None
        if "gold" in user_input: style_filter = "Gold"
        elif "temple" in user_input: style_filter = "Temple"
        elif "modern" in user_input: style_filter = "Modern"
        
        price_limit = float('inf')
        if "under" in user_input or "below" in user_input:
            words = user_input.split()
            for word in words:
                if word.isdigit():
                    price_limit = int(word)
                    break
        
        for item in jewelry_data:
            if style_filter and item.get('style') == style_filter:
                if item.get('price', 0) <= price_limit:
                    matching_items.append(item.get('name'))
        
        if matching_items:
            return f"I recommend checking out these {style_filter} sets: {', '.join(matching_items[:3])}. You can find them in our gallery."
        else:
            return f"I couldn't find any {style_filter} items under LKR {price_limit} specifically, but we have more styles in the catalog!"
            
    return "I'm here to help! Ask me about 'how to book', or specific styles like 'Temple' or 'Gold' or 'Modern'."

def render_chatbot_ui():
    """Integrated Chatbot Interface."""
    st.title("💡 Personal Assistant")
    st.write("Need help finding the perfect jewelry? Just ask!")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your Bridora assistant. How can I help you today?"}]
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        response = chatbot_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
