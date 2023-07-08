import tkinter as tk
from tkinter import ttk
import vlc

chapters = [
    {"title": "Chapter 1", "time": 0},
    {"title": "Chapter 2", "time": 10000},
    {"title": "Chapter 3", "time": 20000},
    # TODO
    #  set chapters
]

class VideoPlayer:
    def __init__(self, video_path):
        self.root = tk.Tk()
        self.root.title("Video Player")

        self.video_path = video_path
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.player_frame = tk.Frame(self.root)
        self.player_frame.pack()

        self.canvas = tk.Canvas(self.player_frame, width=960, height=720)
        self.canvas.pack()

        self.timeline = ttk.Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL, command=self.update_video)
        self.timeline.pack(fill=tk.X)

        self.time_label = tk.Label(self.root, text="00:00 / 00:00")
        self.time_label.pack()

        self.replay_button = ttk.Button(self.root, text="↻", command=self.replay_video)
        self.replay_button.pack()
        self.replay_button.pack_forget()  # Hide the replay button initially

        self.play_button = ttk.Button(self.root, text="⏸", command=self.toggle_playback)
        self.play_button.pack(side="left")
        self.play_button.pack()

        self.chapter_buttons_frame = tk.Frame(self.root)
        self.chapter_buttons_frame.pack()

        # Create a chapter list with buttons
        for chapter in chapters:
            chapter_button = tk.Button(
                self.chapter_buttons_frame,
                text=chapter["title"],
                command=lambda chapter_time=chapter["time"]: self.select_chapter(chapter_time)
            )
            chapter_button.pack(side="left")

        self.play()

        self.root.mainloop()

    def play(self):
        media = self.instance.media_new(self.video_path)
        media.get_mrl()
        self.player.set_media(media)

        # Set the player window inside the frame
        self.player.set_hwnd(self.canvas.winfo_id())

        self.player.play()

        # Register an event for the end of video playback
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.handle_end_reached)

        # Update the time labels periodically
        self.update_time_labels()

    def toggle_playback(self):
        if self.player.get_state() == vlc.State.Playing:
            self.player.pause()
            self.play_button.config(text="▶")
            self.play_button.pack(side="left")
        elif self.player.get_state() == vlc.State.Paused:
            self.player.play()
            self.play_button.config(text="⏸")
            self.play_button.pack(side="left")

    def update_time_labels(self):
        if self.player.get_state() == vlc.State.Playing or self.player.get_state() == vlc.State.Paused:
            # Get the current time and total duration in milliseconds
            current_time = self.player.get_time()
            total_duration = self.player.get_length()

            # Convert the time values to the format HH:MM:SS
            current_time_formatted = self.format_time(current_time)
            total_duration_formatted = self.format_time(total_duration)

            # Update the time label
            self.time_label.config(text=f"{current_time_formatted} / {total_duration_formatted}")

        # Schedule the next update after 200 milliseconds
        self.root.after(200, self.update_time_labels)

    def format_time(self, milliseconds):
        seconds = int(milliseconds / 1000)
        minutes = int(seconds / 60)
        hours = int(minutes / 60)
        seconds %= 60
        minutes %= 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def update_video(self, value):
        position = float(value) / 100 * self.player.get_length()
        self.player.set_time(int(position))

    def handle_end_reached(self, event):
        # When the end of video is reached, show the replay button
        self.replay_button.pack()

    def replay_video(self):
        # Hide the replay button
        self.replay_button.pack_forget()

        # Reset the player's position to the beginning
        self.player.stop()
        self.player.set_time(0)
        self.player.play()

    def select_chapter(self, chapter_time):
        self.player.set_time(chapter_time)
        self.player.play()

        # Update the timeline and time labels accordingly
        self.timeline.set(chapter_time / self.player.get_length() * 100)
        self.update_time_labels()


if __name__ == '__main__':
    # TODO
    #  set path
    video_path = '.mp4'
    player = VideoPlayer(video_path)
