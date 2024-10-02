import tkinter as tk
from tkinter import scrolledtext, PhotoImage, Canvas
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import re
import ttkbootstrap as ttkb

import openai
from openai import OpenAI




# Modify the prompt towards your application, I have removed details regarding our unpublished research
conversation_history = [
            {"role": "system", "content": "You are a friendly chatbot at an exhibit called AI for wellbeing focused on posture and back health. This exhibit is part of a design festival exhibition in London. Engage visitors and ask a series of questions embedded in conversation to learn about their back health routine. "},
            {"role": "assistant", "content": "Engage visitors and ask a series of questions embedded in conversation to learn about their back health routine only in the past week. "},
           
        ]

client = OpenAI(api_key="Place_your_API_Key_here")



def chat_with_gpt2_assessment(prompt,ask_for_assessment=False):
    global conversation_history

    if ask_for_assessment:
        # Request final assessment or summary
        assessment_prompt = "Please provide an overall assessment or summary based on the entire conversation. Make sure to list you scores in a array similar to [100, 50,45,56,70] at the buttom of your response"
        conversation_history.append({"role": "user", "content": assessment_prompt})
        
        # Make the request again including the request for assessment
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            stream=True,
            )
        collected_chunks = []
        collected_messages = []
    else:
        conversation_history.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            stream=True,
            )
        collected_chunks = []
        collected_messages = []
# iterate through the stream of events
    for chunk in response:
        collected_chunks.append(chunk)  # save the event response
        if chunk.choices[0].delta.content is not None:
            chunk_message = chunk.choices[0].delta.content  # extract the message
        collected_messages.append(chunk_message)  # save the message
    return ''.join(map(str, collected_messages))


# Variables to keep track of user input
user_numbers = []
current_step = 0

# Function to draw pentagon graph inside the chat window using Canvas
def draw_pentagon_on_canvas0(scores):

    labels = ['Posture', 'Work Location', 'Work Tasks', 'Stress', 'Movement']

    right_frame.update()  # Ensure the frame size is updated before plotting
    canvas_width = right_frame.winfo_width()
    canvas_height = right_frame.winfo_height()

    # Define number of variables
    num_vars = len(scores)

    # Create a 2D plot with polar coordinates for the pentagon
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Ensure the plot is closed by adding the first value at the end
    scores += scores[:1]
    angles += angles[:1]

    # Set Seaborn style
    sns.set(style="whitegrid")

    # Create a new matplotlib figure
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))

    # Plot the data
    ax.fill(angles, scores, color='lightgrey', alpha=0.25)
    ax.plot(angles, scores, color='grey', linewidth=2)

    # Add labels to each axis
    ax.set_yticklabels([])  # Remove radial labels
    ax.set_xticks(angles[:-1])  # Set tick positions
    #ax.set_xticklabels(labels, fontsize=12)

    # Set the radial limits (based on scores)
    max_score = max(scores)
    ax.set_ylim(0, max_score)

    # Embed the plot into tkinter
    canvas = FigureCanvasTkAgg(fig, master=right_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

def draw_pentagon_on_canvas(scores):
    labels = ['Posture', 'Work Location', 'Work Tasks', 'Stress', 'Movement']
    label_colors = ['#F8E9CB', '#ADC1E0', '#CDD8D6', '#EBBAAD', '#B6A5A1'] # Background colors for labels
    canvas.delete("all")  # Clear the canvas before drawing

    width = 1300
    height = 800
    center_x = width // 2
    center_y = height // 2
    radius = 200

    # Compute the angle for each vertex of the pentagon
    angles = np.linspace(0, 2 * np.pi, 5, endpoint=False).tolist()

    # Coordinates for the vertices of the pentagon
    points = [
        (center_x + radius * np.cos(angle), center_y + radius * np.sin(angle))
        for angle in angles
    ]
    points.append(points[0])  # Close the pentagon

    # Normalize the scores between 0 and 1 (to fit inside the pentagon)
    max_score = max(scores)
    if max_score > 0:
        normalized_scores = [score / max_score for score in scores]
    else:
        normalized_scores = [0] * 5  # Avoid division by zero

    # Draw the outer pentagon (frame)
    for i in range(5):
        canvas.create_line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], fill="black", width=2)

    # Draw concentric pentagons (circular lines for scoring)
    num_levels = 5
    for level in range(1, num_levels + 1):
        level_radius = radius * (level / num_levels)
        level_points = [
            (center_x + level_radius * np.cos(angle), center_y + level_radius * np.sin(angle))
            for angle in angles
        ]
        level_points.append(level_points[0])  # Close the shape
        canvas.create_line(
            *[coord for point in level_points for coord in point],
            fill="gray", dash=(2, 2), width=1
        )

    # Draw the pentagon according to the user scores
    score_points = [
        (center_x + radius * normalized_scores[i] * np.cos(angles[i]), center_y + radius * normalized_scores[i] * np.sin(angles[i]))
        for i in range(5)
    ]
    score_points.append(score_points[0])  # Close the shape

    canvas.create_polygon(score_points, fill='grey', outline="lightgrey", width=2) #cyan  blue #E0FFFF

    # Display the scores and labels at each corner of the pentagon
    label_offset = 1.6 # Offset factor to move labels away from vertices
    for i, (x, y) in enumerate(points[:-1]):
        # Position the label away from the actual point by multiplying coordinates by label_offset
        label_x = center_x + label_offset * (x - center_x)
        label_y = center_y + label_offset * (y - center_y)

        # Create colorful background rectangles for labels 
        rect_width, rect_height = 200, 40 
        canvas.create_rectangle( label_x - rect_width // 2, label_y - rect_height // 2, label_x + rect_width // 2, label_y + rect_height // 2, fill=label_colors[i], outline=label_colors[i] )
        canvas.create_text(label_x, label_y, text=labels[i], font=("Calibri", 16, "bold"), fill="black")
        
        # Display the scores near the midpoints between the vertex and the center
        score_x = (x + score_points[i][0]) / 2
        score_y = (y + score_points[i][1]) / 2
        #canvas.create_text(score_x, score_y, text=str(scores[i]), font=("Arial", 10), fill="red")
def draw_pentagon_on_canvas3(scores):
    
    canvas.delete("all")  # Clear the canvas before drawing

    width = 800
    height = 800
    center_x = width // 2
    center_y = height // 2
    radius = 100

    # Compute the angle for each vertex of the pentagon
    angles = np.linspace(0, 2 * np.pi, 5, endpoint=False).tolist()

    # Coordinates for the vertices of the pentagon
    points = [
        (center_x + radius * np.cos(angle), center_y + radius * np.sin(angle))
        for angle in angles
    ]
    points.append(points[0])  # Close the pentagon

    # Normalize the scores between 0 and 1 (to fit inside the pentagon)
    max_score = max(scores)
    if max_score > 0:
        normalized_scores = [score / max_score for score in scores]
    else:
        normalized_scores = [0] * 5  # Avoid division by zero

    # Draw the outer pentagon (frame)
    for i in range(5):
        canvas.create_line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], fill="black", width=2)

    # Draw the pentagon according to the user scores
    score_points = [
        (center_x + radius * normalized_scores[i] * np.cos(angles[i]), center_y + radius * normalized_scores[i] * np.sin(angles[i]))
        for i in range(5)
    ]
    score_points.append(score_points[0])  # Close the shape

    canvas.create_polygon(score_points, fill="cyan", outline="blue", width=2)


def extract_scores(gpt_response):
    # First, try to find scores with the format "- Category: Score"
    scores = re.findall(r"- \w+(?: \w+)*: (\d+)", gpt_response)
    
    # If no scores were found in the first format, look for numbers inside brackets
    if not scores:
        scores_in_brackets = re.findall(r"\[(\d+(?:, \d+)*)\]", gpt_response)
        
        if scores_in_brackets:
            # Convert the found bracketed numbers into a list of integers
            scores = list(map(int, scores_in_brackets[0].split(", ")))
    
    # Convert the extracted scores to integers if they are not already
    if scores:
        scores = list(map(int, scores))
    
    # Return the extracted scores or None if no scores were found
    return scores if scores else [40, 60, 50, 30, 20]


# Function to handle sending messages
def send_message(event=None):
    global current_step, user_numbers
    
    user_message = input_box.get("1.0", tk.END).strip()
    if user_message:
        chat_box.config(state=tk.NORMAL)
        
        #Scoring user input
        #user_numbers.append(len(user_message))
        current_step =current_step + 1
        
        
        # Insert the user icon next to the user's message
        chat_box.image_create(tk.END, image=user_icon)  # Display user icon
        chat_box.insert(tk.END, f" User: {user_message}\n", "user")
        input_box.delete("1.0", tk.END)
        

        #Check if the user input contains the word "assessment" (case-insensitive)
        ask_for_assessment = "assessment" in user_message.lower() and current_step >=6
        # Bot response - 
        bot_response = chat_with_gpt2_assessment(user_message,ask_for_assessment)
        #bot_response = f"Bot: '{user_message}'"
        
        if ask_for_assessment:
            print(bot_response)
            summary_text.config(state=tk.NORMAL)
            user_numbers = extract_scores(bot_response)

            summary_text.insert("1.0", f" {bot_response}\n", "bot")
            chat_box.insert(tk.END, "Please refer to the graph and summary on the right side of screen\n", "bot")
            draw_pentagon_on_canvas(user_numbers)
        else: 
            # Insert the bot icon next to the bot's response
            chat_box.image_create(tk.END, image=bot_icon)  # Display bot icon
            chat_box.insert(tk.END, f" {bot_response}\n", "bot")
        
        chat_box.config(state=tk.DISABLED)
        chat_box.yview(tk.END)
        

def start_chat():
    ini_scores = [10,10,10,10,10]
    draw_pentagon_on_canvas(ini_scores)
    print("start!")

# Function to display user and bot messages
def display_message(message, is_user):
    chat_box.config(state=tk.NORMAL)

    if is_user:
        tag = "user"
        message = f"{message}\n"
        chat_box.insert(tk.END, message)
        # Align user message to the right
        chat_box.tag_add(tag, f"end-{len(message)}c", tk.END)
        chat_box.tag_configure(tag, justify="right", background="black", foreground="black")
    else:
        tag = "bot"
        message = f"{message}\n"
        chat_box.insert(tk.END, message, "hanging")
        # Align bot message to the left (default)
        chat_box.tag_add(tag, f"end-{len(message)}c", tk.END)
        chat_box.tag_configure(tag, justify="left", background="#F05E77", foreground="#F05E77")

    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)

def display_message1(message, is_user):
    chat_box.config(state=tk.NORMAL)
    
    if is_user:
        chat_box.insert(tk.END, f"User: {message}\n", "user")
    else:
        chat_box.insert(tk.END, f"Bot: {message}\n", "bot")

    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)

def display_message2(message, is_user):
    ## it may cause exception some times
    chat_box.config(state=tk.NORMAL)
   
    # Calculate the width needed for the text
    chat_box_width = chat_box.winfo_width()
    chat_box.update_idletasks()  # Ensure dimensions are updated
    text_width = chat_box.bbox(tk.END)[2]  # Get the width of the text
    max_width = min(text_width + 20, chat_box_width)  # Add padding and ensure it's within the chat box width

    if is_user:
        tag = "user"
        background_color = "back"
    else:
        tag = "bot"
        background_color = "#F05E77"

    chat_box.insert(tk.END, f"{message}\n", tag)
    chat_box.tag_configure(tag, background=background_color, foreground="black")

    # Ensure the chat box width adjusts to content width
    chat_box.config(width=max_width)
    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)

# Function to restart the chatbot
def restart_chat():
    global user_numbers, current_step, conversation_history
    conversation_history = [
            {"role": "system", "content": "You are a friendly chatbot at an exhibit called AI for wellbeing focused on posture and back health. This exhibit is part of a design festival exhibition in London. Engage visitors and ask a series of questions embedded in conversation to learn about their spine health routine. "},
            {"role": "assistant", "content": "Engage visitors and ask a series of questions embedded in conversation to learn about their spine health routine."}
        ]
    user_numbers = []
    current_step = 0
    chat_box.config(state=tk.NORMAL)
    chat_box.delete(1.0, tk.END)  # Clear chat history
    chat_box.config(state=tk.DISABLED)
    canvas.delete("all")  # Clear the pentagon graph
    summary_text.config(state=tk.NORMAL)
    summary_text.delete(1.0, tk.END)
    summary_text.insert(tk.END, "You will receive a summary of your results here at the end of the assessment.")
    start_chat()  # Start fresh



# Create the main window
root = ttkb.Window(themename="lumen")  # cosmo  morph  
root.title("AI for Wellbeing")
root.geometry("2800x1800")
root.configure(bg="lightgrey")  # Set background color for the main window


# Create the left frame for chat and input
left_frame = ttkb.Frame(root, bootstyle="light", width=600, height=600)   #"#F1F0EB"
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create the right frame for the pentagon graph
right_frame = ttkb.Frame(root, bootstyle="light", width=800, height=800) 
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)


# Add title text at the top of the right frame
title_label = tk.Label(right_frame, text="Try paying attention to...", font=("Calibri", 18, "bold")) #, bg="#F6F6F6", fg="black"
title_label.pack(padx = 20,pady=10, anchor="w")

# Create a canvas in the right frame for the pentagon graph
canvas = Canvas(right_frame, width=1400, height=800, bg="white",bd=1, relief="solid", highlightbackground="grey" , highlightthickness = 2,
    highlightcolor = 'light grey')   #  highlightthickness=2
canvas.pack(padx = 20,pady=20,anchor="center") #, 
# Create a Canvas to display the pentagon graph inside the chat window
canvas_frame = tk.Frame(right_frame, bg="white")
canvas_frame.pack(pady=10)

# Add title text at the top of the right frame
title_label_summary = tk.Label(right_frame, text="Summary", font=("Calibri", 18, "bold"))#, bg="#F6F6F6", fg="black"
title_label_summary.pack(padx = 20, pady=10, anchor="w")


# Add a text box underneath the pentagon for the summary
summary_text = tk.Text(right_frame, height=400, bg="white", fg="black", wrap=tk.WORD, font=("Calibri", 16))
summary_text.pack(pady=20, padx=20, fill=tk.BOTH)

# Insert the summary text
summary_text.insert(tk.END, "You will receive a summary of your results here at the end of the assessment.")
summary_text.config(state=tk.DISABLED)  # Make the text box read-only

# Load the image for the restart button (make sure to have restart_icon.png in your directory)
restart_icon = PhotoImage(file="newrestart.png")
restart_icon = restart_icon.subsample(2, 2)  # Adjust the size of the icon if necessary

# Add Restart button at the top of the window with an icon
restart_button = ttkb.Button(left_frame, image=restart_icon, command=restart_chat, bootstyle="light") #create_rounded_button_with_icon(left_frame, restart_icon, restart_chat)#
restart_button.pack(padx = 0, pady=10, anchor='w')


# Load the images for user and bot (make sure to have user_icon.png and bot_icon.png in your directory)
user_icon = PhotoImage(file="usericon.png")
user_icon = user_icon.subsample(15, 15)
bot_icon = PhotoImage(file="boticon.png")
bot_icon = bot_icon.subsample(15, 15)

# Create a frame for chat history with light grey background
chat_frame = tk.Frame(left_frame, bg="white")
chat_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Create a scrollable text box for chat history with light grey background
chat_box = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED, height=15, width = 60, bg="white", fg="black")
chat_box.config(font=("Calibri", 16)) 

chat_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Define tags for text alignment
chat_box.tag_config("user", justify='left', foreground="black", background="white") #"#CDD28E"
chat_box.tag_config("bot", justify='left', foreground="#F05E77", background="white")
chat_box.tag_configure("hanging", lmargin1=0, lmargin2=15)

# Frame for input box and send button
input_frame = tk.Frame(left_frame, bg="white")
input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

# Scrollable input box with a grey border
input_box = tk.Text(input_frame, wrap=tk.WORD, height=4, font=("Calibri", 16), bg="white", fg="black", bd=1, relief="solid") ##D9D9D9
input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 25))
input_box.focus_set()  # Set the focus to the input box to prompt the user to type


# Bind Enter key to send_message function
input_box.bind("<Return>", send_message)
# Load the image for the send button (make sure to have send_icon.png in your directory)

send_icon = PhotoImage(file="newsend.png")
send_icon = send_icon.subsample(3, 3)  # Adjust the size of the icon if necessary

# Button to send message with an icon
send_button = ttkb.Button(input_frame, image=send_icon, command=send_message, bootstyle = "light")
send_button.pack(padx = 0, pady = 0, anchor='w')



# Start the chat with an initial message
start_chat()

# Run the main loop
root.mainloop()

