import re
import customtkinter as ctk
from tkinter import messagebox, Listbox, Canvas
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from PIL import Image
from customtkinter import CTkImage

# ✅ YouTube API
YOUTUBE_API_KEY = "AIzaSyA37JaGIJ5cVQGXbvBgE7rFk6M1IqMo3cY"   # Replace with yours
try:
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
except Exception:
    messagebox.showerror("Error", "Invalid YouTube API Key!")

# ✅ CustomTkinter theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def extract_video_id(url):
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?/\\s]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None


def get_youtube_comments(video_id):
    comments = []
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
            maxResults=100
        )
        response = request.execute()
        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
    except HttpError:
        return []
    return comments


def analyze_sentiment(comment):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(comment)
    if score['compound'] > 0.05:
        return "Good"
    elif score['compound'] < -0.05:
        return "Bad"
    else:
        return "Neutral"


def analyze_comments():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a valid YouTube URL.")
        return

    video_id = extract_video_id(url)
    if not video_id:
        messagebox.showerror("Error", "Invalid YouTube URL.")
        return

    comments = get_youtube_comments(video_id)
    if not comments:
        messagebox.showinfo("No Comments", "No comments found or comments are disabled.")
        return

    good, bad, neutral = 0, 0, 0
    comment_listbox.delete(0, "end")
    for comment in comments:
        sentiment = analyze_sentiment(comment)
        comment_listbox.insert("end", f"{comment[:50]}... - {sentiment}")
        if sentiment == "Good":
            good += 1
        elif sentiment == "Bad":
            bad += 1
        else:
            neutral += 1

    update_circle(total_canvas, len(comments))
    update_circle(good_canvas, good)
    update_circle(bad_canvas, bad)
    update_circle(neutral_canvas, neutral)

    screen1.pack_forget()
    screen2.pack(fill="both", expand=True)


def back_to_input():
    screen2.pack_forget()
    screen1.pack(fill="both", expand=True)


def update_circle(canvas, number):
    canvas.delete("all")
    canvas.create_oval(10, 10, 90, 90, fill="#1E90FF", outline="white", width=3)
    canvas.create_text(50, 50, text=str(number), font=("Arial", 20, "bold"), fill="white")


# ✅ UI Setup
root = ctk.CTk()
root.title("YouTube Comment Analyzer")
root.geometry("1200x700")
root.state("zoomed")

# ✅ Load Background Image
try:
    bg_image = Image.open("C:\\Users\\shrad\\Downloads\\Youtube\\Youtube\\bg.jpg")  # Change path if needed
    bg_image = bg_image.resize((1920, 1080))
    bg_ctk_image = CTkImage(light_image=bg_image, dark_image=bg_image, size=(1920, 1080))
except Exception as e:
    print("Background load error:", e)
    bg_ctk_image = None

# Screen 1
screen1 = ctk.CTkFrame(root)
screen1.pack(fill="both", expand=True)

if bg_ctk_image:
    bg_label1 = ctk.CTkLabel(screen1, image=bg_ctk_image, text="")
    bg_label1.place(relwidth=1, relheight=1)

# Glassmorphic-style input box (solid dark with rounded corners)
input_box = ctk.CTkFrame(
    screen1,
    corner_radius=20,
    fg_color="#1e1e1e",  # solid dark (no alpha)
)
input_box.place(relx=0.5, rely=0.45, anchor="center", relwidth=0.4, relheight=0.25)

url_entry = ctk.CTkEntry(input_box, placeholder_text="Enter YouTube URL",
                         font=("Arial", 18), height=50, corner_radius=10)
url_entry.pack(pady=20, padx=20, fill="x")

youtube_button = ctk.CTkButton(input_box, text="🎥 Analyze YouTube Comments", fg_color="#007BFF",
                               hover_color="#0056b3", height=40,
                               command=analyze_comments, font=("Arial", 16, "bold"))
youtube_button.pack(pady=5, padx=20, fill="x")

# Screen 2
screen2 = ctk.CTkFrame(root)

if bg_ctk_image:
    bg_label2 = ctk.CTkLabel(screen2, image=bg_ctk_image, text="")
    bg_label2.place(relwidth=1, relheight=1)

results_box = ctk.CTkFrame(screen2, corner_radius=20, fg_color="#1e1e1e")
results_box.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.6)

canvas_frame = ctk.CTkFrame(results_box, fg_color="transparent")
canvas_frame.pack(pady=10)

total_canvas = Canvas(canvas_frame, width=100, height=100, bg="black", highlightthickness=0)
good_canvas = Canvas(canvas_frame, width=100, height=100, bg="black", highlightthickness=0)
bad_canvas = Canvas(canvas_frame, width=100, height=100, bg="black", highlightthickness=0)
neutral_canvas = Canvas(canvas_frame, width=100, height=100, bg="black", highlightthickness=0)

for i, (label_text, canvas) in enumerate([
    ("Total", total_canvas), ("😊 Good", good_canvas), ("😡 Bad", bad_canvas), ("😐 Neutral", neutral_canvas)
]):
    canvas.grid(row=0, column=i, padx=20)
    ctk.CTkLabel(canvas_frame, text=label_text, font=("Arial", 14)).grid(row=1, column=i)

comment_listbox = Listbox(results_box, width=80, height=10, font=("Arial", 12))
comment_listbox.pack(pady=10)

ctk.CTkButton(results_box, text="⬅ Back", command=back_to_input, font=("Arial", 16),
              fg_color="#6c757d", hover_color="#5a6268").pack(pady=10)

root.mainloop()
